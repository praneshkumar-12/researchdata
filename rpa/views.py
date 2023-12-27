from . import users
from . import dbadmin
from django.http import HttpResponse

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

def admin_dashboard(request):
    return dbadmin.admin_dashboard(request)

def admin_insert_paper(request):
    return dbadmin.admin_insert_paper(request)