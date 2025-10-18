# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # habilita CORS para desarrollo

DATA_FILE = os.path.join(os.path.dirname(__file__), "inventario.json")


def cargar():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/productos")
def listar():
    return jsonify(cargar())


@app.post("/productos")
def crear():
    body = request.get_json(force=True)
    req = [
        "nombre",
        "categoria",
        "descripcion",
        "precio",
        "cantidad",
        "fecha_vencimiento",
    ]
    faltantes = [k for k in req if k not in body]
    if faltantes:
        return jsonify({"error": f"Campos requeridos: {faltantes}"}), 400
    if float(body["precio"]) < 0 or int(body["cantidad"]) < 0:
        return (
            jsonify({"error": "precio y cantidad deben ser valores no negativos"}),
            400,
        )

    try:
        float(body["precio"])
        int(body["cantidad"])
        if body["fecha_vencimiento"]:
            datetime.fromisoformat(body["fecha_vencimiento"])
    except Exception:
        return jsonify({"error": "Tipos inválidos (precio/cantidad/fecha)"}), 400

    data = cargar()
    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": body["nombre"],
        "categoria": body["categoria"],
        "descripcion": body["descripcion"],
        "precio": float(body["precio"]),
        "cantidad": int(body["cantidad"]),
        "fecha_vencimiento": body["fecha_vencimiento"] or None,
    }
    data.append(nuevo)
    guardar(data)
    return jsonify(nuevo), 201


@app.get("/productos/<id>")
def detalle(id):
    data = cargar()
    prod = next((p for p in data if p["id"] == id), None)
    if not prod:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify(prod)


@app.put("/productos/<id>")
def actualizar(id):
    body = request.get_json(force=True)
    data = cargar()
    i = next((i for i, p in enumerate(data) if p["id"] == id), None)
    if i is None:
        return jsonify({"error": "No encontrado"}), 404
    # VALIDACION DE VALORES NEGATIVOS ANTES DE GUARDAR
    if "precio" in body and float(body["precio"]) < 0:
        return jsonify({"error": "El precio no puede ser negativo"}), 400
    if "cantidad" in body and int(body["cantidad"]) < 0:
        return jsonify({"error": "La cantidad no puede ser negativa"}), 400
    # actualiza los campos 1u3 ll3tqeon
    for k in [
        "nombre",
        "categoria",
        "descripcion",
        "precio",
        "cantidad",
        "fecha_vencimiento",
    ]:
        if k in body:
            data[i][k] = body[k]
    guardar(data)
    return jsonify(data[i])


@app.delete("/productos/<id>")
def eliminar(id):
    data = cargar()
    n = len(data)
    data = [p for p in data if p["id"] != id]
    if len(data) == n:
        return jsonify({"error": "No encontrado"}), 404
    guardar(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
