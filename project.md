# Sistema de Recepción de Pacientes en Emergencias

## Proyecto - Visión General

**Versión:** 1.0  
**Fecha:** 28 de Abril de 2026  
**Estado:** Aprobado para desarrollo MVP

---

## 1. Resumen Ejecutivo

Sistema web para la gestión integral de pacientes en un servicio de emergencias, incluyendo registro de pacientes, clasificación de triage mediante el sistema ESI (Emergency Severity Index), y documentación de la atención médica.

### 1.1 Objetivos

- Digitalizar el proceso de admisión de pacientes en emergencias
- Implementar triage ESI de 5 niveles para priorización
- Registrar la atención médica completa
- Proveer visibilidad en tiempo real del estado de la sala de espera
- Cumplir con regulaciones de protección de datos de salud (Ley 25.326)

### 1.2 Alcance del MVP

| Incluido en MVP | Fase 2 (Post-MVP) |
|-----------------|-------------------|
| Registro de pacientes | App móvil React Native |
| Triage ESI | Integración HL7 FHIR |
| Atención médica | Reportes avanzados personalizables |
| Dashboard de espera | WebSockets tiempo real |
| Reportes básicos y KPIs | Notificaciones push |
| Auditoría completa | |

### 1.3 Módulos del Sistema

| Módulo | Descripción | Spec |
|--------|-------------|------|
| **Core** | Autenticación, autorización, auditoría | [`specs/core.md`](./specs/core.md) |
| **Pacientes** | Registro maestro de pacientes | [`specs/pacientes.md`](./specs/pacientes.md) |
| **Triage** | Clasificación ESI de urgencia | [`specs/triage.md`](./specs/triage.md) |
| **Atención** | Documentación de atención médica | [`specs/atencion.md`](./specs/atencion.md) |
| **Dashboard** | Panel de monitoreo en tiempo real | [`specs/dashboard.md`](./specs/dashboard.md) |
| **Reportes** | Estadísticas y KPIs del servicio | [`specs/reportes.md`](./specs/reportes.md) |

---

## 2. Contexto y Restricciones

### 2.1 Contexto Operativo

| Parámetro | Valor |
|-----------|-------|
| Volumen de pacientes | < 50 pacientes/día |
| Usuarios concurrentes | 5-15 usuarios |
| Horario de operación | 24/7 |
| Idioma | Español (Argentina) |
| País | Argentina |

### 2.2 Restricciones Técnicas

| Restricción | Detalle |
|-------------|---------|
| Despliegue | On-premise (servidores propios) |
| RPO (pérdida de datos aceptable) | 24 horas |
| Regulación | Ley 25.326 de Protección de Datos Personales (Argentina) |
| Timeline | MVP en 6-8 semanas |

### 2.3 Restricciones de Negocio

- Sistema crítico para operación del servicio de emergencias
- Downtime inaceptable en horario de operación
- Datos sensibles de salud requieren máxima seguridad
- Interfaz debe ser intuitiva para uso bajo presión
- Rendimiento debe ser ágil (respuesta < 2 segundos)

---

## 3. Stack Tecnológico

### 3.1 Backend

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| Framework | Django | 5.x | MVC robusto, admin incorporado, ORM potente |
| Lenguaje | Python | 3.12+ | Productividad, legibilidad, ecosistema |
| Base de datos | PostgreSQL | 16 | ACID, integridad referencial, JSON support |
| API REST | Django REST Framework | 3.15+ | Estándar de facto para APIs en Django |
| Auditoría | django-auditlog | latest | Auditoría automática de modelos |
| Permisos | django-guardian | latest | Permisos a nivel de objeto |

### 3.2 Frontend Web

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Templates | Django Templates | Integración nativa, SSR |
| Interactividad | HTMX | Interactividad sin JS pesado |
| Componentes reactivos | Alpine.js | Reactividad ligera en componentes |
| CSS Framework | Bootstrap 5 | Diseño responsive, componentes pre-hechos |
| Formularios | django-crispy-forms | Renderizado elegante de forms |

### 3.3 App Móvil (Fase 2)

| Componente | Tecnología |
|------------|------------|
| Framework | React Native |
| Plataformas | iOS, Android |
| Estado | Redux o Context API |
| Navegación | React Navigation |

### 3.4 Integraciones (Fase 2)

| Sistema | Protocolo | Estándar |
|---------|-----------|----------|
| Historia Clínica Electrónica | HL7 FHIR | FHIR R4 |
| Sistema de Facturación | HL7 FHIR | FHIR R4 |

### 3.5 Librerías Auxiliares

| Necesidad | Librería | Uso |
|-----------|----------|-----|
| Reportes PDF | weasyprint o reportlab | Generación de reportes PDF |
| Reportes Excel | openpyxl | Exportación a Excel |
| Validación DNI | Algoritmo custom | Validar DNI argentino |
| CIE-10 | Dataset público | Códigos de diagnósticos |
| Testing | pytest + pytest-django | Tests automatizados |
| Linting | ruff | Linting y formatting |

