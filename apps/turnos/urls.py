from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_profesional, name="dashboard_profesional"),
    path("clientes/ajax/nuevo/", views.crear_cliente_ajax, name="crear_cliente_ajax"),
    path("turnos/ajax/nuevo/", views.crear_turno_ajax, name="crear_turno_ajax"),
    path("turnos/<int:turno_id>/editar/", views.actualizar_turno_ajax, name="actualizar_turno_ajax"),
    path("turnos/<int:turno_id>/eliminar/", views.eliminar_turno_ajax, name="eliminar_turno_ajax"),
]