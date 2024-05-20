import csv
from django.core.management.base import BaseCommand
from rpa.models import Publications

class Command(BaseCommand):
    help = 'Populate data to the Publications model from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['title']
                updates = {
                    "title" : row['title'],
                    "start_academic_month" : row['start_academic_month'],
                    "start_academic_year" : row['start_academic_year'],
                    "end_academic_month" : row['end_academic_month'],
                    "end_academic_year" : row['end_academic_year'],
                    "first_author" : row['first_author'],
                    "second_author" : row['second_author'],
                    "third_author" : row['third_author'],
                    "other_authors" : row['other_authors'],
                    "is_student_author" : row['is_student_author'],
                    "student_name" : row['student_name'],
                    "student_batch" : row['student_batch'],
                    "specification" : row['specification'],
                    "publication_type" : row['publication_type'],
                    "publication_name" : row['publication_name'],
                    "publisher" : row['publisher'],
                    "year_of_publishing" : row['year_of_publishing'],
                    "month_of_publishing" : int(row['month_of_publishing']) if row['month_of_publishing'] else None,
                    "volume" : row['volume'],
                    "page_number" : row['page_number'],
                    "indexing" : row['indexing'],
                    "quartile" : row['quartile'],
                    "citation" : row['citation'],
                    "doi" : row['doi'],
                    "front_page_path" : row['front_page_path'],
                    "url" : row['url'],
                    "issn" : row['ISSN'],
                    "verified" : row['verified'],
                    "admin_verified" : row['admin_verified'],
                }

                # Creating or updating the publication
                publication, created = Publications.objects.update_or_create(
                    uniqueid=row['uniqueid'],
                    defaults=updates
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Publication "{title}" created successfully'))
                else:
                    self.stdout.write(self.style.WARNING(f'Publication "{title}" updated successfully'))