# Especificación del Módulo Pacientes

**Módulo:** `apps/pacientes/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Registro maestro de pacientes

---

## 1. Objetivos del Módulo

Gestionar el **registro maestro de pacientes** del servicio de emergencias:

- Registrar nuevos pacientes con todos sus datos demográficos
- Buscar pacientes existentes por DNI o nombre
- Actualizar información de contacto y cobertura médica
- Gestionar contactos de emergencia
- Registrar antecedentes médicos relevantes
- Visualizar historial de visitas previas

---

## 2. Casos de Uso

### 2.1 Registrar Nuevo Paciente

**Actor:** Recepcionista, Enfermero, Médico  
**Flujo:**
1. Usuario accede al formulario de nuevo paciente
2. Ingresa DNI y busca si ya existe
3. Si no existe, completa datos demográficos (nombre, apellido, fecha nacimiento, sexo)
4. Completa datos de contacto (teléfono, email, dirección)
5. Completa cobertura médica (obra social, número de afiliado)
6. Completa contacto de emergencia (nombre, relación, teléfono)
7. Opcionalmente registra antecedentes médicos
8. Guarda el paciente y opcionalmente inicia visita de emergencia

**Validaciones:**
- DNI único en el sistema
- DNI con formato válido (7-8 dígitos)
- Fecha de nacimiento en rango válido (no futuro, no > 150 años)
- Teléfono con formato válido
- Email válido (si se proporciona)

### 2.2 Buscar Paciente Existente

**Actor:** Recepcionista, Enfermero, Médico  
**Flujo:**
1. Usuario ingresa término de búsqueda (DNI o nombre/apellido)
2. Sistema busca en base de datos
3. Muestra resultados ordenados por relevancia
4. Usuario selecciona paciente para ver detalle o iniciar visita

**Tipos de búsqueda:**
- Por DNI: búsqueda exacta
- Por nombre/apellido: búsqueda parcial, case-insensitive
- Resultados paginados (20 por página)

### 2.3 Editar Datos de Paciente

**Actor:** Recepcionista, Enfermero, Médico  
**Flujo:**
1. Usuario busca y selecciona paciente
2. Accede al formulario de edición
3. Modifica datos necesarios
4. Guarda cambios
5. Sistema registra auditoría de cambios

**Campos editables:**
- Todos los datos de contacto
- Cobertura médica y número de afiliado
- Contacto de emergencia
- Antecedentes médicos

**Campos no editables:**
- DNI (único e inmutable)
- Fecha de nacimiento (solo admin puede cambiar si error)

### 2.4 Ver Historial de Visitas

**Actor:** Recepcionista, Enfermero, Médico  
**Flujo:**
1. Usuario accede al detalle del paciente
2. Ve lista de visitas previas ordenadas por fecha (más reciente primero)
3. Puede expandir cada visita para ver:
   - Fecha y hora de ingreso/egreso
   - Nivel de triage ESI
   - Diagnósticos
   - Destino (alta, internación, etc.)

---

## 3. Modelos

### 3.1 Referencia a Contratos

Ver [`contracts.md`](../contracts.md) para la definición completa de:
- `Paciente`
- `Cobertura`
- `ContactoEmergencia`
- `AntecedentesMedicos`

### 3.2 Diagrama de Relaciones

```
┌─────────────┐
│  Cobertura  │
└──────┬──────┘
       │
       │ tiene
       ▼
┌─────────────┐         ┌─────────────────────┐
│  Paciente   │────────▶│ ContactoEmergencia  │
└──────┬──────┘   1:1   └─────────────────────┘
       │
       │ 1:1
       ▼
┌─────────────────────┐
│ AntecedentesMedicos │
└─────────────────────┘
       │
       │ 1:N
       ▼
