from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("otp_verification/", views.otp_verification, name="otp_verification"),
    path("user/home", views.user_home, name="user_home"),
    path(
        "user/paper/<paperid>",
        views.user_view_paper_details,
        name="user_view_paper_details",
    ),
    path(
        "user/paper/upload/<uniqueid>",
        views.user_upload_paper,
        name="user_upload_paper",
    ),
    path(
        "user/authenticate/<uniqueid>/<name>",
        views.autheticate_user,
        name="authenticate_user",
    ),
    path("user/paper_verify/verify", views.user_verify_paper, name="user_verify_paper"),
    path("user/dashboard", views.user_dashboard, name="user_dashboard"),
    path("user/verification", views.user_verification, name="user_verification"),
    path("user/get_doi", views.user_get_doi, name="user_get_doi"),
    path("user/get_title", views.user_get_title, name="user_get_title"),
    path("user/insert_paper", views.user_insert_paper, name="user_insert_paper"),
    path("user/error", views.error, name="error"),
    path("user/logout", views.logout, name="log_out"),
    path(
        "static/upload/<filename>",
        views.FileDownloadView.as_view(),
        name="file_download",
    ),
    path(
        "static/upload/<filename>/admin",
        views.AdminFileDownloadView.as_view(),
        name="file_download",
    ),
    path("dbadmin/home", views.admin_home, name="admin_home"),
    path("dbadmin/dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("dbadmin/paper/remove", views.admin_remove_upload, name="admin_remove_upload"),
    path("dbadmin/paper/update", views.admin_update_paper, name="admin_update_paper"),
    path(
        "dbadmin/paper/<paperid>",
        views.admin_view_paper_details,
        name="admin_view_paper_details",
    ),
    path(
        "dbadmin/paper/upload/<uniqueid>",
        views.admin_upload_paper,
        name="admin_upload_paper",
    ),
    path(
        "dbadmin/paper_verify/verify",
        views.admin_verify_paper,
        name="admin_verify_paper",
    ),
    path("dbadmin/verification", views.admin_verification, name="admin_verification"),
    path("dbadmin/get_doi", views.admin_get_doi, name="admin_get_doi"),
    path("dbadmin/get_title", views.admin_get_title, name="admin_get_title"),
    path("dbadmin/insert_paper", views.admin_insert_paper, name="admin_insert_paper"),
    path(
        "dbadmin/manual_add_paper",
        views.admin_manually_insert_paper,
        name="admin_manually_insert_paper",
    ),
    path("dbadmin/delete_paper", views.admin_delete_paper, name="admin_delete_paper"),
    path("dbadmin/error", views.error, name="error"),
]