---

## 4. Arquitectura del Sistema

### 4.1 Diagrama de Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTES                                │
├──────────────┬──────────────┬──────────────────────────────┤
│  Navegador   │  React Native│      Sistemas Externos       │
│  (HTMX)      │  (iOS/Android)│   (HCE, Facturación)        │
└──────┬───────┴──────┬───────┴──────────────┬───────────────┘
       │              │                       │
       └──────────────┼───────────────────────┘
                      │ HTTPS / REST / FHIR
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  Core   │ │Pacientes│ │ Triage  │ │Atención │           │
│  │ (Auth)  │ │         │ │  (ESI)  │ │ Médica  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐                                    │
│  │Dashboard│ │Reportes │                                    │
│  └─────────┘ └─────────┘                                    │
│  ┌─────────────────────────────────────────────┐           │
│  │           API REST (DRF) + FHIR             │           │
│  └─────────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────────┐           │
│  │    Auditoría │ Autenticación │ Permisos     │           │
│  └─────────────────────────────────────────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL 16                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Pacientes │ │ Visitas  │ │Atenciones│ │ Audit    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Estructura del Proyecto Django

```
emergencias/
├── manage.py
├── config/                    # Configuración del proyecto
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py           # Configuración base
│   │   ├── development.py    # Config desarrollo
│   │   └── production.py     # Config producción
│   ├── urls.py               # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── core/                 # Usuarios, autenticación, auditoría
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── audit.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── pacientes/            # Registro y gestión de pacientes
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── triage/               # Clasificación ESI
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── esi_logic.py      # Lógica de sugerencia ESI
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── atencion/             # Atención médica
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── dashboard/            # Panel de monitoreo
│   │   ├── __init__.py
│   │   ├── views.py
│   │   ├── utils.py
│   │   ├── urls.py
│   │   └── tests/
│   └── reportes/             # Estadísticas y reportes
│       ├── __init__.py
│       ├── views.py
│       ├── generators.py
│       ├── exports.py
│       ├── urls.py
│       └── tests/
├── templates/
│   ├── base.html
│   ├── components/
│   ├── pacientes/
│   ├── triage/
│   ├── atencion/
│   ├── dashboard/
│   └── reportes/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/                     # Archivos subidos
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

### 4.3 Flujo de Datos

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  RECEPCIÓN   │────▶│   TRIAGE     │────▶│  ATENCIÓN    │────▶│   DESTINO    │
│              │     │              │     │   MÉDICA     │     │              │
│ - Registro   │     │ - Evaluación │     │ - Evolución  │     │ - Alta       │
│ - Búsqueda   │     │ - Nivel ESI  │     │ - Diagnóstico│     │ - Internación│
│ - Admisión   │     │ - Signos V.  │     │ - Estudios   │     │ - Derivación │
└──────────────┘     └──────────────┘     │ - Recetas    │     └──────────────┘
                                          └──────────────┘

Estado de VisitaEmergencia:
esperando_triage → esperando_atencion → en_atencion → finalizado
```

---

## 5. Roles y Permisos

### 5.1 Definición de Roles

| Rol | Descripción | Cantidad Esperada |
|-----|-------------|-------------------|
| **Recepcionista** | Registra pacientes, gestiona datos demográficos | 2-3 |
| **Enfermero/a de Triage** | Realiza clasificación ESI, registra signos vitales | 2-3 |
| **Médico** | Atiende pacientes, documenta evolución, prescribe | 3-5 |
| **Administrador** | Gestiona usuarios, configuración del sistema | 1-2 |

### 5.2 Matriz de Permisos

| Funcionalidad | Recepcionista | Enfermero | Médico | Admin |
|---------------|:-------------:|:---------:|:------:|:-----:|
| **Pacientes** |
| Registrar nuevo paciente | ✓ | ✓ | ✓ | ✓ |
| Editar datos paciente | ✓ | ✓ | ✓ | ✓ |
| Ver historial de visitas | ✓ | ✓ | ✓ | ✓ |
| Eliminar paciente | ✗ | ✗ | ✗ | ✓ |
| **Triage** |
| Realizar triage | ✗ | ✓ | ✓ | ✓ |
| Modificar triage existente | ✗ | ✓ | ✓ | ✓ |
| **Atención Médica** |
| Iniciar atención | ✗ | ✗ | ✓ | ✓ |
| Registrar evolución | ✗ | ✗ | ✓ | ✓ |
| Solicitar estudios | ✗ | ✗ | ✓ | ✓ |
| Prescribir medicamentos | ✗ | ✗ | ✓ | ✓ |
| Dar destino | ✗ | ✗ | ✓ | ✓ |
| **Dashboard** |
| Ver pacientes en espera | ✓ | ✓ | ✓ | ✓ |
| Ver tiempos de espera | ✓ | ✓ | ✓ | ✓ |
| **Reportes** |
| Ver estadísticas diarias | ✗ | ✓ | ✓ | ✓ |
| Exportar reportes | ✗ | ✗ | ✓ | ✓ |
| Acceder a todos los reportes | ✗ | ✗ | ✗ | ✓ |
| **Administración** |
| Gestionar usuarios | ✗ | ✗ | ✗ | ✓ |
| Ver logs de auditoría | ✗ | ✗ | ✗ | ✓ |
| Configurar sistema | ✗ | ✗ | ✗ | ✓ |

