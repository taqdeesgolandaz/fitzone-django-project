from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
import sys


class Command(BaseCommand):
    help = "Check database connectivity and basic data (users, migrations)"

    def handle(self, *args, **options):
        self.stdout.write('Checking database connection...')

        # Print configured DB engine and NAME for clarity
        db_default = settings.DATABASES.get('default', {})
        engine = db_default.get('ENGINE')
        name = db_default.get('NAME')
        self.stdout.write(f"Configured DB engine: {engine}")
        self.stdout.write(f"Configured DB name: {name}")

        # Try a simple SQL query to ensure the DB is reachable
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT version()')
                version = cursor.fetchone()
                self.stdout.write(f"DB version: {version[0] if version else 'unknown'}")
        except Exception as e:
            self.stderr.write(f"ERROR: Unable to run query against the DB: {e}")
            sys.exit(2)

        # Check django_migrations table
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM django_migrations")
                migrations_count = cursor.fetchone()[0]
                self.stdout.write(f"Applied migrations count: {migrations_count}")
        except Exception:
            self.stdout.write("django_migrations table not found or cannot be queried. Did you run migrations?")

        # Check users
        User = get_user_model()
        try:
            total = User.objects.count()
            self.stdout.write(f"User table row count: {total}")

            admin = User.objects.filter(username='adminuser').values('id', 'username', 'email', 'is_staff').first()
            if admin:
                self.stdout.write(f"Found adminuser: {admin}")
            else:
                self.stdout.write("No user with username 'adminuser' found.")
        except Exception as e:
            self.stderr.write(f"ERROR querying User model: {e}")
            self.stderr.write('Hint: ensure `AUTH_USER_MODEL` is correct and migrations are applied on the target DB')

        # Sample some other tables (optional): count a few app tables if present
        sample_tables = ['accounts_customuser', 'auth_user', 'workouts_userworkoutprogress']
        for tbl in sample_tables:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT count(*) FROM {tbl}")
                    cnt = cursor.fetchone()[0]
                    self.stdout.write(f"{tbl}: {cnt}")
            except Exception:
                # ignore missing tables
                pass

        self.stdout.write('DB check complete.')
