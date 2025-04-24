from rpa.models import Publications
from rpa.models import Edithistory
from rpa.forms import PublicationsForm
from rpa.models import Users
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
import random
from django.db import transaction
import string
import django.db.utils
import calendar
import os
from django.contrib import messages  # Import Django's messages framework
import json
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import pandas as pd
from django.shortcuts import render, redirect
from docx.enum.text import WD_COLOR_INDEX
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

from django.http import HttpResponse
from .models import Publications
from django.db.utils import IntegrityError
import rpa.extractor.extractor as Extractor
from rpa.edit_history import record_update
from rpa.edit_history import commit_record_updates


def admin_home(request):
    papers = Publications.objects.all()

    publication_list = []

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name != "admin" or name == str(None):
        return redirect("/rpa/login")

    for paper in papers:
        publication_list.append(paper)

    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

    context = {"papers": publication_list, "name": name}

    return render(request, "admin_home.html", context)



def admin_excel(request):
    if request.method == "GET":
        return render(request, "add_data_excel.html")

    elif request.method == "POST":
        faculty_name = request.session.get("FACULTY_NAME")
        if faculty_name != "admin":
            return HttpResponse("Unauthorized", status=403)
        
        excel_file = request.FILES.get("excelFile")
        if not excel_file:
            return HttpResponse("No file uploaded.", status=400)

        try:
            # Read all sheets from Excel file
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names
            
            records_to_insert = []
            records_to_update = []
            update_details = []
            skipped_records = []
            deletion_details = []  # Track detailed deletion information
            
            # Precompute mappings
            # Define sheet name to publication type mapping
            SHEET_TYPE_MAPPING = {
                'journal': ('Journal', 'Article'),
                'journals': ('Journal', 'Article'),
                'book': ('Book Chapter', 'inbook'),
                'books': ('Book Chapter', 'inbook'),
                'conference': ('Conference', 'Proceedings'),
                'conferences': ('Conference', 'Proceedings'),
                'proceedings': ('Conference', 'Proceedings')
            }

            # Define flexible column mappings with multiple possible Excel column names for each database field
            COLUMN_MAPPINGS = {
                ('Title of paper', 'Title', 'Paper Title', 'title'): 'title',
                ('Name of the author/s', 'Authors', 'First Author', 'Primary Author', 'first_author'): 'first_author',
                ('Second Author', 'Co-author 1', 'second_author'): 'second_author',
                ('Third Author', 'Co-author 2', 'third_author'): 'third_author',
                ('Other Authors', 'Additional Authors', 'Co-authors', 'other_authors'): 'other_authors',
                ('Student Author', 'Is Student Author', 'Student Publication', 'is_student_author'): 'is_student_author',
                ('Student Name', 'Author Student Name', 'student_name'): 'student_name',
                ('Student Batch', 'Batch', 'Student Year', 'student_batch'): 'student_batch',
                ('Specification', 'Paper Type', 'Article Type', 'specification'): 'specification',
                ('Publication Type', 'Type of Publication', 'Category', 'publication_type'): 'publication_type',
                ('Name of journal', 'Journal Name', 'Publication Name', 'Conference Name', 'Book Name', 'publication_name'): 'publication_name',
                ('Publisher', 'Publisher Name', 'Publishing House', 'publisher'): 'publisher',
                ('Year of publication', 'Year', 'Publication Year', 'year_of_publishing'): 'year_of_publishing',
                ('Month of Publication', 'Month', 'Publication Month', 'month_of_publishing'): 'month_of_publishing',
                ('Vol No', 'Volume', 'Volume Number', 'volume'): 'volume',
                ('Page No', 'Pages', 'Page Numbers', 'Page Range', 'page_number'): 'page_number',
                ('Indexing', 'Index Database', 'Indexed In', 'indexing'): 'indexing',
                ('Scopus', 'scopus', 'SCOPUS', 'Scopus Indexed', 'scopus_indexing'): 'scopus_indexing',
                ('WoS', 'wos', 'WOS', 'Web of Science', 'Web of Science Indexed', 'wos_indexing'): 'wos_indexing',
                ('UGC', 'UGC Care', 'UGC Indexed', 'ugc_indexing'): 'ugc_indexing',
                ('Quartile', 'Q', 'Journal Quartile', 'Q Rating', 'quartile'): 'quartile',
                ('Citation', 'Citation Count', 'Times Cited', 'citation'): 'citation',
                ('DOI', 'Digital Object Identifier', 'DOI Number', 'Link to article/paper/abstract of the article', 'doi'): 'doi',
                ('Front Page', 'Front Page Path', 'First Page', 'front_page_path'): 'front_page_path',
                ('URL', 'Link', 'Website Link', 'Link to website of the Journal', 'url'): 'url',
                ('ISSN number', 'ISSN', 'Journal ISSN', 'issn'): 'issn',
                ('Verified', 'Is Verified', 'Verification Status', 'verified'): 'verified',
                ('Admin Verified', 'Admin Verification', 'Admin Status', 'admin_verified'): 'admin_verified',
                ('Impact Factor', 'IF', 'Journal Impact Factor', 'impact_factor'): 'impact_factor',
                ('Start Academic Month', 'Academic Start Month', 'start_academic_month'): 'start_academic_month',
                ('Start Academic Year', 'Academic Start Year', 'start_academic_year'): 'start_academic_year',
                ('End Academic Month', 'Academic End Month', 'end_academic_month'): 'end_academic_month',
                ('End Academic Year', 'Academic End Year', 'end_academic_year'): 'end_academic_year'
            }

            # Create a flattened lookup dictionary for faster column matching
            COLUMN_LOOKUP = {
                name.strip().lower(): db_field 
                for names, db_field in COLUMN_MAPPINGS.items()
                for name in names
            }

            # Precompute quartile mapping
            QUARTILE_MAPPING = {
                **{str(i): f'Q{i}' for i in range(1, 5)},
                **{f'{i}st': f'Q{i}' for i in [1]},
                **{f'{i}nd': f'Q{i}' for i in [2]},
                **{f'{i}rd': f'Q{i}' for i in [3]},
                **{f'{i}th': f'Q{i}' for i in [4]},
                **{f'q{i}': f'Q{i}' for i in range(1, 5)},
                **{f'Q{i}': f'Q{i}' for i in range(1, 5)},
                **{f'quartile {i}': f'Q{i}' for i in range(1, 5)}
            }

            # Build all fields list once
            ALL_DB_FIELDS = list(set(COLUMN_MAPPINGS.values()))

            for sheet_name in sheet_names:
                # Determine publication type and specification based on sheet name
                sheet_lower = sheet_name.lower()
                publication_type, specification = ('Journal', 'Article')  # Default values
                
                # Find the best matching sheet type
                for key, value in SHEET_TYPE_MAPPING.items():
                    if key in sheet_lower:
                        publication_type, specification = value
                        break
                
                print(f"\nProcessing sheet: {sheet_name} (Type: {publication_type}, Spec: {specification})")
                
                # Read the sheet
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                print(f"Total rows in sheet: {len(df)}")
                print(f"Columns in sheet (Before Cleaning): {df.columns.tolist()}")

                # Map columns more efficiently using the precomputed lookup
                mapped_columns = {}
                for col in df.columns:
                    db_field = COLUMN_LOOKUP.get(col.strip().lower())
                    if db_field:
                        mapped_columns[col] = db_field

                # Rename columns based on mapping
                df = df.rename(columns=mapped_columns)
                print(f"Columns in sheet (After Renaming): {df.columns.tolist()}")

                # Initialize all possible fields with None to ensure no field is missed
                for field in ALL_DB_FIELDS:
                    if field not in df.columns:
                        df[field] = None

                # Replace NaN values with None
                df = df.where(pd.notnull(df), None)
            
                # Precompute months mapping
                MONTH_NAME_TO_NUMBER = {calendar.month_abbr[i].lower(): i for i in range(1, 13)}

                for idx, row in df.iterrows():
                    try:
                        # Initialize data dictionary with all possible fields set to None
                        data = {
                            'publication_type': publication_type,
                            'specification': specification,
                            'title': None,
                            'first_author': None,
                            'second_author': None,
                            'third_author': None,
                            'other_authors': None,
                            'is_student_author': None,
                            'student_name': None,
                            'student_batch': None,
                            'publication_name': None,
                            'publisher': None,
                            'year_of_publishing': None,
                            'month_of_publishing': None,
                            'volume': None,
                            'page_number': None,
                            'indexing': None,
                            'quartile': None,
                            'citation': None,
                            'doi': None,
                            'front_page_path': None,
                            'url': None,
                            'issn': None,
                            'verified': 'False',
                            'admin_verified': 'False',
                            'impact_factor': None,
                            'start_academic_month': None,
                            'start_academic_year': None,
                            'end_academic_month': None,
                            'end_academic_year': None
                        }

                        # Handle required fields
                        if not row.get('title'):
                            raise ValueError("Title is required")

                        # Process all fields systematically
                        for field in list(data.keys()):  # Create a copy of keys to avoid dictionary size change during iteration
                            if field in ['publication_type', 'specification', 'verified', 'admin_verified', 'doi', 'url']:
                                continue  # Skip these fields - they're already set with default values or will be handled separately
                            
                            value = row.get(field)
                            
                            # Check for garbage values and set to None if invalid
                            if isinstance(value, str) and not value.strip():
                                data[field] = None
                                continue
                                
                            if field in ['year_of_publishing', 'volume', 'citation', 'start_academic_year', 'end_academic_year']:
                                try:
                                    data[field] = int(float(str(value).strip()))
                                except (ValueError, TypeError):
                                    data[field] = None
                            elif field in ['impact_factor']:
                                try:
                                    data[field] = float(str(value).strip())
                                except (ValueError, TypeError):
                                    data[field] = None
                            elif field == 'is_student_author':
                                val = str(value).strip().lower()
                                data[field] = val in ['yes', 'true', '1']
                            elif field == 'month_of_publishing':
                                month = str(value).strip().lower()
                                data[field] = str(MONTH_NAME_TO_NUMBER.get(month)) if month in MONTH_NAME_TO_NUMBER else None
                            elif field == 'quartile':
                                raw_quartile = str(value).strip().lower()
                                clean_quartile = raw_quartile.replace('"', '').replace("'", "")
                                data[field] = QUARTILE_MAPPING.get(clean_quartile)
                            elif field == 'indexing':
                                indexing_list = ""

                                # Handle Scopus indexing
                                if 'scopus_indexing' in row and row['scopus_indexing'] is not None:
                                    scopus_value = str(row['scopus_indexing']).strip().lower()
                                    if scopus_value in ['yes', 'y', 'true', '1']:
                                        indexing_list += "Scopus, "

                                # Handle Web of Science indexing
                                if 'wos_indexing' in row and row['wos_indexing'] is not None:
                                    wos_value = str(row['wos_indexing']).strip().lower()
                                    if wos_value in ['yes', 'y', 'true', '1']:
                                        indexing_list += "Web of Sciences, "

                                # Handle UGC indexing
                                if 'ugc_indexing' in row and row['ugc_indexing'] is not None:
                                    ugc_value = str(row['ugc_indexing']).strip()
                                    if ugc_value:
                                        indexing_list += "UGC, "

                                # Remove the trailing comma if present
                                data["indexing"] = indexing_list.rstrip(', ') if indexing_list else None
                            else:
                                # Default handling for string fields
                                str_value = str(value).strip() if value is not None else ""
                                if str_value:
                                    data[field] = str_value
                                else:
                                    data[field] = None  # Set to None for SQL NULL when field is empty

                        # Validate page_number and issn fields
                        page_number_value = row.get('page_number')
                        issn_value = row.get('issn')

                        # Regex pattern to match only numbers and hyphens
                        valid_pattern = re.compile(r'^[0-9-]+$')

                        # Validate page_number
                        if page_number_value and not valid_pattern.match(page_number_value):
                            data['page_number'] = None

                        # Validate issn
                        if issn_value and not valid_pattern.match(issn_value):
                            data['issn'] = None

                        # Process DOI and URL fields
                                            # Process DOI and URL fields
                        doi_value = row.get('doi')
                        url_value = row.get('url')

                        # Define regex pattern for valid DOIs
                        doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)

                        # Case 1: If URL directly contains a value in DOI format (e.g., "10.1109/ACCESS.2024.3523774")
                        if url_value and doi_pattern.match(str(url_value)):
                            # This is actually a DOI, not a URL - move it to the DOI field
                            data['doi'] = url_value  # Put the value in DOI field
                            data['url'] = None  # Clear the URL field

                        # Case 2: If URL contains a DOI within it (e.g., "https://doi.org/10.1109/ACCESS.2024.3523774")
                        elif url_value and doi_pattern.search(str(url_value)):
                            # Extract just the DOI number from the URL
                            doi_match = doi_pattern.search(str(url_value))
                            data['doi'] = doi_match.group(0)  # Store just the DOI number
                            data['url'] = url_value  # Keep the full URL
                            
                        # Case 3: If DOI field has a DOI value
                        elif doi_value and doi_pattern.search(str(doi_value)):
                            # Extract the DOI if it's within other text
                            doi_match = doi_pattern.search(str(doi_value))
                            data['doi'] = doi_match.group(0)  # Store just the DOI number
                            data['url'] = url_value  # Keep any URL as is
                            
                        # Case 4: Neither field has a valid DOI
                        else:
                            # Store URL as is if it exists
                            data['url'] = url_value
                            data['doi'] = None  # No valid DOI found

                        # Ensure verified and admin_verified are set to 'False' string
                        data['verified'] = 'False'
                        data['admin_verified'] = 'False'

                        # Handle authors specifically
                        if row.get('first_author'):
                            first_author_raw = str(row['first_author']).strip()
                            comma_count = first_author_raw.count(',')

                            # Split only if there are enough commas that likely separate authors
                            if comma_count >= 2:
                                authors = [author.strip() for author in first_author_raw.split(',') if author.strip()]
                            else:
                                authors = [first_author_raw]  # Possibly a single author

                            data['first_author'] = authors[0] if len(authors) > 0 else None
                            data['second_author'] = authors[1] if len(authors) > 1 else None
                            data['third_author'] = authors[2] if len(authors) > 2 else None
                            data['other_authors'] = ', '.join(authors[3:]) if len(authors) > 3 else None

                        # Generate unique ID if not exists
                        if not data.get('uniqueid'):
                            data['uniqueid'] = f"{data['year_of_publishing'] or ''}{''.join(random.choices(string.ascii_letters, k=7))}"

                        # Handle academic year determination
                        if data.get('year_of_publishing'):
                            year = data['year_of_publishing']
                            month = data.get('month_of_publishing')
                            
                            data['start_academic_month'] = 'JUL'
                            data['end_academic_month'] = 'JUN'
                            
                            if month and month in ['1', '2', '3', '4', '5', '6']:
                                data['start_academic_year'] = year - 1
                                data['end_academic_year'] = year
                            else:
                                data['start_academic_year'] = year
                                data['end_academic_year'] = year + 1

                        # Check if the record already exists
                        print(f"Checking for existing record with title: '{data['title']}', year: {data['year_of_publishing']}, first author: '{data.get('first_author', '')}'")
                        print(f"Querying with: title__iexact='{data['title']}', year_of_publishing={data['year_of_publishing']}, first_author__iexact='{data.get('first_author', '')}'")
                        existing_record = Publications.objects.filter(
                            title__iexact=data['title'],
                            year_of_publishing=data['year_of_publishing']
                        ).first()

                        if existing_record:
                            print(f"Existing record found: {existing_record.uniqueid}, title: '{existing_record.title}'")
                            record_changes = {}
                            
                            # Compare each field value with the database value
                            for field, new_value in data.items():
                                # Skip primary key and fields we don't want to compare
                                if field in ['uniqueid']:
                                    continue
                                    
                                # Get the existing value from the database
                                existing_value = getattr(existing_record, field, None)
                                
                                # Special case for verified and admin_verified fields
                                if field in ['verified', 'admin_verified']:
                                    if existing_value != 'False':
                                        record_changes[field] = {"old": existing_value, "new": 'False'}
                                        setattr(existing_record, field, 'False')
                                    continue
                                
                                # Handle case where new_value is None - we want to update this as NULL in the database
                                if new_value is None:
                                    if existing_value is not None:
                                        record_changes[field] = {"old": existing_value, "new": None}
                                        setattr(existing_record, field, None)
                                    continue
                                
                                # Only update if the new value differs from existing value
                                if new_value != existing_value:
                                    print(f"Field '{field}' will be updated from '{existing_value}' to '{new_value}'")
                                    # Handle numeric comparisons to avoid type mismatch issues
                                    if field in ['year_of_publishing', 'volume', 'citation', 'start_academic_year', 'end_academic_year']:
                                        # Convert both to integers for comparison if possible
                                        try:
                                            new_int = int(float(str(new_value).strip()))
                                            existing_int = int(float(str(existing_value).strip())) if existing_value is not None else None
                                            if new_int != existing_int:
                                                record_changes[field] = {"old": existing_value, "new": new_value}
                                                setattr(existing_record, field, new_int)
                                        except (ValueError, TypeError):
                                            # Skip if conversion fails
                                            pass
                                    elif field in ['impact_factor']:
                                        # Convert both to float for comparison
                                        try:
                                            new_float = float(str(new_value).strip())
                                            existing_float = float(str(existing_value).strip()) if existing_value is not None else None
                                            if new_float != existing_float:
                                                record_changes[field] = {"old": existing_value, "new": new_value}
                                                setattr(existing_record, field, new_float)
                                        except (ValueError, TypeError):
                                            # Skip if conversion fails
                                            pass
                                    elif field == 'is_student_author':
                                        # Special handling for boolean fields
                                        new_bool = new_value if isinstance(new_value, bool) else (str(new_value).strip().lower() in ['yes', 'true', '1'])
                                        existing_bool = existing_value if isinstance(existing_value, bool) else False
                                        if new_bool != existing_bool:
                                            record_changes[field] = {"old": existing_value, "new": new_value}
                                            setattr(existing_record, field, new_bool)
                                    else:
                                        # String or other fields - normalize strings for comparison
                                        new_str = str(new_value).strip() if new_value is not None else None
                                        existing_str = str(existing_value).strip() if existing_value is not None else None
                                        if new_str != existing_str:
                                            record_changes[field] = {"old": existing_value, "new": new_value}
                                            setattr(existing_record, field, new_str)
                            if record_changes:
                                # Log which fields were changed for debugging/auditing
                                print(f"Updating record {existing_record.uniqueid}, title: '{existing_record.title}', changes: {record_changes}")
                                records_to_update.append(existing_record)
                                update_details.append({
                                    "id": existing_record.uniqueid,
                                    "title": existing_record.title,
                                    "row": idx + 1,
                                    "sheet": sheet_name,
                                    "changes": record_changes
                                })
                            else:
                                print(f"No changes detected for record {existing_record.id}, title: '{existing_record.title}'")
                                skipped_records.append({
                                    "row": idx + 1, 
                                    "sheet": sheet_name, 
                                    "reason": "Record already exists with identical values"
                                })
                        else:
                            # This is a new record, so we'll insert it
                            # Log the values of 'verified' and 'admin_verified' before insertion
                            print(f"Inserting record with verified: {data['verified']}, admin_verified: {data['admin_verified']}")
                            # Log all NULL values for debugging
                            null_fields = [field for field, value in data.items() if value is None]
                            print(f"Fields with NULL values: {null_fields}")
                            
                            new_record = Publications(**data)
                            records_to_insert.append(new_record)

                    except Exception as row_error:
                        skipped_records.append({
                            "row": idx + 1,
                            "sheet": sheet_name,
                            "reason": str(row_error)
                        })
                        continue

            # Perform database operations in a transaction
            with transaction.atomic():
                # Update existing records
                if records_to_update:
                    for record in records_to_update:
                        record.save()
                    print(f"Updated {len(records_to_update)} records individually")

                # Insert new records
                if records_to_insert:
                    Publications.objects.bulk_create(records_to_insert)
                    print(f"Inserted {len(records_to_insert)} new records")

            # Prepare detailed result
            result = {
                "total_sheets": len(sheet_names),
                "inserted": len(records_to_insert),
                "updated": len(records_to_update),
                "skipped": len(skipped_records),
            }

            # Show messages
            messages.success(
                request,
                f"Processed {result['total_sheets']} sheets. "
                f"Inserted: {result['inserted']}, "
                f"Updated : {result['updated']},"
                f"Skipped: {result['skipped']}"
            )

            return render(request, "add_data_excel.html", {"result": result})

        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            print(error_msg)
            messages.error(request, error_msg)
            return render(request, "add_data_excel.html", status=500)

