from django.db import models
import re
from django.conf import settings

class SolicitudTurno(models.Model):
    class Categoria(models.TextChoices):
        COMERCIAL = 'comercial', 'Consulta Comercial'
        TECNICA = 'tecnica', 'Consulta Técnica'
        RRHH = 'rrhh', 'Consulta de RRHH'
        GENERAL = 'general', 'Consulta General'

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    vehiculo = models.CharField(max_length=100)
    patente = models.CharField(max_length=10, blank=True)
    servicio = models.CharField(max_length=20)
    fecha = models.DateField()
    horario = models.CharField(max_length=5)
    comentarios = models.TextField(blank=True)
    categoria = models.CharField(max_length=10, choices=Categoria.choices, default=Categoria.GENERAL)

    @classmethod
    def clasificar_comentarios(cls, comentarios):
        palabras = set(re.findall(r'\b\w+\b', comentarios.casefold()))

        if palabras & {'precio', 'costo', 'tarifa', 'compra'}:
            return cls.Categoria.COMERCIAL
        if palabras & {'soporte', 'error', 'problema', 'ayuda'}:
            return cls.Categoria.TECNICA
        if palabras & {'trabajo', 'cv', 'empleo', 'linkedin'}:
            return cls.Categoria.RRHH
        return cls.Categoria.GENERAL

    def __str__(self):
        return f'{self.nombre} - {self.vehiculo} - {self.fecha:%d/%m/%Y}'


class CorreoAutorizado(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class ValidacionCuenta(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codigo_hash = models.CharField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    intentos = models.PositiveSmallIntegerField(default=0)