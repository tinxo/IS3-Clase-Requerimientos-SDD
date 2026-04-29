# Especificación del Módulo Dashboard

**Módulo:** `apps/dashboard/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Panel de monitoreo en tiempo real

---

## 1. Objetivos

Visualizar el **estado actual** del servicio de emergencias:

- Lista de pacientes en espera ordenados por prioridad
- Contadores por nivel ESI
- Tiempos de espera por paciente
- Estado actual de cada visita
- Indicadores visuales de urgencia

---

## 2. Casos de Uso

### 2.1 Ver Panel de Espera

**Actor:** Todos los roles  
**Flujo:**
1. Usuario accede al dashboard principal
2. Sistema muestra contadores por nivel ESI (1-5)
3. Sistema muestra lista de pacientes activos ordenados por:
   - Prioridad (ESI 1 primero, ESI 5 último)
   - Tiempo de espera (mayor primero dentro del mismo nivel)
4. Usuario puede filtrar por estado
5. Usuario puede actualizar manualmente o esperar polling automático

---

## 3. KPIs Visualizados

### 3.1 Contadores por Nivel ESI

```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ ESI 1   │ │ ESI 2   │ │ ESI 3   │ │ ESI 4   │ │ ESI 5   │
│   0     │ │   2     │ │   5     │ │   3     │ │   1     │
│ 🔴      │ │ 🟠      │ │ 🟡      │ │ 🟢      │ │ 🔵      │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### 3.2 Tiempos de Espera

Por cada paciente:
- **Tiempo de espera total**: desde ingreso
- **Tiempo en estado actual**: desde último cambio de estado
- **Indicador de alerta**: 
  - 🟢 Verde: dentro del tiempo objetivo
  - 🟡 Amarillo: cerca del límite (80-100%)
  - 🔴 Rojo: sobrepasó el tiempo objetivo

---

## 4. Interfaz de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│  EMERGENCIAS - Dashboard               [Usuario] [Salir]    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────┐  │
│  │ ESI 1   │ │ ESI 2   │ │ ESI 3   │ │ ESI 4   │ │ ESI 5│  │
│  │   0     │ │   2     │ │   5     │ │   3     │ │   1  │  │
│  │ 🔴      │ │ 🟠      │ │ 🟡      │ │ 🟢      │ │ 🔵   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────┘  │
│                                                              │
│  PACIENTES EN ESPERA                        [🔄 Actualizar] │
│  Filtros: [☑] Esperando triage  [☑] Esperando atención      │
│           [☑] En atención       [ ] Finalizados             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ESI│Paciente       │Motivo          │Espera │Estado   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │🟠2│García, Juan   │Dolor torácico  │12 min │En atenc.│   │
│  │🟠2│López, María   │Disnea aguda    │18 min │Esperando│   │
│  │🟡3│Pérez, Carlos  │Fractura brazo  │25 min │Esperando│   │
│  │🟡3│Ruiz, Ana      │Dolor abdominal │35 min │En atenc.│   │
│  │🟡3│Gómez, Luis    │Cefalea intensa │🔴 72m │Esperando│   │
│  │🟢4│Martínez, Sofía│Tos y fiebre    │45 min │Esperando│   │
│  │🔵5│Fernández, José│Consulta control│15 min │Esp.triage│  │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Última actualización: 28/04/2026 11:45:23                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Lógica de Ordenamiento

### 5.1 Criterios de Orden

```python
# apps/dashboard/utils.py

def ordenar_visitas_activas(visitas):
    """
    Ordena visitas por prioridad ESI (menor primero) 
    y tiempo de espera (mayor primero).
    """
    return visitas.order_by(
        'triage__nivel_esi',      # ESI 1, 2, 3, 4, 5
        '-fecha_ingreso'           # Más antiguo primero
    )
```

### 5.2 Cálculo de Tiempo de Espera

```python
from django.utils import timezone

def calcular_tiempo_espera(visita):
    """
    Calcula tiempo de espera en minutos desde el ingreso.
    """
    ahora = timezone.now()
    delta = ahora - visita.fecha_ingreso
    return int(delta.total_seconds() / 60)
```

### 5.3 Indicador de Alerta

