from django.db import models
from apps.clientes.models import Cliente
from apps.tenants.models import Profesional


class Turno(models.Model):
  ESTADOS = [
    ('pendiente', 'Pendiente'),
    ('completado', 'Completado'),
    ('reprogramado', 'Reprogramado'),
    ('ausente', 'Ausente'),
    ('cancelado', 'Cancelado'),
]

  profesional = models.ForeignKey(
      Profesional, on_delete=models.CASCADE, related_name="turnos"
  )
  cliente = models.ForeignKey(
      Cliente, on_delete=models.CASCADE, related_name="turnos"
  )
  fecha_hora = models.DateTimeField()
  descripcion = models.TextField(blank=True, null=True) 
  estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
  creado = models.DateTimeField(auto_now_add=True)
  recordatorio_enviado = models.BooleanField(default=False)
  
  def __str__(self):
    return f"Turno: {self.cliente} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"