# meuprojeto_sisu/urls.py

from django.contrib import admin
from django.urls import path
from sisu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'), # A URL principal volta a ser 'dashboard'
    path('prever-notas/', views.prever_notas_api, name='prever_notas_api'),
]