# Especificación del Módulo Core

**Módulo:** `apps/core/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Infraestructura base del sistema

---

## 1. Objetivos del Módulo

El módulo **Core** proporciona la infraestructura fundamental para todo el sistema:

- **Autenticación**: Login/logout seguro de usuarios
- **Autorización**: Control de permisos basado en roles
- **Auditoría**: Registro completo de acciones para cumplimiento normativo
- **Gestión de Usuarios**: Administración de usuarios del sistema
- **Seguridad**: Implementación de medidas de protección de datos

---

## 2. Responsabilidades

### 2.1 Autenticación

- Verificación de credenciales de usuario
- Gestión de sesiones
- Timeout automático de sesiones inactivas (30 minutos)
- Protección contra fuerza bruta

### 2.2 Autorización

- Definición de 4 roles principales: Recepcionista, Enfermero, Médico, Administrador
- Control de acceso a funcionalidades por rol
- Permisos granulares a nivel de modelo y objeto

### 2.3 Auditoría

- Registro automático de todas las acciones sobre modelos sensibles
- Cumplimiento con Ley 25.326 de Argentina
- Trazabilidad completa (quién, qué, cuándo, desde dónde)
- Retención de logs según normativa

### 2.4 Gestión de Usuarios

- CRUD de usuarios
- Asignación de roles
- Activación/desactivación de cuentas
- Reseteo de contraseñas

---

## 3. Modelos

### 3.1 Usuario

Extiende el modelo `User` de Django:

```python
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """
    Extensión del modelo User de Django para el sistema de emergencias.
    """
    
    class Rol(models.TextChoices):
        RECEPCIONISTA = 'recepcionista', 'Recepcionista'
        ENFERMERO = 'enfermero', 'Enfermero/a'
        MEDICO = 'medico', 'Médico/a'
        ADMINISTRADOR = 'administrador', 'Administrador'
    
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCIONISTA
    )
    matricula = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Matrícula profesional (para médicos y enfermeros)"
    )
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    fecha_ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'usuarios'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    @property
    def es_medico(self):
        return self.rol == self.Rol.MEDICO
    
    @property
    def es_enfermero(self):
        return self.rol == self.Rol.ENFERMERO
    
    @property
    def es_recepcionista(self):
        return self.rol == self.Rol.RECEPCIONISTA
    
    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR
```

**Nota**: Alternativamente, si se prefiere no modificar el modelo User de Django, se puede usar un modelo `Profile` con relación OneToOne.

---

## 4. Roles y Permisos Detallados

### 4.1 Definición de Roles

#### Recepcionista

**Responsabilidades:**
- Registrar pacientes nuevos
- Actualizar datos de contacto
- Iniciar visita de emergencia
- Ver lista de espera

**Permisos:**
```python
RECEPCIONISTA_PERMS = [
    'pacientes.add_paciente',
    'pacientes.change_paciente',
    'pacientes.view_paciente',
    'triage.view_visitaemergencia',
    'dashboard.view_dashboard',
]
```

#### Enfermero/a

**Responsabilidades:**
- Todas las de Recepcionista
- Realizar triage
- Modificar signos vitales
- Ver reportes básicos

**Permisos:**
```python
ENFERMERO_PERMS = RECEPCIONISTA_PERMS + [
    'triage.add_triage',
    'triage.change_triage',
    'triage.view_triage',
    'reportes.view_reportes_basicos',
]
```

#### Médico/a

**Responsabilidades:**
- Todas las de Enfermero
- Documentar atención médica
- Agregar diagnósticos
- Solicitar estudios
- Prescribir medicamentos
- Definir destino del paciente
- Exportar reportes

**Permisos:**
```python
MEDICO_PERMS = ENFERMERO_PERMS + [
    'atencion.add_atencion',
    'atencion.change_atencion',
    'atencion.view_atencion',
    'atencion.add_diagnostico',
    'atencion.add_solicitudestudio',
    'atencion.add_prescripcion',
    'reportes.export_reportes',
]
```

#### Administrador

**Responsabilidades:**
- Todas las anteriores
- Gestionar usuarios
- Ver logs de auditoría
- Configurar sistema
- Eliminar registros

**Permisos:**
```python
ADMIN_PERMS = 'ALL'  # Acceso total
```

### 4.2 Implementación de Permisos

Opción 1: **Permisos nativos de Django**

```python
# En views.py
from django.contrib.auth.decorators import permission_required

