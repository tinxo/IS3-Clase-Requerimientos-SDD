# Especificación del Módulo Triage

**Módulo:** `apps/triage/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Clasificación de pacientes según sistema ESI

---

## 1. Objetivos

Implementar el sistema de **triage ESI (Emergency Severity Index)** para:

- Clasificar pacientes en 5 niveles de urgencia
- Registrar signos vitales y evaluaciones clínicas
- Sugerir automáticamente nivel ESI basado en criterios
- Gestionar el estado de las visitas de emergencia
- Optimizar tiempos de atención según prioridad

---

## 2. Sistema ESI (Emergency Severity Index)

### 2.1 Niveles ESI

| Nivel | Nombre | Color | Descripción | Tiempo Objetivo |
|-------|--------|-------|-------------|-----------------|
| **ESI 1** | Resucitación | 🔴 Rojo | Requiere intervención inmediata para salvar la vida | Inmediato |
| **ESI 2** | Emergencia | 🟠 Naranja | Situación de alto riesgo, no puede esperar | < 10 minutos |
| **ESI 3** | Urgencia | 🟡 Amarillo | Requiere múltiples recursos, condición estable | < 60 minutos |
| **ESI 4** | Menos Urgente | 🟢 Verde | Requiere un recurso | < 120 minutos |
| **ESI 5** | No Urgente | 🔵 Azul | No requiere recursos | < 240 minutos |

### 2.2 Criterios de Clasificación

#### ESI 1 - Resucitación
- Paro cardiorrespiratorio
- Intubación inminente
- Apnea / Sin respiración espontánea
- Sin pulso
- No responde a estímulos
- Glasgow < 8
- Compromiso de vía aérea obstruida

#### ESI 2 - Emergencia
- Confusión / Letargia / Desorientación aguda
- Dolor severo (EVA 8-10)
- Saturación O2 < 90%
- Glasgow < 14
- Signos de shock
- Disnea severa
- Sangrado activo significativo

#### ESI 3 - Urgencia
- Requiere 2+ recursos (labs, imágenes, IV, consulta especialista)
- Signos vitales en zona de alerta
- Dolor moderado-severo (EVA 4-7)
- Condición potencialmente seria pero estable

#### ESI 4 - Menos Urgente
- Requiere 1 recurso (ej: solo Rx, o solo lab)
- Signos vitales normales
- Dolor leve-moderado (EVA 1-3)

#### ESI 5 - No Urgente
- No requiere recursos hospitalarios
- Solo necesita examen físico y/o receta
- Signos vitales normales
- Sin dolor o dolor mínimo

---

## 3. Casos de Uso

### 3.1 Realizar Triage

**Actor:** Enfermero, Médico  
**Precondición:** Paciente registrado, visita iniciada  
**Flujo:**
1. Seleccionar visita en estado "esperando_triage"
2. Completar motivo de consulta detallado
3. Registrar signos vitales (PA, FC, T°, SatO2, FR)
4. Registrar dolor EVA (0-10)
5. Evaluar nivel de conciencia (Glasgow)
6. Evaluar vía aérea
7. Sistema sugiere nivel ESI basado en criterios
8. Enfermero confirma o ajusta nivel ESI
9. Guardar triage → Visita pasa a "esperando_atencion"

---

## 4. Modelos

Ver [`contracts.md`](../contracts.md) para definición completa de:
- `VisitaEmergencia`
- `Triage`

### 4.1 Enums Importantes

```python
# NivelESI
RESUCITACION = 1
EMERGENCIA = 2
URGENCIA = 3
MENOS_URGENTE = 4
NO_URGENTE = 5

# ViaAerea
PERMEABLE = 'permeable'
COMPROMETIDA = 'comprometida'
OBSTRUIDA = 'obstruida'

