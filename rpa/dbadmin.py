from rpa.models import Publications
from rpa.forms import PublicationsForm
from rpa.models import Users
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
import random
import string
import django.db.utils
import os
import rpa.extractor.extractor as Extractor


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

    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

    context = {
        "papers": publication_list,
        "form": form,
        "new_sno": f"{int(len(publication_list)) + 1}",
        "name": name,
        "faculties": facs,
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

    Publications.objects.filter(uniqueid=uniqueid).update(**updates)

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

    print(uniqueid, Publications.objects.filter(uniqueid=uniqueid))

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    publication = Publications.objects.get(uniqueid=uniqueid)

    publication.delete()

    return HttpResponse("OK")


def admin_get_charts(request):
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
            key = record.indexing
        chart_records[key] = chart_records.get(key, 0) + 1

    donut_labels = list(chart_records.keys())
    donut_values = list(chart_records.values())

    # Fetch data for bar chart based on academic year/month
    bar_data = Publications.objects.values(
        "start_academic_year",
        "start_academic_month",
        "end_academic_year",
        "end_academic_month",
    ).annotate(total=Count("uniqueid"))
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
    publication_types_data = Publications.objects.values("publication_type").annotate(
        total=Count("uniqueid")
    )
    publication_type_labels = []
    publication_type_values = []
    for pub_type_data in publication_types_data:
        publication_type_labels.append(pub_type_data["publication_type"])
        publication_type_values.append(pub_type_data["total"])

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
        ):
            key = "Others"
        else:
            key = record.quartile
        quartile_records[key] = quartile_records.get(key, 0) + 1

    quartile_labels = list(quartile_records.keys())
    quartile_values = list(quartile_records.values())

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
    }

    return render(request, "charts.html", data)
