# frontend/supermercado/urls.py
from django.urls import path
from . import views

app_name = "supermercado"

urlpatterns = [
    path("", views.home, name="home"),
    path("init/", views.init_sistema, name="init"),
    path("cargar-config/", views.cargar_config, name="cargar_config"),
]