def admin_dashboard(request):
    papers = Publications.objects.all()

    publication_list = []

    facs = []

    faculties = Users.objects.all().order_by("staff_name")

    for row in faculties:
        facs.append(row.staff_name)

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name != "admin" or name == "None":
        return redirect("/rpa/login")

    form = PublicationsForm()

    for paper in papers:
        first_author = paper.first_author if paper.first_author else ""
        second_author = paper.second_author if paper.second_author else ""
        third_author = paper.third_author if paper.third_author else ""
        other_authors = paper.other_authors if paper.other_authors else ""

        if not paper.second_author:
            paper.second_author = "None"
        if not paper.third_author:
            paper.third_author = "None"
        if not paper.other_authors:
            paper.other_authors = "None"
        if not paper.is_student_author:
            paper.is_student_author = "None"
        if not paper.student_name:
            paper.student_name = "None"
        if not paper.student_batch:
            paper.student_batch = "None"
        if not paper.specification:
            paper.specification = "None"
        if not paper.publication_type:
            paper.publication_type = "None"
        if not paper.publication_name:
            paper.publication_name = "None"
        if not paper.publisher:
            paper.publisher = "None"
        if not paper.year_of_publishing:
            paper.year_of_publishing = "None"
        if not paper.month_of_publishing:
            paper.month_of_publishing = "None"
        if not paper.page_number:
            paper.page_number = "None"
        if not paper.indexing:
            paper.indexing = "None"
        if not paper.quartile:
            paper.quartile = "None"
        if not paper.url:
            paper.url = "None"
        if not paper.front_page_path:
            paper.front_page_path = "None"
        if not paper.impact_factor:
            paper.impact_factor = "None"

        publication_list.append(paper)

    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

     # Add the number of publications to the context
    num_publications = len(publication_list)

    context = {
        "papers": publication_list,
        "form": form,
        "new_sno": f"{int(len(publication_list)) + 1}",
        "name": name,
        "faculties": facs,
        "num_publications" : num_publications
    }

    # paper_records =
    return render(request, "admin_dashboard.html", context)



