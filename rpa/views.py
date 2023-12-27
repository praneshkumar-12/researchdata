from django.shortcuts import render, redirect
from django.http import HttpResponse
from rpa.models import Publications
from rpa.models import Users
from rpa.forms import PublicationsForm
import rpa.extractor.extractor as Extractor
from django.http import JsonResponse

# Create your views here.


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        passcode = request.POST.get("pass")

        users = Users.objects.all()

        for user in users:
            if user.email_id == email and user.passkey == passcode:
                request.session["FACULTY_NAME"] = user.staff_name.split(" ")[0]
                return redirect("/rpa/auth/dashboard")

        # if email == "admin@ssn.edu.in" and passcode == "12345":
        else:
            return render(request, "index.html", context={"invalidlogin": True})

    return render(request, "index.html")


def dashboard(request):
    papers = Publications.objects.all()

    publication_list = []

    name = request.session.get("FACULTY_NAME")

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

        if (
            name in first_author
            or name in second_author
            or name in third_author
            or name in other_authors
        ):
            publication_list.append(paper)

    context = {
        "papers": publication_list,
        "form": form,
        "new_sno": f"{int(len(publication_list)) + 1}",
    }

    # paper_records =
    return render(request, "layout.html", context)


def verify_paper(request):
    uniqueid = request.POST.get("uniqueid")

    current_paper = Publications.objects.get(uniqueid=uniqueid)
    current_paper.verified = "True"
    current_paper.save()

    return HttpResponse(f"Updated verification status for {current_paper.title}")


def scrape_data(request):
    title = request.POST.get("title", "")
    doi = request.POST.get("doi", "")

    if not title:
        title = Extractor.get_title(doi)
        if not title:
            return HttpResponse(
                "Cannot fetch only with DOI, please provide title also."
            )

    search_query = title + doi

    try:
        result = Extractor.main(search_query)
    except (IndexError, KeyError):
        return HttpResponse("Cannot fetch data for the given search term!")

    print(result)

    if (result is None) or (result == False):
        return HttpResponse("Cannot fetch data for the given search term!")
    else:
        return JsonResponse(result)


def insert_paper(request):
    print(request.POST)

    args = {}

    faculty_name = request.session["FACULTY_NAME"]

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

    if not (
        faculty_name in first_author
        or faculty_name in second_author
        or faculty_name in third_author
        or faculty_name in other_authors
    ):
        return HttpResponse("You are not an author of this paper. Cannot add paper.")

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