@permission_required('triage.add_triage')
def crear_triage(request, visita_id):
    # ...
```

Opción 2: **django-guardian para permisos a nivel de objeto**

```python
from guardian.decorators import permission_required_or_403

@permission_required_or_403('atencion.change_atencion', 
                            (Atencion, 'id', 'atencion_id'))
def editar_atencion(request, atencion_id):
    # ...
```

---

## 5. Auditoría

### 5.1 Requisitos de Auditoría (Ley 25.326)

La Ley 25.326 de Protección de Datos Personales de Argentina establece requisitos específicos para el tratamiento de datos sensibles (como los datos de salud).

#### Eventos a Auditar

| Evento | Descripción | Retención |
|--------|-------------|-----------|
| `login` | Inicio de sesión exitoso | 2 años |
| `login_failed` | Intento fallido de login | 2 años |
| `logout` | Cierre de sesión | 2 años |
| `view` | Visualización de registro sensible | 10 años |
| `create` | Creación de registro | 10 años |
| `update` | Modificación de registro | 10 años |
| `delete` | Eliminación de registro | 10 años |
| `export` | Exportación de datos | 5 años |

### 5.2 Implementación con django-auditlog

**Instalación:**
```bash
pip install django-auditlog
```

**Configuración en `settings.py`:**
```python
INSTALLED_APPS = [
    # ...
    'auditlog',
]

MIDDLEWARE = [
    # ...
    'auditlog.middleware.AuditlogMiddleware',
]
```

**Registro de modelos en `apps/core/audit.py`:**
```python
from auditlog.registry import auditlog
from apps.pacientes.models import Paciente, ContactoEmergencia, AntecedentesMedicos
from apps.triage.models import VisitaEmergencia, Triage
from apps.atencion.models import Atencion, Diagnostico, Prescripcion, SolicitudEstudio

# Registrar modelos para auditoría
auditlog.register(Paciente)
auditlog.register(ContactoEmergencia)
auditlog.register(AntecedentesMedicos)
auditlog.register(VisitaEmergencia)
auditlog.register(Triage)
auditlog.register(Atencion)
auditlog.register(Diagnostico)
auditlog.register(Prescripcion)
auditlog.register(SolicitudEstudio)
```

**Auditoría de accesos (views):**
```python
from auditlog.models import LogEntry

def log_acceso_paciente(request, paciente):
    """
    Registra el acceso a un registro de paciente.
    """
    LogEntry.objects.create(
        content_type=ContentType.objects.get_for_model(paciente),
        object_pk=paciente.pk,
        object_repr=str(paciente),
        action=LogEntry.Action.ACCESS,
        actor=request.user,
        remote_addr=request.META.get('REMOTE_ADDR'),
        additional_data={'view': 'paciente_detail'}
    )
```

### 5.3 Vista de Logs de Auditoría (Solo Admin)

```python
# apps/core/views.py
from django.contrib.auth.decorators import user_passes_test
from auditlog.models import LogEntry

@user_passes_test(lambda u: u.es_administrador)
def logs_auditoria(request):
    """
    Vista para administradores para ver logs de auditoría.
    """
    logs = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
    
    # Filtros
    if request.GET.get('usuario'):
        logs = logs.filter(actor__id=request.GET['usuario'])
    if request.GET.get('modelo'):
        logs = logs.filter(content_type__model=request.GET['modelo'])
    if request.GET.get('desde'):
        logs = logs.filter(timestamp__gte=request.GET['desde'])
    
    return render(request, 'core/logs_auditoria.html', {
        'logs': logs[:100]  # Limitar a 100 registros
    })
