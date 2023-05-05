from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

import csv


TAGS = (
    ('Завтрак', '#E26C2D', 'breakfast'),
    ('Обед', '#49B64E', 'lunch'),
    ('Ужин', '#8775D2', 'dinner'),
        )

class Command(BaseCommand):
    help = 'Импортирует ингредиенты и тэги'

    def handle(self, *args, **options):
        #Добавить ингредиенты.
        with open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r',
            encoding='utf-8',
        ) as file:
            file_reader = csv.reader(file)
            for row in file_reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)
            file.close()
        #Добавить теги.
        for tag in TAGS:
            name, color, slug = tag
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(
            self.style.SUCCESS('Ингредиенты и тэги импортированны.'))