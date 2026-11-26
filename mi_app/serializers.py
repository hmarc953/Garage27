from rest_framework import serializers

from .models import SolicitudTurno


class SolicitudTurnoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)

    class Meta:
        model = SolicitudTurno
        fields = (
            'id', 'nombre', 'email', 'telefono', 'vehiculo', 'patente',
            'servicio', 'fecha', 'horario', 'comentarios',
            'categoria', 'categoria_nombre',
        )

class ModeloVehiculoSerializer(serializers.Serializer):
    Make_Name = serializers.CharField()
    Model_Name = serializers.CharField()