```

---

## 6. Seguridad

### 6.1 Medidas de Seguridad Implementadas

| Medida | Implementación |
|--------|----------------|
| **Encriptación en tránsito** | HTTPS obligatorio (TLS 1.3) con Nginx |
| **Encriptación en reposo** | PostgreSQL con pgcrypto para campos sensibles (opcional) |
| **Autenticación** | Contraseñas hasheadas con Argon2 |
| **Sesiones** | Timeout de 30 minutos de inactividad |
| **CSRF Protection** | Token CSRF en todos los formularios |
| **XSS Protection** | Django template escaping automático |
| **SQL Injection** | ORM de Django previene inyecciones |
| **Fuerza Bruta** | django-axes para bloqueo tras intentos fallidos |

### 6.2 Configuración de Seguridad en `settings.py`

```python
# Password hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Session settings
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True  # Solo HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Protección contra fuerza bruta (django-axes)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hora
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
```

### 6.3 Validación de Contraseñas

```python
# En settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

**Requisitos de contraseña:**
- Mínimo 10 caracteres
- No puede ser similar al nombre de usuario o email
- No puede ser una contraseña común
- No puede ser completamente numérica

---

## 7. Interfaz de Usuario

### 7.1 Pantalla de Login

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                 🏥  SISTEMA DE EMERGENCIAS                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  Usuario:  [________________________________]          │ │
│  │                                                         │ │
│  │  Contraseña: [________________________________]        │ │
│  │                                                         │ │
│  │                    [  Iniciar Sesión  ]                │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│                  ¿Olvidaste tu contraseña?                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Gestión de Usuarios (Admin)

```
┌─────────────────────────────────────────────────────────────┐
│  ADMINISTRACIÓN - Usuarios                 [+ Nuevo Usuario] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Buscar: [_______________] [Filtrar por rol: ▼ Todos]       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Usuario         │ Rol           │ Estado │ Acciones  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ García, Juan    │ Médico        │ Activo │ [✏️] [🗑️] │   │
│  │ López, María    │ Enfermero     │ Activo │ [✏️] [🗑️] │   │
│  │ Pérez, Carlos   │ Recepcionista │ Activo │ [✏️] [🗑️] │   │
│  │ Ruiz, Ana       │ Administrador │ Activo │ [✏️] [🗑️] │   │
│  │ Gómez, Luis     │ Médico        │ Inactivo│ [✏️] [🗑️]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. API Endpoints

### 8.1 Autenticación

#### Login
```
POST /api/v1/auth/login/

Body:
{
  "username": "juan.garcia",
  "password": "password123"
}

Response (200):
{
  "token": "a1b2c3d4e5f6...",
  "user": {
    "id": 1,
    "username": "juan.garcia",
    "nombre_completo": "Juan García",
    "rol": "medico",
    "email": "juan.garcia@hospital.com"
  }
}
```

#### Logout
```
POST /api/v1/auth/logout/

Response (200):
{
  "message": "Sesión cerrada exitosamente"
}
```

#### Usuario Actual
```
GET /api/v1/auth/me/

Response (200):
{
  "id": 1,
  "username": "juan.garcia",
  "nombre_completo": "Juan García",
  "rol": "medico",
  "email": "juan.garcia@hospital.com",
  "matricula": "MN 123456",
  "permisos": ["atencion.add_atencion", "atencion.change_atencion", ...]
}
```

### 8.2 Usuarios (Solo Admin)

#### Listar Usuarios
```
GET /api/v1/usuarios/

Response (200):
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "username": "juan.garcia",
      "nombre_completo": "Juan García",
      "rol": "medico",
      "activo": true,
      "fecha_ultimo_acceso": "2026-04-28T14:30:00Z"
    },
    ...
  ]
}
```

#### Crear Usuario
```
POST /api/v1/usuarios/

Body:
{
  "username": "nuevo.usuario",
  "email": "nuevo@hospital.com",
  "first_name": "Nuevo",
  "last_name": "Usuario",
  "rol": "enfermero",
  "matricula": "ME 98765",
  "password": "password_seguro_123"
}

