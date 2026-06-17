from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.core.exceptions import ValidationError
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status

from triage.models import Paciente, Cobertura, VisitaEmergencia, Triage
from triage.esi_logic import sugerir_nivel_esi


class ESILogicTestCase(TestCase):
    """Tests para la lógica de sugerencia de nivel ESI."""
    
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
    
    def test_sugerir_esi_nivel_1_saturacion_critica(self):
        """Test ESI 1 por saturación crítica (<85%)."""
        nivel, just = sugerir_nivel_esi(
            {'saturacion_o2': 82},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 1)
        self.assertIn('Saturación O2 crítica', just)
    
    def test_sugerir_esi_nivel_2_via_aerea_comprometida(self):
        """Test ESI 2 por vía aérea comprometida."""
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=0,
            glasgow=15,
            via_aerea='comprometida',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Vía aérea comprometida', just)
    
    def test_sugerir_esi_nivel_2_dolor_severo(self):
        """Test ESI 2 por dolor severo (EVA >= 8)."""
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=9,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Dolor severo', just)
    
    def test_sugerir_esi_nivel_2_glasgow_alterado(self):
        """Test ESI 2 por Glasgow alterado (< 14)."""
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=0,
            glasgow=13,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Glasgow < 14', just)
    
    def test_sugerir_esi_nivel_2_taquicardia_severa(self):
        """Test ESI 2 por taquicardia severa (FC > 150)."""
        nivel, just = sugerir_nivel_esi(
            {'frecuencia_cardiaca': 160},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Frecuencia cardíaca anormal', just)
        self.assertIn('160', just)
    
    def test_sugerir_esi_nivel_2_bradicardia_severa(self):
        """Test ESI 2 por bradicardia severa (FC < 50)."""
        nivel, just = sugerir_nivel_esi(
            {'frecuencia_cardiaca': 45},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Frecuencia cardíaca anormal', just)
        self.assertIn('45', just)
    
    def test_sugerir_esi_nivel_2_hipertension_severa(self):
        """Test ESI 2 por hipertensión severa (PAS > 200)."""
        nivel, just = sugerir_nivel_esi(
            {'presion_sistolica': 210},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 2)
        self.assertIn('Hipertensión severa', just)
        self.assertIn('210', just)
    
    def test_sugerir_esi_nivel_3_taquicardia_moderada(self):
        """Test ESI 3 por taquicardia moderada (FC 120-150)."""
        nivel, just = sugerir_nivel_esi(
            {'frecuencia_cardiaca': 130},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 3)
        self.assertIn('Frecuencia cardíaca en zona de alerta', just)
    
    def test_sugerir_esi_nivel_3_presion_alta(self):
        """Test ESI 3 por presión arterial elevada."""
        nivel, just = sugerir_nivel_esi(
            {'presion_sistolica': 185},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 3)
        self.assertIn('Presión arterial en zona de alerta', just)
    
    def test_sugerir_esi_nivel_3_presion_baja(self):
        """Test ESI 3 por presión arterial baja."""
        nivel, just = sugerir_nivel_esi(
            {'presion_sistolica': 85},
            dolor_eva=0,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 3)
        self.assertIn('Presión arterial en zona de alerta', just)
    
    def test_sugerir_esi_nivel_4_dolor_leve(self):
        """Test ESI 4 por dolor leve."""
        nivel, just = sugerir_nivel_esi(
            {},
            dolor_eva=2,
            glasgow=15,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 4)
        self.assertIn('Dolor leve-moderado', just)
    
    def test_sugerir_esi_prioriza_criterios_criticos(self):
        """Test que ESI 1 tiene prioridad sobre otros criterios."""
        # Vía aérea obstruida debe dar ESI 1 incluso con dolor leve
        nivel, just = sugerir_nivel_esi(
            {'saturacion_o2': 98, 'frecuencia_cardiaca': 80},
            dolor_eva=2,
            glasgow=15,
            via_aerea='obstruida',
            motivo=''
        )
        self.assertEqual(nivel, 1)
        self.assertIn('Vía aérea obstruida', just)
    
    def test_sugerir_esi_con_valores_none(self):
        """Test que la función maneja correctamente valores None."""
        nivel, just = sugerir_nivel_esi(
            {'saturacion_o2': None, 'frecuencia_cardiaca': None},
            dolor_eva=None,
            glasgow=None,
            via_aerea='permeable',
            motivo=''
        )
        self.assertEqual(nivel, 5)
        self.assertIn('Signos vitales estables', just)


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

    def test_dos_triages_para_misma_visita_falla(self):
        """Un triage por visita (OneToOne)."""
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente,
            registrado_por=self.user_recepcion,
            motivo_ingreso_breve='Dolor abdominal'
        )
        Triage.objects.create(
            visita=visita, nivel_esi=3, motivo_consulta='Dolor abd',
            enfermero=self.user_enfermero
        )
        with self.assertRaises(Exception):
            Triage.objects.create(
                visita=visita, nivel_esi=4, motivo_consulta='Otro',
                enfermero=self.user_enfermero
            )

    def test_color_esi_propiedad(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente,
            registrado_por=self.user_recepcion,
            motivo_ingreso_breve='Test'
        )
        triage = Triage.objects.create(
            visita=visita, nivel_esi=1, motivo_consulta='Crítico',
            enfermero=self.user_enfermero
        )
        self.assertEqual(triage.color_esi, 'red')
        triage2 = Triage.objects.create(
            visita=VisitaEmergencia.objects.create(
                paciente=self.paciente, registrado_por=self.user_recepcion,
                motivo_ingreso_breve='Test2'
            ),
            nivel_esi=5, motivo_consulta='Estable', enfermero=self.user_enfermero
        )
        self.assertEqual(triage2.color_esi, 'blue')

    def test_tiempo_objetivo_minutos(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente,
            registrado_por=self.user_recepcion,
            motivo_ingreso_breve='Test'
        )
        triage = Triage.objects.create(
            visita=visita, nivel_esi=2, motivo_consulta='Emergencia',
            enfermero=self.user_enfermero
        )
        self.assertEqual(triage.tiempo_objetivo_minutos, 10)


class TriageModelValidationTestCase(TestCase):
    """Tests de validaciones de modelo Triage."""

    def setUp(self):
        self.user = User.objects.create_user(username='enfermero', password='password123')
        self.paciente = Paciente.objects.create(
            dni='99887766', nombre='Ana', apellido='Gómez',
            fecha_nacimiento=date(1985, 3, 20), sexo='F', telefono='5544332211'
        )

    def test_nivel_esi_fuera_de_rango(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Test'
        )
        with self.assertRaises(ValidationError):
            t = Triage(
                visita=visita, nivel_esi=6, motivo_consulta='X',
                enfermero=self.user
            )
            t.full_clean()

    def test_dolor_eva_fuera_de_rango(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Test'
        )
        with self.assertRaises(ValidationError):
            t = Triage(
                visita=visita, nivel_esi=3, motivo_consulta='X',
                enfermero=self.user, dolor_eva=11
            )
            t.full_clean()

    def test_glasgow_fuera_de_rango(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Test'
        )
        with self.assertRaises(ValidationError):
            t = Triage(
                visita=visita, nivel_esi=1, motivo_consulta='X',
                enfermero=self.user, glasgow=2
            )
            t.full_clean()

    def test_saturacion_o2_fuera_de_rango(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Test'
        )
        with self.assertRaises(ValidationError):
            t = Triage(
                visita=visita, nivel_esi=1, motivo_consulta='X',
                enfermero=self.user, saturacion_o2=45
            )
            t.full_clean()

    def test_via_aerea_default_es_permeable(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Test'
        )
        t = Triage.objects.create(
            visita=visita, nivel_esi=5, motivo_consulta='OK',
            enfermero=self.user
        )
        self.assertEqual(t.via_aerea, 'permeable')

    def test_visita_estado_transicion_completa(self):
        """Test transición completa: esperando_triage -> esperando_atencion."""
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        self.assertEqual(visita.estado, 'esperando_triage')
        Triage.objects.create(
            visita=visita, nivel_esi=3, motivo_consulta='Dolor moderado',
            enfermero=self.user, dolor_eva=5, glasgow=15
        )
        visita.refresh_from_db()
        self.assertEqual(visita.estado, 'esperando_atencion')
        self.assertIsNotNone(visita.triage)


class VisitaEmergenciaModelTestCase(TestCase):
    """Tests del modelo VisitaEmergencia."""

    def setUp(self):
        self.user = User.objects.create_user(username='recepcionista', password='password123')
        self.paciente = Paciente.objects.create(
            dni='11223344', nombre='Carlos', apellido='López',
            fecha_nacimiento=date(1978, 11, 5), sexo='M', telefono='1122334455'
        )

    def test_estado_default_es_esperando_triage(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Fiebre'
        )
        self.assertEqual(visita.estado, 'esperando_triage')

    def test_tiene_triage_propiedad(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        self.assertFalse(hasattr(visita, 'triage') and visita.triage is not None)


# ===== API Tests =====

class CoberturaAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password123')
        self.client.force_authenticate(user=self.user)
        self.cobertura = Cobertura.objects.create(
            nombre='OSDE', tipo='prepaga', codigo='OSDE-001'
        )

    def test_listar_coberturas(self):
        response = self.client.get('/api/v1/coberturas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_cobertura(self):
        response = self.client.post('/api/v1/coberturas/', {
            'nombre': 'Swiss Medical', 'tipo': 'prepaga', 'codigo': 'SM-001'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detalle_cobertura(self):
        response = self.client.get(f'/api/v1/coberturas/{self.cobertura.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'OSDE')

    def test_eliminar_cobertura(self):
        response = self.client.delete(f'/api/v1/coberturas/{self.cobertura.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_sin_autenticacion(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/coberturas/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PacienteAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password123')
        self.client.force_authenticate(user=self.user)
        self.paciente = Paciente.objects.create(
            dni='30123456', nombre='María', apellido='García',
            fecha_nacimiento=date(1995, 7, 22), sexo='F', telefono='1155667788'
        )

    def test_listar_pacientes(self):
        response = self.client.get('/api/v1/pacientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_paciente(self):
        response = self.client.post('/api/v1/pacientes/', {
            'dni': '30999888', 'nombre': 'Pedro', 'apellido': 'Rodríguez',
            'fecha_nacimiento': '1988-01-15', 'sexo': 'M', 'telefono': '1199887766'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buscar_por_dni(self):
        response = self.client.get('/api/v1/pacientes/?search=30123456')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_buscar_por_nombre(self):
        response = self.client.get('/api/v1/pacientes/?search=García')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_detalle_paciente(self):
        response = self.client.get(f'/api/v1/pacientes/{self.paciente.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_visitas_paciente(self):
        VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        response = self.client.get(f'/api/v1/pacientes/{self.paciente.pk}/visitas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class VisitaEmergenciaAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='enfermero', password='password123')
        self.client.force_authenticate(user=self.user)
        self.paciente = Paciente.objects.create(
            dni='40111222', nombre='Laura', apellido='Martínez',
            fecha_nacimiento=date(1988, 4, 10), sexo='F', telefono='1133445566'
        )

    def test_crear_visita(self):
        response = self.client.post('/api/v1/visitas/', {
            'paciente_id': self.paciente.pk,
            'motivo_ingreso_breve': 'Dolor de espalda'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listar_visitas(self):
        VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        response = self.client.get('/api/v1/visitas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filtrar_por_estado(self):
        VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        response = self.client.get('/api/v1/visitas/?estado=esperando_triage')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_triage_via_endpoint(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor torácico'
        )
        response = self.client.post(f'/api/v1/visitas/{visita.pk}/triage/', {
            'nivel_esi': 3,
            'motivo_consulta': 'Dolor torácico opresivo',
            'presion_sistolica': 150,
            'presion_diastolica': 90,
            'frecuencia_cardiaca': 90,
            'saturacion_o2': 95,
            'dolor_eva': 6,
            'glasgow': 15,
            'via_aerea': 'permeable'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nivel_esi'], 3)
        self.assertEqual(response.data['color_esi'], 'yellow')
        self.assertEqual(response.data['enfermero'], 'enfermero')
        visita.refresh_from_db()
        self.assertEqual(visita.estado, 'esperando_atencion')

    def test_triage_duplicado_conflict(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        self.client.post(f'/api/v1/visitas/{visita.pk}/triage/', {
            'nivel_esi': 4, 'motivo_consulta': 'Dolor',
            'dolor_eva': 2, 'glasgow': 15, 'via_aerea': 'permeable'
        })
        response = self.client.post(f'/api/v1/visitas/{visita.pk}/triage/', {
            'nivel_esi': 3, 'motivo_consulta': 'Otro',
            'dolor_eva': 5, 'glasgow': 15, 'via_aerea': 'permeable'
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_obtener_triage(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        Triage.objects.create(
            visita=visita, nivel_esi=2, motivo_consulta='Emergencia',
            enfermero=self.user, dolor_eva=9, glasgow=14
        )
        response = self.client.get(f'/api/v1/visitas/{visita.pk}/triage/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nivel_esi'], 2)

    def test_obtener_triage_inexistente(self):
        visita = VisitaEmergencia.objects.create(
            paciente=self.paciente, registrado_por=self.user,
            motivo_ingreso_breve='Dolor'
        )
        response = self.client.get(f'/api/v1/visitas/{visita.pk}/triage/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SugerirESIApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='enfermero', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_sugerir_esi_ok(self):
        response = self.client.post('/api/v1/triages/sugerir-esi/', {
            'presion_sistolica': 160,
            'frecuencia_cardiaca': 95,
            'saturacion_o2': 95,
            'dolor_eva': 6,
            'glasgow': 15,
            'via_aerea': 'permeable',
            'motivo': 'Dolor torácico'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('nivel_sugerido', response.data)
        self.assertIn('justificacion', response.data)
        self.assertIn('color', response.data)
        self.assertIn('emoji', response.data)
        self.assertEqual(response.data['nivel_sugerido'], 3)
        self.assertEqual(response.data['color'], 'yellow')

    def test_sugerir_esi_via_aerea_obstruida(self):
        response = self.client.post('/api/v1/triages/sugerir-esi/', {
            'via_aerea': 'obstruida'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nivel_sugerido'], 1)
        self.assertEqual(response.data['color'], 'red')

    def test_sugerir_esi_datos_minimos(self):
        response = self.client.post('/api/v1/triages/sugerir-esi/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nivel_sugerido'], 5)

    def test_sugerir_esi_via_aerea_invalida(self):
        response = self.client.post('/api/v1/triages/sugerir-esi/', {
            'via_aerea': 'invalida'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
