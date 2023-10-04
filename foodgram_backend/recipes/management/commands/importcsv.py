import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        Command.run_seed()
        self.stdout.write('done.')

    @staticmethod
    def clear_data():
        """Deletes all the table data"""
        print('Clear data started')
        Ingredient.objects.all().delete()

    @staticmethod
    def run_seed():
        Command.clear_data()
        Command.seed_ingredients()

    @staticmethod
    def seed_ingredients():
        print('Seed ingredients started')
        with open('../data/ingredients.csv') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                ingredient = Ingredient(name=row[0], measurement_unit=row[1])
                ingredient.save()

