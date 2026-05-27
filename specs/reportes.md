# Especificación del Módulo Reportes

**Módulo:** `apps/reportes/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Estadísticas y reportes del servicio

---

## 1. Objetivos

Generar **reportes y estadísticas** para análisis del servicio:

- Reportes diarios de actividad
- KPIs de emergencias (Door-to-Triage, Door-to-Doctor, LWBS)
- Distribución de niveles ESI
- Productividad médica
- Diagnósticos más frecuentes
- Exportación a Excel y PDF

---

## 2. Reportes Incluidos en MVP

### 2.1 Resumen Diario

**Contenido:**
- Total de pacientes atendidos
- Distribución por nivel ESI
- Distribución por destino (alta, internación, etc.)
- Tiempos promedio de espera
- Pacientes por turno (mañana, tarde, noche)

**Filtros:** Fecha específica

### 2.2 Tiempos de Espera

**Contenido:**
- Door-to-Triage promedio
- Door-to-Doctor por nivel ESI
- Tiempo total de estancia promedio
- Distribución por rangos de tiempo

**Filtros:** Rango de fechas, nivel ESI

### 2.3 Productividad Médica

**Contenido:**
- Atenciones por médico
- Tiempo promedio de atención por médico
- Distribución de diagnósticos por médico

**Filtros:** Rango de fechas, médico específico

### 2.4 Diagnósticos Frecuentes

**Contenido:**
- Top 10-20 diagnósticos CIE-10
- Distribución por capítulo CIE-10
- Tendencias temporales

**Filtros:** Rango de fechas, top N

### 2.5 Censo Actual

**Contenido:**
- Pacientes actualmente en servicio
- Pacientes en espera por nivel ESI
- Ocupación vs capacidad (si se define)

**Filtros:** Ninguno (tiempo real)

---

## 3. KPIs de Emergencias

### 3.1 Door-to-Triage

**Definición:** Tiempo desde ingreso del paciente hasta realización del triage

**Cálculo:**
```python
def calcular_door_to_triage(visita):
    """
    Retorna tiempo en minutos desde ingreso hasta triage.
    """
    if not hasattr(visita, 'triage'):
        return None
    
    delta = visita.triage.timestamp - visita.fecha_ingreso
    return int(delta.total_seconds() / 60)
```

**Meta:** < 10 minutos

### 3.2 Door-to-Doctor

**Definición:** Tiempo desde ingreso hasta inicio de atención médica

**Cálculo:**
```python
def calcular_door_to_doctor(visita):
    """
    Retorna tiempo en minutos desde ingreso hasta atención.
    """
    if not hasattr(visita, 'atencion'):
        return None
    
    delta = visita.atencion.fecha_inicio - visita.fecha_ingreso
    return int(delta.total_seconds() / 60)
```

**Meta:** Según nivel ESI (ver tabla)

### 3.3 Tiempos Objetivo por Nivel ESI

| Nivel ESI | Door-to-Doctor |
|-----------|----------------|
| ESI 1 | Inmediato |
| ESI 2 | < 10 minutos |
| ESI 3 | < 60 minutos |
| ESI 4 | < 120 minutos |
| ESI 5 | < 240 minutos |

### 3.4 LWBS (Left Without Being Seen)

**Definición:** Porcentaje de pacientes que abandonan sin ser atendidos

**Cálculo:**
```python
def calcular_lwbs(fecha_inicio, fecha_fin):
    """
    Retorna porcentaje de pacientes que abandonaron sin atención.
    """
    total = VisitaEmergencia.objects.filter(
        fecha_ingreso__range=(fecha_inicio, fecha_fin)
    ).count()
    
    abandonos = VisitaEmergencia.objects.filter(
        fecha_ingreso__range=(fecha_inicio, fecha_fin),
        estado='abandono'
    ).exclude(atencion__isnull=False).count()
    
    return (abandonos / total * 100) if total > 0 else 0
```

**Meta:** < 2%

### 3.5 Tiempo Promedio de Estancia

**Definición:** Tiempo total que el paciente permanece en emergencias

**Cálculo:**
```python
def calcular_tiempo_estancia(visita):
    """
    Retorna tiempo total en minutos desde ingreso hasta egreso.
    """
    if not visita.fecha_egreso:
        return None
    
    delta = visita.fecha_egreso - visita.fecha_ingreso
    return int(delta.total_seconds() / 60)
```

**Meta:** < 4 horas (240 minutos)

---

## 4. Formatos de Exportación

### 4.1 Excel (openpyxl)

```python
# apps/reportes/exports.py
from openpyxl import Workbook
from openpyxl.styles import Font, Fill