┌─────────────────────┐
│  VisitaEmergencia   │
└─────────────────────┘
```

---

## 4. Validaciones Específicas

### 4.1 Validación de DNI Argentino

Ver [`contracts.md`](../contracts.md) sección 5.1 para implementación completa.

```python
# Resumen
- Formato: 7-8 dígitos sin puntos
- Único en el sistema
- Validación en modelo y formulario
```

### 4.2 Validación de Edad

```python
def validar_fecha_nacimiento(fecha):
    from datetime import date
    hoy = date.today()
    
    if fecha > hoy:
        raise ValidationError("La fecha de nacimiento no puede ser futura")
    
    edad = hoy.year - fecha.year
    if edad > 150:
        raise ValidationError("La fecha de nacimiento no es válida")
    
    return fecha
```

### 4.3 Validación de Teléfono

```python
import re

def validar_telefono_argentino(telefono):
    """
    Acepta formatos:
    - 1122334455
    - 11 2233 4455
    - (011) 2233-4455
    """
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    
    if not telefono_limpio.isdigit():
        raise ValidationError("El teléfono debe contener solo números")
    
    if len(telefono_limpio) < 10:
        raise ValidationError("El teléfono debe tener al menos 10 dígitos")
    
    return telefono_limpio
```

---

## 5. Interfaz de Usuario

### 5.1 Búsqueda de Paciente

```
┌─────────────────────────────────────────────────────────────┐
│  BÚSQUEDA DE PACIENTE                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Buscar por DNI o Nombre: [________________] [🔍 Buscar]    │
│                                            [+ Nuevo Paciente]│
│                                                              │
│  Resultados:                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ DNI        │ Nombre Completo   │ Edad │ Acciones    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 30.555.444 │ García, Juan      │ 45   │ [Ver] [📋] │   │
│  │ 25.123.456 │ López, María      │ 52   │ [Ver] [📋] │   │
│  │ 35.789.012 │ Pérez, Carlos     │ 38   │ [Ver] [📋] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Ver] = Ver detalle   [📋] = Iniciar visita                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Registro de Paciente

```
┌─────────────────────────────────────────────────────────────┐
│  REGISTRO DE PACIENTE                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Buscar paciente existente: [________________] [Buscar DNI] │
│                                                              │
│  ─── Datos Personales ───────────────────────────────────── │
│  DNI: [________]  Nombre: [______________]                  │
│  Apellido: [______________]  Fecha Nac: [__/__/____]        │
│  Sexo: (●) Masculino  ( ) Femenino  ( ) Otro                │
│                                                              │
│  ─── Contacto ───────────────────────────────────────────── │
│  Teléfono: [__________]  Tel. Alt.: [__________]            │
│  Email: [____________________]                               │
│  Dirección: [_____________________________________________] │
│  Localidad: [______________]  Provincia: [______________]   │
│  Código Postal: [______]                                     │
│                                                              │
│  ─── Cobertura Médica ───────────────────────────────────── │
│  Obra Social: [▼ Seleccionar]  Nro Afiliado: [__________]  │
│                                                              │
│  ─── Contacto de Emergencia ─────────────────────────────── │
│  Nombre: [____________________]  Relación: [__________]     │
│  Teléfono: [__________]  Tel. Alt.: [__________]            │
│                                                              │
│  ─── Antecedentes Médicos (Opcional) ────────────────────── │
│  [☑] Completar ahora  [ ] Completar después                 │
│                                                              │
│  Alergias: [_____________________________________________]  │
│  Medicación Crónica: [___________________________________]  │
│  Enfermedades Crónicas: [________________________________]  │
│  Grupo Sanguíneo: [▼ Seleccionar]                           │
│                                                              │
│  ─── Motivo de Ingreso ──────────────────────────────────── │
│  [___________________________________________________________]│
│                                                              │
│                     [Cancelar]  [Guardar e Ir a Triage]     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Detalle de Paciente

```
┌─────────────────────────────────────────────────────────────┐
│  PACIENTE: García, Juan (DNI: 30.555.444)          [Editar] │
├─────────────────────────────────────────────────────────────┤
│ [Datos] [Antecedentes] [Historial de Visitas]               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Edad: 45 años  |  Sexo: Masculino  |  Grupo: O+            │
│  Teléfono: 11 2233-4455  |  Email: juan.garcia@email.com    │
│  Dirección: Av. Corrientes 1234, CABA                        │
│  Cobertura: OSDE (N° 123456789)                              │
│  Contacto Emerg: María García (Esposa) - 11 5566-7788       │
│                                                              │
│  ─── Historial de Visitas ──────────────────────────────────│
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Fecha       │ ESI │ Diagnóstico      │ Destino       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 28/04/26    │ 🟠2 │ I20.0 Angina     │ Internación   │   │
│  │ 10:35       │     │                  │               │   │
│  │ ────────────────────────────────────────────────────  │   │
│  │ 15/03/26    │ 🟡3 │ M79.3 Lumbalgia  │ Alta médica   │   │
│  │ 14:20       │     │                  │               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│                                    [Iniciar Nueva Visita]    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. API Endpoints

