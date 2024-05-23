import csv
from django.core.management.base import BaseCommand
from rpa.models import Publications

class Command(BaseCommand):
    help = 'Insert data to the Publications model from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['title']
                unique_id = row['uniqueid']

                updates = row.copy()

                for key, value in row.items():
                    if key == "ISSN":
                        temp = updates[key]
                        del updates[key]
                        updates["issn"] = temp
                        continue
                    if not value:
                        del updates[key]
                    if value.lower() == "null" or value.lower() == "none":
                        del updates[key]
                
                try:
                    created = Publications.objects.create(**updates)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Publication "{title}" with UID "{unique_id}" created successfully'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Publication "{title}" with UID "{unique_id}" was not created successfully'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Publication "{title}" with UID "{unique_id}" was not created successfully'))
                    self.stdout.write(self.style.ERROR(f'Error: {e}'))
                    continue
                
