from django.urls import path, include
from rest_framework.routers import DefaultRouter
from triage import views

router = DefaultRouter()
router.register(r'coberturas', views.CoberturaViewSet, basename='cobertura')
router.register(r'pacientes', views.PacienteViewSet, basename='paciente')
router.register(r'visitas', views.VisitaEmergenciaViewSet, basename='visita')
router.register(r'triages', views.TriageViewSet, basename='triage')

urlpatterns = [
    path('', include(router.urls)),
]
