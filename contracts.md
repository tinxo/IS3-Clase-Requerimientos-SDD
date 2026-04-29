# Contratos y Convenciones Compartidas

**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Propósito:** Define los contratos compartidos entre módulos (modelos, APIs, convenciones)

---

## 1. Introducción

Este documento establece los **contratos** que todos los módulos del sistema deben respetar. Incluye:

- **Modelo de datos completo**: Definición de todas las entidades y sus relaciones
- **Enums y constantes**: Valores predefinidos compartidos
- **Convenciones de API REST**: Estructura de endpoints y respuestas
- **Validaciones comunes**: Reglas de validación reutilizables
- **Convenciones de naming**: Estándares de nomenclatura
- **Auditoría**: Especificaciones de logging y trazabilidad

Todos los módulos (`core`, `pacientes`, `triage`, `atencion`, `dashboard`, `reportes`) deben referenciar este documento como fuente de verdad para los contratos compartidos.

---

## 2. Modelo de Datos Completo

### 2.1 Diagrama Entidad-Relación

```
┌─────────────────┐       ┌─────────────────┐
│    Usuario      │       │   Cobertura     │
│  (Django User)  │       │    Medica       │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ registra/atiende        │ tiene
         │                         │
         ▼                         ▼
┌─────────────────────────────────────────────┐
│                 Paciente                     │
├─────────────────────────────────────────────┤
│ - dni (único)                               │
│ - nombre, apellido                          │
│ - fecha_nacimiento, sexo                    │
│ - telefono, email, direccion                │
│ - cobertura → Cobertura                     │
│ - created_at, updated_at                    │
└────────────────────┬────────────────────────┘
                     │
                     │ tiene 0..1
                     ▼
       ┌─────────────────────────┐
       │  ContactoEmergencia     │
       │  AntecedentesMedicos    │
       └─────────────────────────┘
                     │
                     │ tiene muchas
                     ▼
┌─────────────────────────────────────────────┐
│            VisitaEmergencia                  │
├─────────────────────────────────────────────┤
│ - paciente → Paciente                       │
│ - fecha_ingreso                             │
│ - fecha_egreso (nullable)                   │
│ - estado (enum)                             │
│ - registrado_por → Usuario                  │
│ - motivo_ingreso_breve                      │
└──────────┬─────────────────┬────────────────┘
           │                 │
           │ tiene 0..1      │ tiene 0..1
           ▼                 ▼
┌──────────────────┐  ┌──────────────────────┐
│     Triage       │  │      Atencion        │
├──────────────────┤  ├──────────────────────┤
│ - nivel_esi      │  │ - medico → Usuario   │
│ - motivo_consulta│  │ - nota_evolucion     │
│ - signos_vitales │  │ - destino            │
│ - dolor_eva      │  │ - fecha_inicio       │
│ - glasgow        │  │ - fecha_fin          │
│ - via_aerea      │  └──────────┬───────────┘
│ - enfermero      │             │
│ - timestamp      │             │ tiene muchos
└──────────────────┘             ▼
                     ┌───────────────────────┐
                     │ - Diagnostico (CIE-10)│
                     │ - SolicitudEstudio    │
                     │ - Prescripcion        │
                     └───────────────────────┘
```

### 2.2 Definición de Modelos Django

#### 2.2.1 Paciente

```python
from django.db import models
from django.contrib.auth.models import User

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
        'Cobertura', 
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
```

#### 2.2.2 Cobertura

```python
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
```

#### 2.2.3 Contacto de Emergencia

```python
class ContactoEmergencia(models.Model):
    """
    Persona de contacto en caso de emergencia.
    """
    paciente = models.OneToOneField(
        Paciente, 
        on_delete=models.CASCADE,
        related_name='contacto_emergencia'
    )
    nombre = models.CharField(max_length=200)
    relacion = models.CharField(
        max_length=50,
        help_text="Ej: Padre, Madre, Cónyuge, Hijo/a, Hermano/a"
    )
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'contactos_emergencia'
    
    def __str__(self):
        return f"{self.nombre} ({self.relacion})"
```

