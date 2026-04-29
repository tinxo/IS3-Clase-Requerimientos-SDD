# Sistema de Recepción de Pacientes en Emergencias

## Especificaciones Técnicas y Funcionales

**Versión:** 1.0  
**Fecha:** 15 de Abril de 2026  
**Estado:** Aprobado para desarrollo MVP

---

## 1. Resumen Ejecutivo

Sistema web para la gestión integral de pacientes en un servicio de emergencias, incluyendo registro de pacientes, clasificación de triage mediante el sistema ESI (Emergency Severity Index), y documentación de la atención médica.

### 1.1 Objetivos

- Digitalizar el proceso de admisión de pacientes en emergencias
- Implementar triage ESI de 5 niveles para priorización
- Registrar la atención médica completa
- Proveer visibilidad en tiempo real del estado de la sala de espera
- Cumplir con regulaciones de protección de datos de salud (Ley 25.326)

### 1.2 Alcance del MVP

| Incluido en MVP | Fase 2 (Post-MVP) |
|-----------------|-------------------|
| Registro de pacientes | App móvil React Native |
| Triage ESI | Integración HL7 FHIR |
| Atención médica | Reportes avanzados personalizables |
| Dashboard de espera | WebSockets tiempo real |
| Reportes básicos y KPIs | Notificaciones push |
| Auditoría completa | |

---

## 2. Contexto y Restricciones

### 2.1 Contexto Operativo

| Parámetro | Valor |
|-----------|-------|
| Volumen de pacientes | < 50 pacientes/día |
| Usuarios concurrentes | 5-15 usuarios |
| Horario de operación | 24/7 |
| Idioma | Español (Argentina) |

### 2.2 Restricciones Técnicas

| Restricción | Detalle |
|-------------|---------|
| Despliegue | On-premise (servidores propios) |
| RPO (pérdida de datos aceptable) | 24 horas |
| Regulación | Ley 25.326 de Protección de Datos Personales (Argentina) |
| Timeline | MVP en 6-8 semanas |

---

## 3. Stack Tecnológico

### 3.1 Backend

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | Django | 5.x |
| Lenguaje | Python | 3.12+ |
| Base de datos | PostgreSQL | 16 |
| API REST | Django REST Framework | 3.15+ |
| Auditoría | django-auditlog | latest |
| Permisos | django-guardian | latest |

### 3.2 Frontend Web

| Componente | Tecnología |
|------------|------------|
| Templates | Django Templates |
| Interactividad | HTMX |
| Componentes reactivos | Alpine.js |
| CSS Framework | Bootstrap 5 |
| Formularios | django-crispy-forms |

### 3.3 App Móvil (Fase 2)

| Componente | Tecnología |
|------------|------------|
| Framework | React Native |
| Plataformas | iOS, Android |

### 3.4 Integraciones (Fase 2)

| Sistema | Protocolo |
|---------|-----------|
| Historia Clínica Electrónica | HL7 FHIR |
| Sistema de Facturación | HL7 FHIR |

### 3.5 Librerías Auxiliares

| Necesidad | Librería |
|-----------|----------|
| Reportes PDF | weasyprint o reportlab |
| Reportes Excel | openpyxl |
| Validación DNI | Algoritmo custom argentino |
| CIE-10 | Dataset público + autocompletado |

---

## 4. Arquitectura del Sistema

### 4.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTES                                │
├──────────────┬──────────────┬──────────────────────────────┤
│  Navegador   │  React Native│      Sistemas Externos       │
│  (HTMX)      │  (iOS/Android)│   (HCE, Facturación)        │
└──────┬───────┴──────┬───────┴──────────────┬───────────────┘
       │              │                       │
       └──────────────┼───────────────────────┘
                      │ HTTPS / REST / FHIR
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Registro │ │ Triage  │ │Atención │ │Reportes │           │
│  │Pacientes│ │  ESI    │ │ Médica  │ │  & KPIs │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────────────────────────────────────────┐           │
│  │           API REST (DRF) + FHIR             │           │
│  └─────────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────────┐           │
│  │    Auditoría │ Autenticación │ Permisos     │           │
│  └─────────────────────────────────────────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Pacientes │ │ Visitas  │ │Atenciones│ │ Audit    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Estructura del Proyecto Django

