from datetime import datetime
from django.core.mail import send_mail


def _formatear_fecha(fecha_hora):
    """Convierte string o datetime a formato legible DD/MM/AAAA a las HH:MM"""
    if isinstance(fecha_hora, str):
        try:
            fecha_dt = datetime.fromisoformat(fecha_hora)
        except ValueError:
            fecha_dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
    else:
        fecha_dt = fecha_hora
    return fecha_dt.strftime("%d/%m/%Y a las %H:%M")


def enviar_correo_turno(turno, tipo="creacion"):
    """Envía un correo al cliente según el evento"""
    cliente = turno.cliente
    if not cliente.correo:
        return False

    negocio = turno.profesional.nombre_negocio
    fecha_formateada = _formatear_fecha(turno.fecha_hora)
    motivo = f"\nMotivo: {turno.descripcion}" if turno.descripcion else ""

    if tipo == "creacion":
        subject = f"Turno Agendado - {negocio}"
        message = (
            f"Hola {cliente.nombre},\n\n"
            f"Tu turno con {negocio} ha sido agendado exitosamente para el día {fecha_formateada}.{motivo}\n\n"
            f"¡Te esperamos!"
        )
    elif tipo == "reprogramado":
        subject = f"Turno Reprogramado - {negocio}"
        message = (
            f"Hola {cliente.nombre},\n\n"
            f"Te informamos que tu turno en {negocio} fue reprogramado.\n"
            f"Nueva fecha y hora: {fecha_formateada}.{motivo}\n\n"
            f"Si tenés algún inconveniente con este horario, por favor comunicate con nosotros."
        )
    elif tipo == "cancelado":
        subject = f"Turno Cancelado - {negocio}"
        message = (
            f"Hola {cliente.nombre},\n\n"
            f"Te avisamos que tu turno del día {fecha_formateada} en {negocio} ha sido cancelado.\n\n"
            f"Contactanos cuando quieras volver a agendar."
        )
    elif tipo == "recordatorio":
        subject = f"Recordatorio de tu turno en {negocio}"
        message = (
            f"Hola {cliente.nombre},\n\n"
            f"Te recordamos que tenés un turno agendado para mañana {fecha_formateada} en {negocio}.{motivo}\n\n"
            f"¡Te esperamos!"
        )
    else:
        return False

    try:
        send_mail(subject, message, None, [cliente.correo])
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False


def enviar_whatsapp_turno(turno, tipo="creacion"):
    """Envía un WhatsApp al cliente según el evento"""
    cliente = turno.cliente
    if not cliente.telefono:
        return False

    negocio = turno.profesional.nombre_negocio
    fecha_formateada = _formatear_fecha(turno.fecha_hora)

    if tipo == "creacion":
        mensaje = (
            f"Hola *{cliente.nombre}* 👋, te confirmamos tu turno en "
            f"*{negocio}* para el día *{fecha_formateada}*. ¡Te esperamos!"
        )
    elif tipo == "reprogramado":
        mensaje = (
            f"Hola *{cliente.nombre}* 🔄, te avisamos que tu turno en *{negocio}* "
            f"fue reprogramado para el día *{fecha_formateada}*."
        )
    elif tipo == "cancelado":
        mensaje = (
            f"Hola *{cliente.nombre}* ❌, te informamos que tu turno del "
            f"*{fecha_formateada}* en *{negocio}* fue cancelado."
        )
    elif tipo == "recordatorio":
        mensaje = (
            f"Hola *{cliente.nombre}* ⏰, te recordamos tu turno para mañana "
            f"*{fecha_formateada}* en *{negocio}*."
        )
    else:
        return False

    print(f"\n--- [WHATSAPP API SIMULADOR ({tipo.upper()})] ---")
    print(f"Para: {cliente.telefono} ({cliente.nombre} {cliente.apellido})")
    print(f"Mensaje: {mensaje}")
    print(f"----------------------------------\n")

    return True