def exportar_resumen_diario_excel(fecha):
    """
    Exporta resumen diario a Excel.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = f"Resumen {fecha}"
    
    # Headers
    ws['A1'] = 'Nivel ESI'
    ws['B1'] = 'Cantidad'
    ws['A1'].font = Font(bold=True)
    
    # Data
    contadores = contar_por_esi(fecha)
    row = 2
    for nivel, cantidad in contadores.items():
        ws[f'A{row}'] = f'ESI {nivel}'
        ws[f'B{row}'] = cantidad
        row += 1
    
    return wb
```

### 4.2 PDF (weasyprint)

```python
# apps/reportes/exports.py
from weasyprint import HTML
from django.template.loader import render_to_string

def exportar_resumen_diario_pdf(fecha):
    """
    Exporta resumen diario a PDF.
    """
    context = {
        'fecha': fecha,
        'contadores': contar_por_esi(fecha),
        'tiempos': calcular_tiempos_promedio(fecha),
        # ...
    }
    
    html_string = render_to_string('reportes/resumen_diario_pdf.html', context)
    html = HTML(string=html_string)
    return html.write_pdf()
```

---

## 5. API Endpoints

### 5.1 Resumen Diario

```
GET /api/v1/reportes/resumen-diario/?fecha=2026-04-28&format=json

Response (200):
{
  "fecha": "2026-04-28",
  "total_pacientes": 35,
  "por_nivel_esi": {
    "1": 0,
    "2": 3,
    "3": 15,
    "4": 12,
    "5": 5
  },
  "por_destino": {
    "alta_medica": 28,
    "internacion": 5,
    "derivacion": 1,
    "abandono": 1
  },
  "tiempos_promedio": {
    "door_to_triage": 8.5,
    "door_to_doctor": 35.2,
    "estancia_total": 180.5
  },
  "por_turno": {
    "mañana": 15,
    "tarde": 12,
    "noche": 8
  }
}

# Exportar a Excel
GET /api/v1/reportes/resumen-diario/?fecha=2026-04-28&format=excel
Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

# Exportar a PDF
GET /api/v1/reportes/resumen-diario/?fecha=2026-04-28&format=pdf
Response: application/pdf
```

### 5.2 Tiempos de Espera

```
GET /api/v1/reportes/tiempos-espera/?desde=2026-04-01&hasta=2026-04-30

Response (200):
{
  "periodo": {
    "desde": "2026-04-01",
    "hasta": "2026-04-30"
  },
  "door_to_triage": {
    "promedio": 9.2,
    "min": 2,
    "max": 35,
    "dentro_objetivo": 85.5  // % < 10 min
  },
  "door_to_doctor_por_esi": {
    "1": {"promedio": 0.5, "objetivo": 0, "cumplimiento": 50.0},
    "2": {"promedio": 12.3, "objetivo": 10, "cumplimiento": 45.2},
    "3": {"promedio": 42.1, "objetivo": 60, "cumplimiento": 78.5},
    "4": {"promedio": 95.3, "objetivo": 120, "cumplimiento": 82.3},
    "5": {"promedio": 180.2, "objetivo": 240, "cumplimiento": 90.1}
  }
}
```

### 5.3 Productividad Médica

```
GET /api/v1/reportes/productividad-medica/?desde=2026-04-01&hasta=2026-04-30

Response (200):
{
  "periodo": {
    "desde": "2026-04-01",
    "hasta": "2026-04-30"
  },
  "medicos": [
    {
      "id": 5,
      "nombre": "Dr. García, Juan",
      "total_atenciones": 120,
      "tiempo_promedio_atencion": 45.5,
      "pacientes_por_turno": 4.0,
      "diagnosticos_frecuentes": [
        {"codigo": "I10", "descripcion": "HTA", "cantidad": 25},
        {"codigo": "J06.9", "descripcion": "IRA", "cantidad": 18}
      ]
    },
    ...
  ]
}
```

### 5.4 Diagnósticos Frecuentes

```
GET /api/v1/reportes/diagnosticos-frecuentes/?desde=2026-04-01&hasta=2026-04-30&top=10

Response (200):
{
  "periodo": {
    "desde": "2026-04-01",
    "hasta": "2026-04-30"
  },
  "total_diagnosticos": 450,
  "top_diagnosticos": [
    {
      "codigo": "I10",
      "descripcion": "Hipertensión esencial (primaria)",
      "cantidad": 45,
      "porcentaje": 10.0
    },
    {
      "codigo": "J06.9",
      "descripcion": "Infección respiratoria aguda",
      "cantidad": 38,
      "porcentaje": 8.4
    },
    ...
  ]
}
```

### 5.5 Censo Actual

```
GET /api/v1/reportes/censo-actual/

Response (200):
{
  "timestamp": "2026-04-28T11:45:00Z",
  "total_pacientes_activos": 11,
  "por_estado": {
    "esperando_triage": 1,
    "esperando_atencion": 6,
    "en_atencion": 4
  },
  "por_nivel_esi": {
    "1": 0,
    "2": 2,
    "3": 5,
    "4": 3,
    "5": 1
  },
  "tiempo_espera_promedio": 42.5
}
```

---

## 6. Interfaz de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│  REPORTES Y ESTADÍSTICAS                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Seleccionar Reporte: [▼ Resumen Diario          ]         │
│                                                              │
│  ─── Filtros ────────────────────────────────────────────── │
│  Fecha: [28/04/2026]                [📊 Generar]            │
│                                                              │
│  ─── Resultados ─────────────────────────────────────────── │
│  Resumen Diario - 28/04/2026                                │
│                                                              │
│  Total de Pacientes: 35                                     │
│                                                              │
│  Distribución por Nivel ESI:                                │
│  🔴 ESI 1: 0  |  🟠 ESI 2: 3  |  🟡 ESI 3: 15              │
│  🟢 ESI 4: 12 |  🔵 ESI 5: 5                                │
│                                                              │
│  Destinos:                                                   │
│  Alta médica: 28 | Internación: 5 | Derivación: 1          │
│  Abandono: 1                                                 │
│                                                              │
│  Tiempos Promedio:                                           │
│  Door-to-Triage: 8.5 min  ✓                                 │
│  Door-to-Doctor: 35.2 min                                   │
│  Estancia Total: 180.5 min (3h)                             │
│                                                              │
│                    [📥 Excel]  [📥 PDF]  [📧 Enviar Email]  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Lógica de Cálculo

### 7.1 Queries Eficientes

```python
# apps/reportes/generators.py
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField

def generar_resumen_diario(fecha):
    """
    Genera resumen de actividad del día.
    """
    visitas = VisitaEmergencia.objects.filter(
        fecha_ingreso__date=fecha
    ).select_related('paciente', 'triage', 'atencion')
    
    # Contadores por ESI
    por_esi = visitas.values('triage__nivel_esi').annotate(
        cantidad=Count('id')
    )
    
    # Contadores por destino
    por_destino = visitas.filter(
        atencion__isnull=False
    ).values('atencion__destino').annotate(
        cantidad=Count('id')
    )
    
    # Tiempos promedio
    visitas_con_tiempos = visitas.annotate(
        door_to_triage=ExpressionWrapper(
            F('triage__timestamp') - F('fecha_ingreso'),
            output_field=DurationField()
        )
    )
    
    tiempos = visitas_con_tiempos.aggregate(
        avg_door_to_triage=Avg('door_to_triage')
    )
    
    return {
        'fecha': fecha,
        'total': visitas.count(),
        'por_esi': dict(por_esi),
        'por_destino': dict(por_destino),
        'tiempos': tiempos
    }
```

---

## 8. Permisos

| Reporte | Recepcionista | Enfermero | Médico | Admin |
|---------|:-------------:|:---------:|:------:|:-----:|
| Ver estadísticas diarias | ✗ | ✓ | ✓ | ✓ |
| Exportar reportes | ✗ | ✗ | ✓ | ✓ |
| Reportes de productividad | ✗ | ✗ | ✗ | ✓ |
| Todos los reportes | ✗ | ✗ | ✗ | ✓ |

---

## 9. Dependencias

**Requiere:**
- Core (autenticación, permisos)
- Pacientes (datos de visitas)
- Triage (niveles ESI, tiempos)
- Atención (diagnósticos, destinos)

---

## 10. Tests

```python
def test_calcular_door_to_triage():
    hace_1_hora = timezone.now() - timedelta(hours=1)
    hace_50_min = timezone.now() - timedelta(minutes=50)
    
    visita = VisitaEmergencia.objects.create(fecha_ingreso=hace_1_hora, ...)
    Triage.objects.create(visita=visita, timestamp=hace_50_min, ...)
    
    tiempo = calcular_door_to_triage(visita)
    assert 9 <= tiempo <= 11  # ~10 minutos

def test_kpi_lwbs():
    # Crear 10 visitas
    for i in range(10):
        VisitaEmergencia.objects.create(...)
    
    # 2 abandonos sin atención
    for i in range(2):
        VisitaEmergencia.objects.create(estado='abandono', ...)
    
    lwbs = calcular_lwbs(fecha_inicio, fecha_fin)
    assert lwbs == 20.0  # 2/10 = 20%
```

---

## 11. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md)
- **Módulos**: Core, Pacientes, Triage, Atención

---

*Especificación del módulo Reportes - Sistema de Recepción de Pacientes en Emergencias*