```
emergencias/
├── manage.py
├── config/                    # Configuración del proyecto
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                  # Usuarios, autenticación, auditoría
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   └── audit.py
│   ├── pacientes/             # Registro y gestión de pacientes
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── serializers.py
│   ├── triage/                # Clasificación ESI
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── esi_logic.py       # Lógica de sugerencia ESI
│   │   └── serializers.py
│   ├── atencion/              # Atención médica
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── serializers.py
│   ├── dashboard/             # Panel de monitoreo
│   │   ├── views.py
│   │   └── utils.py
│   └── reportes/              # Estadísticas y reportes
│       ├── views.py
│       ├── generators.py
│       └── exports.py
├── templates/
├── static/
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## 5. Modelo de Datos

### 5.1 Diagrama Entidad-Relación

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
│ - contacto_emergencia → ContactoEmergencia  │
│ - created_at, updated_at                    │
└────────────────────┬────────────────────────┘
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
└──────────┬─────────────────┬────────────────┘
           │                 │
           │ tiene uno       │ tiene una
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

### 5.2 Definición de Modelos

#### 5.2.1 Paciente

```python
class Paciente(models.Model):
    # Datos demográficos
    dni = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'Otro')
    ])
    
    # Contacto
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Cobertura médica
    cobertura = models.ForeignKey('Cobertura', null=True, blank=True, on_delete=models.SET_NULL)
    numero_afiliado = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 5.2.2 Contacto de Emergencia

```python
class ContactoEmergencia(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    relacion = models.CharField(max_length=50)  # Padre, Madre, Cónyuge, etc.
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True)
```

#### 5.2.3 Antecedentes Médicos

```python
class AntecedentesMedicos(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    alergias = models.TextField(blank=True, help_text="Alergias conocidas")
    medicacion_cronica = models.TextField(blank=True, help_text="Medicación habitual")
    enfermedades_cronicas = models.TextField(blank=True, help_text="Condiciones crónicas")
    cirugias_previas = models.TextField(blank=True)
    antecedentes_familiares = models.TextField(blank=True)
    grupo_sanguineo = models.CharField(max_length=5, blank=True)
    observaciones = models.TextField(blank=True)
```

#### 5.2.4 Visita de Emergencia

```python
class VisitaEmergencia(models.Model):
    class Estado(models.TextChoices):
        ESPERANDO_TRIAGE = 'esperando_triage', 'Esperando Triage'
        ESPERANDO_ATENCION = 'esperando_atencion', 'Esperando Atención'
        EN_ATENCION = 'en_atencion', 'En Atención'
        FINALIZADO = 'finalizado', 'Finalizado'
        ABANDONO = 'abandono', 'Abandono'
    
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
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
    motivo_ingreso_breve = models.CharField(max_length=200)
```

#### 5.2.5 Triage

```python
class Triage(models.Model):
    class NivelESI(models.IntegerChoices):
        RESUCITACION = 1, 'ESI 1 - Resucitación'
        EMERGENCIA = 2, 'ESI 2 - Emergencia'
        URGENCIA = 3, 'ESI 3 - Urgencia'
        MENOS_URGENTE = 4, 'ESI 4 - Menos Urgente'
        NO_URGENTE = 5, 'ESI 5 - No Urgente'
    
    visita = models.OneToOneField(VisitaEmergencia, on_delete=models.CASCADE)
    nivel_esi = models.IntegerField(choices=NivelESI.choices)
    motivo_consulta = models.TextField()
    
    # Signos vitales
    presion_sistolica = models.IntegerField(null=True, blank=True)
    presion_diastolica = models.IntegerField(null=True, blank=True)
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    saturacion_o2 = models.IntegerField(null=True, blank=True)
    frecuencia_respiratoria = models.IntegerField(null=True, blank=True)
    
    # Evaluaciones
    dolor_eva = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    glasgow = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(3), MaxValueValidator(15)]
    )
    via_aerea = models.CharField(
        max_length=20,
        choices=[
            ('permeable', 'Permeable'),
            ('comprometida', 'Comprometida'),
            ('obstruida', 'Obstruida')
        ],
        default='permeable'
    )
    
    # Metadata
    enfermero = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='triages_realizados'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
```

#### 5.2.6 Atención Médica

