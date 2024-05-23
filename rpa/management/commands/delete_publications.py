import csv
from django.core.management.base import BaseCommand
from rpa.models import Publications


class Command(BaseCommand):

    help = 'Delete records from the Publications model from a CSV file based on uniqueIDs'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

            
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        unique_ids = self.read_id(csv_file)
        if unique_ids:
            for unique_id in unique_ids:
                temp = Publications.objects.filter(uniqueid=unique_id)
                if temp:
                    temp.delete()
                    self.stdout.write(self.style.SUCCESS(f'Publication {unique_id} deleted successfully.'))
                else:
                    self.stdout.write(self.style.ERROR(f'Publication {unique_id} not deleted. Publication not found.'))


    def read_id(self, csv_file):
        with open(csv_file,'r', encoding='utf-8') as f:
            unique_ids = []
            reader = csv.reader(f)
            for row in reader:
                if row:
                    unique_ids.append(row[0])
        return unique_ids
    