#### 2.2.4 Antecedentes Médicos

```python
class AntecedentesMedicos(models.Model):
    """
    Historial médico relevante del paciente.
    """
    paciente = models.OneToOneField(
        Paciente, 
        on_delete=models.CASCADE,
        related_name='antecedentes'
    )
    alergias = models.TextField(
        blank=True, 
        help_text="Alergias conocidas (medicamentos, alimentos, etc.)"
    )
    medicacion_cronica = models.TextField(
        blank=True, 
        help_text="Medicación habitual que toma el paciente"
    )
    enfermedades_cronicas = models.TextField(
        blank=True, 
        help_text="Diabetes, HTA, EPOC, etc."
    )
    cirugias_previas = models.TextField(blank=True)
    antecedentes_familiares = models.TextField(blank=True)
    grupo_sanguineo = models.CharField(
        max_length=5, 
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'antecedentes_medicos'
    
    def __str__(self):
        return f"Antecedentes de {self.paciente.nombre_completo}"
```

#### 2.2.5 Visita de Emergencia

```python
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
```

#### 2.2.6 Triage

```python
from django.core.validators import MinValueValidator, MaxValueValidator

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
```

#### 2.2.7 Atención Médica

```python
class Atencion(models.Model):
    """
    Atención médica realizada al paciente.
    """
    
    class Destino(models.TextChoices):
        ALTA_MEDICA = 'alta_medica', 'Alta Médica'
        INTERNACION = 'internacion', 'Internación'
        DERIVACION = 'derivacion', 'Derivación'
        CIRUGIA = 'cirugia', 'Cirugía'
        OBSERVACION = 'observacion', 'Observación'
        OBITO = 'obito', 'Óbito'
        FUGA = 'fuga', 'Fuga / Abandono'
    
    visita = models.OneToOneField(
        VisitaEmergencia, 
        on_delete=models.CASCADE,
        related_name='atencion'
    )
    medico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='atenciones_realizadas'
    )
    
    # Evolución
    nota_evolucion = models.TextField()
    
    # Destino
    destino = models.CharField(max_length=20, choices=Destino.choices)
    destino_detalle = models.TextField(
        blank=True,
        help_text="Detalle del destino (ej: servicio, cama, institución)"
    )
    
    # Timestamps
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'atenciones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Atención {self.id} - Dr. {self.medico.get_full_name()}"


class Diagnostico(models.Model):
    """
    Diagnósticos según clasificación CIE-10.
    """
    atencion = models.ForeignKey(
        Atencion, 
        on_delete=models.CASCADE, 
        related_name='diagnosticos'
    )
    codigo_cie10 = models.CharField(
        max_length=10,
        help_text="Código CIE-10 (ej: I20.0)"
    )
    descripcion = models.CharField(max_length=500)
    es_principal = models.BooleanField(
        default=False,
        help_text="Marca si es el diagnóstico principal"
    )
    
    class Meta:
        db_table = 'diagnosticos'
        ordering = ['-es_principal', 'id']
    
    def __str__(self):
        principal = " (Principal)" if self.es_principal else ""
        return f"{self.codigo_cie10} - {self.descripcion}{principal}"


class SolicitudEstudio(models.Model):
    """
    Estudios solicitados (laboratorio, imágenes, etc.).
    """
    
    class TipoEstudio(models.TextChoices):
        LABORATORIO = 'laboratorio', 'Laboratorio'
        RADIOGRAFIA = 'radiografia', 'Radiografía'
        ECOGRAFIA = 'ecografia', 'Ecografía'
        TOMOGRAFIA = 'tomografia', 'Tomografía'
        RESONANCIA = 'resonancia', 'Resonancia'
        ECG = 'ecg', 'Electrocardiograma'
        OTRO = 'otro', 'Otro'
    
    atencion = models.ForeignKey(
        Atencion, 
        on_delete=models.CASCADE, 
        related_name='estudios'
    )
    tipo = models.CharField(max_length=20, choices=TipoEstudio.choices)
    descripcion = models.TextField()
    urgente = models.BooleanField(default=False)
    solicitado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'solicitudes_estudio'
        ordering = ['-urgente', '-solicitado_at']
    
    def __str__(self):
        urgente = " [URGENTE]" if self.urgente else ""
        return f"{self.get_tipo_display()}: {self.descripcion[:50]}{urgente}"


class Prescripcion(models.Model):
    """
    Prescripciones médicas (medicamentos).
    """
    atencion = models.ForeignKey(
        Atencion, 
        on_delete=models.CASCADE, 
        related_name='prescripciones'
    )
    medicamento = models.CharField(max_length=200)
    dosis = models.CharField(max_length=100, help_text="Ej: 500mg")
    via = models.CharField(
        max_length=50,
        help_text="Ej: Oral, IV, IM, SC"
    )
    frecuencia = models.CharField(
        max_length=100,
        help_text="Ej: cada 8 horas, stat, etc."
    )
    duracion = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Ej: 7 días, 1 dosis"
    )
    indicaciones = models.TextField(
        blank=True,
        help_text="Indicaciones especiales"
    )
    
    class Meta:
        db_table = 'prescripciones'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.medicamento} {self.dosis} - {self.via}"
```

