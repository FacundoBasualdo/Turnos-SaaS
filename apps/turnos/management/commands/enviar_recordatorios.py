from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.turnos.models import Turno
from apps.turnos.utils import enviar_correo_turno, enviar_whatsapp_turno


class Command(BaseCommand):
    help = "Envía recordatorios por correo y WhatsApp para turnos dentro de las próximas 24 horas"

    def handle(self, *args, **kwargs):
        ahora = timezone.now()
        limite_24hs = ahora + timedelta(hours=24)

        turnos_proximos = Turno.objects.filter(
            estado__in=["pendiente", "reprogramado"],
            recordatorio_enviado=False,
            fecha_hora__gt=ahora,
            fecha_hora__lte=limite_24hs,
        )

        enviados = 0
        for turno in turnos_proximos:
            enviar_correo_turno(turno, tipo="recordatorio")
            enviar_whatsapp_turno(turno, tipo="recordatorio")
            
            turno.recordatorio_enviado = True
            turno.save(update_fields=["recordatorio_enviado"])
            enviados += 1

        self.stdout.write(self.style.SUCCESS(f"Recordatorios procesados: {enviados}"))


    ## 0 * * * * python manage.py enviar_recordatorios
    ## CONFIGURAR EN EL SERVIDOR PARA QUE SE EJECUTE AUTOMÁTICAMENTE CADA DÍA A LAS 8:00 AM