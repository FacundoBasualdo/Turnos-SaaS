from django.http import Http404, HttpResponse
from apps.tenants.models import Profesional


class TenantMiddleware:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if request.path.startswith("/admin/"):
      request.tenant = None
      return self.get_response(request)

    host = request.get_host().split(":")[0]
    parts = host.split(".")

    if "onrender.com" in host or host in ["localhost", "127.0.0.1"]:
      request.tenant = None
    elif len(parts) > 2 or (len(parts) == 2 and parts[1] != "localhost"):
      subdominio = parts[0]

      if subdominio not in ["www", "admin", "localhost"]:
        try:
          tenant = Profesional.objects.get(subdominio=subdominio)

          if not tenant.esta_activo():
            return HttpResponse(
                "<h1>Tu suscripción ha vencido</h1><p>Por favor realiza el"
                " pago para reactivar tu cuenta.</p>",
                status=403,
            )

          request.tenant = tenant
        except Profesional.DoesNotExist:
          raise Http404("El Profesional no existe.")
      else:
        request.tenant = None
    else:
      request.tenant = None

    response = self.get_response(request)
    return response