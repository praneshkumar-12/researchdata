from rpa.models import Publications
from rpa.forms import PublicationsForm
from django.shortcuts import render, redirect
from django.http import HttpResponse


def admin_dashboard(request):
    papers = Publications.objects.all()

    publication_list = []

    form = PublicationsForm()

    for paper in papers:
        first_author = paper.first_author if paper.first_author else ""
        second_author = paper.second_author if paper.second_author else ""
        third_author = paper.third_author if paper.third_author else ""
        other_authors = paper.other_authors if paper.other_authors else ""

        if not paper.second_author:
            paper.second_author = "NULL"
        if not paper.third_author:
            paper.third_author = "NULL"
        if not paper.other_authors:
            paper.other_authors = "NULL"
        if not paper.is_student_author:
            paper.is_student_author = "NULL"
        if not paper.student_name:
            paper.student_name = "NULL"
        if not paper.student_batch:
            paper.student_batch = "NULL"
        if not paper.specification:
            paper.specification = "NULL"
        if not paper.publication_type:
            paper.publication_type = "NULL"
        if not paper.publication_name:
            paper.publication_name = "NULL"
        if not paper.publisher:
            paper.publisher = "NULL"
        if not paper.year_of_publishing:
            paper.year_of_publishing = "NULL"
        if not paper.month_of_publishing:
            paper.month_of_publishing = "NULL"
        if not paper.page_number:
            paper.page_number = "NULL"
        if not paper.indexing:
            paper.indexing = "NULL"
        if not paper.quartile:
            paper.quartile = "NULL"
        if not paper.url:
            paper.url = "NULL"
        if not paper.issn:
            paper.issn = "NULL"
        if not paper.front_page_path:
            paper.front_page_path = "NULL"

        publication_list.append(paper)

    context = {
        "papers": publication_list,
        "form": form,
        "new_sno": f"{int(len(publication_list)) + 1}",
    }

    return render(request, "admin_layout.html", context)

def admin_insert_paper(request):
    print(request.POST)

    args = {}


    uniqueid = request.POST.get("uniqueid")

    exists = Publications.objects.filter(uniqueid=uniqueid)

    if exists:
        return HttpResponse("Paper already exists! Cannot add paper.")

    title = request.POST.get("title")
    first_author = request.POST.get("first_author")
    second_author = request.POST.get("second_author")
    third_author = request.POST.get("third_author")
    other_authors = request.POST.get("other_authors")
    is_student_author = request.POST.get("is_student_author")
    student_name = request.POST.get("student_name")
    student_batch = request.POST.get("student_batch")
    specification = request.POST.get("specification")
    publication_type = request.POST.get("publication_type")
    publication_name = request.POST.get("publication_name")
    publisher = request.POST.get("publisher")
    month_of_publishing = request.POST.get("month_of_publishing")
    page_number = request.POST.get("page_number")
    indexing = request.POST.get("indexing")
    quartile = request.POST.get("quartile")
    doi = request.POST.get("doi")
    url = request.POST.get("url")
    issn = request.POST.get("issn")

    front_page_path = request.POST.get("front_page_path")
    AY = request.POST.get("AY")
    split_content = AY.split(" - ")
    start_AY = split_content[0]
    end_AY = split_content[1]

    start_academic_month, start_academic_year = start_AY.split(" ")
    end_academic_month, end_academic_year = end_AY.split(" ")

    year_of_publishing = request.POST.get("year_of_publishing")
    citation = request.POST.get("citation")
    volume = request.POST.get("volume")

    integer_fields = ["year_of_publishing", "citation", "volume"]

    fields = {
        "uniqueid": uniqueid,
        "title": title,
        "first_author": first_author,
        "second_author": second_author,
        "third_author": third_author,
        "other_authors": other_authors,
        "is_student_author": is_student_author,
        "student_name": student_name,
        "student_batch": student_batch,
        "specification": specification,
        "publication_type": publication_type,
        "publication_name": publication_name,
        "publisher": publisher,
        "month_of_publishing": month_of_publishing,
        "page_number": page_number,
        "indexing": indexing,
        "quartile": quartile,
        "doi": doi,
        "url": url,
        "issn": issn,
        "start_academic_month": start_academic_month,
        "start_academic_year": start_academic_year,
        "end_academic_month": end_academic_month,
        "end_academic_year": end_academic_year,
        "front_page_path": front_page_path,
        "year_of_publishing": year_of_publishing,
        "citation": citation,
        "volume": volume,
    }

    for key, val in fields.items():
        if val == "NULL":
            continue
        else:
            if key in integer_fields:
                if val == "":
                    args[key] = 0
                else:
                    args[key] = int(val)
            elif key == "front_page_path" and "Yet" in val:
                continue
            else:
                args[key] = val

    print(args)

    new_record = Publications(**args)

    new_record.save()

    return HttpResponse("Paper inserted successfully!")

def admin_verify_paper(request):
    uniqueid = request.POST.get("uniqueid")

    current_paper = Publications.objects.get(uniqueid=uniqueid)
    current_paper.admin_verified = "True"
    current_paper.save()

    return HttpResponse(f"Updated verification status for {current_paper.title}")

