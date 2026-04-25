# Contracts

Este archivo define las interfaces públicas de cada módulo: qué expone, qué consume, y qué eventos emite. Es un documento vivo que el equipo mantiene en conjunto.

Regla: Si un módulo cambia algo que otro consume, primero actualizar este archivo y acordarlo con el responsable del módulo afectado. Nunca cambiar una interfaz pública de forma unilateral.

## Sección 1 — DTOs compartidos

Un módulo nunca expone el objeto de la BD directamente en su API.
Siempre devuelve un DTO (objeto mapeado) con solo los campos  necesarios.
Los DTOs de esta sección son los acordados para cuando un módulo necesita datos de una entidad que pertenece a otro módulo.

DTO: PacienteResumen
Usado cuando un módulo necesita mostrar datos básicos del paciente.

PacienteResumen {
  id:              number
  dni:             string
  nombre:          string
  apellido:        string
  fechaNacimiento: string   // ISO 8601: "YYYY-MM-DD"
}

MedicoResumen {
  id:          number
  nombre:      string
  apellido:    string
  matricula:   string
  especialidad: string
}

## Sección 2 — Catálogo de endpoints públicos por módulo

M2 — Turnos y Agenda

GET /api/turnos/disponibles?especialidad=&medicoId=&desde=&hasta=
Devuelve turnos disponibles en los próximos 30 días. Usado por el frontend de recepción y potencialmente por M5 (Reportes).

{
  "data": [
    {
      "id": 15,
      "medico": { "...":  "MedicoResumen" },
      "fecha": "2025-07-01T09:00:00Z",
      "duracionMinutos": 20,
      "estado": "DISPONIBLE"
    }
  ],
  "error": null,
  "message": "OK"
}

GET /api/turnos/:id
Detalle de un turno. Puede ser usado por M5 (Reportes).

{
  "data": {
    "id": 15,
    "medico": { "...": "MedicoResumen" },
    "paciente": { "...": "PacienteResumen" },
    "fecha": "2025-07-01T09:00:00Z",
    "duracionMinutos": 20,
    "estado": "RESERVADO",
    "motivoConsulta": "Control de rutina",
    "reservadoEn": "2025-06-20T10:00:00Z"
  },
  "error": null,
  "message": "OK"
}

M1 — Emergencias

GET /api/emergencias/atenciones/activas
Devuelve todas las atenciones en curso. Usado por M5 (Reportes).

{
  "data": [
    {
      "id": 1,
      "paciente": { "...": "PacienteResumen" },
      "estado": "ESPERANDO_TRIAGE",
      "prioridad": null,
      "motivoConsulta": "Dolor abdominal",
      "ingresadoEn": "2025-06-10T14:32:00Z"
    }
  ],
  "error": null,
  "message": "OK"
}

GET /api/emergencias/atenciones/:id
Detalle de una atención. Usado por M3 (Internación) al recibir una derivación.

{
  "data": {
    "id": 1,
    "paciente": { "...": "PacienteResumen" },
    "estado": "DERIVADO",
    "prioridad": "ROJO",
    "diagnostico": "Fractura de cadera",
    "areaDerivacion": "INTERNACION",
    "ingresadoEn": "2025-06-10T14:32:00Z",
    "cerradoEn": "2025-06-10T16:10:00Z"
  },
  "error": null,
  "message": "OK"
}

## Sección 3 — Eventos entre módulos
Los eventos describen qué notifica un módulo cuando algo importante ocurre.

Para la práctica: implementar como llamadas HTTP directas entre backends.
No hacer el call desde el frontend.
En producción real esto sería un message broker (RabbitMQ, Kafka, etc.).


EVT-01: Paciente derivado a Internación
Origen: M1 — cuando se registra cierre con areaDerivacion === "INTERNACION"
Destino: M3
Internación recibe la notificación y pre-carga un formulario de admisión con los datos del paciente y el diagnóstico de emergencias.

// M1 hace POST a:
// POST /api/internacion/admisiones/pre-ingreso
{
  "pacienteId": 42,
  "atencionEmergenciaId": 18,
  "diagnostico": "Fractura de cadera",
  "prioridad": "AMARILLO",
  "notaDerivacion": "Requiere cirugía en las próximas 6hs"
}