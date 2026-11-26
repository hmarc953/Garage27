from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .forms import IniciarSesionForm

urlpatterns = [
    path('', views.index, name='index'),
    path('servicios/', views.servicios, name='servicios'),
    path('trabajos/', views.trabajos, name='trabajos'),
    path('turnos/', views.turnos, name='turnos'),
    path('registro/', views.registro, name='registro'),
    path('validar-cuenta/', views.validar_cuenta, name='validar_cuenta'),
    path('login/', auth_views.LoginView.as_view(
        template_name='mi_app/login.html',
        authentication_form=IniciarSesionForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('panel/', views.panel_solicitudes, name='panel_solicitudes'),
    path('panel/nueva/', views.guardar_solicitud_panel, name='panel_solicitud_nueva'),
    path('panel/<int:pk>/editar/', views.guardar_solicitud_panel, name='panel_solicitud_editar'),
    path('panel/<int:pk>/eliminar/', views.eliminar_solicitud_panel, name='panel_solicitud_eliminar'),
    path('api/consultas/', views.ConsultasAPI.as_view(), name='api_consultas'),
    path('api/consultas/<int:pk>/', views.ConsultaDetalleAPI.as_view(), name='api_consulta_detalle'),
    path('api/vehiculos/catalogo/', views.catalogo_vehiculos_api, name='catalogo_vehiculos'),
]