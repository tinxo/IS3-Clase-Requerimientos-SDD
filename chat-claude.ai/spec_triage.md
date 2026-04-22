# spec.md — Sistema de Registro de Pacientes en Emergencias

> **Versión:** 1.0  
> **Fecha:** 2025-06  
> **Estado:** Borrador inicial  
> **Stack aprobado:** React + Node.js + PostgreSQL

---

## 1. Objetivo y Contexto

### ¿Qué se está construyendo?

Un sistema web para gestionar el flujo completo de atención en el área de emergencias de una clínica, desde que el paciente llega hasta que recibe el alta o es derivado a otra área.

### ¿Por qué es necesario?

Actualmente el registro se hace en papel o en planillas de Excel, lo que genera demoras, errores de legibilidad y pérdida de información crítica. Se necesita un flujo digital que garantice que ningún paciente pase a atención médica sin haber sido evaluado por triage, y que quede registro completo de cada atención.

### Alcance de esta spec

Cubre tres flujos principales:
1. **Alta del paciente** (registro de ingreso)
2. **Triage** (categorización por gravedad)
3. **Registro de atención** con cierre (alta médica o derivación)

No incluye: sistema de turnos, historia clínica completa, facturación ni módulo de farmacia.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU-01 — Registro de ingreso del paciente

**Como** recepcionista,  
**quiero** registrar los datos básicos de un paciente que llega a emergencias,  
**para que** quede identificado en el sistema y pueda pasar al área de triage.

**Criterios de aceptación:**

- [ ] El formulario solicita: nombre, apellido, DNI, fecha de nacimiento, sexo, y motivo de consulta.
- [ ] El campo DNI acepta únicamente números y debe tener entre 7 y 8 dígitos.
- [ ] El sistema impide registrar dos pacientes activos con el mismo DNI.
- [ ] Al guardar exitosamente, el paciente aparece en la lista de espera de triage con estado `ESPERANDO_TRIAGE`.
- [ ] Si el paciente ya existe en el sistema (mismo DNI), se muestra su historial y se ofrece crear una nueva atención.

---

### HU-02 — Evaluación de triage

**Como** enfermero/a,  
**quiero** registrar la evaluación de triage de un paciente en espera,  
**para** asignarle una prioridad de atención según su estado clínico.

**Criterios de aceptación:**

- [ ] Solo se pueden evaluar pacientes con estado `ESPERANDO_TRIAGE`.
- [ ] El formulario de triage registra: presión arterial (sistólica/diastólica), frecuencia cardíaca, temperatura, saturación de oxígeno, y descripción de síntomas.
- [ ] El enfermero asigna manualmente una de tres prioridades: 🔴 **Rojo** (crítico), 🟡 **Amarillo** (urgente), 🟢 **Verde** (leve).
- [ ] El sistema sugiere automáticamente la prioridad según reglas (ver sección 3), pero el enfermero puede sobrescribirla.
- [ ] Al guardar el triage, el estado del paciente cambia a `EN_ESPERA_MEDICO` y aparece en la cola médica ordenada por prioridad (Rojo primero).
- [ ] Un paciente no puede pasar a atención médica si no tiene triage registrado. **Este control es obligatorio.**

---

### HU-03 — Registro de atención médica

**Como** médico/a,  
**quiero** registrar el diagnóstico y tratamiento del paciente,  
**para** formalizar la atención y definir el cierre del caso.

**Criterios de aceptación:**

- [ ] Solo se pueden atender pacientes con estado `EN_ESPERA_MEDICO`.
- [ ] El formulario registra: diagnóstico (texto libre), tratamiento indicado, y observaciones.
- [ ] Al finalizar la atención, el médico elige obligatoriamente una de dos opciones de cierre:
  - **Alta médica**: el paciente es dado de alta con indicaciones escritas.
  - **Derivación**: se especifica el área destino (ej: cirugía, cardiología, UTI) y se agrega una nota.
- [ ] Al cerrar la atención, el estado del paciente cambia a `ALTA` o `DERIVADO`.
- [ ] El sistema registra la hora de cierre y el nombre del médico que firmó.

---

### HU-04 — Vista del panel de emergencias

