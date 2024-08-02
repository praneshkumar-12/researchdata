import csv
from django.core.management.base import BaseCommand
from rpa.models import Users

class Command(BaseCommand):
    help = 'Insert data to the Users model from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                updates = {
                    "staff_name": row["staff_name"],
                    "email_id": row["email_id"],
                    "passkey": row["passkey"]
                }
                
                try:
                    created = Users.objects.create(**updates)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Admin "{row['staff_name']}" with email ID "{row['email_id']}" created successfully'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Admin "{row['staff_name']}" with email ID "{row['email_id']}" was not created successfully'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Admin "{row['staff_name']}" with email ID "{row['email_id']}" was not created successfully'))
                    self.stdout.write(self.style.ERROR(f'Error: {e}'))
                    continue
                