```python
class Atencion(models.Model):
    class Destino(models.TextChoices):
        ALTA_MEDICA = 'alta_medica', 'Alta Médica'
        INTERNACION = 'internacion', 'Internación'
        DERIVACION = 'derivacion', 'Derivación'
        CIRUGIA = 'cirugia', 'Cirugía'
        OBSERVACION = 'observacion', 'Observación'
        OBITO = 'obito', 'Óbito'
        FUGA = 'fuga', 'Fuga / Abandono'
    
    visita = models.OneToOneField(VisitaEmergencia, on_delete=models.CASCADE)
    medico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='atenciones_realizadas'
    )
    
    # Evolución
    nota_evolucion = models.TextField()
    
    # Destino
    destino = models.CharField(max_length=20, choices=Destino.choices)
    destino_detalle = models.TextField(blank=True)  # Para derivación: a dónde
    
    # Timestamps
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)


class Diagnostico(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, related_name='diagnosticos')
    codigo_cie10 = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=500)
    es_principal = models.BooleanField(default=False)


class SolicitudEstudio(models.Model):
    class TipoEstudio(models.TextChoices):
        LABORATORIO = 'laboratorio', 'Laboratorio'
        RADIOGRAFIA = 'radiografia', 'Radiografía'
        ECOGRAFIA = 'ecografia', 'Ecografía'
        TOMOGRAFIA = 'tomografia', 'Tomografía'
        RESONANCIA = 'resonancia', 'Resonancia'
        ECG = 'ecg', 'Electrocardiograma'
        OTRO = 'otro', 'Otro'
    
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, related_name='estudios')
    tipo = models.CharField(max_length=20, choices=TipoEstudio.choices)
    descripcion = models.TextField()
    urgente = models.BooleanField(default=False)
    solicitado_at = models.DateTimeField(auto_now_add=True)


class Prescripcion(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, related_name='prescripciones')
    medicamento = models.CharField(max_length=200)
    dosis = models.CharField(max_length=100)
    via = models.CharField(max_length=50)  # Oral, IV, IM, etc.
    frecuencia = models.CharField(max_length=100)
    duracion = models.CharField(max_length=100, blank=True)
    indicaciones = models.TextField(blank=True)
```

---

## 6. Sistema de Triage ESI

### 6.1 Niveles ESI (Emergency Severity Index)

| Nivel | Nombre | Color | Descripción | Tiempo Objetivo |
|-------|--------|-------|-------------|-----------------|
| ESI 1 | Resucitación | Rojo | Requiere intervención inmediata para salvar la vida | Inmediato |
| ESI 2 | Emergencia | Naranja | Situación de alto riesgo, no puede esperar | < 10 minutos |
| ESI 3 | Urgencia | Amarillo | Requiere múltiples recursos, condición estable | < 60 minutos |
| ESI 4 | Menos Urgente | Verde | Requiere un recurso | < 120 minutos |
| ESI 5 | No Urgente | Azul | No requiere recursos | < 240 minutos |

### 6.2 Criterios de Clasificación

#### ESI 1 - Resucitación
- Paro cardiorrespiratorio
- Intubación inminente
- Apnea
- Sin pulso
- No responde

#### ESI 2 - Emergencia
- Confusión/letargia/desorientación
- Dolor severo (EVA 8-10)
- Saturación O2 < 90%
- Glasgow < 14
- Signos de shock

#### ESI 3 - Urgencia
- Requiere 2+ recursos (labs, imágenes, IV, etc.)
- Signos vitales en zona de peligro
- Dolor moderado (EVA 4-7)

#### ESI 4 - Menos Urgente
- Requiere 1 recurso
- Signos vitales normales
- Dolor leve (EVA 1-3)

#### ESI 5 - No Urgente
- No requiere recursos
- Examen y/o receta únicamente

---

## 7. Roles y Permisos

### 7.1 Definición de Roles

| Rol | Descripción |
|-----|-------------|
| Recepcionista | Registra pacientes, gestiona datos demográficos |
| Enfermero/a de Triage | Realiza clasificación ESI, registra signos vitales |
| Médico | Atiende pacientes, documenta evolución, prescribe |
| Administrador | Gestiona usuarios, configuración del sistema |

### 7.2 Matriz de Permisos

