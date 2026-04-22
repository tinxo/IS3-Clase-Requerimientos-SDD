# spec.md — Módulo: Turnos y Agenda (M2)
 
> **Módulo:** M2 — Turnos y Agenda
> **Responsable:** —
> **Versión:** 1.0 | **Estado:** Borrador | **Última revisión:** 2025-06
>
> **Stack, convenciones y modelos compartidos:** ver `/project.md` — no se repiten acá.
> **Interfaces con otros módulos:** ver `/contracts.md §M2`.

## 1. Objetivo y Contexto
 
### ¿Qué resuelve este módulo?
 
La gestión de turnos programados con médicos de la clínica. Permite que los pacientes
reserven un turno, que la recepción lo confirme o cancele, y que el médico pueda ver
su agenda del día.
 
### Lugar en el sistema
 
Este módulo es el **punto de entrada principal de pacientes nuevos** al sistema.
Cuando un paciente saca un turno por primera vez, se crea su registro en el sistema.
Los demás módulos consultan ese registro pero no lo crean.
 
### Fuera del alcance de este módulo
 
- Videollamadas o teleconsulta
- Recordatorios automáticos por SMS o email (se deja preparado el campo, no se implementa)
- Gestión de vacaciones o licencias del médico
---

## 2. Historias de Usuario y Criterios de Aceptación
 
### HU-01 — Reserva de turno por recepción
 
**Como** recepcionista,
**quiero** buscar turnos disponibles por especialidad o médico y reservar uno para un paciente,
**para que** el paciente tenga un horario confirmado de atención.
 
**Criterios de aceptación:**
 
- [ ] Puedo filtrar turnos por especialidad, por médico específico, o por ambos.
- [ ] El sistema muestra solo los turnos disponibles en los próximos 30 días.
- [ ] Al seleccionar un turno, busco al paciente por DNI. Si no existe, puedo crearlo en el mismo flujo.
- [ ] Un turno reservado deja de aparecer como disponible inmediatamente.
- [ ] Al confirmar la reserva, el sistema muestra un resumen con fecha, hora y médico.
- [ ] No se puede reservar más de un turno activo por paciente con el mismo médico en el mismo día.
---

## 3. Requisitos Funcionales y Reglas de Negocio
 
### 3.1 Validaciones específicas de este módulo
 
| Campo | Regla |
|-------|-------|
| DNI | Solo números, 7 u 8 dígitos (ver también `project.md` — modelo Paciente) |
| Fecha de turno | No puede ser en el pasado |
| Cancelación | No permitida con menos de 1 hora de anticipación |
| Turno duplicado | Un paciente no puede tener dos turnos `PENDIENTE` con el mismo médico el mismo día |
 
### 3.2 Estados de un turno y transiciones válidas
 
```
DISPONIBLE → RESERVADO → REALIZADO
                       → AUSENTE
                       → CANCELADO → DISPONIBLE
```
 
Un turno `CANCELADO` vuelve a estar `DISPONIBLE`. Las demás transiciones son finales.

## 4. Restricciones técnicas específicas de este módulo

> El stack completo está en `/project.md §2`. Acá solo van restricciones adicionales
> que aplican únicamente a este módulo.
 
- La búsqueda de turnos disponibles debe devolver resultados en menos de 500ms.
  Si la consulta es lenta, agregar índice en `(medico_id, fecha, estado)`.
- Los slots de turno se almacenan con fecha y hora en UTC. La conversión a zona horaria
  local se hace en el frontend con `date-fns`.
- No implementar un sistema de recordatorios por ahora, pero el modelo debe tener el campo `emailRecordatorio: Boolean` listo para una implementación futura.

## 5. Modelo de datos de este módulo
 
> Los modelos `Paciente` y `Medico` están en `/project.md §6`. No redefinirlos acá.
> Agregar solo los modelos nuevos al `/prisma/schema.prisma`.
 
```prisma
model Turno {
  id              Int          @id @default(autoincrement())
  medicoId        Int
  medico          Medico       @relation(fields: [medicoId], references: [id])
  pacienteId      Int?
  paciente        Paciente?    @relation(fields: [pacienteId], references: [id])
  fecha           DateTime     // fecha + hora del turno (UTC)
  duracionMinutos Int          @default(20)
  estado          EstadoTurno  @default(DISPONIBLE)
  motivoConsulta  String?
  emailRecordatorio Boolean    @default(false)
  // Metadata de gestión
  reservadoEn     DateTime?
  reservadoPor    String?      // nombre del recepcionista
  canceladoEn     DateTime?
  canceladoPor    String?
  creadoEn        DateTime     @default(now())
 
  @@index([medicoId, fecha, estado])
}
 
enum EstadoTurno {
  DISPONIBLE
  RESERVADO
  REALIZADO
  AUSENTE
  CANCELADO
}
```

## 6. Plan de Tareas
 
> **Instrucción para Claude Code (leer antes de empezar):**
> Implementá las tareas de a una por vez, en el orden indicado.
> Al finalizar cada tarea, completá el **Reporte de cierre** que figura al final de ella
> y escribí la frase de pausa exacta. No avances a la siguiente tarea hasta recibir
> una confirmación explícita del usuario. Si el usuario escribe "continuar", "ok", "aprobado"
> o similar, recién entonces pasás a la tarea siguiente.
 
---
 
### T1 — Modelo de datos y seed
 
**Entregables:**
- Modelo `Turno` agregado al `schema.prisma` compartido sin romper los modelos existentes.
- Migración ejecutada: `prisma migrate dev --name add-turnos`.
- Seed con: 3 médicos de distintas especialidades, 1 paciente existente, turnos generados para los próximos 7 días (mezcla de disponibles, reservados y realizados).

**Reporte de cierre — completar antes de detenerse:**
- Archivos creados o modificados: (listar)
- Resultado de `prisma migrate dev`: (pegar output)
- Resultado de `prisma db seed`: (pegar output)
- Estados de turno presentes en el seed: (listar cuántos de cada tipo)
- Qué NO se implementó en esta tarea que pertenece a tareas siguientes: (describir)
> ⏸ **STOP — T1 completa. Esperando confirmación para continuar con T2.**
 
---

## 7. Estrategia de Verificación
 
Igual que el estándar en `project.md` más estas verificaciones específicas:
 
- [ ] La búsqueda de turnos disponibles responde en menos de 500ms con el índice aplicado.
- [ ] No es posible reservar dos veces el mismo turno (probar concurrencia básica).
- [ ] El seed genera suficientes datos para probar todos los estados del turno.
- [ ] Los turnos se muestran en el huso horario correcto en el frontend.


### Orden de verificación
 
```
T1 (BD + seed) → T2 (API búsqueda/pacientes) → T4 (Frontend reserva)
              → T3 (API reserva/cancelación) → T4 (completar frontend)
              → T6 (API agenda)              → T5 (Frontend agenda)
```
 
---