def admin_view_paper_details(request, paperid):
    if request.method != "GET":
        return render(request, "error.html")

    if not paperid:
        return render(request, "error.html")

    try:
        paper = Publications.objects.get(uniqueid=paperid)
    except Publications.DoesNotExist:
        return render(request, "error.html")

    name = str(request.session.get("FACULTY_NAME"))

    if name.lower().strip() != "admin":
        return render(
            request,
            "custom_error.html",
            {
                "error_title": "Unauthorized!",
                "error_message": "You are unauthorized to view the details of this publication.",
            },
        )

    return render(request, "admin_publication.html", {"paper": paper, "name": name})


def admin_upload_paper(request, uniqueid):
    if request.method == "GET":
        try:
            publ = Publications.objects.get(uniqueid=uniqueid)
        except Publications.DoesNotExist:
            return render(request, "error.html")

        name = str(request.session.get("FACULTY_NAME"))

        if name.lower() != "admin":
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Unauthorized!",
                    "error_message": "You are unauthorized to view the details of this publication.",
                },
            )

        return render(
            request, "admin_upload.html", {"title": publ.title, "uniqueid": uniqueid}
        )
    else:
        publ = Publications.objects.get(uniqueid=uniqueid)
        name = str(request.session.get("FACULTY_NAME"))

        if name.lower() != "admin":
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Unauthorized!",
                    "error_message": "You are unauthorized to view the details of this publication.",
                },
            )
        try:
            if not os.path.exists("rpa/static/upload/"):
                os.mkdir("rpa/static/upload/")

            upload_file = request.FILES["file"]

            complete_path = "rpa/static/upload/" + uniqueid.strip() + ".pdf"

            publ = Publications.objects.get(uniqueid=uniqueid)

            with open(complete_path, "wb+") as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

            publ.front_page_path = complete_path

            publ.save()

            return render(
                request,
                "upload.html",
                {"alertmessage": "Upload successful!", "uniqueid": uniqueid},
            )
        except Exception as e:
            return render(
                request,
                "upload.html",
                {"alertmessage": str(e), "reload": "yes", "uniqueid": uniqueid},
            )


