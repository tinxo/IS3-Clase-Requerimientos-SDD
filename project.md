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

Backend (estructura interna de cada módulo)

```
src/
  controllers/    ← Recibe requests HTTP, delega, devuelve respuestas
  services/       ← Lógica de negocio (nunca en controllers)
  repositories/   ← Acceso a la base de datos vía Prisma
  routes/         ← Definición de endpoints y asignación de middlewares
  middlewares/    ← Validación de esquemas con Zod
```

Frontend (estructura compartida)

```
src/
  pages/          ← Una página por flujo principal
  components/     ← Componentes reutilizables (formularios, tablas, badges)
  services/       ← Funciones fetch para llamar a la API
  hooks/          ← Custom hooks por dominio (ej: useTurnos, usePaciente)
```

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

Códigos HTTP estándar

| Código | Cuándo usarlo |
|--------|---------------|
| 200 | Operación exitosa (GET, PATCH, PUT) |
| 201 | Recurso creado (POST) |
| 400 | Error de validación de formato o campos |
| 404 | Recurso no encontrado |
| 409 | Conflicto de unicidad (ej: DNI duplicado activo) |
| 422 | Error de lógica de negocio (ej: transición de estado inválida) |
| 500 | Error interno del servidor |

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

Medico

model Medico {
  id            Int      @id @default(autoincrement())
  nombre        String
  apellido      String
  matricula     String   @unique
  especialidad  String
  telefono      String?
  email         String?
  creadoEn      DateTime @default(now())
  actualizadoEn DateTime @updatedAt
}


7. Roles del sistema

Los roles que existen en el sistema. Cada módulo define en su spec qué acciones puede realizar cada rol dentro de ese módulo.

| Rol | Descripción |
|-----|-------------|
| Recepcionista | Registra ingresos y gestiona turnos |
| Enfermero | Realiza evaluaciones de triage |
| Médico | Atiende pacientes, emite diagnósticos y cierres |
| Administrador | Acceso completo al sistema |

Para esta práctica: el rol se selecciona en una pantalla simple al entrar al sistema. Sin autenticación real ni JWT.

8. Dependencias aprobadas

