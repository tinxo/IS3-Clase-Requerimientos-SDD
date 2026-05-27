# Especificación del Módulo Atención Médica

**Módulo:** `apps/atencion/`  
**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Responsable:** Documentación de la atención médica

---

## 1. Objetivos

Documentar la **atención médica completa** del paciente:

- Registrar nota de evolución médica
- Codificar diagnósticos según CIE-10
- Solicitar estudios complementarios
- Prescribir medicamentos
- Definir destino del paciente (alta, internación, derivación, etc.)
- Completar el flujo de atención en emergencias

---

## 2. Casos de Uso

### 2.1 Iniciar Atención
**Actor:** Médico  
**Flujo:**
1. Médico selecciona paciente en "esperando_atencion"
2. Sistema muestra datos: paciente, triage, antecedentes, visitas previas
3. Médico inicia atención → estado cambia a "en_atencion"

### 2.2 Documentar Atención
**Actor:** Médico  
**Flujo:**
1. Registrar nota de evolución (anamnesis, examen físico, impresión)
2. Buscar y agregar diagnósticos CIE-10 (al menos 1 principal)
3. Solicitar estudios si necesario (marcar urgentes)
4. Prescribir medicamentos si necesario
5. Definir destino del paciente
6. Finalizar atención → estado cambia a "finalizado"

---

## 3. Modelos

Ver [`contracts.md`](../contracts.md) para definición completa de:
- `Atencion`
- `Diagnostico`
- `SolicitudEstudio`
- `Prescripcion`

### 3.1 Destinos Posibles

| Destino | Descripción | Requiere Detalle |
|---------|-------------|------------------|
| **Alta médica** | Paciente se retira sin necesidad de internación | No |
| **Internación** | Paciente ingresa a servicio de internación | Sí (servicio, cama) |
| **Derivación** | Paciente es derivado a otra institución | Sí (institución, motivo) |
| **Cirugía** | Paciente pasa a quirófano | Sí (tipo de cirugía) |
| **Observación** | Paciente queda en observación | Sí (tiempo estimado) |
| **Óbito** | Fallecimiento del paciente | Sí (certificado) |
| **Fuga** | Paciente abandona sin alta | Sí (circunstancias) |

---

## 4. Integración con CIE-10

### 4.1 Dataset de Códigos

**Fuente:** OMS - Clasificación Internacional de Enfermedades, 10ª revisión

**Implementación:**
```python
# Opción 1: Tabla en BD
class CodigoCIE10(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=500)
    capitulo = models.CharField(max_length=200)
    
# Opción 2: Archivo JSON estático
# static/data/cie10.json
```

### 4.2 Autocompletado en UI

```javascript
// Usando HTMX o Select2
<input 
  type="text" 
  hx-get="/api/v1/cie10/?search={query}" 
  hx-trigger="keyup changed delay:500ms" 
  hx-target="#diagnosticos-sugeridos"
  placeholder="Buscar diagnóstico..."
/>
```

---

## 5. Interfaz de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│  ATENCIÓN MÉDICA - García, Juan            Triage: ESI 2 🟠 │
│  DNI: 30.555.444 | 45 años | M              Espera: 12 min  │
├─────────────────────────────────────────────────────────────┤
│ [Datos] [Triage] [Antecedentes] [Visitas Anteriores]        │
├─────────────────────────────────────────────────────────────┤
│  ─── Nota de Evolución ─────────────────────────────────────│
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Paciente consulta por dolor torácico opresivo de     │   │
│  │ 2hs de evolución. Irradia a brazo izquierdo.         │   │
│  │ Antecedentes: HTA. Medicación: Enalapril.            │   │
│  │ EF: TA 160/95, FC 95, lúcido, orientado.             │   │
│  │ AC: rítmico, sin soplos. AP: murmullo vesicular      │   │
│  │ conservado.                                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ─── Diagnósticos (CIE-10) ─────────────────────────────────│
│  [Buscar diagnóstico...              ] [+ Agregar]          │
│  • I20.0 - Angina inestable (Principal)         [x]         │
│  • I10 - Hipertensión esencial                  [x]         │
│                                                              │
│  ─── Estudios Solicitados ──────────────────────────────────│
│  Tipo: [▼ ECG           ] [Descripción...] [+]              │
│  • ECG: 12 derivaciones                  [Urgente ✓] [x]    │
│  • Laboratorio: Enzimas cardíacas        [Urgente ✓] [x]    │
│                                                              │
│  ─── Prescripciones ────────────────────────────────────────│
│  [+ Agregar medicamento]                                     │
│  • AAS 100mg - VO - Stat                         [x]        │
│  • Atorvastatina 40mg - VO - 1 vez/día x 30 días [x]        │
│                                                              │
│  ─── Destino ───────────────────────────────────────────────│
│  ( ) Alta  (●) Internación  ( ) Derivación  ( ) Observación│
│  Detalle: [Unidad Coronaria - Cama 3                    ]   │
│                                                              │
│                      [Guardar Borrador]  [Finalizar]        │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. API Endpoints

