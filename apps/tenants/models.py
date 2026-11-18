from django.conf import settings
from django.db import models
from django.utils import timezone


class Profesional(models.Model):
  usuario = models.OneToOneField(
      settings.AUTH_USER_MODEL, on_delete=models.CASCADE
  )
  nombre_negocio = models.CharField(
      max_length=150
  )  
  subdominio = models.CharField(
      max_length=50, unique=True
  )  
  telefono = models.CharField(max_length=30, blank=True, null=True)

  activo = models.BooleanField(default=True)
  fecha_vencimiento = models.DateTimeField(default=timezone.now)

  creado = models.DateTimeField(auto_now_add=True)

  def esta_activo(self):
    """Verifica si la suscripción sigue vigente"""
    return self.activo and self.fecha_vencimiento >= timezone.now()

  def __str__(self):
    return f"{self.nombre_negocio} ({self.subdominio})"


class PagoSuscripcion(models.Model):
  """Historial de pagos de la suscripción (Mercado Pago)"""

  profesional = models.ForeignKey(
      Profesional, on_delete=models.CASCADE, related_name="pagos"
  )
  monto = models.DecimalField(max_digits=10, decimal_places=2)
  fecha_pago = models.DateTimeField(auto_now_add=True)
  fecha_inicio_vigencia = models.DateTimeField()
  fecha_fin_vigencia = models.DateTimeField()
  id_transaccion_mp = models.CharField(
      max_length=100, unique=True, blank=True, null=True
  )  
  estado = models.CharField(
      max_length=20, default="aprobado"
  )

  def __str__(self):
    return f"Pago de {self.profesional.nombre_negocio} - ${self.monto} ({self.fecha_pago.strftime('%d/%m/%Y')})"