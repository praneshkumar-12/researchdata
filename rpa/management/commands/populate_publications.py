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
                temp = {
                    "title" : row.get('title') if row.get('title') else None,
                    "start_academic_month" : row.get('start_academic_month') if row.get('start_academic_month') else None,
                    "start_academic_year" : row.get('start_academic_year') if row.get('start_academic_year') else None,
                    "end_academic_month" : row.get('end_academic_month') if row.get('end_academic_month') else None,
                    "end_academic_year" : row.get('end_academic_year') if row.get('end_academic_year') else None,
                    "first_author" : row.get('first_author') if row.get('first_author') else None,
                    "second_author" : row.get('second_author') if row.get('second_author') else None,
                    "third_author" : row.get('third_author') if row.get('third_author') else None,
                    "other_authors" : row.get('other_authors') if row.get('other_authors') else None,
                    "is_student_author" : row.get('is_student_author') if row.get('is_student_author') else None,
                    "student_name" : row.get('student_name') if row.get('student_name') else None,
                    "student_batch" : row.get('student_batch') if row.get('student_batch') else None,
                    "specification" : row.get('specification') if row.get('specification') else None,
                    "publication_type" : row.get('publication_type') if row.get('publication_type') else None,
                    "publication_name" : row.get('publication_name') if row.get('publication_name') else None,
                    "publisher" : row.get('publisher') if row.get('publisher') else None,
                    "year_of_publishing" : row.get('year_of_publishing') if row.get('year_of_publishing') else None,
                    "month_of_publishing" : row.get('month_of_publishing') if row.get('month_of_publishing') else None,
                    "volume" : row.get('volume') if row.get('volume') else None,
                    "page_number" : row.get('page_number') if row.get('page_number') else None,
                    "indexing" : row.get('indexing') if row.get('indexing') else None,
                    "quartile" : row.get('quartile') if row.get('quartile') else None,
                    "citation" : row.get('citation') if row.get('citation') else None,
                    "doi" : row.get('doi') if row.get('doi') else None,
                    "front_page_path" : row.get('front_page_path') if row.get('front_page_path') else None,
                    "url" : row.get('url') if row.get('url') else None,
                    "issn" : row.get('ISSN') if row.get('ISSN') else None,
                    "verified" : row.get('verified') if row.get('verified') else None,
                    "admin_verified" : row.get('admin_verified') if row.get('admin_verified') else None,
                    "impact_factor": row.get("impact_factor") if row.get("impact_factor") else None,
                }

                updates = temp.copy()

                for key, value in temp.items():
                    if not value:
                        del updates[key]

                # Creating or updating the publication
                publication, created = Publications.objects.update_or_create(
                    uniqueid=row['uniqueid'],
                    defaults=updates
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Publication "{title}" created successfully'))
                else:
                    self.stdout.write(self.style.WARNING(f'Publication "{title}" updated successfully'))