def admin_remove_upload(request):
    uniqueid = request.POST.get("uniqueid")

    name = str(request.session.get("FACULTY_NAME", ""))

    if name != "admin":
        return HttpResponse("Unauthorized")

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    publ = Publications.objects.get(uniqueid=uniqueid)

    complete_path = "rpa/static/upload/" + uniqueid.strip() + ".pdf"

    if os.path.exists(complete_path):
        os.remove(complete_path)
    else:
        return HttpResponse("File not found!")

    publ.front_page_path = None

    publ.save()

    return HttpResponse("OK")

def admin_edit_history(request, uniqueid):
    version_history = Edithistory.objects.filter(uniqueid=uniqueid)
    return render(request, "edit_version.html", {"version_history":version_history})


def admin_verify_paper(request):
    uniqueid = request.POST.get("uniqueid")

    name = str(request.session.get("FACULTY_NAME"))

    if name != "admin":
        return HttpResponse("Unauthorized")

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    current_paper = Publications.objects.get(uniqueid=uniqueid)
    current_paper.admin_verified = "True"
    current_paper.save()

    return HttpResponse("OK")


def admin_update_paper(request):
    uniqueid = request.POST.get("uniqueid")
    print(request.POST)

    name = str(request.session.get("FACULTY_NAME"))

    if name != "admin":
        return HttpResponse("Unauthorized")

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    updateData = dict(request.POST)

    updates = {}

    for key, value in updateData.items():
        if (
            key != "csrfmiddlewaretoken"
            and key != "uniqueid"
            and key != "academic_year"
        ):
            if key == "student_author":
                key = "is_student_author"
            if key == "publication_year":
                key = "year_of_publishing"
            if key == "publication_month":
                key = "month_of_publishing"
            if key == "citations":
                key = "citation"
            if key == "page_numbers":
                key = "page_number"
            try:
                updates[key] = value[0]
            except IndexError:
                updates[key] = "NULL"

    academic_year = request.POST.get("academic_year").replace(" -", "").split(" ")

    start_academic_month = academic_year[0]
    start_academic_year = academic_year[1]
    end_academic_month = academic_year[2]
    end_academic_year = academic_year[3]

    updates["start_academic_year"] = int(start_academic_year)
    updates["start_academic_month"] = start_academic_month
    updates["end_academic_year"] = int(end_academic_year)
    updates["end_academic_month"] = end_academic_month
    updates["volume"] = int(updates["volume"])
    updates["citation"] = int(updates["citation"])
    updates["year_of_publishing"] = int(updates["year_of_publishing"])

    updates["verified"] = "False"
    updates["admin_verified"] = "False"

    updates =  {k: v for k, v in updates.items() if v != ''}

    to_save = record_update(uniqueid, name, updates, Publications)

    Publications.objects.filter(uniqueid=uniqueid).update(**updates)

    commit_record_updates(to_save)

    return HttpResponse("OK")


def admin_verification(request):
    papers = Publications.objects.all()

    publication_list = []

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name != "admin" or name == str(None):
        return redirect("/rpa/login")

    for paper in papers:
        publication_list.append(paper)

    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

    context = {"papers": publication_list, "name": name}

    return render(request, "admin_verification.html", context)


def admin_get_doi(request):
    if request.method == "POST":
        doi = request.POST.get("doi")
        ay = request.POST.get("AY")

        title = Extractor.get_title(doi)

        if not title:
            return render(request, "admin_get_title.html", {"doi": doi, "AY": ay})

        search_query = title

        try:
            result = Extractor.main(search_query, ay)
        except (IndexError, KeyError):
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Uh-Oh! Unable to fetch!",
                    "error_message": "Cannot fetch data for the given term!",
                },
            )

        if (result is None) or (result == False):
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Uh-Oh! Unable to fetch!",
                    "error_message": "Cannot fetch data for the given term!",
                },
            )
        else:
            if result.get("volume") is None:
                result["volume"] = 0
            if result.get("citation") is None:
                result["citation"] = 0

            return render(request, "admin_add_publication.html", {"result": result})

    name = request.session.get("FACULTY_NAME", "")

    if name != "admin":
        return redirect("/rpa/user/error")

    return render(request, "admin_get_doi.html", {"name": name})


