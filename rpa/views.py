from . import users
from . import dbadmin
from django.http import FileResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import render
from django.views import View
import os
from rpa.models import Publications

# Common for users and admin


def login(request):
    return users.login(request)


def forgot_password(request):
    return users.forgot_password(request)


def otp_verification(request):
    return users.otp_verification(request)


def logout(request):
    name = str(request.session.get("FACULTY_NAME"))
    request.session["FACULTY_NAME"] = None
    return HttpResponse("Logged out successfully!")


def reset_password(request):
    return users.reset_password(request)


# User specific


def user_home(request):
    return users.user_home(request)


def user_view_paper_details(request, paperid):
    return users.user_view_paper_details(request, paperid)


def autheticate_user(request, uniqueid, name):
    return users.authenticate_user(request, uniqueid, name)


def request_changes(request, uniqueid):
    return users.request_changes(request, uniqueid)


def error(request):
    return users.error(request)


def user_verify_paper(request):
    return users.user_verify_paper(request)


def user_dashboard(request):
    return users.user_dashboard(request)


def user_verification(request):
    return users.user_verification(request)


def user_get_doi(request):
    return users.user_get_doi(request)


def user_get_title(request):
    return users.user_get_title(request)


def user_insert_paper(request):
    return users.user_insert_paper(request)


def user_upload_paper(request, uniqueid):
    return users.user_upload_paper(request, uniqueid)


class FileDownloadView(View):
    def get(self, request, filename):
        file_path = f"rpa/static/upload/{filename}"

        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file and create a FileResponse
            file = open(file_path, "rb")
            response = FileResponse(file, as_attachment=True)
            try:
                publ = Publications.objects.get(uniqueid=filename.replace(".pdf", ""))
            except Publications.DoesNotExist:
                return HttpResponseNotFound("Some error occurred!")
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

            response["Content-Disposition"] = f'attachment; filename="{publ.title}.pdf"'
            return response
        else:
            # Return a 404 response if the file does not exist
            return HttpResponseNotFound("File not found!")


# Admin


def admin_home(request):
    return dbadmin.admin_home(request)


def admin_dashboard(request):
    return dbadmin.admin_dashboard(request)


def admin_view_paper_details(request, paperid):
    return dbadmin.admin_view_paper_details(request, paperid)


def admin_upload_paper(request, uniqueid):
    return dbadmin.admin_upload_paper(request, uniqueid)


def admin_remove_upload(request):
    return dbadmin.admin_remove_upload(request)


def admin_update_paper(request):
    return dbadmin.admin_update_paper(request)


def admin_insert_paper(request):
    return dbadmin.admin_insert_paper(request)


def admin_manually_insert_paper(request):
    return dbadmin.admin_manually_insert_paper(request)


def admin_delete_paper(request):
    return dbadmin.admin_delete_paper(request)

def admin_get_word(request):
    return dbadmin.admin_get_word(request)


def admin_verify_paper(request):
    return dbadmin.admin_verify_paper(request)


def admin_verification(request):
    return dbadmin.admin_verification(request)


def admin_get_doi(request):
    return dbadmin.admin_get_doi(request)


def admin_get_title(request):
    return dbadmin.admin_get_title(request)


def admin_get_charts(request):
    return dbadmin.admin_get_charts(request)


class AdminFileDownloadView(View):
    def get(self, request, filename):
        file_path = f"rpa/static/upload/{filename}"

        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file and create a FileResponse
            file = open(file_path, "rb")
            response = FileResponse(file, as_attachment=True)
            try:
                publ = Publications.objects.get(uniqueid=filename.replace(".pdf", ""))
            except Publications.DoesNotExist:
                return HttpResponseNotFound("Some error occurred!")
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

            response["Content-Disposition"] = f'attachment; filename="{publ.title}.pdf"'
            return response
        else:
            # Return a 404 response if the file does not exist
            return HttpResponseNotFound("File not found!")

class AdminWordDownloadView(View):
    def get(self, request):
        file_path = "research_publications.docx"

        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file and create a FileResponse
            file = open(file_path, "rb")
            response = FileResponse(file, as_attachment=True)
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

            response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return response
        else:
            # Return a 404 response if the file does not exist
            return HttpResponseNotFound("File not found!")
