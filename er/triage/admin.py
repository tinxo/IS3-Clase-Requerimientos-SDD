from django.contrib import admin
from triage.models import Cobertura, Paciente, VisitaEmergencia, Triage


@admin.register(Cobertura)
class CoberturaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'codigo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'codigo']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['dni', 'apellido', 'nombre', 'fecha_nacimiento', 'edad', 'sexo', 'cobertura', 'activo']
    list_filter = ['sexo', 'activo', 'cobertura']
    search_fields = ['dni', 'nombre', 'apellido']
    readonly_fields = ['created_at', 'updated_at', 'edad']
    fieldsets = (
        ('Datos Personales', {
            'fields': ('dni', 'nombre', 'apellido', 'fecha_nacimiento', 'edad', 'sexo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'telefono_alternativo', 'email', 'direccion', 'localidad', 'provincia', 'codigo_postal')
        }),
        ('Cobertura Médica', {
            'fields': ('cobertura', 'numero_afiliado')
        }),
        ('Metadata', {
            'fields': ('activo', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VisitaEmergencia)
class VisitaEmergenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'fecha_ingreso', 'estado', 'nivel_esi_display', 'tiempo_espera_minutos', 'registrado_por']
    list_filter = ['estado', 'fecha_ingreso']
    search_fields = ['paciente__dni', 'paciente__nombre', 'paciente__apellido', 'motivo_ingreso_breve']
    readonly_fields = ['fecha_ingreso', 'tiempo_espera_minutos']
    raw_id_fields = ['paciente', 'registrado_por']
    
    def nivel_esi_display(self, obj):
        if hasattr(obj, 'triage'):
            return f"{obj.triage.emoji_esi} ESI {obj.triage.nivel_esi}"
        return "Sin triage"
    nivel_esi_display.short_description = "Nivel ESI"


@admin.register(Triage)
class TriageAdmin(admin.ModelAdmin):
    list_display = ['id', 'visita', 'nivel_esi_display', 'dolor_eva', 'glasgow', 'via_aerea', 'enfermero', 'timestamp']
    list_filter = ['nivel_esi', 'via_aerea', 'timestamp']
    search_fields = ['visita__paciente__dni', 'visita__paciente__nombre', 'visita__paciente__apellido', 'motivo_consulta']
    readonly_fields = ['timestamp', 'color_esi', 'nombre_nivel_esi', 'emoji_esi', 'tiempo_objetivo_minutos']
    raw_id_fields = ['visita', 'enfermero']
    
    fieldsets = (
        ('Visita y Clasificación', {
            'fields': ('visita', 'nivel_esi', 'nombre_nivel_esi', 'color_esi', 'emoji_esi', 'tiempo_objetivo_minutos')
        }),
        ('Motivo de Consulta', {
            'fields': ('motivo_consulta', 'observaciones')
        }),
        ('Signos Vitales', {
            'fields': (
                ('presion_sistolica', 'presion_diastolica'),
                ('frecuencia_cardiaca', 'frecuencia_respiratoria'),
                ('temperatura', 'saturacion_o2')
            )
        }),
        ('Evaluación Clínica', {
            'fields': ('dolor_eva', 'glasgow', 'via_aerea')
        }),
        ('Metadata', {
            'fields': ('enfermero', 'timestamp'),
        }),
    )
    
    def nivel_esi_display(self, obj):
        return f"{obj.emoji_esi} ESI {obj.nivel_esi} - {obj.nombre_nivel_esi}"
    nivel_esi_display.short_description = "Nivel ESI"