def admin_get_title(request):
    if request.method == "POST":
        title = request.POST.get("title", "")
        doi = request.POST.get("doi", "")
        ay = request.POST.get("AY", "")

        search_query = title + doi

        try:
            result = Extractor.main(search_query, ay)
        except (IndexError, KeyError):
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Uh-Oh! Unable to fetch!",
                    "error_message": "Cannot fetch data for the given term!",
                },
            )

        if (result is None) or (result == False):
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Uh-Oh! Unable to fetch!",
                    "error_message": "Cannot fetch data for the given term!",
                },
            )
        else:
            if result.get("volume") is None:
                result["volume"] = 0
            if result.get("citation") is None:
                result["citation"] = 0

            return render(request, "admin_add_publication.html", {"result": result})

    name = request.session.get("FACULTY_NAME", "")

    if name != "admin":
        return redirect("/rpa/user/error")

    return render(request, "admin_get_title.html", {"name": name})


def admin_insert_paper(request):
    data_to_be_inserted = {}

    faculty_name = request.session["FACULTY_NAME"]

    if faculty_name != "admin":
        return HttpResponse("Unauthorized")

    uniqueid = request.POST.get("uniqueid")

    exists = Publications.objects.filter(uniqueid=uniqueid)

    if exists:
        return HttpResponse("Paper already exists! Cannot add paper.")

    data_to_be_inserted = {}

    for key, value in request.POST.items():
        if (
            key != "csrfmiddlewaretoken"
            and key != "uniqueid"
            and key != "academic_year"
        ):
            if key == "student_author":
                key = "is_student_author"
            if key == "publication_year":
                key = "year_of_publishing"
            if key == "publication_month":
                key = "month_of_publishing"
            if key == "citations":
                key = "citation"
            if key == "page_numbers":
                key = "page_number"
            try:
                data_to_be_inserted[key] = value
            except IndexError:
                data_to_be_inserted[key] = "NULL"

    data_to_be_inserted["uniqueid"] = uniqueid

    academic_year = request.POST.get("academic_year").replace(" -", "").split(" ")

    start_academic_month = academic_year[0]
    start_academic_year = academic_year[1]
    end_academic_month = academic_year[2]
    end_academic_year = academic_year[3]

    data_to_be_inserted["start_academic_year"] = int(start_academic_year)
    data_to_be_inserted["start_academic_month"] = start_academic_month
    data_to_be_inserted["end_academic_year"] = int(end_academic_year)
    data_to_be_inserted["end_academic_month"] = end_academic_month
    data_to_be_inserted["volume"] = int(data_to_be_inserted["volume"])
    data_to_be_inserted["citation"] = int(data_to_be_inserted["citation"])
    data_to_be_inserted["year_of_publishing"] = int(
        data_to_be_inserted["year_of_publishing"]
    )

    data_to_be_inserted = {k: v for k, v in data_to_be_inserted.items() if v != ''}

    new_record = Publications(**data_to_be_inserted)
    try:
        new_record.save()
    except django.db.utils.IntegrityError:
        return HttpResponse("Paper already exists! Cannot add paper.")

    return HttpResponse("OK")


def admin_manually_insert_paper(request):
    if request.method == "GET":
        name = request.session.get("FACULTY_NAME", "")

        if name != "admin":
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Unauthorized!",
                    "error_message": "You are unauthorized to do this operation!",
                },
            )

        return render(request, "admin_manually_add_paper.html", {"name": name})

    elif request.method == "POST":
        name = str(request.session.get("FACULTY_NAME"))

        if name != "admin":
            return HttpResponse("Unauthorized")

        updateData = dict(request.POST)

        updates = {}

        for key, value in updateData.items():
            if (
                key != "csrfmiddlewaretoken"
                and key != "uniqueid"
                and key != "academic_year"
            ):
                if key == "student_author":
                    key = "is_student_author"
                if key == "publication_year":
                    key = "year_of_publishing"
                if key == "publication_month":
                    key = "month_of_publishing"
                if key == "citations":
                    key = "citation"
                if key == "page_numbers":
                    key = "page_number"
                try:
                    updates[key] = value[0]
                except IndexError:
                    updates[key] = "NULL"

        academic_year = request.POST.get("academic_year").replace(" -", "").split(" ")

        start_academic_month = academic_year[0]
        start_academic_year = academic_year[1]
        end_academic_month = academic_year[2]
        end_academic_year = academic_year[3]

        updates["start_academic_year"] = int(start_academic_year)
        updates["start_academic_month"] = start_academic_month
        updates["end_academic_year"] = int(end_academic_year)
        updates["end_academic_month"] = end_academic_month
        updates["volume"] = int(updates["volume"])
        updates["citation"] = int(updates["citation"])
        updates["year_of_publishing"] = int(updates["year_of_publishing"])

        updates["verified"] = "False"
        updates["admin_verified"] = "False"

        uniqueid = (
            str(start_academic_year)
            + str(start_academic_month)
            + "".join(random.choices(string.ascii_letters, k=7))
        )

        updates["uniqueid"] = uniqueid

        updates = {k: v for k, v in updates.items() if v != ''}

        if Publications.objects.filter(uniqueid=uniqueid):
            return HttpResponse("Paper already exists! Cannot add paper.")

        new_record = Publications(**updates)

        try:
            new_record.save()
        except django.db.utils.IntegrityError:
            return HttpResponse("Paper already exists! Cannot add paper.")

        return HttpResponse("OK")


def admin_delete_paper(request):
    uniqueid = request.POST.get("uniqueid")

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    publication = Publications.objects.get(uniqueid=uniqueid)

    publication.delete()

    return HttpResponse("OK")