Response (201):
{
  "id": 11,
  "username": "nuevo.usuario",
  "nombre_completo": "Nuevo Usuario",
  "rol": "enfermero"
}
```

### 8.3 Logs de Auditoría (Solo Admin)

```
GET /api/v1/auditoria/logs/?usuario=1&modelo=paciente&desde=2026-04-01

Response (200):
{
  "count": 50,
  "results": [
    {
      "id": 1234,
      "timestamp": "2026-04-28T14:30:00Z",
      "usuario": "Juan García",
      "accion": "update",
      "modelo": "Paciente",
      "objeto_id": 123,
      "cambios": {
        "telefono": {
          "anterior": "1122334455",
          "nuevo": "1155667788"
        }
      },
      "ip": "192.168.1.100"
    },
    ...
  ]
}
```

---

## 9. Configuración del Proyecto

### 9.1 Settings por Ambiente

**`config/settings/base.py`** - Configuración compartida
**`config/settings/development.py`** - Desarrollo local
**`config/settings/production.py`** - Producción

```python
# config/settings/base.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'auditlog',
    'guardian',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Apps locales
    'apps.core',
    'apps.pacientes',
    'apps.triage',
    'apps.atencion',
    'apps.dashboard',
    'apps.reportes',
]

AUTH_USER_MODEL = 'core.Usuario'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ... resto de configuración
```

### 9.2 Variables de Entorno (`.env`)

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=emergencias.hospital.com

# Database
DB_NAME=emergencias_db
DB_USER=emergencias_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Email (para reseteo de contraseñas)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sistema@hospital.com
EMAIL_HOST_PASSWORD=email_password_here
```

---

## 10. Dependencias del Módulo

Este módulo no depende de otros módulos del sistema (es la base).

Otros módulos dependen de Core para:
- Autenticación (decoradores de login)
- Autorización (permisos)
- Auditoría (logs automáticos)

---

## 11. Tests Requeridos

### 11.1 Tests de Autenticación

```python
# apps/core/tests/test_auth.py
from django.test import TestCase, Client
from apps.core.models import Usuario

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='test_medico',
            password='password123',
            rol=Usuario.Rol.MEDICO
        )
    
    def test_login_exitoso(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_medico',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())
    
    def test_login_fallido(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_medico',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_logout(self):
        self.client.login(username='test_medico', password='password123')
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)
```

### 11.2 Tests de Permisos

```python
# apps/core/tests/test_permisos.py
from django.test import TestCase
from apps.core.models import Usuario

class PermisosTestCase(TestCase):
    def test_medico_puede_crear_atencion(self):
        medico = Usuario.objects.create_user(
            username='medico',
            password='pass',
            rol=Usuario.Rol.MEDICO
        )
        self.assertTrue(medico.has_perm('atencion.add_atencion'))
    
    def test_recepcionista_no_puede_crear_atencion(self):
        recepcionista = Usuario.objects.create_user(
            username='recepcionista',
            password='pass',
            rol=Usuario.Rol.RECEPCIONISTA
        )
        self.assertFalse(recepcionista.has_perm('atencion.add_atencion'))
```

### 11.3 Tests de Auditoría

```python
# apps/core/tests/test_auditoria.py
from django.test import TestCase
from auditlog.models import LogEntry
from apps.pacientes.models import Paciente
from apps.core.models import Usuario

class AuditoriaTestCase(TestCase):
    def test_creacion_paciente_se_audita(self):
        admin = Usuario.objects.create_user(
            username='admin',
            password='pass',
            rol=Usuario.Rol.ADMINISTRADOR
        )
        
        paciente = Paciente.objects.create(
            dni='12345678',
            nombre='Juan',
            apellido='Pérez',
            fecha_nacimiento='1980-01-01',
            sexo='M',
            telefono='1122334455'
        )
        
        logs = LogEntry.objects.filter(
            content_type__model='paciente',
            object_pk=paciente.pk,
            action=LogEntry.Action.CREATE
        )
        self.assertTrue(logs.exists())
```

---

## 12. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md) - Modelos y convenciones compartidas
- **Módulos relacionados**: Todos los demás módulos dependen de Core

---

*Especificación del módulo Core - Sistema de Recepción de Pacientes en Emergencias*