| Funcionalidad | Recepcionista | Enfermero | Médico | Admin |
|---------------|:-------------:|:---------:|:------:|:-----:|
| **Pacientes** |
| Registrar nuevo paciente | ✓ | ✓ | ✓ | ✓ |
| Editar datos paciente | ✓ | ✓ | ✓ | ✓ |
| Ver historial de visitas | ✓ | ✓ | ✓ | ✓ |
| Eliminar paciente | ✗ | ✗ | ✗ | ✓ |
| **Triage** |
| Realizar triage | ✗ | ✓ | ✓ | ✓ |
| Modificar triage existente | ✗ | ✓ | ✓ | ✓ |
| **Atención Médica** |
| Iniciar atención | ✗ | ✗ | ✓ | ✓ |
| Registrar evolución | ✗ | ✗ | ✓ | ✓ |
| Solicitar estudios | ✗ | ✗ | ✓ | ✓ |
| Prescribir medicamentos | ✗ | ✗ | ✓ | ✓ |
| Dar destino | ✗ | ✗ | ✓ | ✓ |
| **Dashboard** |
| Ver pacientes en espera | ✓ | ✓ | ✓ | ✓ |
| Ver tiempos de espera | ✓ | ✓ | ✓ | ✓ |
| **Reportes** |
| Ver estadísticas diarias | ✗ | ✓ | ✓ | ✓ |
| Exportar reportes | ✗ | ✗ | ✓ | ✓ |
| Acceder a todos los reportes | ✗ | ✗ | ✗ | ✓ |
| **Administración** |
| Gestionar usuarios | ✗ | ✗ | ✗ | ✓ |
| Ver logs de auditoría | ✗ | ✗ | ✗ | ✓ |
| Configurar sistema | ✗ | ✗ | ✗ | ✓ |

---

## 8. Auditoría y Cumplimiento

### 8.1 Requisitos de Auditoría (Ley 25.326)

La Ley 25.326 de Protección de Datos Personales de Argentina establece requisitos específicos para el tratamiento de datos sensibles (como los datos de salud).

#### Datos a Auditar

| Evento | Datos Registrados |
|--------|-------------------|
| Acceso al sistema | Usuario, IP, timestamp, éxito/fallo |
| Visualización de registro | Usuario, registro accedido, timestamp |
| Creación de registro | Usuario, datos creados, timestamp |
| Modificación de registro | Usuario, valores anteriores, valores nuevos, timestamp |
| Eliminación de registro | Usuario, datos eliminados, timestamp |
| Exportación de datos | Usuario, tipo de exportación, filtros aplicados, timestamp |

#### Retención de Logs

- **Logs de acceso**: Mínimo 2 años
- **Logs de modificación de datos clínicos**: Mínimo 10 años
- **Logs de sistema**: Mínimo 1 año

### 8.2 Implementación con django-auditlog

```python
# Configuración en settings.py
AUDITLOG_INCLUDE_ALL_MODELS = True

# En cada modelo sensible
from auditlog.registry import auditlog

auditlog.register(Paciente)
auditlog.register(Triage)
auditlog.register(Atencion)
auditlog.register(Diagnostico)
auditlog.register(Prescripcion)
```

### 8.3 Seguridad de Datos

| Medida | Implementación |
|--------|----------------|
| Encriptación en tránsito | HTTPS obligatorio (TLS 1.3) |
| Encriptación en reposo | PostgreSQL con pgcrypto para campos sensibles |
| Autenticación | Contraseñas hasheadas (Argon2) |
| Sesiones | Timeout de 30 minutos de inactividad |
| Backups | Diarios, encriptados, rotación 30 días |

---

## 9. Interfaces de Usuario

### 9.1 Flujo Principal

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  RECEPCIÓN   │────▶│   TRIAGE     │────▶│  ATENCIÓN    │────▶│   DESTINO    │
│              │     │              │     │   MÉDICA     │     │              │
│ - Registro   │     │ - Evaluación │     │ - Evolución  │     │ - Alta       │
│ - Búsqueda   │     │ - Nivel ESI  │     │ - Diagnóstico│     │ - Internación│
│ - Admisión   │     │ - Signos V.  │     │ - Estudios   │     │ - Derivación │
└──────────────┘     └──────────────┘     │ - Recetas    │     └──────────────┘
                                          └──────────────┘
