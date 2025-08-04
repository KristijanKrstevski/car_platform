import os
import json
from django.core.management.base import BaseCommand
from dealership_app.models import CarBrand, CarModel


class Command(BaseCommand):
    help = "Load car brands and models from cars.json"

    def handle(self, *args, **kwargs):
        # Точно најди го manage.py директориумот
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(base_dir, "cars.json")

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"❌ cars.json NOT FOUND at: {json_path}"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        created_brands = 0
        created_models = 0

        for brand_name, models in data.items():
            brand, created = CarBrand.objects.get_or_create(name=brand_name.strip())
            if created:
                created_brands += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created brand: {brand_name}"))

            for model_name in models:
                if model_name.strip():
                    _, model_created = CarModel.objects.get_or_create(
                        brand=brand, name=model_name.strip()
                    )
                    if model_created:
                        created_models += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Finished loading: {created_brands} brands and {created_models} models!"
            )
        )
