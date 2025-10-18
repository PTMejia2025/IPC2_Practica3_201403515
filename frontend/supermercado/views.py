import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

API = settings.API_BASE_URL


def lista_productos(request):
    try:
        r = requests.get(f"{API}/productos", timeout=5)
        r.raise_for_status()
        productos = r.json()
    except Exception as e:
        messages.error(request, f"Error al cargar productos: {e}")
        productos = []
    return render(
        request, "supermercado/lista_productos.html", {"productos": productos}
    )


def crear_producto(request):
    if request.method == "POST":
        payload = {
            "nombre": request.POST.get("nombre"),
            "categoria": request.POST.get("categoria"),
            "descripcion": request.POST.get("descripcion"),
            "precio": request.POST.get("precio"),
            "cantidad": request.POST.get("cantidad"),
            "fecha_vencimiento": request.POST.get("fecha_vencimiento") or None,
        }
        try:
            r = requests.post(f"{API}/productos", json=payload, timeout=5)
            if r.status_code == 201:
                messages.success(request, "Producto creado.")
                return redirect("lista_productos")
            messages.error(request, f"Error al crear: {r.json()}")
        except Exception as e:
            messages.error(request, f"Error de red: {e}")
    return render(request, "supermercado/crear_producto.html")


def actualizar_producto(request, pid):
    if request.method == "POST":
        payload = {
            k: v
            for k, v in {
                "nombre": request.POST.get("nombre"),
                "categoria": request.POST.get("categoria"),
                "descripcion": request.POST.get("descripcion"),
                "precio": request.POST.get("precio"),
                "cantidad": request.POST.get("cantidad"),
                "fecha_vencimiento": request.POST.get("fecha_vencimiento") or None,
            }.items()
            if v not in [None, ""]
        }
        try:
            r = requests.put(f"{API}/productos/{pid}", json=payload, timeout=5)
            if r.ok:
                messages.success(request, "Producto actualizado.")
                return redirect("lista_productos")
            messages.error(request, f"Error al actualizar: {r.text}")
        except Exception as e:
            messages.error(request, f"Error de red: {e}")

    # Cargar datos existentes para el form
    try:
        detalle = requests.get(f"{API}/productos/{pid}", timeout=5).json()
    except Exception:
        detalle = {}
    return render(request, "supermercado/actualizar_producto.html", {"p": detalle})


def eliminar_producto(request, pid):
    try:
        r = requests.delete(f"{API}/productos/{pid}", timeout=5)
        if r.ok:
            messages.success(request, "Producto eliminado.")
        else:
            messages.error(request, f"No se pudo eliminar: {r.text}")
    except Exception as e:
        messages.error(request, f"Error de red: {e}")
    return redirect("lista_productos")