```

### 9.2 Pantallas Principales

#### 9.2.1 Dashboard Principal

```
┌─────────────────────────────────────────────────────────────────────┐
│  EMERGENCIAS - Dashboard                           [Usuario] [Salir]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ ESI 1   │ │ ESI 2   │ │ ESI 3   │ │ ESI 4   │ │ ESI 5   │       │
│  │   0     │ │   2     │ │   5     │ │   3     │ │   1     │       │
│  │ 🔴      │ │ 🟠      │ │ 🟡      │ │ 🟢      │ │ 🔵      │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│                                                                      │
│  PACIENTES EN ESPERA                                    [Actualizar] │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ ESI │ Paciente      │ Motivo           │ Espera  │ Estado     │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ 🟠2 │ García, Juan  │ Dolor torácico   │ 5 min   │ En triage  │  │
│  │ 🟠2 │ López, María  │ Disnea aguda     │ 12 min  │ Esperando  │  │
│  │ 🟡3 │ Pérez, Carlos │ Fractura brazo   │ 25 min  │ Esperando  │  │
│  │ 🟡3 │ Ruiz, Ana     │ Dolor abdominal  │ 35 min  │ En atención│  │
│  │ ...                                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 9.2.2 Registro de Paciente

```
┌─────────────────────────────────────────────────────────────────────┐
│  REGISTRO DE PACIENTE                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Buscar paciente existente: [________________] [Buscar por DNI]     │
│                                                                      │
│  ─── Datos Personales ───────────────────────────────────────────   │
│  DNI: [________]  Nombre: [______________]  Apellido: [__________]  │
│  Fecha Nac: [__/__/____]  Sexo: [▼ Masculino]                       │
│                                                                      │
│  ─── Contacto ───────────────────────────────────────────────────   │
│  Teléfono: [__________]  Email: [____________________]              │
│  Dirección: [_________________________________________________]     │
│  Localidad: [______________]  Provincia: [______________]           │
│                                                                      │
│  ─── Cobertura Médica ───────────────────────────────────────────   │
│  Obra Social: [▼ Seleccionar]  Nro Afiliado: [______________]       │
│                                                                      │
│  ─── Contacto de Emergencia ─────────────────────────────────────   │
│  Nombre: [____________________]  Relación: [__________]             │
│  Teléfono: [______________]                                          │
│                                                                      │
│  ─── Motivo de Ingreso ──────────────────────────────────────────   │
│  [_______________________________________________________________]  │
│                                                                      │
│                                    [Cancelar]  [Guardar e Ir a Triage]│
└─────────────────────────────────────────────────────────────────────┘
```

#### 9.2.3 Triage ESI

```
┌─────────────────────────────────────────────────────────────────────┐
│  TRIAGE - García, Juan (DNI: 30.555.444)              Ingreso: 10:35│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ─── Motivo de Consulta ─────────────────────────────────────────   │
│  [                                                                ]  │
│  [                                                                ]  │
│                                                                      │
│  ─── Signos Vitales ─────────────────────────────────────────────   │
│  PA: [___]/[___] mmHg    FC: [___] lpm    T°: [____] °C            │
│  SatO2: [___] %          FR: [___] rpm                              │
│                                                                      │
│  ─── Evaluación ─────────────────────────────────────────────────   │
│  Dolor (EVA 0-10): [▼ 0]                                            │
│  Glasgow: [▼ 15]                                                     │
│  Vía Aérea: (●) Permeable  ( ) Comprometida  ( ) Obstruida         │
│                                                                      │
│  ─── Nivel ESI ──────────────────────────────────────────────────   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                           │
│  │  1  │ │  2  │ │  3  │ │  4  │ │  5  │                           │
│  │ 🔴  │ │ 🟠  │ │ 🟡  │ │ 🟢  │ │ 🔵  │                           │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                           │
│  💡 Sugerencia del sistema: ESI 2 (basado en signos vitales)       │
│                                                                      │
│  Observaciones: [______________________________________________]    │
│                                                                      │
│                                         [Cancelar]  [Guardar Triage] │
└─────────────────────────────────────────────────────────────────────┘
```

#### 9.2.4 Atención Médica

