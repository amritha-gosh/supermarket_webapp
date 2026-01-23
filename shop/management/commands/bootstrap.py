from django.core.management.base import BaseCommand
from shop.models import Store

class Command(BaseCommand):
    help = "Seed initial data like stores (idempotent)."

    def handle(self, *args, **options):
        stores = [
            {"key": "wigan", "name": "Wigan", "active": True},
            {"key": "southport", "name": "Southport", "active": True},
        ]

        created = 0
        for data in stores:
            _, was_created = Store.objects.get_or_create(
                key=data["key"],
                defaults=data
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Bootstrap done. Created {created} stores."))
