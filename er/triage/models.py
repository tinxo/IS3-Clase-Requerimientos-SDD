from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ===== Modelos Base (deberían estar en módulo 'pacientes') =====
# Por ahora los incluimos aquí para desarrollo del módulo triage

class Cobertura(models.Model):
    """
    Obras sociales y prepagas.
    """
    nombre = models.CharField(max_length=200, unique=True)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('obra_social', 'Obra Social'),
            ('prepaga', 'Prepaga'),
            ('particular', 'Particular'),
        ],
        default='obra_social'
    )
    codigo = models.CharField(max_length=50, blank=True, help_text="Código interno o de PAMI")
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'coberturas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    """
    Modelo maestro de pacientes.
    
    Representa el registro permanente de un paciente en el sistema.
    Un paciente puede tener múltiples visitas a emergencias a lo largo del tiempo.
    """
    
    # Datos demográficos
    dni = models.CharField(
        max_length=15, 
        unique=True,
        help_text="DNI argentino sin puntos ni espacios"
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(
        max_length=1, 
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('X', 'Otro')
        ]
    )
    
    # Contacto
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Cobertura médica
    cobertura = models.ForeignKey(
        Cobertura, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='pacientes'
    )
    numero_afiliado = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'pacientes'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['apellido', 'nombre']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"
    
    @property
    def edad(self):
        """Calcula la edad del paciente en años."""
        from datetime import date
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class VisitaEmergencia(models.Model):
    """
    Representa un ingreso del paciente al servicio de emergencias.
    
    Una visita puede tener:
    - Un triage (relación 1:1)
    - Una atención médica (relación 1:1)
    """
    
    class Estado(models.TextChoices):
        ESPERANDO_TRIAGE = 'esperando_triage', 'Esperando Triage'
        ESPERANDO_ATENCION = 'esperando_atencion', 'Esperando Atención'
        EN_ATENCION = 'en_atencion', 'En Atención'
        FINALIZADO = 'finalizado', 'Finalizado'
        ABANDONO = 'abandono', 'Abandono'
    
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.PROTECT,
        related_name='visitas'
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_egreso = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ESPERANDO_TRIAGE
    )
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='visitas_registradas'
    )
    motivo_ingreso_breve = models.CharField(
        max_length=200,
        help_text="Motivo breve registrado en recepción"
    )
    
    class Meta:
        db_table = 'visitas_emergencia'
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['estado', 'fecha_ingreso']),
            models.Index(fields=['paciente', '-fecha_ingreso']),
        ]
    
    def __str__(self):
        return f"Visita {self.id} - {self.paciente.nombre_completo} - {self.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def tiempo_espera_minutos(self):
        """Calcula el tiempo de espera en minutos desde el ingreso."""
        from django.utils import timezone
        if self.fecha_egreso:
            fin = self.fecha_egreso
        else:
            fin = timezone.now()
        delta = fin - self.fecha_ingreso
        return int(delta.total_seconds() / 60)


# ===== Modelo Triage =====

class Triage(models.Model):
    """
    Clasificación de triage según ESI (Emergency Severity Index).
    """
    
    class NivelESI(models.IntegerChoices):
        RESUCITACION = 1, 'ESI 1 - Resucitación'
        EMERGENCIA = 2, 'ESI 2 - Emergencia'
        URGENCIA = 3, 'ESI 3 - Urgencia'
        MENOS_URGENTE = 4, 'ESI 4 - Menos Urgente'
        NO_URGENTE = 5, 'ESI 5 - No Urgente'
    
    class ViaAerea(models.TextChoices):
        PERMEABLE = 'permeable', 'Permeable'
        COMPROMETIDA = 'comprometida', 'Comprometida'
        OBSTRUIDA = 'obstruida', 'Obstruida'
    
    visita = models.OneToOneField(
        VisitaEmergencia, 
        on_delete=models.CASCADE,
        related_name='triage'
    )
    nivel_esi = models.IntegerField(choices=NivelESI.choices)
    motivo_consulta = models.TextField()
    
    # Signos vitales
    presion_sistolica = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(40), MaxValueValidator(300)],
        help_text="mmHg"
    )
    presion_diastolica = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(200)],
        help_text="mmHg"
    )
    frecuencia_cardiaca = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="latidos por minuto"
    )
    temperatura = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(30.0), MaxValueValidator(45.0)],
        help_text="°C"
    )
    saturacion_o2 = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        help_text="%"
    )
    frecuencia_respiratoria = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        help_text="respiraciones por minuto"
    )
    
    # Evaluaciones
    dolor_eva = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Escala Visual Analógica 0-10"
    )
    glasgow = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(3), MaxValueValidator(15)],
        help_text="Escala de Coma de Glasgow"
    )
    via_aerea = models.CharField(
        max_length=20,
        choices=ViaAerea.choices,
        default=ViaAerea.PERMEABLE
    )
    
    # Metadata
    enfermero = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='triages_realizados'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'triages'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Triage ESI {self.nivel_esi} - Visita {self.visita.id}"
    
    @property
    def color_esi(self):
        """Retorna el color asociado al nivel ESI."""
        colores = {
            1: 'red',
            2: 'orange',
            3: 'yellow',
            4: 'green',
            5: 'blue',
        }
        return colores.get(self.nivel_esi, 'gray')
    
    @property
    def nombre_nivel_esi(self):
        """Retorna el nombre descriptivo del nivel ESI."""
        nombres = {
            1: 'Resucitación',
            2: 'Emergencia',
            3: 'Urgencia',
            4: 'Menos Urgente',
            5: 'No Urgente',
        }
        return nombres.get(self.nivel_esi, 'Desconocido')
    
    @property
    def emoji_esi(self):
        """Retorna el emoji asociado al nivel ESI."""
        emojis = {
            1: '🔴',
            2: '🟠',
            3: '🟡',
            4: '🟢',
            5: '🔵',
        }
        return emojis.get(self.nivel_esi, '⚪')
    
    @property
    def tiempo_objetivo_minutos(self):
        """Retorna el tiempo objetivo de atención según nivel ESI."""
        tiempos = {
            1: 0,      # Inmediato
            2: 10,     # < 10 minutos
            3: 60,     # < 1 hora
            4: 120,    # < 2 horas
            5: 240,    # < 4 horas
        }
        return tiempos.get(self.nivel_esi, 240)