---

## 3. Enums y Constantes

### 3.1 Estados de Visita

```python
# VisitaEmergencia.Estado
ESPERANDO_TRIAGE = 'esperando_triage'
ESPERANDO_ATENCION = 'esperando_atencion'
EN_ATENCION = 'en_atencion'
FINALIZADO = 'finalizado'
ABANDONO = 'abandono'
```

### 3.2 Niveles ESI

```python
# Triage.NivelESI
ESI_1_RESUCITACION = 1    # Rojo
ESI_2_EMERGENCIA = 2      # Naranja
ESI_3_URGENCIA = 3        # Amarillo
ESI_4_MENOS_URGENTE = 4   # Verde
ESI_5_NO_URGENTE = 5      # Azul
```

### 3.3 Colores ESI

```python
COLORES_ESI = {
    1: {'hex': '#DC2626', 'nombre': 'rojo', 'emoji': '🔴'},
    2: {'hex': '#EA580C', 'nombre': 'naranja', 'emoji': '🟠'},
    3: {'hex': '#EAB308', 'nombre': 'amarillo', 'emoji': '🟡'},
    4: {'hex': '#16A34A', 'nombre': 'verde', 'emoji': '🟢'},
    5: {'hex': '#2563EB', 'nombre': 'azul', 'emoji': '🔵'},
}
```

### 3.4 Tiempos Objetivo ESI (minutos)

```python
TIEMPOS_OBJETIVO_ESI = {
    1: 0,      # Inmediato
    2: 10,     # < 10 minutos
    3: 60,     # < 1 hora
    4: 120,    # < 2 horas
    5: 240,    # < 4 horas
}
```

### 3.5 Destinos de Atención

```python
# Atencion.Destino
ALTA_MEDICA = 'alta_medica'
INTERNACION = 'internacion'
DERIVACION = 'derivacion'
CIRUGIA = 'cirugia'
OBSERVACION = 'observacion'
OBITO = 'obito'
FUGA = 'fuga'
```

---

## 4. Convenciones de API REST

### 4.1 Estructura de URLs

Base URL: `/api/v1/`

```
/api/v1/pacientes/
/api/v1/visitas/
/api/v1/triages/
/api/v1/atenciones/
/api/v1/dashboard/
/api/v1/reportes/
```

