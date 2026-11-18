from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from apps.tenants.models import Profesional


def custom_login_view(request):
  """Vista de login personalizada para que los profesionales accedan a su cuenta"""
  error = None

  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)

      if user.is_superuser:
        return redirect("/admin/")

      try:
        profesional = Profesional.objects.get(usuario=user)
        return redirect("dashboard_profesional")
      except Profesional.DoesNotExist:
        error = "Este usuario no tiene un consultorio asociado."
    else:
      error = "Usuario o contraseña incorrectos."

  return render(request, "cuentas/login.html", {"error": error})