### 6.1 Búsqueda y Listado

```
GET /api/v1/pacientes/?search={query}

Query params:
- search: Término de búsqueda (DNI o nombre)
- page: Número de página (default: 1)
- page_size: Tamaño de página (default: 20)

Response (200):
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "dni": "30555444",
      "nombre": "Juan",
      "apellido": "García",
      "nombre_completo": "García, Juan",
      "edad": 45,
      "sexo": "M",
      "telefono": "1122334455",
      "email": "juan.garcia@email.com",
      "cobertura": {
        "id": 1,
        "nombre": "OSDE"
      },
      "tiene_antecedentes": true,
      "cantidad_visitas": 2
    },
    ...
  ]
}
```

### 6.2 Obtener Paciente Específico

```
GET /api/v1/pacientes/{dni}/

Response (200):
{
  "id": 1,
  "dni": "30555444",
  "nombre": "Juan",
  "apellido": "García",
  "fecha_nacimiento": "1981-05-15",
  "sexo": "M",
  "edad": 45,
  "telefono": "1122334455",
  "telefono_alternativo": "",
  "email": "juan.garcia@email.com",
  "direccion": "Av. Corrientes 1234",
  "localidad": "CABA",
  "provincia": "Buenos Aires",
  "codigo_postal": "1043",
  "cobertura": {
    "id": 1,
    "nombre": "OSDE",
    "tipo": "prepaga"
  },
  "numero_afiliado": "123456789",
  "contacto_emergencia": {
    "nombre": "María García",
    "relacion": "Esposa",
    "telefono": "1155667788"
  },
  "antecedentes": {
    "alergias": "Penicilina",
    "medicacion_cronica": "Enalapril 10mg",
    "enfermedades_cronicas": "Hipertensión arterial",
    "grupo_sanguineo": "O+"
  },
  "created_at": "2025-01-10T10:30:00Z",
  "updated_at": "2026-04-28T14:30:00Z"
}
```

### 6.3 Crear Paciente

```
POST /api/v1/pacientes/

Body:
{
  "dni": "35789012",
  "nombre": "Carlos",
  "apellido": "Pérez",
  "fecha_nacimiento": "1990-03-20",
  "sexo": "M",
  "telefono": "1133445566",
  "email": "carlos.perez@email.com",
  "direccion": "Calle Falsa 123",
  "localidad": "La Plata",
  "provincia": "Buenos Aires",
  "cobertura_id": 2,
  "numero_afiliado": "987654321",
  "contacto_emergencia": {
    "nombre": "Ana Pérez",
    "relacion": "Hermana",
    "telefono": "1144556677"
  },
  "antecedentes": {
    "alergias": "Ninguna conocida",
    "grupo_sanguineo": "A+"
  }
}

Response (201):
{
  "id": 123,
  "dni": "35789012",
  "nombre": "Carlos",
  "apellido": "Pérez",
  ...
}
```

### 6.4 Actualizar Paciente

```
PUT /api/v1/pacientes/{dni}/

Body: (mismos campos que POST, excepto DNI)

Response (200):
{
  "id": 123,
  ...
}
```

### 6.5 Historial de Visitas

```
GET /api/v1/pacientes/{dni}/visitas/

Response (200):
{
  "count": 5,
  "results": [
    {
      "id": 456,
      "fecha_ingreso": "2026-04-28T10:35:00Z",
      "fecha_egreso": "2026-04-28T16:20:00Z",
      "estado": "finalizado",
      "triage": {
        "nivel_esi": 2,
        "motivo_consulta": "Dolor torácico"
      },
      "atencion": {
        "diagnostico_principal": "I20.0 - Angina inestable",
        "destino": "internacion"
      }
    },
    ...
  ]
}
```

