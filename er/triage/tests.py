from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.core.exceptions import ValidationError
from decimal import Decimal

from triage.models import Paciente, Cobertura, VisitaEmergencia, Triage
from triage.esi_logic import sugerir_nivel_esi


class ESILogicTestCase(TestCase):
    def test_sugerir_esi_nivel_2_por_saturacion(self):
        nivel, just = sugerir_nivel_esi(
            {'saturacion_o2': 88},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Saturación O2 < 90%', just)

    def test_sugerir_esi_nivel_1_via_aerea_obstruida(self):
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=0,
            glasgow=15,
            via_aerea='obstruida',
            motivo=''
        )
        self.assertEqual(nivel, 1)
        self.assertIn('Vía aérea obstruida', just)

    def test_sugerir_esi_nivel_1_glasgow_critico(self):
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=0,
            glasgow=7,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 1)
        self.assertIn('Glasgow < 8', just)

    def test_sugerir_esi_nivel_3_dolor_moderado(self):
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=5,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 3)
        self.assertIn('Dolor moderado-severo', just)

    def test_sugerir_esi_nivel_5_estable(self):
        nivel, _ = sugerir_nivel_esi(
            {'saturacion_o2': 98, 'frecuencia_cardiaca': 80, 'presion_sistolica': 120},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 5)


class TriageWorkflowTestCase(TestCase):
    def setUp(self):
        self.user_recepcion = User.objects.create_user(username='recepcionista', password='password123')
        self.user_enfermero = User.objects.create_user(username='enfermero', password='password123')
        self.cobertura = Cobertura.objects.create(nombre='Particular', tipo='particular')
        self.paciente = Paciente.objects.create(
            dni='12345678',
            nombre='Juan',
            apellido='Pérez',
            fecha_nacimiento=date(1990, 5, 15),
            sexo='M',
            telefono='1122334455',
            cobertura=self.cobertura
        )

    def test_crear_triage_cambia_estado_visita(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente,
            registrado_por=self.user_recepcion,
            motivo_ingreso_breve='Dolor de cabeza'
        )
        self.assertEqual(visita.estado, 'esperando_triage')
        
        triage = Triage.objects.create(
            visita=visita,
            nivel_esi=3,
            motivo_consulta='Dolor de cabeza intenso',
            enfermero=self.user_enfermero,
            presion_sistolica=130,
            presion_diastolica=80,
            frecuencia_cardiaca=85,
            temperatura=Decimal('36.8'),
            saturacion_o2=98,
            frecuencia_respiratoria=16,
            dolor_eva=5,
            glasgow=15,
            via_aerea='permeable'
        )
        
        visita.refresh_from_db()
        self.assertEqual(visita.estado, 'esperando_atencion')

    def test_crear_triage_visita_no_esperando_triage_fails(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente,
            registrado_por=self.user_recepcion,
            motivo_ingreso_breve='Dolor de cabeza',
            estado=VisitaEmergencia.Estado.ESPERANDO_ATENCION
        )
        
        with self.assertRaises(ValidationError):
            Triage.objects.create(
                visita=visita,
                nivel_esi=3,
                motivo_consulta='Dolor de cabeza intenso',
                enfermero=self.user_enfermero,
                presion_sistolica=130,
                presion_diastolica=80,
                frecuencia_cardiaca=85,
                temperatura=Decimal('36.8'),
                saturacion_o2=98,
                frecuencia_respiratoria=16,
                dolor_eva=5,
                glasgow=15,
                via_aerea='permeable'
            )
