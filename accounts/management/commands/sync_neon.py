import json
from datetime import datetime

import dj_database_url
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.db.utils import ConnectionHandler

MODEL_LABELS = [
    'accounts.CustomUser',
    'membership.MembershipPlan',
    'membership.UserMembership',
]


class Command(BaseCommand):
    help = (
        'Compare local SQLite data against a remote Neon database and optionally import missing records.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--remote-url',
            help='Remote Neon DATABASE_URL to compare against',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only report differences without importing anything.',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Import missing local records into the remote database.',
        )
        parser.add_argument(
            '--import',
            dest='apply',
            action='store_true',
            help='Alias for --apply.',
        )
        parser.add_argument(
            '--export-file',
            help='Export local model records to a JSON file for later import.',
        )
        parser.add_argument(
            '--models',
            default=','.join(MODEL_LABELS),
            help='Comma-separated list of model labels to compare or export.',
        )

    def handle(self, *args, **options):
        remote_url = options.get('remote_url')
        dry_run = options['dry_run']
        apply = options['apply']
        export_file = options.get('export_file')
        model_labels = [label.strip() for label in options['models'].split(',') if label.strip()] or MODEL_LABELS

        if not remote_url and not export_file:
            self.stderr.write('ERROR: You must specify --remote-url for comparison/import or --export-file for export.')
            return

        if remote_url:
            # Configure remote database connection
            remote_db_config = dj_database_url.config(
                default=remote_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
            if not remote_db_config.get('ENGINE'):
                remote_db_config['ENGINE'] = 'django.db.backends.postgresql'

            # Ensure settings.DATABASES exists and add remote config
            if not hasattr(settings, 'DATABASES'):
                settings.DATABASES = {}
            settings.DATABASES['remote_neon'] = remote_db_config
            # Propagate TIME_ZONE to remote DB settings for consistency
            settings.DATABASES['remote_neon']['TIME_ZONE'] = getattr(settings, 'TIME_ZONE', 'UTC')
            # Ensure autocommit behavior is enabled for remote connections
            settings.DATABASES['remote_neon']['AUTOCOMMIT'] = True
            # Register with Django connections
            if 'remote_neon' not in connections.databases:
                connections.databases['remote_neon'] = settings.DATABASES['remote_neon']
            # Force connection initialization
            _ = connections['remote_neon']
            self.stdout.write('Remote database connection configured as `remote_neon`.')

        if export_file:
            self._export_local_data(model_labels, export_file)

        if remote_url and model_labels:
            self._compare_and_sync(model_labels, dry_run, apply)

    def _setup_remote_connection(self, remote_url):
        remote_db_config = dj_database_url.config(
            default=remote_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
        if not remote_db_config.get('ENGINE'):
            remote_db_config['ENGINE'] = 'django.db.backends.postgresql'

        settings.DATABASES['remote_neon'] = remote_db_config
        if 'remote_neon' not in connections.databases:
            connections.databases['remote_neon'] = settings.DATABASES['remote_neon']

        # Force connection initialization
        _ = connections['remote_neon']
        self.stdout.write('Remote database connection configured as `remote_neon`.')

    def _export_local_data(self, model_labels, export_file):
        payload = []
        for model_label in model_labels:
            app_label, model_name = model_label.split('.')
            model = apps.get_model(app_label, model_name)
            queryset = model.objects.using('default').all()
            records = [self._serialize_instance(obj) for obj in queryset]
            payload.append({'model': model_label, 'records': records})

        with open(export_file, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, default=str)

        self.stdout.write(f'Exported {len(payload)} model sections to {export_file}.')

    def _serialize_instance(self, instance):
        data = {}
        for field in instance._meta.concrete_fields:
            value = getattr(instance, field.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            data[field.name] = value
        return data

    def _compare_and_sync(self, model_labels, dry_run, apply):
        for model_label in model_labels:
            app_label, model_name = model_label.split('.')
            model = apps.get_model(app_label, model_name)
            self.stdout.write(f'\n== Comparing {model_label} ==')
            local_items = list(model.objects.using('default').all())
            remote_items = list(model.objects.using('remote_neon').all())
            local_map = {self._record_key(model_label, obj): obj for obj in local_items}
            remote_map = {self._record_key(model_label, obj): obj for obj in remote_items}

            missing_keys = [key for key in local_map if key not in remote_map]
            self.stdout.write(f'Local count: {len(local_items)}, Remote count: {len(remote_items)}, Missing on remote: {len(missing_keys)}')
            for key in missing_keys[:20]:
                self.stdout.write(f'  + {key}')
            if len(missing_keys) > 20:
                self.stdout.write(f'  ... and {len(missing_keys)-20} more')

            if apply and missing_keys:
                self.stdout.write('Applying missing records to remote...')
                for key in missing_keys:
                    local_obj = local_map[key]
                    self._copy_object_to_remote(model_label, local_obj)
                self.stdout.write(f'Imported {len(missing_keys)} {model_label} records to remote.')
            elif dry_run:
                self.stdout.write('Dry run only; no changes applied.')

    def _record_key(self, model_label, obj):
        if model_label == 'accounts.CustomUser':
            return (obj.email or obj.username).lower()
        if model_label == 'membership.MembershipPlan':
            return f'{obj.name}|{obj.duration}'
        if model_label == 'membership.UserMembership':
            return f'{obj.user.email.lower() if obj.user and obj.user.email else obj.user_id}|{obj.plan.name}|{obj.start_date.isoformat()}'
        return str(obj.pk)

    def _copy_object_to_remote(self, model_label, obj):
        if model_label == 'accounts.CustomUser':
            self._copy_custom_user(obj)
        elif model_label == 'membership.MembershipPlan':
            self._copy_plan(obj)
        elif model_label == 'membership.UserMembership':
            self._copy_membership(obj)
        else:
            self.stderr.write(f'Unsupported model for remote sync: {model_label}')

    def _copy_custom_user(self, obj):
        User = get_user_model()
        fields = [f.name for f in User._meta.concrete_fields if f.name not in ('id',)]
        data = {name: getattr(obj, name) for name in fields}
        remote_user = User.objects.using('remote_neon').create(**data)
        self.stdout.write(f'Created remote user {remote_user.email}')

    def _copy_plan(self, obj):
        Plan = apps.get_model('membership', 'MembershipPlan')
        fields = [f.name for f in Plan._meta.concrete_fields if f.name not in ('id',)]
        data = {name: getattr(obj, name) for name in fields}
        remote_plan = Plan.objects.using('remote_neon').create(**data)
        self.stdout.write(f'Created remote plan {remote_plan.name} ({remote_plan.duration})')

    def _copy_membership(self, obj):
        Membership = apps.get_model('membership', 'UserMembership')
        user_key = (obj.user.email or obj.user.username).lower()
        plan_key = f'{obj.plan.name}|{obj.plan.duration}'
        try:
            remote_user = apps.get_model('accounts', 'CustomUser').objects.using('remote_neon').get(email__iexact=(obj.user.email or obj.user.username))
        except Exception:
            self.stderr.write(f'Unable to find remote user for membership {user_key}; skipping')
            return
        try:
            remote_plan = apps.get_model('membership', 'MembershipPlan').objects.using('remote_neon').get(name=obj.plan.name, duration=obj.plan.duration)
        except Exception:
            self.stderr.write(f'Unable to find remote plan for membership {plan_key}; skipping')
            return

        fields = [f.name for f in Membership._meta.concrete_fields if f.name not in ('id',)]
        data = {name: getattr(obj, name) for name in fields}
        data['user'] = remote_user
        data['plan'] = remote_plan
        remote_membership = Membership.objects.using('remote_neon').create(**data)
        self.stdout.write(f'Created remote membership for {remote_user.email} plan {remote_plan.name}')
