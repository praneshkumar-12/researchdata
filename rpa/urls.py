from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("auth/dashboard", views.dashboard, name="dashboard"),
    path("auth/verify", views.verify_paper, name="verify_paper"),
    path("auth/scrape", views.scrape_data, name="scrape_data"),
    path("auth/add_paper", views.insert_paper, name="insert_paper"),
    path("auth/upload/<uniqueid>", views.upload_paper, name="upload_paper"),
    path("auth/removeupload", views.remove_upload, name="remove_upload"),
    path("auth/update_paper", views.update_paper, name="update_paper"),
    path(
        "static/upload/<filename>",
        views.FileDownloadView.as_view(),
        name="file_download",
    ),
    # path("auth/upload/<uniqueid>", views.upload_paper),
    path("dbadmin/dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("dbadmin/add_paper", views.admin_insert_paper, name="admin_insert_paper"),
    path("dbadmin/verify", views.admin_verify_paper, name="admin_verify_paper"),
    path("dbadmin/delete", views.admin_delete_paper, name="admin_delete_paper"),
    path("dbadmin/update", views.admin_update_paper, name="admin_update_paper"),
]