# Estado de Visita
ESPERANDO_TRIAGE = 'esperando_triage'
ESPERANDO_ATENCION = 'esperando_atencion'
EN_ATENCION = 'en_atencion'
FINALIZADO = 'finalizado'
```

---

## 5. Lógica de Sugerencia ESI

### 5.1 Algoritmo de Sugerencia

```python
# apps/triage/esi_logic.py

def sugerir_nivel_esi(signos_vitales, dolor_eva, glasgow, via_aerea, motivo):
    """
    Sugiere nivel ESI basado en signos vitales y evaluaciones.
    
    Returns:
        int: Nivel ESI sugerido (1-5)
        str: Justificación de la sugerencia
    """
    
    # ESI 1: Condiciones críticas
    if via_aerea == 'obstruida':
        return 1, "Vía aérea obstruida - Requiere intervención inmediata"
    
    if glasgow and glasgow < 8:
        return 1, "Glasgow < 8 - Estado crítico de conciencia"
    
    if not signos_vitales.get('saturacion_o2') or signos_vitales['saturacion_o2'] < 85:
        return 1, "Saturación O2 crítica"
    
    # ESI 2: Emergencia
    if glasgow and glasgow < 14:
        return 2, "Glasgow < 14 - Alteración del nivel de conciencia"
    
    if signos_vitales.get('saturacion_o2') and signos_vitales['saturacion_o2'] < 90:
        return 2, "Saturación O2 < 90% - Requiere atención urgente"
    
    if dolor_eva and dolor_eva >= 8:
        return 2, "Dolor severo (EVA 8-10)"
    
    if via_aerea == 'comprometida':
        return 2, "Vía aérea comprometida"
    
    # Taquicardia/bradicardia severa
    fc = signos_vitales.get('frecuencia_cardiaca')
    if fc and (fc > 150 or fc < 50):
        return 2, f"Frecuencia cardíaca anormal ({fc} lpm)"
    
    # Hipertensión severa
    pas = signos_vitales.get('presion_sistolica')
    if pas and pas > 200:
        return 2, f"Hipertensión severa (PAS {pas} mmHg)"
    
    # ESI 3: Urgencia
    if dolor_eva and dolor_eva >= 4:
        return 3, "Dolor moderado-severo (EVA 4-7)"
    
    # Alteraciones moderadas de signos vitales
    if fc and (fc > 120 or fc < 60):
        return 3, "Frecuencia cardíaca en zona de alerta"
    
    if pas and (pas > 180 or pas < 90):
        return 3, "Presión arterial en zona de alerta"
    
    # ESI 4: Menos urgente
    if dolor_eva and dolor_eva >= 1:
        return 4, "Dolor leve-moderado"
    
    # ESI 5: No urgente (default)
    return 5, "Signos vitales estables, sin urgencia aparente"
```

### 5.2 Uso de la Sugerencia

```python
# En views.py
from apps.triage.esi_logic import sugerir_nivel_esi

def crear_triage_view(request):
    # ...
    nivel_sugerido, justificacion = sugerir_nivel_esi(
        signos_vitales={
            'presion_sistolica': 160,
            'frecuencia_cardiaca': 95,
            'saturacion_o2': 95,
            # ...
        },
        dolor_eva=6,
        glasgow=15,
        via_aerea='permeable',
        motivo=motivo_consulta
    )
    
    # Mostrar sugerencia al enfermero
    context['nivel_sugerido'] = nivel_sugerido
    context['justificacion'] = justificacion
