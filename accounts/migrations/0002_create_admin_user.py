from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_admin_user(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')

    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@fitzone.local',
            'first_name': 'Admin',
            'last_name': 'User',
            'full_name': 'Admin User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )

    admin_user.email = 'admin@fitzone.local'
    admin_user.first_name = 'Admin'
    admin_user.last_name = 'User'
    admin_user.full_name = 'Admin User'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.password = make_password('admin123')
    admin_user.save()


def remove_admin_user(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, remove_admin_user),
    ]