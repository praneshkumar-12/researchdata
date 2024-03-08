from django.shortcuts import render, redirect
from django.http import HttpResponse
from rpa.models import Publications
from rpa.models import Users
from rpa.models import AdminUsers
from rpa.forms import PublicationsForm
import django.db.utils
import rpa.extractor.extractor as Extractor
import os
import random


def login(request):
    users = Users.objects.all()
    adminusers = AdminUsers.objects.all()
    
    if request.method == "POST":
        email = request.POST.get("email")
        passcode = request.POST.get("pass")

        for adminuser in adminusers:
            if adminuser.email_id == email and adminuser.passkey == passcode and passcode == "Admin@123":
                return render(request, "reset_password.html", {"email": email})
            elif adminuser.email_id == email and adminuser.passkey == passcode:
                request.session["FACULTY_NAME"] = "admin"
                return redirect("/rpa/dbadmin/home")

        for user in users:
            if user.email_id == email and user.passkey == passcode and passcode == "Welcome123":
                return render(request, "reset_password.html", {"email": email})
            elif user.email_id == email and user.passkey == passcode:
                request.session["FACULTY_NAME"] = user.staff_name.split(" ")[0]
                return redirect("/rpa/user/home")
            
        return render(request, "index.html", context={"invalidlogin": "yes"})

    user_name = request.session.get("FACULTY_NAME")

    if user_name:
        if user_name == "admin":
            return redirect("/rpa/dbadmin/home")
        elif user_name in [user.staff_name.split(" ")[0] for user in users]:
            return redirect("/rpa/user/home")
    
    return render(request, "index.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return render(request, "forgot_password.html", {"alertmessage": "Please fill the email field!"})
        
        user = Users.objects.filter(email_id=email)
        admin = AdminUsers.objects.filter(email_id=email)


        if (not admin) and (not user):
            return render(request, "forgot_password.html", {"alertmessage": "Cannot find email id!"})
        
        otp = random.randint(11111,99999)

        print(otp)

        request.session['otp'] = int(otp)
        request.session['email'] = email

        return render(request, "verify_otp.html")


    return render(request, "forgot_password.html")


def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("pass", "")
        confirm_password = request.POST.get("confirm_pass", "")
        email = request.POST.get("email", "")

        if not email:
            return redirect("/rpa/user/error")

        if (not password) or (not confirm_password):
            return render(request, "reset_password.html", {"alertmessage": "Please fill the password field!", "email": email})
        
        if password != confirm_password:
            return render(request, "reset_password.html", {"alertmessage": "Passwords do not match!", "email": email})

        if password == "Welcome123" or password == "Admin@123":
            return render(request, "reset_password.html", {"alertmessage": "Password cannot be default password!", "email": email})
        
        updates = {"passkey": password}

        
        if Users.objects.filter(email_id=email):
            Users.objects.filter(email_id=email).update(**updates)
        elif AdminUsers.objects.filter(email_id=email):
            AdminUsers.objects.filter(email_id=email).update(**updates)
        else:
            return redirect("/rpa/users/error")

        return render(request, "index.html", {"alertmessage": "Password change successful!"})

    return redirect("/rpa/user/error")


def otp_verification(request):
    if request.method == "POST":
        otp = request.POST.get("otp", "")
        password = request.POST.get("pass", "")
        confirm_password = request.POST.get("confirm_pass", "")


        if not otp.isnumeric():
            return render(request, "verify_otp.html", {"alertmessage": "Invalid OTP!"})

        if int(otp) != int(request.session.get("otp", 0)):
            return render(request, "verify_otp.html", {"alertmessage": "Invalid OTP!"})

        if (not password) or (not confirm_password):
            return render(request, "verify_otp.html", {"alertmessage": "Please fill the password field!"})
        
        if password != confirm_password:
            return render(request, "verify_otp.html", {"alertmessage": "Passwords do not match!"})
        

        email = request.session.get("email", "")

        updates = {"passkey": password}

        if not email:
            return redirect("/rpa/user/error")
        
        if Users.objects.filter(email_id=email):
            Users.objects.filter(email_id=email).update(**updates)
        elif AdminUsers.objects.filter(email_id=email):
            AdminUsers.objects.filter(email_id=email).update(**updates)
        else:
            return redirect("/rpa/users/error")

        return render(request, "index.html", {"alertmessage": "Password change successful!"})
    else:
        return redirect("/rpa/user/error")
    
def user_home(request):
    papers = Publications.objects.all()

    publication_list = []

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name == "admin" or name == str(None):
        return redirect("/rpa/login")

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
        if not paper.publication_name:
            paper.publication_name = "NULL"
        if not paper.publisher:
            paper.publisher = "NULL"

        if (
            name in first_author
            or name in second_author
            or name in third_author
            or name in other_authors
        ):
            publication_list.append(paper)
        
    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

    context = {"papers": publication_list, "name": name}

    return render(request, "user_home.html", context)


def user_view_paper_details(request, paperid):
    if request.method != "GET":
        return render(request, "error.html")

    if not paperid:
        return render(request, "error.html")

    try:
        paper = Publications.objects.get(uniqueid=paperid)
    except Publications.DoesNotExist:
        return render(request, "error.html")

    name = str(request.session.get("FACULTY_NAME"))

    if not (
        name in paper.first_author
        or name in paper.second_author
        or name in paper.third_author
        or name in paper.other_authors
    ):
        return render(
            request,
            "custom_error.html",
            {
                "error_title": "Unauthorized!",
                "error_message": "You are unauthorized to view the details of this publication.",
            },
        )

    return render(request, "publication.html", {"paper": paper, "name": name})


def user_upload_paper(request, uniqueid):
    if request.method == "GET":
        try:
            publ = Publications.objects.get(uniqueid=uniqueid)
        except Publications.DoesNotExist:
            return render(request, "error.html")

        name = str(request.session.get("FACULTY_NAME"))

        if not (
            name in publ.first_author
            or name in publ.second_author
            or name in publ.third_author
            or name in publ.other_authors
        ):
            return render(
                request,
                "custom_error.html",
                {
                    "error_title": "Unauthorized!",
                    "error_message": "You are unauthorized to view the details of this publication.",
                },
            )

        return render(
            request, "upload.html", {"title": publ.title, "uniqueid": uniqueid}
        )
    else:
        publ = Publications.objects.get(uniqueid=uniqueid)
        name = str(request.session.get("FACULTY_NAME"))

        if not (
            name in publ.first_author
            or name in publ.second_author
            or name in publ.third_author
            or name in publ.other_authors
        ):
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


def authenticate_user(request, unqiueid, name):
    if request.method == "POST":
        return HttpResponse("Invalid request")

    try:
        paper = Publications.objects.get(uniqueid=unqiueid)
    except Publications.DoesNotExist:
        return HttpResponse("false")

    if (
        name in paper.first_author
        or name in paper.second_author
        or name in paper.third_author
        or name in paper.other_authors
    ):
        return HttpResponse("true")
    return HttpResponse("false")


def error(request):
    return render(
        request,
        "error.html"
    )


def user_verify_paper(request):
    if request.method == "GET":
        return HttpResponse("Invalid Request!")

    updateData = dict(request.POST)

    updates = {}

    uniqueid = request.POST.get("uniqueid")

    for key, value in updateData.items():
        if key != "csrfmiddlewaretoken" and key != "uniqueid":
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

    name = str(request.session.get("FACULTY_NAME"))
    try:
        paper = Publications.objects.get(uniqueid=uniqueid)
    except Publications.DoesNotExist:
        return HttpResponse("Error")

    updates["verified"] = "True"

    if not (
        name in paper.first_author
        or name in paper.second_author
        or name in paper.third_author
        or name in paper.other_authors
    ):
        return HttpResponse("Unauthorized")

    if not Publications.objects.filter(uniqueid=uniqueid):
        return HttpResponse("Paper not found!")

    Publications.objects.filter(uniqueid=uniqueid).update(**updates)

    return HttpResponse("OK")


def user_dashboard(request):
    papers = Publications.objects.all()

    publication_list = []

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name == "admin" or name == "None":
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

        if (
            name in first_author
            or name in second_author
            or name in third_author
            or name in other_authors
        ):
            publication_list.append(paper)
    
    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)

    context = {
        "papers": publication_list,
        "form": form,
        "new_sno": f"{int(len(publication_list)) + 1}",
        "name": name,
    }

    # paper_records =
    return render(request, "dashboard.html", context)


