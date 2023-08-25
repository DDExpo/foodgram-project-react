from csv import DictReader
from typing import List, Dict, Type

from django.db import models
from django.core.management.base import BaseCommand

from recipes.models import Ingredients, MODELS_FIELDS, Tags
from foodgram.settings import DATA_DIR


MODELS_CSV: Dict[Type[models.Model], str] = {Ingredients: 'ingredients.csv',
                                             Tags: 'tags.csv'}


class Command(BaseCommand):
    help = 'populate database with instance of Ingredient model'

    def get_model_fields(self, model: Type[models.Model]) -> List[str]:
        return [field.name for field in model._meta.get_fields()
                if field.name in MODELS_FIELDS]

    def handle(self, *args, **options):

        for model_clas, file_data in MODELS_CSV.items():

            fields_model = self.get_model_fields(model_clas)
            data_to_create: List[models.Model] = []

            with open(
                f'{DATA_DIR}/{str(model_clas._meta.model_name)}/{file_data}',
                 'r', encoding='utf-8') as data:

                reader = DictReader(data, fieldnames=fields_model)

                for record in reader:
                    data_to_create.append(model_clas(**record))

                model_clas.objects.bulk_create(data_to_create)

            self.stdout.write(self.style.SUCCESS(
                f'Данные {model_clas._meta.model_name} загружены!'))