**Como** cualquier miembro del equipo,  
**quiero** ver en tiempo real el estado de todos los pacientes activos,  
**para** coordinar la atención sin depender de comunicación verbal.

**Criterios de aceptación:**

- [ ] El panel muestra una tabla con: nombre del paciente, hora de ingreso, prioridad (con color), estado actual, y acciones disponibles según el rol.
- [ ] Los pacientes se ordenan por prioridad (🔴 primero) y, dentro de la misma prioridad, por hora de ingreso.
- [ ] Solo se muestran pacientes con estado activo (`ESPERANDO_TRIAGE`, `EN_ESPERA_MEDICO`).
- [ ] El panel se actualiza sin necesidad de recargar la página (polling cada 30 segundos o WebSocket).

---

## 3. Requisitos Funcionales y Reglas de Negocio

### 3.1 Validaciones de datos

| Campo | Regla |
|-------|-------|
| DNI | Solo números, 7 u 8 dígitos |
| Fecha de nacimiento | No puede ser futura; el paciente debe tener entre 0 y 120 años |
| Presión arterial | Sistólica: 60–250 mmHg; Diastólica: 40–150 mmHg |
| Frecuencia cardíaca | 30–250 bpm |
| Temperatura | 34–42 °C |
| Saturación O₂ | 70–100 % |

### 3.2 Lógica de sugerencia de triage (automática, no obligatoria)

El sistema calcula una sugerencia basada en los signos vitales:

| Condición | Prioridad sugerida |
|-----------|--------------------|
| Saturación O₂ < 90% | 🔴 Rojo |
| Frecuencia cardíaca < 40 o > 150 bpm | 🔴 Rojo |
| Presión sistólica > 180 o < 80 mmHg | 🔴 Rojo |
| Temperatura > 39.5 °C | 🟡 Amarillo |
| Presión sistólica > 140 mmHg | 🟡 Amarillo |
| Saturación O₂ entre 90–94% | 🟡 Amarillo |
| Ninguna condición anterior | 🟢 Verde |

> La sugerencia se muestra visualmente al enfermero pero **no se guarda automáticamente**. El enfermero siempre debe confirmar o modificar la prioridad antes de guardar.

### 3.3 Estados del paciente y transiciones válidas

```
ESPERANDO_TRIAGE → EN_ESPERA_MEDICO → ALTA
                                    → DERIVADO
```

Ninguna transición inversa está permitida. Un paciente en `ALTA` o `DERIVADO` no puede volver a estados previos; para un nuevo ingreso se crea una nueva atención.

### 3.4 Roles y permisos

| Acción | Recepcionista | Enfermero | Médico |
|--------|:---:|:---:|:---:|
| Registrar ingreso | ✅ | ❌ | ❌ |
| Realizar triage | ❌ | ✅ | ❌ |
| Registrar atención y cierre | ❌ | ❌ | ✅ |
| Ver panel general | ✅ | ✅ | ✅ |

> Para esta versión de práctica, el rol se selecciona en una pantalla simple al entrar al sistema (sin autenticación real). La autenticación con JWT queda fuera del alcance.

---

## 4. Restricciones y Decisiones Técnicas

### 4.1 Stack tecnológico (no negociable)

- **Frontend:** React 18 con Vite
- **Backend:** Node.js con Express
- **Base de datos:** PostgreSQL
- **ORM:** Prisma
- **Validaciones:** Zod (tanto en frontend como en backend)
- **Estilos:** Tailwind CSS

### 4.2 Restricciones de dependencias

- **No instalar nuevas librerías** sin acordarlo primero. Si una tarea parece requerir una dependencia adicional, detenerse y consultar.
- Usar `fetch` nativo del navegador para llamadas HTTP (no instalar axios).
- No usar librerías de UI de componentes (no MUI, no Ant Design). Solo Tailwind.

### 4.3 Arquitectura del backend

Seguir un patrón de tres capas:

```
src/
  controllers/    ← Recibe requests HTTP, delega, devuelve respuestas
  services/       ← Lógica de negocio y reglas (triage, validaciones)
  repositories/   ← Acceso a la base de datos vía Prisma
  routes/         ← Definición de endpoints
  middlewares/    ← Validación de esquemas con Zod
```