def admin_delete_paper(request):
    uniqueid = request.POST.get("uniqueid")

    publications = Publications.objects.get(uniqueid=uniqueid)

    name = publications.title

    publications.delete()

    return HttpResponse(f"Deleted paper: {name}")

def admin_update_paper(request):
    try:
        args = {}

        uniqueid = request.POST.get("uniqueid")
        title = request.POST.get("title")
        first_author = request.POST.get("first_author")
        second_author = request.POST.get("second_author")
        third_author = request.POST.get("third_author")
        other_authors = request.POST.get("other_authors")
        is_student_author = request.POST.get("is_student_author")
        student_name = request.POST.get("student_name")
        student_batch = request.POST.get("student_batch")
        specification = request.POST.get("specification")
        publication_type = request.POST.get("publication_type")
        publication_name = request.POST.get("publication_name")
        publisher = request.POST.get("publisher")
        month_of_publishing = request.POST.get("month_of_publishing")
        page_number = request.POST.get("page_number")
        indexing = request.POST.get("indexing")
        quartile = request.POST.get("quartile")
        doi = request.POST.get("doi")
        url = request.POST.get("url")
        issn = request.POST.get("issn")

        front_page_path = request.POST.get("front_page_path")
        AY = request.POST.get("AY")
        split_content = AY.split(" - ")
        start_AY = split_content[0]
        end_AY = split_content[1]

        start_academic_month, start_academic_year = start_AY.split(" ")
        end_academic_month, end_academic_year = end_AY.split(" ")

        year_of_publishing = request.POST.get("year_of_publishing")
        citation = request.POST.get("citation")
        volume = request.POST.get("volume")

        integer_fields = ["year_of_publishing", "citation", "volume"]

        fields = {
            "uniqueid": uniqueid,
            "title": title,
            "first_author": first_author,
            "second_author": second_author,
            "third_author": third_author,
            "other_authors": other_authors,
            "is_student_author": is_student_author,
            "student_name": student_name,
            "student_batch": student_batch,
            "specification": specification,
            "publication_type": publication_type,
            "publication_name": publication_name,
            "publisher": publisher,
            "month_of_publishing": month_of_publishing,
            "page_number": page_number,
            "indexing": indexing,
            "quartile": quartile,
            "doi": doi,
            "url": url,
            "issn": issn,
            "start_academic_month": start_academic_month,
            "start_academic_year": start_academic_year,
            "end_academic_month": end_academic_month,
            "end_academic_year": end_academic_year,
            "front_page_path": front_page_path,
            "year_of_publishing": year_of_publishing,
            "citation": citation,
            "volume": volume,
        }

        for key, val in fields.items():
            if val == "NULL":
                continue
            else:
                if key in integer_fields:
                    if val == "":
                        args[key] = 0
                    else:
                        args[key] = int(val)
                elif key == "front_page_path" and ("Yet" in (val if val is not None else "Yet")):
                    continue
                else:
                    args[key] = val
        
        print(args)
        
        existing_data = Publications.objects.get(uniqueid=uniqueid)

        
        existing_data.uniqueid = args.get("uniqueid")
        existing_data.title = args.get("title")
        existing_data.first_author = args.get("first_author")
        existing_data.second_author = args.get("second_author")
        existing_data.third_author = args.get("third_author")
        existing_data.other_authors = args.get("other_authors")
        existing_data.is_student_author = args.get("is_student_author")
        existing_data.student_name = args.get("student_name")
        existing_data.student_batch = args.get("student_batch")
        existing_data.specification = args.get("specification")
        existing_data.publication_type = args.get("publication_type")
        existing_data.publication_name = args.get("publication_name")
        existing_data.publisher = args.get("publisher")
        existing_data.month_of_publishing = args.get("month_of_publishing")
        existing_data.page_number = args.get("page_number")
        existing_data.indexing = args.get("indexing")
        existing_data.quartile = args.get("quartile")
        existing_data.doi = args.get("doi")
        existing_data.url = args.get("url")
        existing_data.issn = args.get("issn")
        existing_data.start_academic_month = args.get("start_academic_month")
        existing_data.start_academic_year = args.get("start_academic_year")
        existing_data.end_academic_month = args.get("end_academic_month")
        existing_data.end_academic_year = args.get("end_academic_year")
        existing_data.front_page_path = args.get("front_page_path")
        existing_data.year_of_publishing = args.get("year_of_publishing")
        existing_data.citation = args.get("citation")
        existing_data.volume = args.get("volume")
        existing_data.verified = "False"
        existing_data.admin_verified = "False"
        
    # Save the updated instance
        existing_data.save()
        return HttpResponse(f"Update successful for {args['title']}")

    except Exception as e:
        return HttpResponse(str(e))   
    
def admin_remove_upload(request):
    uniqueid = request.POST.get("uniqueid")

    print(uniqueid)

    publ = Publications.objects.get(uniqueid=uniqueid)

    publ.front_page_path = None

    publ.save()

    return HttpResponse(f"Removed first page path for {publ.title}")