**Implementación**: Ver [`specs/core.md`](./specs/core.md) para detalles de implementación de permisos.

---

## 6. Consideraciones de Infraestructura

### 6.1 Requisitos de Servidor (On-Premise)

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Almacenamiento | 100 GB SSD | 250 GB SSD |
| Sistema Operativo | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| Red | 100 Mbps | 1 Gbps |

### 6.2 Stack de Producción

```
┌─────────────────────────────────────────┐
│              Nginx (Reverse Proxy)       │
│         + SSL Termination (TLS 1.3)      │
└─────────────────┬───────────────────────┘
                  │ :8000
┌─────────────────▼───────────────────────┐
│              Gunicorn                    │
│         (WSGI Application Server)        │
│              4-8 workers                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Django Application             │
└─────────────────┬───────────────────────┘
                  │ :5432
┌─────────────────▼───────────────────────┐
│             PostgreSQL 16                │
│         (con backups diarios)            │
└─────────────────────────────────────────┘
```

### 6.3 Backup y Recuperación

| Tipo | Frecuencia | Retención | Ubicación | Encriptación |
|------|------------|-----------|-----------|--------------|
| Full DB | Diario (02:00 AM) | 30 días | Servidor backup | AES-256 |
| Incremental | Cada 6 horas | 7 días | Local | AES-256 |
| Archivos/Media | Diario | 30 días | Servidor backup | AES-256 |
| Logs de auditoría | Semanal | 10 años | Servidor backup | AES-256 |

**Estrategia de recuperación:**
- RTO (Recovery Time Objective): 4 horas
- RPO (Recovery Point Objective): 24 horas
- Pruebas de restore: Mensual

### 6.4 Monitoreo y Alertas

| Métrica | Herramienta | Umbral de Alerta |
|---------|-------------|------------------|
| Uptime | Uptimerobot / Pingdom | < 99.5% |
| Tiempo de respuesta | New Relic / Sentry | > 2 segundos |
| CPU | Prometheus + Grafana | > 80% |
| RAM | Prometheus + Grafana | > 85% |
| Disco | Prometheus + Grafana | > 90% |
| Errores 500 | Sentry | > 10/hora |

---

## 7. Plan de Implementación

### 7.1 Cronograma MVP (8 Semanas)

```
Semana 1  ████████████████████████████████ Setup y Estructura Base
Semana 2  ████████████████████████████████ Módulo de Pacientes
Semana 3  ████████████████████████████████ Módulo de Triage ESI
Semana 4  ████████████████████████████████ Módulo de Atención Médica
Semana 5  ████████████████████████████████ Dashboard y Lista de Espera
Semana 6  ████████████████████████████████ Reportes Básicos y KPIs
Semana 7  ████████████████████████████████ Testing y Ajustes
Semana 8  ████████████████████████████████ Deploy y Capacitación
```

### 7.2 Hitos y Entregables

| Semana | Hito | Entregable | Criterio de Aceptación |
|--------|------|------------|------------------------|
| 1 | Infraestructura base | Proyecto Django configurado, DB lista | Login funcional, admin accesible |
| 2 | Módulo Pacientes | CRUD de pacientes completo | Registrar y buscar pacientes |
| 3 | Módulo Triage | Triage ESI funcional | Clasificar paciente con nivel ESI |
| 4 | Módulo Atención | Atención médica completa | Documentar atención con diagnóstico |
| 5 | Dashboard | Panel de espera operativo | Ver pacientes en espera ordenados |
| 6 | Reportes | Reportes básicos generados | Exportar resumen diario a Excel/PDF |
| 7 | Testing | Tests pasando, bugs corregidos | > 80% cobertura de tests |
| 8 | Deploy | Sistema en producción | Personal capacitado, sistema operativo |

### 7.3 Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Retraso en obtener dataset CIE-10 | Media | Bajo | Usar subset básico, completar después |
| Dificultad de adopción por usuarios | Media | Alto | Capacitación intensiva, UX simple |
| Bugs críticos en producción | Baja | Alto | Testing exhaustivo, deploy gradual |
| Integración FHIR compleja | Alta | Medio | Dejar para Fase 2 |
| Performance en horas pico | Media | Medio | Indexar DB, cachear queries frecuentes |

