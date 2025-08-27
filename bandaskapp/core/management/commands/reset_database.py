from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Reset the database completely and start fresh'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation',
        )
    
    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING(
                'This will DELETE ALL DATA and reset the database completely!'
            ))
            confirm = input('Are you sure? Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write('Database reset cancelled.')
                return
        
        self.stdout.write(self.style.ERROR('Resetting database...'))
        
        # Get database file path
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        
        # Close database connection
        connection.close()
        
        # Remove database file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(f'✓ Removed database file: {db_path}')
        
        # Run migrations to create fresh database
        self.stdout.write('Creating fresh database...')
        call_command('migrate', verbosity=0)
        self.stdout.write('✓ Database created and migrated')
        
        # Create superuser if needed
        self.stdout.write('Creating superuser...')
        try:
            call_command('createsuperuser', interactive=False, username='admin', email='admin@example.com')
            self.stdout.write('✓ Superuser created (username: admin, password: admin)')
        except:
            self.stdout.write('⚠ Superuser creation failed (may already exist)')
        
        # Setup hardware
        self.stdout.write('Setting up hardware configuration...')
        call_command('setup_hardware')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase reset completed successfully!'))
        self.stdout.write('You can now start the application with a fresh database.')