def convert_to_dict(row):
    order_of_headers = [
        "skip_sno",
        "uniqueid",
        "title",
        "url",
        "AY",
        "first_author",
        "second_author",
        "third_author",
        "other_authors",
        "is_student_author",
        "student_name",
        "student_batch",
        "specification",
        "publication_type",
        "publication_name",
        "publisher",
        "year_of_publishing",
        "month_of_publishing",
        "volume",
        "page_number",
        "indexing",
        "quartile",
        "impact_factor",
        "citation",
        "doi",
        "front_page_path",
        "issn",
        "verified",
        "admin_verified",
    ]
    row_data = {
        "uniqueid": row[order_of_headers.index("uniqueid")]
        if row[order_of_headers.index("uniqueid")]
        and row[order_of_headers.index("uniqueid")].lower() != "null"
        and row[order_of_headers.index("uniqueid")].lower() != "none"
        else "",
        "title": row[order_of_headers.index("title")]
        if row[order_of_headers.index("title")]
        and row[order_of_headers.index("title")].lower() != "null"
        and row[order_of_headers.index("title")].lower() != "none"
        else "",
        "AY": row[order_of_headers.index("AY")]
        if row[order_of_headers.index("AY")]
        and row[order_of_headers.index("AY")].lower() != "null"
        and row[order_of_headers.index("AY")].lower() != "none"
        else "",
        "first_author": row[order_of_headers.index("first_author")]
        if row[order_of_headers.index("first_author")]
        and row[order_of_headers.index("first_author")].lower() != "null"
        and row[order_of_headers.index("first_author")].lower() != "none"
        else "",
        "second_author": row[order_of_headers.index("second_author")]
        if row[order_of_headers.index("second_author")]
        and row[order_of_headers.index("second_author")].lower() != "null"
        and row[order_of_headers.index("second_author")].lower() != "none"
        else "",
        "third_author": row[order_of_headers.index("third_author")]
        if row[order_of_headers.index("third_author")]
        and row[order_of_headers.index("third_author")].lower() != "null"
        and row[order_of_headers.index("third_author")].lower() != "none"
        else "",
        "other_authors": row[order_of_headers.index("other_authors")]
        if row[order_of_headers.index("other_authors")]
        and row[order_of_headers.index("other_authors")].lower() != "null"
        and row[order_of_headers.index("other_authors")].lower() != "none"
        else "",
        "specification": row[order_of_headers.index("specification")]
        if row[order_of_headers.index("specification")]
        and row[order_of_headers.index("specification")].lower() != "null"
        and row[order_of_headers.index("specification")].lower() != "none"
        else "",
        "publication_type": row[order_of_headers.index("publication_type")]
        if row[order_of_headers.index("publication_type")]
        and row[order_of_headers.index("publication_type")].lower() != "null"
        and row[order_of_headers.index("publication_type")].lower() != "none"
        else "",
        "publication_name": row[order_of_headers.index("publication_name")]
        if row[order_of_headers.index("publication_name")]
        and row[order_of_headers.index("publication_name")].lower() != "null"
        and row[order_of_headers.index("publication_name")].lower() != "none"
        else "",
        "publisher": row[order_of_headers.index("publisher")]
        if row[order_of_headers.index("publisher")]
        and row[order_of_headers.index("publisher")].lower() != "null"
        and row[order_of_headers.index("publisher")].lower() != "none"
        else "",
        "year_of_publishing": row[order_of_headers.index("year_of_publishing")]
        if row[order_of_headers.index("year_of_publishing")]
        and row[order_of_headers.index("year_of_publishing")].lower() != "null"
        and row[order_of_headers.index("year_of_publishing")].lower() != "none"
        else "",
        "month_of_publishing": row[order_of_headers.index("month_of_publishing")]
        if row[order_of_headers.index("month_of_publishing")]
        and row[order_of_headers.index("month_of_publishing")].lower() != "null"
        and row[order_of_headers.index("month_of_publishing")].lower() != "none"
        else "",
        "volume": row[order_of_headers.index("volume")]
        if row[order_of_headers.index("volume")]
        and row[order_of_headers.index("volume")].lower() != "0"
        else "",
        "page_number": row[order_of_headers.index("page_number")]
        if row[order_of_headers.index("page_number")]
        and row[order_of_headers.index("page_number")].lower() != "null"
        and row[order_of_headers.index("page_number")].lower() != "none"
        else "",
        "indexing": row[order_of_headers.index("indexing")]
        if row[order_of_headers.index("indexing")]
        and row[order_of_headers.index("indexing")].lower() != "null"
        and row[order_of_headers.index("indexing")].lower() != "none"
        else "",
        "quartile": row[order_of_headers.index("quartile")]
        if row[order_of_headers.index("quartile")]
        and row[order_of_headers.index("quartile")].lower() != "null"
        and row[order_of_headers.index("quartile")].lower() != "none"
        else "",
        "doi": row[order_of_headers.index("doi")]
        if row[order_of_headers.index("doi")]
        and row[order_of_headers.index("doi")].lower() != "null"
        and row[order_of_headers.index("doi")].lower() != "none"
        else "",
        "url": row[order_of_headers.index("url")]
        if row[order_of_headers.index("url")]
        and row[order_of_headers.index("url")].lower() != "null"
        and row[order_of_headers.index("url")].lower() != "none"
        else "",
        "issn": row[order_of_headers.index("issn")]
        if row[order_of_headers.index("issn")]
        and row[order_of_headers.index("issn")].lower() != "null"
        and row[order_of_headers.index("issn")].lower() != "none"
        else "",
        "impact_factor": row[order_of_headers.index("impact_factor")]
        if row[order_of_headers.index("impact_factor")]
        and row[order_of_headers.index("impact_factor")].lower() != "null"
        and row[order_of_headers.index("impact_factor")].lower() != "none"
        else "",
        # "citation" : row['citation'],
        # "front_page_path" : row['front_page_path'],
        # "is_student_author" : row['is_student_author'],
        # "student_name" : row['student_name'],
        # "student_batch" : row['student_batch'],
        # "verified" : row['verified'],
        # "admin_verified" : row['admin_verified'],
    }
    return row_data


def IEEEFormat(paper):
    """
    Author initials. Last name, "Article title," Journal Name, vol. Volume, no. Number, pp. Page range, Month Year, DOI.
    """

    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    format_string = ""

    if paper.get("first_author"):
        format_string += str(paper.get("first_author")) + str(", ")

    if paper.get("second_author"):
        format_string += str(paper.get("second_author")) + str(", ")

    if paper.get("third_author"):
        format_string += str(paper.get("third_author")) + str(", ")

    if paper.get("other_authors"):
        format_string += str(paper.get("other_authors")) + str(", ")

    if paper.get("title"):
        format_string += str('"') + str(paper.get("title")) + str('", ')

    if paper.get("publication_name"):
        format_string += str(paper.get("publication_name")) + str(", ")

    if paper.get("publisher"):
        format_string += str(paper.get("publisher")) + str(", ")

    if paper.get("volume") and paper.get("volume") != "0":
        format_string += str("vol. ") + str(paper.get("volume")) + str(", ")

    if paper.get("page_number"):
        format_string += str("pp. ") + str(paper.get("page_number")) + str(", ")

    if paper.get("year_of_publishing"):
        month_str = str(paper.get("month_of_publishing", "")).strip()
        if month_str and month_str.isdigit() and 1 <= int(month_str) <= 12:
            format_string += str(months.get(int(month_str), "")) + str(" ") + str(paper.get("year_of_publishing")) + str(", ")
        else:
            format_string += str(paper.get("year_of_publishing")) + str(", ")

    if paper.get("doi"):
        format_string += str("DOI: ") + str(paper.get("doi")) + str(", ")

    if paper.get("issn"):
        format_string += str("ISSN: ") + str(paper.get("issn")) + str(", ")

    if paper.get("indexing") or paper.get("quartile"):
        if paper.get("indexing") and paper.get("quartile"):
            quartile = paper.get("quartile")
            if paper.get("quartile").lower() == "q4":
                quartile = "< Q3"
            format_string += (
                str("(Indexed in: ")
                + str(paper.get("indexing"))
                + str(" Quartile: ")
                + str(quartile)
                + str("), ")
            )
        elif paper.get("indexing"):
            format_string += (
                str("(Indexed in: ") + str(paper.get("indexing")) + str("), ")
            )
        elif paper.get("quartile"):
            quartile = paper.get("quartile")
            if paper.get("quartile").lower() == "q4":
                quartile = "< Q3"
            format_string += str("(Quartile: ") + str(quartile) + str("), ")

    if paper.get("impact_factor"):
        format_string += str("IF: ") + str(paper.get("impact_factor")) + str(", ")

    if paper.get("url"):
        format_string += str("URL: ") + str(paper.get("url"))

    format_string = format_string.rstrip(", ")

    return " ".join(format_string.split())


