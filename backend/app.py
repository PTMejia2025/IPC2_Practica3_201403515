# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
import re

from data.xml_tienda import (
    init_all, add_recurso, add_categoria, add_config,
    add_cliente, add_instancia
)
from models.entidades import parse_float

app = Flask(__name__)
CORS(app)

DATE_RX = re.compile(r'(\b\d{2}/\d{2}/\d{4}\b)')
NIT_RX = re.compile(r'^\d+-([0-9]|K)$', re.IGNORECASE)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/init", methods=["POST"])
def api_init():
    res = init_all()
    return jsonify(res), 200

@app.route("/api/config", methods=["POST"])
def api_config():
    """
    Recibe un archivo XML con secciones:
    <config>
      <recursos>
        <recurso nombre="" tipo="" costo_hora=""/>
      </recursos>
      <categorias>
        <categoria nombre="" descripcion=""/>
      </categorias>
      <configuraciones>
        <configuracion nombre="" categoria="NOMBRE_CATEGORIA" precio_base="">
          <recursos><recurso nombre="..."/></recursos> <!-- por nombre -->
        </configuracion>
      </configuraciones>
      <clientes>
        <cliente nombre="" nit="">
          <instancias>
             <instancia configuracion="NOMBRE_CONFIG" estado="Vigente|Cancelada"
                        fecha_inicio="dd/mm/yyyy" fecha_fin="dd/mm/yyyy?"/>
          </instancias>
        </cliente>
      </clientes>
    </config>
    """
    if "file" not in request.files:
        return jsonify({"error": "Falta archivo XML (file)"}), 400

    xml_file = request.files["file"]
    try:
        tree = ET.parse(xml_file)
    except Exception as e:
        return jsonify({"error": f"XML inválido: {e}"}), 400

    root = tree.getroot()

    # Mapas por nombre -> id para poder referenciar por nombre en el XML de entrada
    nombre_recurso_id = {}
    nombre_categoria_id = {}
    nombre_config_id = {}

    cnt = {"recursos": 0, "categorias": 0, "configuraciones": 0, "clientes": 0, "instancias": 0}
    errores = []

    # --------- Recursos ---------
    for r in root.findall("./recursos/recurso"):
        try:
            nombre = (r.get("nombre") or "").strip()
            tipo = (r.get("tipo") or "").strip()
            costo = parse_float(r.get("costo_hora") or "0")
            if tipo not in ("Hardware", "Software"):
                raise ValueError("tipo debe ser Hardware o Software")
            rid = add_recurso(nombre, tipo, costo)
            nombre_recurso_id[nombre] = rid
            cnt["recursos"] += 1
        except Exception as ex:
            errores.append(f"recurso '{r.get('nombre')}': {ex}")

<<<<<<< HEAD
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
    # actualiza los campos
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
=======
    # --------- Categorías ---------
    for c in root.findall("./categorias/categoria"):
        try:
            nombre = (c.get("nombre") or "").strip()
            descripcion = (c.get("descripcion") or "").strip()
            cid = add_categoria(nombre, descripcion)
            nombre_categoria_id[nombre] = cid
            cnt["categorias"] += 1
        except Exception as ex:
            errores.append(f"categoria '{c.get('nombre')}': {ex}")
>>>>>>> 795109fd4728d28b4643b24318f2ab706c16595f

    # --------- Configuraciones ---------
    for cfg in root.findall("./configuraciones/configuracion"):
        try:
            nombre = (cfg.get("nombre") or "").strip()
            cat_nombre = (cfg.get("categoria") or "").strip()
            precio_base = parse_float(cfg.get("precio_base") or "0")
            if cat_nombre not in nombre_categoria_id:
                raise ValueError(f"categoría '{cat_nombre}' no registrada")
            recursos_elems = cfg.findall("./recursos/recurso")
            recursos_ids = []
            for rr in recursos_elems:
                rn = (rr.get("nombre") or "").strip()
                if rn not in nombre_recurso_id:
                    raise ValueError(f"recurso '{rn}' no registrado")
                recursos_ids.append(nombre_recurso_id[rn])
            cfg_id = add_config(nombre, nombre_categoria_id[cat_nombre], precio_base, recursos_ids)
            nombre_config_id[nombre] = cfg_id
            cnt["configuraciones"] += 1
        except Exception as ex:
            errores.append(f"configuracion '{cfg.get('nombre')}': {ex}")

    # --------- Clientes + Instancias ---------
    for cl in root.findall("./clientes/cliente"):
        try:
            nombre = (cl.get("nombre") or "").strip()
            nit = (cl.get("nit") or "").strip()
            if not NIT_RX.match(nit):
                raise ValueError("NIT no cumple el formato general 0000000-0/K")
            cliente_id = add_cliente(nombre, nit)
            cnt["clientes"] += 1

            for ins in cl.findall("./instancias/instancia"):
                try:
                    cfg_nombre = (ins.get("configuracion") or "").strip()
                    estado = (ins.get("estado") or "Vigente").strip()
                    fecha_inicio = (ins.get("fecha_inicio") or "").strip()
                    fecha_fin = (ins.get("fecha_fin") or "").strip() or None

                    if estado not in ("Vigente", "Cancelada"):
                        raise ValueError("estado inválido (Vigente|Cancelada)")

                    if not DATE_RX.search(fecha_inicio):
                        raise ValueError("fecha_inicio no válida (dd/mm/yyyy)")

                    if estado == "Cancelada" and not (fecha_fin and DATE_RX.search(fecha_fin)):
                        raise ValueError("fecha_fin requerida si estado=Cancelada")

                    if cfg_nombre not in nombre_config_id:
                        raise ValueError(f"configuracion '{cfg_nombre}' no registrada")

                    add_instancia(cliente_id, nombre_config_id[cfg_nombre], estado, fecha_inicio, fecha_fin)
                    cnt["instancias"] += 1
                except Exception as exi:
                    errores.append(f"instancia cliente '{nombre}': {exi}")

        except Exception as exc:
            errores.append(f"cliente '{cl.get('nombre')}': {exc}")

    return jsonify({"cargados": cnt, "errores": errores}), 200

if __name__ == "__main__":
    # python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