```python
from apps.contracts import TIEMPOS_OBJETIVO_ESI

def obtener_indicador_alerta(visita):
    """
    Retorna color de alerta según tiempo objetivo ESI.
    """
    if not hasattr(visita, 'triage'):
        return 'gray'  # Sin triage aún
    
    tiempo_espera = calcular_tiempo_espera(visita)
    tiempo_objetivo = TIEMPOS_OBJETIVO_ESI[visita.triage.nivel_esi]
    
    if tiempo_objetivo == 0:  # ESI 1 - Inmediato
        return 'red' if tiempo_espera > 0 else 'green'
    
    porcentaje = (tiempo_espera / tiempo_objetivo) * 100
    
    if porcentaje < 80:
        return 'green'
    elif porcentaje < 100:
        return 'yellow'
    else:
        return 'red'
```

---

## 6. API Endpoints

### 6.1 Obtener Visitas Activas

```
GET /api/v1/dashboard/visitas-activas/

Query params:
- estados: esperando_triage,esperando_atencion,en_atencion (default: todas)

Response (200):
{
  "visitas": [
    {
      "id": 456,
      "paciente": {
        "id": 123,
        "nombre_completo": "García, Juan",
        "dni": "30555444"
      },
      "fecha_ingreso": "2026-04-28T10:35:00Z",
      "tiempo_espera_minutos": 70,
      "estado": "en_atencion",
      "estado_display": "En Atención",
      "triage": {
        "id": 789,
        "nivel_esi": 2,
        "color": "orange",
        "motivo_consulta": "Dolor torácico opresivo"
      },
      "alerta": "red",
      "atencion": {
        "medico": "Dr. García"
      }
    },
    ...
  ]
}
```

### 6.2 Obtener Contadores ESI

```
GET /api/v1/dashboard/contadores-esi/

Response (200):
{
  "contadores": {
    "1": 0,
    "2": 2,
    "3": 5,
    "4": 3,
    "5": 1
  },
  "total": 11
}
```

---

## 7. Actualización de Datos

### 7.1 Estrategia en MVP

**Manual o Polling suave:**
- Botón "Actualizar" para refresh manual
- Polling opcional cada 30 segundos (configurable)
- Sin WebSockets en MVP (Fase 2)

```javascript
// Polling con HTMX
<div hx-get="/dashboard/visitas-activas-html/" 
     hx-trigger="every 30s" 
     hx-target="#lista-visitas">
  <!-- Contenido de la tabla -->
</div>
```

### 7.2 Fase 2: WebSockets

```python
# apps/dashboard/consumers.py (Django Channels)
class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            "dashboard",
            self.channel_name
        )
    
    def dashboard_update(self, event):
        self.send(text_data=json.dumps(event['data']))
```

---

## 8. Filtros

| Filtro | Descripción |
|--------|-------------|
| **Estado** | Esperando triage, Esperando atención, En atención |
| **Nivel ESI** | 1, 2, 3, 4, 5 |
| **Tiempo de espera** | < 30min, 30-60min, > 60min |

```
GET /api/v1/dashboard/visitas-activas/?estado=esperando_atencion&nivel_esi=2
```

---

## 9. Dependencias

**Requiere:**
- Core (autenticación)
- Pacientes (datos de paciente)
- Triage (nivel ESI, tiempos)

**Usado por:**
- Todos los usuarios del sistema

---

## 10. Tests

```python
def test_ordenar_por_prioridad_esi():
    v1 = crear_visita_con_triage(nivel_esi=3)
    v2 = crear_visita_con_triage(nivel_esi=1)
    v3 = crear_visita_con_triage(nivel_esi=2)
    
    visitas = ordenar_visitas_activas([v1, v2, v3])
    assert list(visitas) == [v2, v3, v1]  # ESI 1, 2, 3

def test_calculo_tiempo_espera():
    hace_30_min = timezone.now() - timedelta(minutes=30)
    visita = VisitaEmergencia.objects.create(fecha_ingreso=hace_30_min, ...)
    
    tiempo = calcular_tiempo_espera(visita)
    assert 29 <= tiempo <= 31  # Margen de 1 minuto

def test_indicador_alerta_rojo_si_supera_objetivo():
    visita = crear_visita_con_triage(
        nivel_esi=2,  # Objetivo: 10 min
        hace=15  # 15 minutos atrás
    )
    assert obtener_indicador_alerta(visita) == 'red'
```

---

## 11. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md)
- **Módulos**: Core, Pacientes, Triage

---

*Especificación del módulo Dashboard - Sistema de Recepción de Pacientes en Emergencias*