def generate_word_document(data):
    sorted_data = sorted(data, key=lambda x: x["AY"]) #data sorting based on years

    journals = {}
    conference = {}
    book_series = {}
    count = 0

    for data in sorted_data:
        if data["publication_type"].lower().strip() == "journal":
            if data["AY"] not in journals:
                journals[data["AY"]] = {}

                # print(f'{data["quartile"]=}, {bool(data["quartile"])}')

                if (
                    data["quartile"]
                    and data["quartile"].lower() != "null"
                    and data["quartile"].lower() != "none"
                ):
                    if data["quartile"].lower() == "q4":
                        quartile = "< Q3"
                    else:
                        quartile = data["quartile"]
                else:
                    quartile = "< Q3"

                if quartile not in journals[data["AY"]]:
                    journals[data["AY"]][quartile] = [data]
                else:
                    journals[data["AY"]][quartile].append(data)
                count += 1
            else:
                # print(f'{data["quartile"]=}, {bool(data["quartile"])}')

                if (
                    data["quartile"]
                    and data["quartile"].lower() != "null"
                    and data["quartile"].lower() != "none"
                ):
                    if data["quartile"].lower() == "q4":
                        quartile = "< Q3"
                    else:
                        quartile = data["quartile"]
                else:
                    quartile = "< Q3"

                if quartile not in journals[data["AY"]]:
                    journals[data["AY"]][quartile] = [data]
                else:
                    journals[data["AY"]][quartile].append(data)

        elif data["publication_type"].lower().strip() == "conference":
            if data["AY"] not in conference:
                conference[data["AY"]] = [data]
            else:
                conference[data["AY"]].append(data)
        elif data["publication_type"].lower().strip() == "book chapter":
            if data["AY"] not in book_series:
                book_series[data["AY"]] = [data]
            else:
                book_series[data["AY"]].append(data)

    '''total_len = sum(
        len(category)
        if isinstance(category, dict) else sum(len(q) for q in category.values())
        for category in [journals, conference, book_series]
    )'''

    total_len = len(sorted_data)

    print(len(sorted_data))
    print(book_series)

    # Create a new Word document
    doc = docx.Document()

    heading1 = doc.add_heading("Department of Information Technology", level=1)
    heading1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = heading1.runs[0]
    run.font.size = Pt(24)
    run.bold = True
    run.underline = True

    heading1 = doc.add_heading("Research Publications", level=1)
    heading1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = heading1.runs[0]
    run.font.size = Pt(20)
    run.bold = True
    run.underline = True

    total_paragraph_top = doc.add_paragraph()
    total_paragraph_top.paragraph_format.space_before = Pt(10)  # adds space above the line
    total_paragraph_top.paragraph_format.space_after = Pt(6) 
    run = total_paragraph_top.add_run(f"Total number of publications: {total_len}")
    run.bold = True
    run.font.size = Pt(14)
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW


    if journals:
        journal_heading = doc.add_heading("Journals", level=1)
        run = journal_heading.runs[0]
        run.underline = True

        for AY, details in journals.items():
            if details:
                AY_heading = doc.add_heading(AY, level=2)
                run = AY_heading.runs[0]
                run.underline = True

                details = sort_quartile_records(details)

                for quartile, papers in details.items():
                    if papers:
                        quartile_heading = doc.add_heading(
                            f"Publications under {quartile}", level=3
                        )
                        run = quartile_heading.runs[0]
                        run.underline = True

                        for idx, paper in enumerate(papers):
                            paragraph = doc.add_paragraph(
                                str(idx + 1) + ". " + IEEEFormat(paper)
                            )
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if book_series:
        book_series_heading = doc.add_heading("Book Series", level=1)
        run = book_series_heading.runs[0]
        run.underline = True

        for AY, details in book_series.items():
            if details:
                AY_heading = doc.add_heading(AY, level=2)
                run = AY_heading.runs[0]
                run.underline = True

                for idx, paper in enumerate(details):
                    paragraph = doc.add_paragraph(
                        str(idx + 1) + ". " + IEEEFormat(paper)
                    )
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if conference:
        conference_heading = doc.add_heading("Conference", level=1)
        run = conference_heading.runs[0]
        run.underline = True

        for AY, details in conference.items():
            if details:
                AY_heading = doc.add_heading(AY, level=2)
                run = AY_heading.runs[0]
                run.underline = True

                for idx, paper in enumerate(details):
                    paragraph = doc.add_paragraph(
                        str(idx + 1) + ". " + IEEEFormat(paper)
                    )
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.save("research_publications.docx")


def admin_get_word(request):
    if request.method == "POST":
        table_data = request.POST.get("data")
        table_dict = json.loads(f'{{"rows": {table_data}}}')

        table_rows = table_dict.get("rows")

        all_row_data = []

        for row in table_rows:
            row_data = convert_to_dict(row)
            all_row_data.append(row_data)

        generate_word_document(all_row_data)

    return JsonResponse({})


def sort_quartile_records(input_dict):
    # Define the desired order of keys
    desired_order = ["Q1", "Q2", "Q3", "< Q3"]

    # Create a new dictionary with keys sorted according to the desired order
    sorted_dict = {key: input_dict[key] for key in desired_order if key in input_dict}

    return sorted_dict