La lógica de negocio **nunca** va en los controllers. Los controllers solo orquestan.

### 4.4 Estructura del frontend

```
src/
  pages/          ← Una página por flujo (Ingreso, Triage, Atencion, Panel)
  components/     ← Componentes reutilizables (formularios, tabla, badge de prioridad)
  services/       ← Funciones para llamar a la API
  hooks/          ← Custom hooks (ej: usePatients, useTriage)
```

### 4.5 Convenciones

- Nombres de variables y funciones en **camelCase** en JS/TS.
- Nombres de tablas y columnas en la BD en **snake_case**.
- Todos los endpoints devuelven JSON con estructura `{ data, error, message }`.
- Los errores de validación devuelven HTTP 400 con detalle del campo fallido.
- Los errores de negocio (ej: transición inválida de estado) devuelven HTTP 422.

---

## 5. Plan de Tareas

Las tareas se ejecutan **en orden**. No comenzar T2 hasta que T1 esté completa y verificada.

---

### T1 — Modelo de datos y base de datos

**Objetivo:** Definir y crear las tablas en PostgreSQL con Prisma.

**Entregables:**
- Archivo `schema.prisma` con los modelos `Paciente`, `Atencion`, y enumeraciones de estado y prioridad.
- Migración ejecutada exitosamente (`prisma migrate dev`).
- Seed con al menos 3 pacientes en diferentes estados para desarrollo.

**Modelo esperado (referencia, puede ajustarse):**

```prisma
model Paciente {
  id              Int       @id @default(autoincrement())
  dni             String    @unique
  nombre          String
  apellido        String
  fechaNacimiento DateTime
  sexo            String
  creadoEn        DateTime  @default(now())
  atenciones      Atencion[]
}

model Atencion {
  id              Int       @id @default(autoincrement())
  pacienteId      Int
  paciente        Paciente  @relation(fields: [pacienteId], references: [id])
  estado          EstadoAtencion @default(ESPERANDO_TRIAGE)
  motivoConsulta  String
  // Triage
  prioridad       Prioridad?
  presionSistolica Int?
  presionDiastolica Int?
  frecuenciaCardiaca Int?
  temperatura     Float?
  saturacionO2    Int?
  sintomasDescripcion String?
  // Atencion medica
  diagnostico     String?
  tratamiento     String?
  tipoCierre      TipoCierre?
  areaDerivacion  String?
  notasCierre     String?
  // Timestamps
  ingresadoEn     DateTime  @default(now())
  triajeEn        DateTime?
  atendidoEn      DateTime?
  cerradoEn       DateTime?
  medicoNombre    String?
}

enum EstadoAtencion {
  ESPERANDO_TRIAGE
  EN_ESPERA_MEDICO
  ALTA
  DERIVADO
}

enum Prioridad {
  ROJO
  AMARILLO
  VERDE
}

enum TipoCierre {
  ALTA_MEDICA
  DERIVACION
}
```

---

### T2 — API de ingreso de pacientes

**Objetivo:** Crear el endpoint para registrar el ingreso de un nuevo paciente.

**Entregables:**
- `POST /api/atenciones` — Crea paciente (si no existe) y una nueva atención.
- Validación con Zod del body en un middleware.
- Responde 400 si el DNI tiene formato incorrecto.
- Responde 409 si el paciente ya tiene una atención activa.
- Tests unitarios para el service (flujo exitoso + casos de error).

---

### T3 — Formulario de ingreso (frontend)

**Objetivo:** Crear la pantalla de registro de ingreso para el recepcionista.

**Entregables:**
- Página `IngresoPage` con formulario controlado en React.
- Validación en cliente con Zod antes de hacer el fetch.
- Mensajes de error inline por campo.
- Al enviar exitosamente, redirigir al panel general.
- No requiere estilos elaborados, solo funcional con Tailwind básico.

---

### T4 — API de triage

**Objetivo:** Crear el endpoint para registrar el triage de una atención.

