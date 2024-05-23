import csv
from django.core.management.base import BaseCommand
from rpa.models import Publications

class Command(BaseCommand):
    help = 'Update data to the Publications model from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)
                unique_id = row['uniqueid']

                updates = row.copy()

                for key, value in row.items():
                    if key == "ISSN":
                        temp = updates[key]
                        del updates[key]
                        updates["issn"] = temp
                        continue
                    if key == "uniqueid":
                        del updates[key]
                    if not value:
                        del updates[key]
                    if value.lower() == "null" or value.lower() == "none":
                        del updates[key]
                    

                update_object = Publications.objects.filter(uniqueid = unique_id)

                if not update_object:
                    self.stdout.write(self.style.ERROR(f'Publication with UID "{unique_id}" not found'))
                else:
                    update_object.update(**updates)
                    self.stdout.write(self.style.SUCCESS(f'Publication with UID "{unique_id}" updataed successfully'))