---

## 8. Fase 2 (Post-MVP)

Una vez estable el MVP, se pueden agregar las siguientes funcionalidades:

### 8.1 App Móvil React Native (4-6 semanas)

**Funcionalidades:**
- Autenticación
- Dashboard de espera (lectura)
- Registro rápido de pacientes
- Visualización de datos de paciente
- Notificaciones push para médicos (paciente crítico, llamada a consultorio)

**Ventajas:**
- Movilidad para médicos y enfermeros
- Notificaciones en tiempo real
- Acceso desde tablets

### 8.2 Integración HL7 FHIR (4 semanas)

**Recursos FHIR a mapear:**
- `Patient` ↔ `Paciente`
- `Encounter` ↔ `VisitaEmergencia`
- `Condition` ↔ `Diagnostico`
- `Observation` ↔ `Triage` (signos vitales)
- `MedicationRequest` ↔ `Prescripcion`

**Sistemas a integrar:**
- Historia Clínica Electrónica (sincronizar pacientes)
- Sistema de Facturación (enviar atenciones)

### 8.3 Reportes Avanzados (2-3 semanas)

- Generador de reportes personalizable (arrastrar y soltar campos)
- Dashboards con gráficos interactivos (Chart.js o D3.js)
- Exportación programada (envío por email automático)
- Reportes regulatorios automáticos (PAMI, obras sociales)

### 8.4 Tiempo Real (2 semanas)

- WebSockets para dashboard (Django Channels)
- Actualizaciones instantáneas de lista de espera
- Notificaciones en navegador (Web Push API)
- Indicadores visuales de cambios en tiempo real

---

## 9. Glosario

| Término | Definición |
|---------|------------|
| **ESI** | Emergency Severity Index - Sistema de clasificación de triage de 5 niveles utilizado internacionalmente para priorizar la atención en emergencias |
| **Triage** | Proceso de clasificación de pacientes según gravedad y urgencia para priorizar la atención médica |
| **CIE-10** | Clasificación Internacional de Enfermedades, 10ª revisión - Sistema de codificación de diagnósticos médicos |
| **EVA** | Escala Visual Analógica - Método de medición del dolor del 0 (sin dolor) al 10 (dolor máximo) |
| **Glasgow** | Escala de Coma de Glasgow - Sistema de evaluación del nivel de conciencia (3-15 puntos) |
| **LWBS** | Left Without Being Seen - Pacientes que abandonan el servicio sin ser atendidos |
| **Door-to-Doctor** | Tiempo transcurrido desde el ingreso del paciente hasta ser visto por un médico |
| **Door-to-Triage** | Tiempo desde el ingreso hasta la realización del triage |
| **HL7 FHIR** | Fast Healthcare Interoperability Resources - Estándar moderno de interoperabilidad en salud |
| **RPO** | Recovery Point Objective - Máxima pérdida de datos aceptable en caso de falla |
| **RTO** | Recovery Time Objective - Tiempo máximo de recuperación del sistema tras falla |
| **Ley 25.326** | Ley de Protección de Datos Personales de Argentina - Regula el tratamiento de datos sensibles |
| **On-premise** | Infraestructura alojada en servidores propios (no en la nube) |
| **PAMI** | Programa de Atención Médica Integral - Obra social de jubilados en Argentina |

---

## 10. Referencias

### 10.1 Documentos del Proyecto

- **Contratos**: [`contracts.md`](./contracts.md) - Modelos, APIs y convenciones compartidas
- **Especificaciones Modulares**:
  - [`specs/core.md`](./specs/core.md) - Autenticación, autorización, auditoría
  - [`specs/pacientes.md`](./specs/pacientes.md) - Registro de pacientes
  - [`specs/triage.md`](./specs/triage.md) - Clasificación ESI
  - [`specs/atencion.md`](./specs/atencion.md) - Atención médica
  - [`specs/dashboard.md`](./specs/dashboard.md) - Panel de monitoreo
  - [`specs/reportes.md`](./specs/reportes.md) - Reportes y KPIs

### 10.2 Referencias Externas

- **ESI Algorithm**: https://www.esitriage.org/
- **CIE-10**: https://www.who.int/standards/classifications/classification-of-diseases
- **HL7 FHIR**: https://www.hl7.org/fhir/
- **Ley 25.326**: http://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/norma.htm
- **Django Docs**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/

---

## 11. Control de Versiones del Documento

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2026-04-28 | - | Versión inicial tras reestructuración modular |

---

*Documento de visión general del Sistema de Recepción de Pacientes en Emergencias. Para detalles técnicos, consultar [`contracts.md`](./contracts.md) y las especificaciones modulares en [`specs/`](./specs/).*