### 4.2 Endpoints Estándar por Recurso

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/v1/{recurso}/` | Listar recursos (con paginación) |
| POST | `/api/v1/{recurso}/` | Crear nuevo recurso |
| GET | `/api/v1/{recurso}/{id}/` | Obtener recurso específico |
| PUT | `/api/v1/{recurso}/{id}/` | Actualizar recurso completo |
| PATCH | `/api/v1/{recurso}/{id}/` | Actualizar recurso parcial |
| DELETE | `/api/v1/{recurso}/{id}/` | Eliminar recurso |

### 4.3 Autenticación

```http
Authorization: Token {token}
```

O mediante sesión de Django (cookies).

### 4.4 Formato de Respuestas

#### Respuesta Exitosa (200, 201)

```json
{
  "data": {
    "id": 123,
    "nombre": "Juan",
    "apellido": "García"
  }
}
```

#### Respuesta Lista (200)

```json
{
  "count": 100,
  "next": "http://api.example.com/api/v1/pacientes/?page=2",
  "previous": null,
  "results": [
    {"id": 1, "nombre": "Juan"},
    {"id": 2, "nombre": "María"}
  ]
}
```

#### Respuesta Error (400, 404, 500)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "DNI ya existe en el sistema",
    "details": {
      "dni": ["Este campo debe ser único"]
    }
  }
}
```

### 4.5 Códigos de Error Estándar

| Código | Significado |
|--------|-------------|
| `VALIDATION_ERROR` | Error de validación de datos |
| `NOT_FOUND` | Recurso no encontrado |
| `UNAUTHORIZED` | No autenticado |
| `FORBIDDEN` | Sin permisos suficientes |
| `CONFLICT` | Conflicto (ej: DNI duplicado) |
| `INTERNAL_ERROR` | Error interno del servidor |

### 4.6 Paginación

Query params:
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (default: 20, max: 100)

```
GET /api/v1/pacientes/?page=2&page_size=50
```

### 4.7 Filtros y Búsqueda

Query params:
- `search`: Búsqueda en campos relevantes
- Campos específicos como filtros

```
GET /api/v1/pacientes/?search=garcía
GET /api/v1/visitas/?estado=esperando_atencion&nivel_esi=2
```

---

## 5. Validaciones Comunes

### 5.1 Validación de DNI Argentino

```python
import re

def validar_dni_argentino(dni):
    """
    Valida formato de DNI argentino.
    Acepta: 12345678 o 12.345.678 (se normalizará sin puntos)
    """
    # Remover puntos y espacios
    dni_limpio = re.sub(r'[.\s]', '', dni)
    
    # Verificar que sean solo dígitos
    if not dni_limpio.isdigit():
        raise ValidationError("El DNI debe contener solo números")
    
    # Verificar longitud (7-8 dígitos)
    if len(dni_limpio) < 7 or len(dni_limpio) > 8:
        raise ValidationError("El DNI debe tener entre 7 y 8 dígitos")
    
    return dni_limpio
```

### 5.2 Rangos de Signos Vitales

| Signo Vital | Mínimo | Máximo | Unidad |
|-------------|--------|--------|--------|
| Presión Sistólica | 40 | 300 | mmHg |
| Presión Diastólica | 20 | 200 | mmHg |
| Frecuencia Cardíaca | 30 | 300 | lpm |
| Temperatura | 30.0 | 45.0 | °C |
| Saturación O2 | 50 | 100 | % |
| Frecuencia Respiratoria | 5 | 60 | rpm |
| Dolor EVA | 0 | 10 | - |
| Glasgow | 3 | 15 | - |

### 5.3 Validación de Email (opcional)

```python
from django.core.validators import EmailValidator

email_validator = EmailValidator(message="Email inválido")
```

### 5.4 Formatos de Fecha/Hora

- **Almacenamiento**: UTC en PostgreSQL
- **API**: ISO 8601 (`2026-04-28T14:30:00Z`)
- **Display**: Formato local argentino (`28/04/2026 11:30` - UTC-3)

