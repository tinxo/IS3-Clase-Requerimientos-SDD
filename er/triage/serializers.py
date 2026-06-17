from rest_framework import serializers
from triage.models import Cobertura, Paciente, VisitaEmergencia, Triage
from triage.esi_logic import sugerir_nivel_esi


class CoberturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobertura
        fields = ['id', 'nombre', 'tipo', 'codigo', 'activo']


class PacienteListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listados."""
    edad = serializers.ReadOnlyField()
    nombre_completo = serializers.ReadOnlyField()
    cobertura = CoberturaSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = ['id', 'dni', 'nombre', 'apellido', 'nombre_completo', 'edad', 'sexo', 'telefono', 'cobertura']


class PacienteSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle y creación."""
    edad = serializers.ReadOnlyField()
    nombre_completo = serializers.ReadOnlyField()
    cobertura = CoberturaSerializer(read_only=True)
    cobertura_id = serializers.PrimaryKeyRelatedField(
        queryset=Cobertura.objects.all(),
        source='cobertura',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Paciente
        fields = [
            'id', 'dni', 'nombre', 'apellido', 'nombre_completo',
            'fecha_nacimiento', 'edad', 'sexo',
            'telefono', 'telefono_alternativo', 'email',
            'direccion', 'localidad', 'provincia', 'codigo_postal',
            'cobertura', 'cobertura_id', 'numero_afiliado',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VisitaEmergenciaSerializer(serializers.ModelSerializer):
    paciente = PacienteListSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=Paciente.objects.all(),
        source='paciente',
        write_only=True
    )
    registrado_por = serializers.StringRelatedField(read_only=True)
    tiempo_espera_minutos = serializers.ReadOnlyField()
    tiene_triage = serializers.SerializerMethodField()

    class Meta:
        model = VisitaEmergencia
        fields = [
            'id', 'paciente', 'paciente_id', 'fecha_ingreso', 'fecha_egreso',
            'estado', 'registrado_por', 'motivo_ingreso_breve',
            'tiempo_espera_minutos', 'tiene_triage'
        ]
        read_only_fields = ['fecha_ingreso', 'registrado_por']

    def get_tiene_triage(self, obj):
        return hasattr(obj, 'triage') and obj.triage is not None

    def create(self, validated_data):
        validated_data['registrado_por'] = self.context['request'].user
        return super().create(validated_data)


class TriageSerializer(serializers.ModelSerializer):
    enfermero = serializers.StringRelatedField(read_only=True)
    color_esi = serializers.ReadOnlyField()
    nombre_nivel_esi = serializers.ReadOnlyField()
    emoji_esi = serializers.ReadOnlyField()
    tiempo_objetivo_minutos = serializers.ReadOnlyField()

    class Meta:
        model = Triage
        fields = [
            'id', 'visita', 'nivel_esi', 'nombre_nivel_esi', 'color_esi', 'emoji_esi',
            'motivo_consulta',
            'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
            'temperatura', 'saturacion_o2', 'frecuencia_respiratoria',
            'dolor_eva', 'glasgow', 'via_aerea',
            'enfermero', 'timestamp', 'observaciones',
            'tiempo_objetivo_minutos',
        ]
        read_only_fields = ['enfermero', 'timestamp']

    def create(self, validated_data):
        validated_data['enfermero'] = self.context['request'].user
        return super().create(validated_data)


class SugerirESISerializer(serializers.Serializer):
    """Serializer para el endpoint de sugerencia de nivel ESI."""
    presion_sistolica = serializers.IntegerField(required=False, allow_null=True)
    presion_diastolica = serializers.IntegerField(required=False, allow_null=True)
    frecuencia_cardiaca = serializers.IntegerField(required=False, allow_null=True)
    temperatura = serializers.DecimalField(max_digits=4, decimal_places=1, required=False, allow_null=True)
    saturacion_o2 = serializers.IntegerField(required=False, allow_null=True)
    frecuencia_respiratoria = serializers.IntegerField(required=False, allow_null=True)
    dolor_eva = serializers.IntegerField(required=False, allow_null=True)
    glasgow = serializers.IntegerField(required=False, allow_null=True)
    via_aerea = serializers.ChoiceField(
        choices=['permeable', 'comprometida', 'obstruida'],
        default='permeable'
    )
    motivo = serializers.CharField(required=False, default='')
