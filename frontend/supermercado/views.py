# frontend/supermercado/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from . import services

def home(request):
    # Pequeña verificación del backend
    ok = False
    try:
        h = services.api_health()
        ok = h.get("status") == "ok"
    except Exception as e:
        messages.error(request, f"Backend no disponible: {e}")
    return render(request, "supermercado/operaciones.html", {"backend_ok": ok})

@require_http_methods(["POST"])
def init_sistema(request):
    try:
        res = services.api_init()
        messages.success(request, f"Sistema reiniciado: {res.get('message')}")
    except Exception as e:
        messages.error(request, f"Error al inicializar: {e}")
    return redirect("supermercado:home")

@require_http_methods(["GET", "POST"])
def cargar_config(request):
    contexto = {}
    if request.method == "POST":
        f = request.FILES.get("archivo_xml")
        if not f:
            messages.error(request, "Debes adjuntar un archivo XML.")
            return redirect("supermercado:cargar_config")
        try:
            result = services.api_config(f)
            contexto["resultado"] = result
            messages.success(request, "Configuración procesada.")
        except Exception as e:
            messages.error(request, f"Error al procesar XML: {e}")
    return render(request, "supermercado/cargar_config.html", contexto)
