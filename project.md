# Project 

Contenido:
- Stack
- Convenciones de código
- estrucra de direcrios (framework generalmente)
- modelos (compartidos o generales)
- dependencias (versiones)
- (si es una API formatos de respuestas y requests)

1. Descripción del sistema
Sistema web para la gestión integral de una clínica mediana. Cubre el flujo completo del paciente: desde la reserva de turno hasta el alta médica, pasando por emergencias, internación y farmacia.

Listado de módulos y la vinculación al archivo de specs

2. Stack tecnológico (no negociable)
   
Estas decisiones aplican a todos los módulos. Ninguna spec puede contradecirlas ni reemplazarlas.
Frontend

Framework: React 18 con Vite
Estilos: Tailwind CSS — sin librerías de componentes (no MUI, no Ant Design, no shadcn)
Validaciones cliente: Zod
HTTP: fetch nativo — no instalar axios ni similares
Routing: React Router v6

Backend

Runtime: Node.js 20 LTS
Framework: Express 4
Validaciones servidor: Zod (en middlewares, no en controllers)
ORM: Prisma 5

Base de datos

Motor: PostgreSQL 15
Esquema compartido: Un solo schema.prisma en /prisma/schema.prisma
Migraciones: prisma migrate dev — nunca modificar la BD directamente

Testing

Framework: Vitest
Cobertura mínima: flujo exitoso + al menos dos casos de error por endpoint

3. Estructura del repositorio

(completar dependiendo de lo anterior)

4. Convenciones de código

Variables y funciones de JS: camelcase. Ejemplo: pacienteId, calcularEmergencia()
Tablas en BD: snake_case. Ejemplo: turnos_medicos

5. Formato estándar de respuestas HTTP

Todos los endpoints tienen que responder con esta estructura:

{
  "data": { },
  "error": null,
  "message": "Operación exitosa"
}

En caso de error:

{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "fields": {
      "dni": "Debe tener entre 7 y 8 dígitos numéricos"
    }
  },
  "message": "Error de validación"
}

6. Modelos de datos compartidos

Estos modelos tienen que ser usados por todos los módulos. Se definen en (el archivo de schema del ORM) y no se deben reimplementar.

Paciente

model Paciente {
  id              Int      @id @default(autoincrement())
  dni             String   @unique
  nombre          String
  apellido        String
  fechaNacimiento DateTime
  sexo            String   // "M" | "F" | "X"
  telefono        String?
  email           String?
  creadoEn        DateTime @default(now())
  actualizadoEn   DateTime @updatedAt
}


7. Roles del sistema

8. Dependencias aprobadas