**Entregables:**
- `PATCH /api/atenciones/:id/triage` — Actualiza signos vitales, prioridad y cambia estado.
- Validar que la atención exista y esté en estado `ESPERANDO_TRIAGE` (devolver 422 si no).
- El service calcula la sugerencia de prioridad y la incluye en la respuesta, pero guarda la prioridad enviada por el cliente.
- Tests: triage exitoso, intento en estado incorrecto, valores de signos vitales fuera de rango.

---

### T5 — Formulario de triage (frontend)

**Objetivo:** Crear la pantalla de triage para el enfermero.

**Entregables:**
- Página `TriagePage` que carga los datos del paciente y muestra el formulario de signos vitales.
- Al cargar los valores, mostrar visualmente la prioridad sugerida (badge de color).
- El enfermero puede cambiar la prioridad sugerida antes de confirmar.
- Al guardar, actualizar la vista y volver al panel.

---

### T6 — API de atención y cierre

**Objetivo:** Crear los endpoints para registrar la atención médica y cerrar el caso.

**Entregables:**
- `PATCH /api/atenciones/:id/atencion` — Registra diagnóstico y tratamiento (estado pasa a "en atención").
- `PATCH /api/atenciones/:id/cierre` — Registra el cierre con tipo (alta o derivación).
- Validar transiciones de estado. Devolver 422 si la transición no es válida.
- Tests para ambos endpoints.

---

### T7 — Formulario de atención médica (frontend)

**Objetivo:** Crear la pantalla de registro de atención para el médico.

**Entregables:**
- Página `AtencionPage` con formulario de diagnóstico y tratamiento.
- Sección de cierre con selector de tipo (alta / derivación) y campo condicional de área destino.
- Validación: no se puede guardar sin elegir un tipo de cierre.

---

### T8 — Panel general de emergencias

**Objetivo:** Crear la vista central del sistema.

**Entregables:**
- `GET /api/atenciones/activas` — Devuelve atenciones activas ordenadas por prioridad y hora.
- Página `PanelPage` con tabla de pacientes activos.
- Columnas: nombre, hora de ingreso, prioridad (badge de color), estado, acciones.
- Botones de acción según estado: "Ir a triage" o "Atender" (según corresponda).
- Polling automático cada 30 segundos para refrescar.

---

## 6. Estrategia de Verificación

### Por tarea

Cada tarea de API debe incluir tests unitarios que cubran:
1. **Flujo exitoso** (happy path): datos válidos, respuesta correcta.
2. **Error de validación**: datos con formato incorrecto → 400.
3. **Error de negocio**: transición inválida u objeto no encontrado → 422 o 404.

### Checklist de verificación manual (antes de considerar una tarea "hecha")

- [ ] El endpoint responde con la estructura `{ data, error, message }`.
- [ ] Los errores incluyen el campo que falló (no solo un mensaje genérico).
- [ ] Se probó el caso de error más crítico a mano con un cliente REST (ej: Thunder Client).
- [ ] El formulario del frontend muestra errores inline (no `alert()`).
- [ ] No hay `console.log` de debugging en el código entregado.

### Orden de verificación sugerido

```
T1 (BD) → T2 (API ingreso) → T3 (Form ingreso) 
       → T4 (API triage)  → T5 (Form triage)
       → T6 (API cierre)  → T7 (Form médico)
       → T8 (Panel)
```

No avanzar al siguiente paso sin que los tests de la tarea anterior pasen.

---

## 7. Preguntas abiertas / Decisiones pendientes

> Registrar acá todo lo que no está resuelto para no bloquearse. Responder antes de iniciar la tarea correspondiente.

| # | Pregunta | Tarea afectada | Respuesta |
|---|----------|---------------|-----------|
| 1 | ¿Se necesita que el panel muestre pacientes DADOS DE ALTA o solo los activos? | T8 | _pendiente_ |
| 2 | ¿El campo "médico que firma" se tipea o se selecciona de una lista? | T6 | _pendiente_ |
| 3 | ¿Se implementa WebSocket o alcanza con polling para el panel? | T8 | Polling por ahora |

---

*Este documento es la fuente única de verdad para este módulo. Cualquier cambio en requisitos, reglas de negocio o decisiones técnicas debe reflejarse acá antes de modificar código.*