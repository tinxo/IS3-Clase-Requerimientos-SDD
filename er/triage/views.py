from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from triage.models import Cobertura, Paciente, VisitaEmergencia, Triage
from triage.serializers import (
    CoberturaSerializer,
    PacienteSerializer,
    PacienteListSerializer,
    VisitaEmergenciaSerializer,
    TriageSerializer,
    SugerirESISerializer,
)
from triage.esi_logic import sugerir_nivel_esi


class CoberturaViewSet(viewsets.ModelViewSet):
    """CRUD de coberturas médicas (obras sociales / prepagas)."""
    queryset = Cobertura.objects.filter(activo=True)
    serializer_class = CoberturaSerializer
    permission_classes = [IsAuthenticated]


class PacienteViewSet(viewsets.ModelViewSet):
    """CRUD de pacientes con búsqueda por DNI o nombre."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PacienteListSerializer
        return PacienteSerializer

    def get_queryset(self):
        queryset = Paciente.objects.select_related('cobertura').filter(activo=True)
        search = self.request.query_params.get('search', '').strip()
        if search:
            if search.isdigit():
                queryset = queryset.filter(dni=search)
            else:
                queryset = queryset.filter(
                    Q(nombre__icontains=search) | Q(apellido__icontains=search)
                )
        return queryset.order_by('apellido', 'nombre')

    @action(detail=True, methods=['get'], url_path='visitas')
    def visitas(self, request, pk=None):
        """Devuelve el historial de visitas de un paciente."""
        paciente = self.get_object()
        visitas = VisitaEmergencia.objects.filter(paciente=paciente).order_by('-fecha_ingreso')
        serializer = VisitaEmergenciaSerializer(visitas, many=True, context={'request': request})
        return Response(serializer.data)


class VisitaEmergenciaViewSet(viewsets.ModelViewSet):
    """
    CRUD de visitas de emergencia.
    Permite filtrar por estado y nivel ESI.
    """
    serializer_class = VisitaEmergenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = VisitaEmergencia.objects.select_related(
            'paciente', 'paciente__cobertura', 'registrado_por'
        ).order_by('-fecha_ingreso')

        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        nivel_esi = self.request.query_params.get('nivel_esi')
        if nivel_esi:
            queryset = queryset.filter(triage__nivel_esi=nivel_esi)

        return queryset

    @action(detail=True, methods=['post', 'get'], url_path='triage')
    def triage(self, request, pk=None):
        """
        GET: devuelve el triage de la visita (si existe).
        POST: crea un nuevo triage para la visita.
        """
        visita = self.get_object()

        if request.method == 'GET':
            if not hasattr(visita, 'triage'):
                return Response({'detail': 'Esta visita aún no tiene triage.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TriageSerializer(visita.triage)
            return Response(serializer.data)

        # POST
        if hasattr(visita, 'triage'):
            return Response(
                {'detail': 'Esta visita ya tiene triage registrado.'},
                status=status.HTTP_409_CONFLICT
            )

        data = request.data.copy()
        data['visita'] = visita.pk
        serializer = TriageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TriageViewSet(viewsets.ModelViewSet):
    """CRUD de registros de triage."""
    serializer_class = TriageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Triage.objects.select_related('visita', 'enfermero').order_by('-timestamp')

    @action(detail=False, methods=['post'], url_path='sugerir-esi')
    def sugerir_esi(self, request):
        """
        Sugiere un nivel ESI basado en signos vitales y evaluaciones clínicas.
        No requiere triage previo ni visita existente.
        """
        serializer = SugerirESISerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        signos_vitales = {
            'presion_sistolica': data.get('presion_sistolica'),
            'presion_diastolica': data.get('presion_diastolica'),
            'frecuencia_cardiaca': data.get('frecuencia_cardiaca'),
            'saturacion_o2': data.get('saturacion_o2'),
            'frecuencia_respiratoria': data.get('frecuencia_respiratoria'),
        }

        nivel, justificacion = sugerir_nivel_esi(
            signos_vitales=signos_vitales,
            dolor_eva=data.get('dolor_eva'),
            glasgow=data.get('glasgow'),
            via_aerea=data.get('via_aerea', 'permeable'),
            motivo=data.get('motivo', ''),
        )

        colores = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'green', 5: 'blue'}
        emojis = {1: '🔴', 2: '🟠', 3: '🟡', 4: '🟢', 5: '🔵'}

        return Response({
            'nivel_sugerido': nivel,
            'justificacion': justificacion,
            'color': colores.get(nivel, 'gray'),
            'emoji': emojis.get(nivel, '⚪'),
        })