def user_verification(request):
    papers = Publications.objects.all()

    publication_list = []

    name = str(request.session.get("FACULTY_NAME"))

    if name is None or name == "admin" or name == str(None):
        return redirect("/rpa/login")

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
        if not paper.publication_name:
            paper.publication_name = "NULL"
        if not paper.publisher:
            paper.publisher = "NULL"

        if (
            name in first_author
            or name in second_author
            or name in third_author
            or name in other_authors
        ):
            publication_list.append(paper)

    publication_list.sort(reverse=True, key=lambda x: x.end_academic_year)
    
    context = {"papers": publication_list, "name": name}

    return render(request, "verification.html", context)


def user_get_doi(request):
    if request.method == "POST":
        doi = request.POST.get("doi")
        ay = request.POST.get("AY")

        title = Extractor.get_title(doi)

        if not title:
            return render(request, "get_title.html", {"doi": doi, "AY": ay})

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
            return render(request, "add_publication.html", {"result": result})

    name = request.session.get("FACULTY_NAME", "")

    if (name == "") or (name is None):
        return redirect("/rpa/user/error")

    return render(request, "get_doi.html", {"name": name})


def user_get_title(request):
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
            return render(request, "add_publication.html", {"result": result})

    name = request.session.get("FACULTY_NAME", "")

    if (name == "") or (name is None):
        return redirect("/rpa/user/error")

    return render(request, "get_title.html", {"name": name})


def user_insert_paper(request):
    data_to_be_inserted = {}

    faculty_name = request.session["FACULTY_NAME"]

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

    first_author = request.POST.get("first_author")
    second_author = request.POST.get("second_author")
    third_author = request.POST.get("third_author")
    other_authors = request.POST.get("other_authors")

    if not (
        faculty_name in first_author
        or faculty_name in second_author
        or faculty_name in third_author
        or faculty_name in other_authors
    ):
        return HttpResponse("You are not an author of this paper. Cannot add paper.")

    new_record = Publications(**data_to_be_inserted)

    try:
        new_record.save()
    except django.db.utils.IntegrityError:
        return HttpResponse("Paper already exists! Cannot add paper.")

    return HttpResponse("OK")
