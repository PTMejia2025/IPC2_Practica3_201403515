import requests
from django.conf import settings
from django.shortcuts import render, redirect

API = settings.API_BASE_URL


def lista_productos(request):
    try:
        r = requests.get(f"{API}/productos", timeout=5)
        r.raise_for_status()
        productos = r.json()
    except Exception:
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
                return redirect("lista_productos")
            # mostrar error simple en el formulario (sin messages)
            try:
                err = r.json().get("error", "Error desconocido")
            except Exception:
                err = "Error desconocido"
            return render(request, "supermercado/crear_producto.html", {"error": err})
        except Exception as e:
            return render(
                request, "supermercado/crear_producto.html", {"error": str(e)}
            )
    return render(request, "supermercado/crear_producto.html")


def detalle_producto(request, pid):
    try:
        r = requests.get(f"{API}/productos/{pid}", timeout=5)
        if r.status_code == 404:
            return redirect("lista_productos")
        r.raise_for_status()
        p = r.json()
    except Exception:
        return redirect("lista_productos")
    return render(request, "supermercado/detalle_producto.html", {"p": p})


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
                return redirect("lista_productos")
            try:
                err = r.json().get("error", "Error desconocido")
            except Exception:
                err = "Error desconocido"
            # recargar el detalle para completar el form
            detalle = requests.get(f"{API}/productos/{pid}", timeout=5).json()
            return render(
                request,
                "supermercado/actualizar_producto.html",
                {"p": detalle, "error": err},
            )
        except Exception as e:
            try:
                detalle = requests.get(f"{API}/productos/{pid}", timeout=5).json()
            except Exception:
                detalle = {}
            return render(
                request,
                "supermercado/actualizar_producto.html",
                {"p": detalle, "error": str(e)},
            )

    # GET: cargar datos
    try:
        p = requests.get(f"{API}/productos/{pid}", timeout=5).json()
    except Exception:
        p = {}
    return render(request, "supermercado/actualizar_producto.html", {"p": p})


def eliminar_producto(request, pid):
    try:
        requests.delete(f"{API}/productos/{pid}", timeout=5)
    except Exception:
        pass
    return redirect("lista_productos")
