from django.core.management.base import BaseCommand
from modules.identity_access.application.services import ensure_seed_users

class Command(BaseCommand):
    help = "Seed default users for dev (admin/registrar/instructor/student)"

    def handle(self, *args, **options):
        users = ensure_seed_users()
        self.stdout.write(self.style.SUCCESS(f"Seeded users: {', '.join(users)}"))