```python
from django.utils import timezone

# Obtener timestamp actual
ahora = timezone.now()

# Para API
fecha_iso = ahora.isoformat()  # "2026-04-28T14:30:00Z"

# Para display
fecha_display = ahora.strftime("%d/%m/%Y %H:%M")  # "28/04/2026 11:30"
```

---

## 6. Auditoría

### 6.1 Eventos Auditados

| Evento | Descripción |
|--------|-------------|
| `login` | Inicio de sesión exitoso |
| `login_failed` | Intento fallido de login |
| `logout` | Cierre de sesión |
| `view` | Visualización de registro sensible |
| `create` | Creación de registro |
| `update` | Modificación de registro |
| `delete` | Eliminación de registro |
| `export` | Exportación de datos |

### 6.2 Datos de Auditoría

Cada evento de auditoría registra:

```python
{
    "timestamp": "2026-04-28T14:30:00Z",
    "usuario": "juan.garcia@hospital.com",
    "usuario_id": 42,
    "accion": "update",
    "modelo": "Paciente",
    "objeto_id": 123,
    "ip": "192.168.1.100",
    "cambios": {
        "telefono": {
            "anterior": "1122334455",
            "nuevo": "1155667788"
        }
    }
}
```

### 6.3 Retención de Logs

| Tipo de Log | Retención Mínima |
|-------------|------------------|
| Accesos al sistema | 2 años |
| Modificación de datos clínicos | 10 años |
| Logs de sistema | 1 año |
| Exportaciones | 5 años |

### 6.4 Implementación con django-auditlog

```python
from auditlog.registry import auditlog

# Registrar modelos para auditoría
auditlog.register(Paciente)
auditlog.register(VisitaEmergencia)
auditlog.register(Triage)
auditlog.register(Atencion)
auditlog.register(Diagnostico)
auditlog.register(Prescripcion)
```

---

## 7. Naming Conventions

### 7.1 Modelos

- **PascalCase**: `Paciente`, `VisitaEmergencia`, `ContactoEmergencia`
- Nombres en **singular**
- Español para entidades de dominio

### 7.2 Campos de Modelos

- **snake_case**: `fecha_nacimiento`, `numero_afiliado`, `motivo_consulta`
- Español para campos de dominio
- Timestamps: `created_at`, `updated_at`
- Foreign Keys: nombre del modelo en singular + `_id` (automático en Django)

### 7.3 Apps de Django

- **minúsculas sin guiones**: `pacientes`, `triage`, `atencion`, `dashboard`, `reportes`
- Plural cuando representan múltiples entidades

### 7.4 URLs

- **kebab-case**: `/pacientes/`, `/visitas-emergencia/`, `/contacto-emergencia/`
- Plural para recursos

### 7.5 Variables Python

- **snake_case**: `paciente_actual`, `tiempo_espera`, `nivel_esi`
- Descriptivas y en español para lógica de dominio

### 7.6 Constantes

- **UPPER_SNAKE_CASE**: `TIEMPOS_OBJETIVO_ESI`, `COLORES_ESI`, `MAX_NIVEL_ESI`

---

## 8. Referencias

Este documento es referenciado por:

- [`project.md`](./project.md) - Visión general del proyecto
- [`specs/core.md`](./specs/core.md) - Especificación del módulo core
- [`specs/pacientes.md`](./specs/pacientes.md) - Especificación del módulo pacientes
- [`specs/triage.md`](./specs/triage.md) - Especificación del módulo triage
- [`specs/atencion.md`](./specs/atencion.md) - Especificación del módulo atención
- [`specs/dashboard.md`](./specs/dashboard.md) - Especificación del módulo dashboard
- [`specs/reportes.md`](./specs/reportes.md) - Especificación del módulo reportes

---

## 9. Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-28 | Versión inicial |

---

*Este documento define los contratos compartidos entre todos los módulos del Sistema de Recepción de Pacientes en Emergencias.*
