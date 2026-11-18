from apps.clientes.models import Cliente
from apps.cuentas.views import custom_login_view
from apps.tenants.models import Profesional
from apps.turnos.models import Turno
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone 
from django.db import models
from apps.turnos.utils import enviar_correo_turno, enviar_whatsapp_turno
import threading
from django.db import connection


def dashboard_profesional(request):
    """Panel principal del profesional"""
    tenant = getattr(request, "tenant", None)

    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            tenant = None

    if not tenant:
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("/admin/")
        return redirect("login")

    clientes = Cliente.objects.filter(profesional=tenant)

    ahora = timezone.now()
    hoy = timezone.localdate()

    turnos = Turno.objects.filter(profesional=tenant).filter(
        models.Q(fecha_hora__date=hoy) |
        models.Q(fecha_hora__gte=ahora)
    ).order_by("fecha_hora")

    dias_restantes = None
    if tenant and tenant.fecha_vencimiento:
        dias_restantes = (tenant.fecha_vencimiento - ahora).days

    context = {
        "tenant": tenant, 
        "clientes": clientes, 
        "turnos": turnos,
        "dias_restantes": dias_restantes  
    }
    return render(request, "turnos/dashboard.html", context)



def crear_cliente(request):
    """Permite al profesional registrar un nuevo paciente/cliente"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return redirect("dashboard_profesional")

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")

        Cliente.objects.create(
            profesional=tenant,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            correo=correo,
        )
        return redirect("dashboard_profesional")

    return render(request, "turnos/crear_cliente.html", {"tenant": tenant})


def crear_turno(request):
    """Permite al profesional agendar un turno para un cliente"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return redirect("dashboard_profesional")

    clientes = Cliente.objects.filter(profesional=tenant)

    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        fecha_hora = request.POST.get("fecha_hora")
        descripcion = request.POST.get("descripcion")

        cliente = get_object_or_404(Cliente, id=cliente_id, profesional=tenant)

        Turno.objects.create(
            profesional=tenant,
            cliente=cliente,
            fecha_hora=fecha_hora,
            descripcion=descripcion,
        )
        return redirect("dashboard_profesional")

    context = {"tenant": tenant, "clientes": clientes}
    return render(request, "turnos/crear_turno.html", context)



def _enviar_notificaciones_background(turno, tipo="creacion"):
    """Ejecuta los envíos en segundo plano sin frenar la respuesta web"""
    try:
        enviar_correo_turno(turno, tipo=tipo)
        enviar_whatsapp_turno(turno, tipo=tipo)
    finally:
        connection.close()


def crear_turno_ajax(request):
    """Vista AJAX para agendar un turno desde el modal del dashboard"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        fecha_hora = request.POST.get("fecha_hora")
        descripcion = request.POST.get("descripcion")

        cliente = get_object_or_404(Cliente, id=cliente_id, profesional=tenant)

        turno_existente = Turno.objects.filter(
            profesional=tenant,
            cliente=cliente,
            fecha_hora=fecha_hora,
            estado__in=["pendiente", "reprogramado"]
        ).first()

        if turno_existente:
            return JsonResponse({
                "success": True,
                "mensaje": "¡Turno agendado correctamente!"
            })

        nuevo_turno = Turno.objects.create(
            profesional=tenant,
            cliente=cliente,
            fecha_hora=fecha_hora,
            descripcion=descripcion,
        )

        threading.Thread(
            target=_enviar_notificaciones_background,
            args=(nuevo_turno,),
            daemon=True
        ).start()

        return JsonResponse({
            "success": True, 
            "mensaje": "¡Turno agendado correctamente!"
        })

    return JsonResponse({"success": False}, status=400)


def crear_cliente_ajax(request):
    """Vista AJAX para crear un cliente rápido desde el modal de turnos"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "No autorizado"}, status=403
            )

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")

        cliente = Cliente.objects.create(
            profesional=tenant,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            correo=correo,
        )

        return JsonResponse({
            "success": True,
            "cliente_id": cliente.id,
            "cliente_texto": f"{cliente.apellido}, {cliente.nombre}",
            "mensaje": "¡Cliente registrado con éxito!"
        })

    return JsonResponse({"success": False}, status=400)


def actualizar_cliente_ajax(request, cliente_id):
    """Vista AJAX para actualizar los datos de un paciente desde el modal"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "No autorizado"}, status=403
            )

    cliente = get_object_or_404(Cliente, id=cliente_id, profesional=tenant)

    if request.method == "POST":
        cliente.nombre = request.POST.get("nombre")
        cliente.apellido = request.POST.get("apellido")
        cliente.telefono = request.POST.get("telefono")
        cliente.correo = request.POST.get("correo")
        cliente.save()

        return JsonResponse({
            "success": True,
            "nombre_completo": f"{cliente.apellido}, {cliente.nombre}",
            "mensaje": "¡Datos del paciente actualizados!"
        })

    return JsonResponse({"success": False}, status=400)



def actualizar_turno_ajax(request, turno_id):
    """Vista AJAX para actualizar un turno completo o solo su estado rápido"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    turno = get_object_or_404(Turno, id=turno_id, profesional=tenant)

    if request.method == "POST":
        estado_anterior = turno.estado
        fecha_anterior = turno.fecha_hora.strftime("%Y-%m-%dT%H:%M")

        nueva_fecha = request.POST.get("fecha_hora")
        nuevo_estado = request.POST.get("estado")

        if nueva_fecha:
            turno.fecha_hora = nueva_fecha
        if "descripcion" in request.POST:
            turno.descripcion = request.POST.get("descripcion")
        if nuevo_estado:
            turno.estado = nuevo_estado

        if turno.estado == "reprogramado" or (nueva_fecha and nueva_fecha != fecha_anterior):
            if hasattr(turno, "recordatorio_enviado"):
                turno.recordatorio_enviado = False

        turno.save()

        tipo_notificacion = None
        if turno.estado == "cancelado" and estado_anterior != "cancelado":
            tipo_notificacion = "cancelado"
        elif (turno.estado == "reprogramado" and estado_anterior != "reprogramado") or (
            nueva_fecha and nueva_fecha != fecha_anterior and turno.estado in ["pendiente", "reprogramado"]
        ):
            tipo_notificacion = "reprogramado"

        if tipo_notificacion:
            threading.Thread(
                target=_enviar_notificaciones_background,
                args=(turno, tipo_notificacion),
                daemon=True
            ).start()

        return JsonResponse({
            "success": True,
            "mensaje": "¡Turno actualizado con éxito!"
        })

    return JsonResponse({"success": False}, status=400)


def eliminar_turno_ajax(request, turno_id):
    """Vista AJAX para eliminar permanentemente un turno erróneo"""
    tenant = getattr(request, "tenant", None)
    if not tenant and request.user.is_authenticated:
        try:
            tenant = Profesional.objects.get(usuario=request.user)
        except Profesional.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "No autorizado"}, status=403
            )

    turno = get_object_or_404(Turno, id=turno_id, profesional=tenant)

    if request.method == "POST":
        turno.delete()
        return JsonResponse({
            "success": True,
            "mensaje": "Turno eliminado correctamente."
        })

    return JsonResponse({"success": False}, status=400)