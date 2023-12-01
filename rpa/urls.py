from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('auth/dashboard', views.dashboard, name='dashboard'),
    path('auth/verify', views.verify_paper, name='verify_paper'),
    path('auth/scrape', views.scrape_data, name='scrape_data'),
]