### 6.1 Iniciar Atención

```
POST /api/v1/visitas/{visita_id}/atencion/

Body:
{
  "fecha_inicio": "2026-04-28T11:00:00Z"
}

Response (201):
{
  "id": 123,
  "visita_id": 456,
  "medico": {
    "id": 5,
    "nombre_completo": "Dr. García, Juan",
    "matricula": "MN 123456"
  },
  "fecha_inicio": "2026-04-28T11:00:00Z",
  "nota_evolucion": "",
  "diagnosticos": [],
  "estudios": [],
  "prescripciones": []
}
```

### 6.2 Actualizar Atención

```
PUT /api/v1/atenciones/{atencion_id}/

Body:
{
  "nota_evolucion": "Paciente consulta por dolor torácico...",
  "destino": "internacion",
  "destino_detalle": "Unidad Coronaria - Cama 3"
}

Response (200):
{
  "id": 123,
  ...
}
```

### 6.3 Agregar Diagnóstico

```
POST /api/v1/atenciones/{atencion_id}/diagnosticos/

Body:
{
  "codigo_cie10": "I20.0",
  "descripcion": "Angina inestable",
  "es_principal": true
}

Response (201):
{
  "id": 789,
  "atencion_id": 123,
  "codigo_cie10": "I20.0",
  "descripcion": "Angina inestable",
  "es_principal": true
}
```

### 6.4 Solicitar Estudio

```
POST /api/v1/atenciones/{atencion_id}/estudios/

Body:
{
  "tipo": "ecg",
  "descripcion": "ECG de 12 derivaciones",
  "urgente": true
}

Response (201):
{
  "id": 456,
  ...
}
```

### 6.5 Prescribir Medicamento

```
POST /api/v1/atenciones/{atencion_id}/prescripciones/

Body:
{
  "medicamento": "Aspirina",
  "dosis": "100mg",
  "via": "VO",
  "frecuencia": "Stat (dosis única)",
  "duracion": "",
  "indicaciones": "Administrar de inmediato"
}

Response (201):
{
  "id": 321,
  ...
}
```

### 6.6 Buscar Códigos CIE-10

```
GET /api/v1/cie10/?search=angina

Response (200):
{
  "results": [
    {
      "codigo": "I20.0",
      "descripcion": "Angina inestable"
    },
    {
      "codigo": "I20.1",
      "descripcion": "Angina de pecho con espasmo coronario documentado"
    },
    {
      "codigo": "I20.8",
      "descripcion": "Otras formas de angina de pecho"
    }
  ]
}
```

### 6.7 Finalizar Atención

```
POST /api/v1/atenciones/{atencion_id}/finalizar/

Body:
{
  "fecha_fin": "2026-04-28T12:30:00Z"
}

Response (200):
{
  "id": 123,
  "fecha_fin": "2026-04-28T12:30:00Z",
  "visita": {
    "id": 456,
    "estado": "finalizado",
    "fecha_egreso": "2026-04-28T12:30:00Z"
  }
}
```

---

## 7. Validaciones

**Antes de finalizar atención:**
- [ ] Nota de evolución no vacía
- [ ] Al menos 1 diagnóstico principal
- [ ] Destino definido
- [ ] Destino con detalle (si aplica)

**Reglas de negocio:**
- Solo 1 diagnóstico puede ser principal
- Una atención por visita (OneToOne)
- Solo médicos pueden crear atenciones
- Visita debe estar en "esperando_atencion" o "en_atencion"

---

## 8. Transiciones de Estado

```
VisitaEmergencia.estado:

esperando_atencion
  ↓ [POST /atencion/]
en_atencion
  ↓ [POST /atencion/{id}/finalizar/]
finalizado
```

---

## 9. Dependencias

**Requiere:**
- Core (autenticación, permisos)
- Pacientes (datos del paciente, antecedentes)
- Triage (ver datos de triage previo)
- Dataset CIE-10

**Usado por:**
- Reportes (diagnósticos frecuentes, productividad médica)

---

## 10. Tests

```python
def test_crear_atencion():
    visita = VisitaEmergencia.objects.create(estado='esperando_atencion', ...)
    atencion = Atencion.objects.create(visita=visita, medico=medico, ...)
    assert visita.estado == 'en_atencion'

def test_requiere_diagnostico_principal():
    atencion = Atencion.objects.create(...)
    Diagnostico.objects.create(atencion=atencion, es_principal=False, ...)
    
    with pytest.raises(ValidationError):
        atencion.finalizar()  # Falta diagnóstico principal

def test_finalizar_atencion_cambia_estado():
    atencion = Atencion.objects.create(...)
    atencion.finalizar(destino='alta_medica')
    assert atencion.visita.estado == 'finalizado'
```

---

## 11. Referencias

- **Proyecto**: [`project.md`](../project.md)
- **Contratos**: [`contracts.md`](../contracts.md)
- **CIE-10**: https://www.who.int/standards/classifications/classification-of-diseases

---

*Especificación del módulo Atención - Sistema de Recepción de Pacientes en Emergencias*