def admin_get_charts(request):
    if request.method == "GET":
        name = str(request.session.get("FACULTY_NAME"))

        if name is None or name != "admin" or name == str(None):
            return redirect("/rpa/login")

        # Fetch data for donut chart
        chart_records = {}
        all_records = Publications.objects.all()
        for record in all_records:
            if (
                not record.indexing
                or record.indexing == "NULL"
                or record.indexing == "None"
            ):
                key = "Others"
            else:
                # indices = record.indexing.split(", ")
                indices = record.indexing
                if indices:
                    if indices not in [
                        "Scopus",
                        "Web of Sciences",
                        "Scopus, Web of Sciences",
                        "Web of Sciences, Scopus",
                    ]:
                        key = "Others"
                        chart_records[key] = chart_records.get(key, 0) + 1
                        continue
                    if (
                        indices == "Scopus, Web of Sciences"
                        or indices == "Web of Sciences, Scopus"
                    ):
                        key = "Web of Sciences"
                    else:
                        key = indices
                    chart_records[key] = chart_records.get(key, 0) + 1

                # for index in indices:
                #     #print(index)
                #     if index not in ['Scopus', 'Web of Sciences']:
                #         key = "Others"
                #         chart_records[key] = chart_records.get(key, 0) + 1
                #         continue
                #     key = index
                #     chart_records[key] = chart_records.get(key, 0) + 1

        donut_labels = list(chart_records.keys())
        donut_values = list(chart_records.values())

        # Fetch data for bar chart based on academic year/month
        bar_data = (
            Publications.objects.values(
                "start_academic_year",
                "start_academic_month",
                "end_academic_year",
                "end_academic_month",
            )
            .annotate(total=Count("uniqueid"))
            .order_by("start_academic_year")
        )
        bar_labels = []
        bar_values = []
        for data in bar_data:
            start_academic_year = data["start_academic_year"]
            start_academic_month = data["start_academic_month"]
            end_academic_year = data["end_academic_year"]
            end_academic_month = data["end_academic_month"]
            label = f"{start_academic_month} {start_academic_year} - {end_academic_month} {end_academic_year}"
            bar_labels.append(label)
            bar_values.append(data["total"])

        # Fetch data for another bar chart based on publication types
        publication_types_data = Publications.objects.values(
            "publication_type"
        ).annotate(total=Count("uniqueid"))
        publication_type_labels = []
        publication_type_values = []
        for pub_type_data in publication_types_data:
            publication_type_labels.append(pub_type_data["publication_type"])
            publication_type_values.append(pub_type_data["total"])

        temp = {}

        for i in range(len(publication_type_labels)):
            temp[publication_type_labels[i]] = publication_type_values[i]

        publication_type_values = [temp]
        publication_type_labels = ["Overall"]

        # Fetch data for quartile bar chart
        quartile_records = {}
        quartile_labels = []
        quartile_values = []
        qr_records = Publications.objects.all()
        for record in qr_records:
            if (
                not record.quartile
                or record.quartile == "NULL"
                or record.quartile == "None"
                or record.quartile == "Q4"
            ):
                key = "< Q3"
            else:
                key = record.quartile
            quartile_records[key] = quartile_records.get(key, 0) + 1

        quartile_records = sort_quartile_records(quartile_records)

        quartile_labels = list(quartile_records.keys())
        quartile_values = list(quartile_records.values())

        yearly_quartiles = {}
        for data in bar_data:
            year = f"{data['start_academic_year']} - {data['end_academic_year']}"
            if year not in yearly_quartiles:
                yearly_quartiles[year] = {"Q1": 0, "Q2": 0, "Q3": 0, "< Q3": 0}
            year_records = all_records.filter(
                start_academic_year=data["start_academic_year"],
                end_academic_year=data["end_academic_year"],
                start_academic_month=data["start_academic_month"],
                end_academic_month=data["end_academic_month"],
            )
            for record in year_records:
                if (
                    record.quartile
                    and record.quartile != "NULL"
                    and record.quartile in ("Q1", "Q2", "Q3")
                ):
                    yearly_quartiles[year][record.quartile] += 1
                else:
                    yearly_quartiles[year]["< Q3"] += 1
        yearwise_label = list(yearly_quartiles.keys())
        yearwise_values = list(yearly_quartiles.values())

        # Prepare data for rendering
        data = {
            "donut_labels": donut_labels,
            "donut_values": donut_values,
            "bar_labels": bar_labels,
            "bar_values": bar_values,
            "publication_type_labels": publication_type_labels,
            "publication_type_values": publication_type_values,
            "quartile_labels": quartile_labels,
            "quartile_values": quartile_values,
            "name": name,
            "yearwise_label": yearwise_label,
            "yearwise_values": yearwise_values,
        }

        return render(request, "charts.html", data)
    elif request.method == "POST":
        name = str(request.session.get("FACULTY_NAME"))

        if name is None or name != "admin" or name == str(None):
            return redirect("/rpa/login")

        AY = request.POST.get("AY")

        if AY == "all":
            return redirect("/rpa/dbadmin/charts")

        start, end = AY.split(" - ")
        start_academic_month, start_academic_year = start.split(" ")
        end_academic_month, end_academic_year = end.split(" ")

        # Fetch data for donut chart
        chart_records = {}
        all_records = Publications.objects.filter(
            start_academic_year=start_academic_year,
            end_academic_year=end_academic_year,
            start_academic_month=start_academic_month,
            end_academic_month=end_academic_month,
        )
        for record in all_records:
            if (
                not record.indexing
                or record.indexing == "NULL"
                or record.indexing == "None"
            ):
                key = "Others"
            else:
                indices = record.indexing
                print(indices)
                if indices:
                    if indices not in [
                        "Scopus",
                        "Web of Sciences",
                        "Scopus, Web of Sciences",
                        "Web of Sciences, Scopus",
                    ]:
                        key = "Others"
                        chart_records[key] = chart_records.get(key, 0) + 1
                        continue
                    if (
                        indices == "Scopus, Web of Sciences"
                        or indices == "Web of Sciences, Scopus"
                    ):
                        key = "Web of Sciences"
                    else:
                        key = indices
                    chart_records[key] = chart_records.get(key, 0) + 1
                # indices = record.indexing.split(", ")
                # for index in indices:
                #     if index not in ['Scopus', 'Web of Sciences']:
                #         key = "Others"
                #         chart_records[key] = chart_records.get(key, 0) + 1
                #         continue
                #     key = index
                #     chart_records[key] = chart_records.get(key, 0) + 1

        donut_labels = list(chart_records.keys())
        donut_values = list(chart_records.values())

        # Fetch data for bar chart based on academic year/month
        bar_data = (
            Publications.objects.values(
                "start_academic_year",
                "start_academic_month",
                "end_academic_year",
                "end_academic_month",
            )
            .annotate(total=Count("uniqueid"))
            .order_by("start_academic_year")
        )
        bar_labels = []
        bar_values = []
        for data in bar_data:
            start_academic_year = data["start_academic_year"]
            start_academic_month = data["start_academic_month"]
            end_academic_year = data["end_academic_year"]
            end_academic_month = data["end_academic_month"]
            label = f"{start_academic_month} {start_academic_year} - {end_academic_month} {end_academic_year}"
            bar_labels.append(label)
            bar_values.append(data["total"])

        # Fetch data for another bar chart based on publication types
        publication_types_data = all_records
        publication_type_labels = []
        publication_type_values = []
        count_data = {}
        for pub_type_data in publication_types_data:
            if pub_type_data.publication_type in count_data:
                count_data[pub_type_data.publication_type] += 1
            else:
                count_data[pub_type_data.publication_type] = 1

        publication_type_labels = list(count_data.keys())
        publication_type_values = list(count_data.values())

        temp = {}

        for i in range(len(publication_type_labels)):
            temp[publication_type_labels[i]] = publication_type_values[i]

        publication_type_values = [temp]
        publication_type_labels = [AY]

        # Fetch data for quartile bar chart
        quartile_records = {}
        quartile_labels = []
        quartile_values = []
        qr_records = all_records

        for record in qr_records:
            if (
                not record.quartile
                or record.quartile == "NULL"
                or record.quartile == "None"
                or record.quartile == "Q4"
            ):
                key = "< Q3"
            else:
                key = record.quartile
            quartile_records[key] = quartile_records.get(key, 0) + 1

        quartile_records = sort_quartile_records(quartile_records)

        quartile_labels = list(quartile_records.keys())
        quartile_values = list(quartile_records.values())

        yearly_quartiles = {}
        yearly_quartiles[AY] = {"Q1": 0, "Q2": 0, "Q3": 0, "< Q3": 0}
        for data in bar_data:
            # year = f"{data['start_academic_year']} - {data['end_academic_year']}"
            year_records = all_records.filter(
                start_academic_year=data["start_academic_year"],
                end_academic_year=data["end_academic_year"],
                start_academic_month=data["start_academic_month"],
                end_academic_month=data["end_academic_month"],
            )
            for record in year_records:
                if (
                    record.quartile
                    and record.quartile != "NULL"
                    and record.quartile in ("Q1", "Q2", "Q3")
                ):
                    yearly_quartiles[AY][record.quartile] += 1
                else:
                    yearly_quartiles[AY]["< Q3"] += 1
        yearwise_label = list(yearly_quartiles.keys())
        yearwise_values = list(yearly_quartiles.values())

        # Prepare data for rendering
        data = {
            "donut_labels": donut_labels,
            "donut_values": donut_values,
            "bar_labels": bar_labels,
            "bar_values": bar_values,
            "publication_type_labels": publication_type_labels,
            "publication_type_values": publication_type_values,
            "quartile_labels": quartile_labels,
            "quartile_values": quartile_values,
            "name": name,
            "AY": AY,
            "yearwise_label": yearwise_label,
            "yearwise_values": yearwise_values,
        }

        return render(request, "charts.html", data)