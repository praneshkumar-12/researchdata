from . import users
from . import dbadmin
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views import View
import os

def login(request):
    return users.login(request)


def dashboard(request):
    return users.dashboard(request)


def verify_paper(request):
    return users.verify_paper(request)


def scrape_data(request):
    return users.scrape_data(request)


def insert_paper(request):
    return users.insert_paper(request)

def upload_paper(request, uniqueid):
    return users.upload_paper(request, uniqueid)

def admin_dashboard(request):
    return dbadmin.admin_dashboard(request)

def admin_insert_paper(request):
    return dbadmin.admin_insert_paper(request)

def admin_verify_paper(request):
    return dbadmin.admin_verify_paper(request)

def admin_delete_paper(request):
    return dbadmin.admin_delete_paper(request)

def admin_update_paper(request):
    return dbadmin.admin_update_paper(request)

class FileDownloadView(View):
    def get(self, request, filename):
        file_path = f'rpa/static/upload/{filename}'
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file and create a FileResponse
            file =  open(file_path, 'rb')
            response = FileResponse(file, as_attachment=True)
            return response
        else:
            # Return a 404 response if the file does not exist
            return HttpResponseNotFound("File not found!")
        
def remove_upload(request):
    return dbadmin.admin_remove_upload(request)