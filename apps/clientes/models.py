from django.db import models
from apps.tenants.models import Profesional


class Cliente(models.Model):
  profesional = models.ForeignKey(
      Profesional, on_delete=models.CASCADE, related_name="clientes"
  )
  nombre = models.CharField(max_length=100)
  apellido = models.CharField(max_length=100)
  telefono = models.CharField(max_length=30)
  correo = models.EmailField(blank=True, null=True)
  creado = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.apellido}, {self.nombre} ({self.profesional.nombre_negocio})"