from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path("productos/nuevo/", views.crear_producto, name="crear_producto"),
    path(
        "productos/<str:pid>/editar/",
        views.actualizar_producto,
        name="actualizar_producto",
    ),
    path(
        "productos/<str:pid>/eliminar/",
        views.eliminar_producto,
        name="eliminar_producto",
    ),
]