```
┌─────────────────────────────────────────────────────────────────────┐
│  ATENCIÓN MÉDICA - García, Juan                    Triage: ESI 2 🟠 │
│  DNI: 30.555.444 | 45 años | Masculino              Espera: 8 min   │
├─────────────────────────────────────────────────────────────────────┤
│ [Datos Paciente] [Triage] [Antecedentes] [Visitas Anteriores]       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ─── Nota de Evolución ──────────────────────────────────────────   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                                │  │
│  │                                                                │  │
│  │                                                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ─── Diagnósticos (CIE-10) ──────────────────────────────────────   │
│  [Buscar diagnóstico...                          ] [+ Agregar]      │
│  • I20.0 - Angina inestable (Principal)                    [x]      │
│                                                                      │
│  ─── Estudios Solicitados ───────────────────────────────────────   │
│  [▼ Tipo] [Descripción...                        ] [+ Agregar]      │
│  • Laboratorio: Enzimas cardíacas, hemograma     [Urgente ✓]  [x]   │
│  • ECG: Electrocardiograma de 12 derivaciones              [x]      │
│                                                                      │
│  ─── Prescripciones ─────────────────────────────────────────────   │
│  [+ Agregar medicamento]                                             │
│  • AAS 100mg - VO - Stat                                    [x]     │
│                                                                      │
│  ─── Destino ────────────────────────────────────────────────────   │
│  ( ) Alta médica  (●) Internación  ( ) Derivación  ( ) Observación  │
│  Detalle: [Unidad Coronaria - Cama 3                           ]    │
│                                                                      │
│                                     [Guardar Borrador]  [Finalizar] │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Reportes y KPIs

### 10.1 Reportes Incluidos en MVP

| Reporte | Descripción | Formato |
|---------|-------------|---------|
| Resumen Diario | Pacientes atendidos, por nivel ESI, destinos | PDF, Excel |
| Tiempos de Espera | Promedio por nivel ESI, por turno | PDF, Excel |
| Productividad Médica | Atenciones por médico, tiempos promedio | PDF, Excel |
| Diagnósticos Frecuentes | Top diagnósticos CIE-10 del período | PDF, Excel |
| Censo Actual | Pacientes en espera/atención en tiempo real | Pantalla |

### 10.2 KPIs de Emergencias

| KPI | Descripción | Meta |
|-----|-------------|------|
| Door-to-Triage | Tiempo desde ingreso hasta triage | < 10 min |
| Door-to-Doctor | Tiempo desde ingreso hasta atención médica | Según ESI |
| LWBS (Left Without Being Seen) | % pacientes que abandonan sin ser vistos | < 2% |
| Tiempo promedio de estancia | Tiempo total en emergencias | < 4 horas |
| Ocupación | Pacientes actuales vs capacidad | Monitor |

### 10.3 Tiempos Objetivo por Nivel ESI

| Nivel ESI | Door-to-Doctor |
|-----------|----------------|
| ESI 1 | Inmediato |
| ESI 2 | < 10 minutos |
| ESI 3 | < 60 minutos |
| ESI 4 | < 120 minutos |
| ESI 5 | < 240 minutos |

---

## 11. Plan de Implementación

### 11.1 Cronograma MVP (8 Semanas)

```
Semana 1  ████████████████████████████████ Setup y Estructura Base
Semana 2  ████████████████████████████████ Módulo de Pacientes
Semana 3  ████████████████████████████████ Módulo de Triage ESI
Semana 4  ████████████████████████████████ Módulo de Atención Médica
Semana 5  ████████████████████████████████ Dashboard y Lista de Espera
Semana 6  ████████████████████████████████ Reportes Básicos y KPIs
Semana 7  ████████████████████████████████ Testing y Ajustes
Semana 8  ████████████████████████████████ Deploy y Capacitación
```

### 11.2 Detalle por Semana

#### Semana 1: Setup y Estructura Base
- [ ] Configurar proyecto Django con estructura modular
- [ ] Configurar PostgreSQL
- [ ] Setup Docker Compose para desarrollo
- [ ] Configurar django-auditlog
- [ ] Implementar sistema de autenticación con roles
- [ ] Crear templates base (layout, navegación)

#### Semana 2: Módulo de Pacientes
- [ ] Modelo Paciente con todos los campos
- [ ] Modelo Cobertura (obras sociales)
- [ ] Modelo ContactoEmergencia
- [ ] Modelo AntecedentesMedicos
- [ ] CRUD completo de pacientes
- [ ] Búsqueda rápida por DNI/nombre
- [ ] Validación de DNI argentino

#### Semana 3: Módulo de Triage ESI
- [ ] Modelo VisitaEmergencia
- [ ] Modelo Triage con todos los campos
- [ ] Lógica de sugerencia de nivel ESI
- [ ] Interfaz de triage optimizada
- [ ] Validaciones de signos vitales
- [ ] Transiciones de estado de visita

#### Semana 4: Módulo de Atención Médica
- [ ] Modelo Atencion
- [ ] Modelo Diagnostico con CIE-10
- [ ] Modelo SolicitudEstudio
- [ ] Modelo Prescripcion
- [ ] Editor de notas de evolución
- [ ] Autocompletado de diagnósticos CIE-10
- [ ] Flujo completo de atención

#### Semana 5: Dashboard y Lista de Espera
- [ ] Vista de pacientes en espera
- [ ] Ordenamiento por prioridad y tiempo
- [ ] Indicadores visuales de tiempo
- [ ] Filtros por estado
- [ ] Contadores por nivel ESI
- [ ] Actualización con polling (30 seg)

#### Semana 6: Reportes Básicos y KPIs
- [ ] Reporte diario de atenciones
- [ ] Tiempos promedio de espera
- [ ] Distribución de niveles ESI
- [ ] Reporte de destinos
- [ ] Exportación a Excel y PDF
- [ ] Filtros por fecha y turno

#### Semana 7: Testing y Ajustes
- [ ] Tests unitarios de modelos
- [ ] Tests de integración
- [ ] Pruebas con usuarios reales
- [ ] Corrección de bugs
- [ ] Ajustes de UX/UI
- [ ] Optimización de performance

#### Semana 8: Deploy y Capacitación
- [ ] Configuración servidor producción
- [ ] Deploy de aplicación
- [ ] Configuración de backups
- [ ] Documentación de usuario
- [ ] Capacitación al personal
- [ ] Soporte post-implementación

---

## 12. Fase 2 (Post-MVP)

### 12.1 App Móvil React Native (4-6 semanas)

- Autenticación
- Dashboard de espera (lectura)
- Registro rápido de pacientes
- Visualización de datos de paciente
- Notificaciones push para médicos

### 12.2 Integración HL7 FHIR (4 semanas)

- Mapeo de recursos FHIR (Patient, Encounter, Condition)
- API de integración con HCE
- Sincronización de datos de pacientes
- Envío de datos a facturación

### 12.3 Reportes Avanzados (2-3 semanas)

- Generador de reportes personalizable
- Dashboards con gráficos interactivos
- Exportación programada
- Reportes regulatorios automáticos

### 12.4 Tiempo Real (2 semanas)

- WebSockets para dashboard
- Actualizaciones instantáneas
- Notificaciones en navegador

---

## 13. Consideraciones de Infraestructura

### 13.1 Requisitos de Servidor (On-Premise)

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Almacenamiento | 100 GB SSD | 250 GB SSD |
| Sistema Operativo | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |

### 13.2 Stack de Producción

```
┌─────────────────────────────────────────┐
│              Nginx (Reverse Proxy)       │
│              + SSL Termination           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│              Gunicorn                    │
│         (WSGI Application Server)        │
│              4-8 workers                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Django Application             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│             PostgreSQL 16                │
│         (con backups diarios)            │
└─────────────────────────────────────────┘
```

### 13.3 Backup y Recuperación

| Tipo | Frecuencia | Retención | Ubicación |
|------|------------|-----------|-----------|
| Full DB | Diario (02:00) | 30 días | Servidor backup |
| Incremental | Cada 6 horas | 7 días | Local |
| Archivos/Media | Diario | 30 días | Servidor backup |

---

## 14. Glosario

| Término | Definición |
|---------|------------|
| **ESI** | Emergency Severity Index - Sistema de clasificación de triage de 5 niveles |
| **Triage** | Proceso de clasificación de pacientes según gravedad y urgencia |
| **CIE-10** | Clasificación Internacional de Enfermedades, 10ª revisión |
| **EVA** | Escala Visual Analógica - medición del dolor de 0 a 10 |
| **Glasgow** | Escala de Coma de Glasgow - evaluación del nivel de conciencia |
| **LWBS** | Left Without Being Seen - pacientes que abandonan sin ser atendidos |
| **Door-to-Doctor** | Tiempo desde el ingreso hasta ser visto por un médico |
| **HL7 FHIR** | Fast Healthcare Interoperability Resources - estándar de interoperabilidad |
| **RPO** | Recovery Point Objective - pérdida de datos aceptable en caso de falla |

---

## 15. Control de Versiones del Documento

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2026-04-15 | - | Versión inicial |

---

*Documento generado como parte del proceso de definición de requerimientos para el Sistema de Recepción de Pacientes en Emergencias.*