---

## 7. Lógica de Negocio

### 7.1 Búsqueda de Pacientes

```python
# apps/pacientes/views.py
from django.db.models import Q

def buscar_pacientes(query):
    """
    Busca pacientes por DNI (exacto) o nombre/apellido (parcial).
    """
    if query.isdigit():
        # Búsqueda por DNI (exacto)
        return Paciente.objects.filter(dni=query)
    else:
        # Búsqueda por nombre/apellido (parcial, case-insensitive)
        return Paciente.objects.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        ).order_by('apellido', 'nombre')
```

### 7.2 Evitar Duplicados

```python
# En forms.py o serializers.py
def validate_dni(self, dni):
    """
    Valida que el DNI no exista ya en el sistema.
    """
    from apps.pacientes.models import Paciente
    from apps.core.contracts import validar_dni_argentino
    
    # Validar formato
    dni_limpio = validar_dni_argentino(dni)
    
    # Validar unicidad (solo en creación)
    if not self.instance.pk:  # Es nuevo
        if Paciente.objects.filter(dni=dni_limpio).exists():
            raise ValidationError(
                f"Ya existe un paciente con DNI {dni_limpio}"
            )
    
    return dni_limpio
```

### 7.3 Soft Delete

Los pacientes no se eliminan físicamente, solo se marcan como inactivos:

```python
# En models.py (ya definido en contracts.md)
class Paciente(models.Model):
    # ...
    activo = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """Soft delete: marcar como inactivo en lugar de eliminar."""
        self.activo = False
        self.save()
```

---

## 8. Dependencias

### 8.1 Módulos Requeridos

- **Core**: Autenticación, permisos, auditoría

### 8.2 Módulos que Dependen de Pacientes

- **Triage**: Necesita datos del paciente para crear VisitaEmergencia
- **Atención**: Accede a datos del paciente y antecedentes
- **Dashboard**: Muestra datos básicos del paciente en lista de espera
- **Reportes**: Usa datos de pacientes para estadísticas

---

## 9. Tests Requeridos

```python
# apps/pacientes/tests/test_paciente.py
from django.test import TestCase
from apps.pacientes.models import Paciente
from apps.core.models import Usuario

class PacienteTestCase(TestCase):
    def test_crear_paciente_valido(self):
        paciente = Paciente.objects.create(
            dni='30555444',
            nombre='Juan',
            apellido='García',
            fecha_nacimiento='1981-05-15',
            sexo='M',
            telefono='1122334455'
        )
        self.assertEqual(paciente.edad, 45)
        self.assertEqual(str(paciente), 'García, Juan (DNI: 30555444)')
    
    def test_dni_duplicado(self):
        Paciente.objects.create(dni='12345678', nombre='Test', ...)
        
        with self.assertRaises(IntegrityError):
            Paciente.objects.create(dni='12345678', nombre='Test2', ...)
    
    def test_buscar_por_dni(self):
        paciente = Paciente.objects.create(dni='30555444', ...)
        resultado = Paciente.objects.filter(dni='30555444')
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first(), paciente)
    
    def test_buscar_por_nombre_parcial(self):
        Paciente.objects.create(dni='11111111', nombre='Juan', apellido='García', ...)
        Paciente.objects.create(dni='22222222', nombre='María', apellido='García', ...)
        
        resultados = Paciente.objects.filter(apellido__icontains='garc')
        self.assertEqual(resultados.count(), 2)
```

---

## 10. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md) - Modelos Paciente, Cobertura, ContactoEmergencia, AntecedentesMedicos
- **Módulos relacionados**:
  - Core: [`specs/core.md`](./core.md) - Autenticación y permisos
  - Triage: [`specs/triage.md`](./triage.md) - Usa datos de pacientes

---

*Especificación del módulo Pacientes - Sistema de Recepción de Pacientes en Emergencias*
