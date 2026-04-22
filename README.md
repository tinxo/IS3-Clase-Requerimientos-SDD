# IS3-ACI - Requerimientos con SDD

Repositorio utilizado en clase para implementar SDD para un proyecto.

El escenario es una gestión de la recepción de pacientes para hacer triage en un área de Emergencias de una Clínica (clase inicial). Posteriormente se amplió a generar más módulos (ver `tmp/modulos.md`) para el proyecto para que sea una solución más general para la Clínica y segmentar los archivos generados (clase final del tema).

Los archivos disponibles se detallan a continuación:
- `chat-claude-ai` contiene un archivo de sepcs generado desde la interfaz web de Claude sobre este escenario. El stack está más vinculado a TS.
- `opencode-plan-mode` contiene un archivo de specs generado utilizando plan mode con OpenCode sobre el mismo escenario. El stack está más vinculado a Python.

En la clase final del tema se plantea la generación de un archivo `projects.md` y `contracts.md` para que ciertos aspectos de la solución no sean re-implementados en cada spec. Se movieron contenidos a esos archivos y se generó un nuevo archivo de specs para un módulo individual como es el de `turnos/spec_turnos.md`. Estos contenidos están basados en la spec generada por Claude por eso la selección tecnológica.

El archivo de `steps.md` plantea los pasos a seguir para la implementación del TP2.