```

---

## 6. Interfaz de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│  TRIAGE - García, Juan (DNI: 30.555.444)      Ingreso: 10:35│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ─── Motivo de Consulta ────────────────────────────────────│
│  [                                                         ] │
│  [                                                         ] │
│                                                              │
│  ─── Signos Vitales ────────────────────────────────────────│
│  PA: [___]/[___] mmHg    FC: [___] lpm    T°: [____] °C    │
│  SatO2: [___] %          FR: [___] rpm                      │
│                                                              │
│  ─── Evaluación ────────────────────────────────────────────│
│  Dolor (EVA 0-10): [▼ 0]    Glasgow: [▼ 15]                │
│  Vía Aérea: (●) Permeable  ( ) Comprometida  ( ) Obstruida │
│                                                              │
│  ─── Nivel ESI ─────────────────────────────────────────────│
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │
│  │  1  │ │  2  │ │  3  │ │  4  │ │  5  │                   │
│  │ 🔴  │ │ 🟠  │ │ 🟡  │ │ 🟢  │ │ 🔵  │                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                   │
│                                                              │
│  💡 Sugerencia: ESI 3 (Dolor moderado-severo)               │
│                                                              │
│  Observaciones: [__________________________________________]│
│                                                              │
│                          [Cancelar]  [Guardar Triage]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. API Endpoints

### 7.1 Crear Triage

```
POST /api/v1/visitas/{visita_id}/triage/

Body:
{
  "nivel_esi": 3,
  "motivo_consulta": "Dolor torácico opresivo de 2 horas de evolución",
  "presion_sistolica": 160,
  "presion_diastolica": 95,
  "frecuencia_cardiaca": 95,
  "temperatura": 36.5,
  "saturacion_o2": 95,
  "frecuencia_respiratoria": 20,
  "dolor_eva": 6,
  "glasgow": 15,
  "via_aerea": "permeable",
  "observaciones": "Paciente ansioso, refiere antecedentes de HTA"
}

Response (201):
{
  "id": 789,
  "visita_id": 456,
  "nivel_esi": 3,
  "color_esi": "yellow",
  "enfermero": "López, María",
  "timestamp": "2026-04-28T10:45:00Z",
  ...
}
```

### 7.2 Sugerir Nivel ESI

```
POST /api/v1/triage/sugerir-esi/

Body:
{
  "presion_sistolica": 160,
  "frecuencia_cardiaca": 95,
  "saturacion_o2": 95,
  "dolor_eva": 6,
  "glasgow": 15,
  "via_aerea": "permeable"
}

Response (200):
{
  "nivel_sugerido": 3,
  "justificacion": "Dolor moderado-severo (EVA 4-7)",
  "color": "yellow"
}
```

---

## 8. Validaciones

Ver [`contracts.md`](../contracts.md) sección 5.2 para rangos de signos vitales.

**Validaciones adicionales:**
- Un `Triage` por `VisitaEmergencia` (OneToOne)
- Solo enfermeros y médicos pueden crear triage
- Visita debe estar en estado "esperando_triage"
- Al guardar, visita pasa a "esperando_atencion"

---

## 9. Transiciones de Estado

```
VisitaEmergencia.estado:

[Creación] → esperando_triage
           ↓ [Guardar triage]
        esperando_atencion
           ↓ [Médico inicia atención]
        en_atencion
           ↓ [Médico finaliza con destino]
        finalizado
```

---

## 10. Dependencias

**Requiere:**
- Core (autenticación, permisos)
- Pacientes (VisitaEmergencia vinculada a Paciente)

**Usado por:**
- Dashboard (muestra nivel ESI en lista de espera)
- Reportes (distribución de niveles ESI)

---

## 11. Tests

```python
def test_sugerir_esi_nivel_2_por_saturacion():
    nivel, just = sugerir_nivel_esi(
        {'saturacion_o2': 88},
        dolor_eva=0,
        glasgow=15,
        via_aerea='permeable',
        motivo=''
    )
    assert nivel == 2
    assert 'Saturación O2 < 90%' in just

def test_crear_triage_cambia_estado_visita():
    visita = VisitaEmergencia.objects.create(...)
    assert visita.estado == 'esperando_triage'
    
    Triage.objects.create(visita=visita, nivel_esi=3, ...)
    visita.refresh_from_db()
    assert visita.estado == 'esperando_atencion'
```

---

## 12. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md)
- **ESI Algorithm**: https://www.esitriage.org/

---

*Especificación del módulo Triage - Sistema de Recepción de Pacientes en Emergencias*
