# backend/data/xml_tienda.py
import os
import xml.etree.ElementTree as ET
from typing import Tuple, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR  # ya estás en backend/data/

FILES = {
    "recursos": "recursos.xml",
    "categorias": "categorias.xml",
    "configuraciones": "configuraciones.xml",
    "clientes_instancias": "clientes_instancias.xml",
    "consumos": "consumos.xml",
    "facturas": "facturas.xml",
}

ROOTS = {
    "recursos": "recursos",
    "categorias": "categorias",
    "configuraciones": "configuraciones",
    "clientes_instancias": "clientes_instancias",
    "consumos": "consumos",
    "facturas": "facturas",
}

def _full(path_key: str) -> str:
    return os.path.join(DATA_DIR, FILES[path_key])

def _ensure_file(path_key: str) -> None:
    path = _full(path_key)
    if not os.path.exists(path):
        root = ET.Element(ROOTS[path_key])
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

def init_all() -> Dict[str, str]:
    """Reinicia todos los XML con su elemento raíz."""
    for key in FILES:
        path = _full(key)
        if os.path.exists(path):
            os.remove(path)
        _ensure_file(key)
    return {"status": "ok", "message": "XML inicializados"}

def get_tree(path_key: str) -> Tuple[ET.ElementTree, ET.Element]:
    _ensure_file(path_key)
    tree = ET.parse(_full(path_key))
    return tree, tree.getroot()

def save_tree(path_key: str, tree: ET.ElementTree) -> None:
    tree.write(_full(path_key), encoding="utf-8", xml_declaration=True)

def next_id(parent: ET.Element, tag: str = None) -> int:
    """Saca el siguiente id entero buscando atributos id."""
    max_id = 0
    for elem in parent.findall(f".//{tag}" if tag else ".//*"):
        try:
            v = int(elem.get("id", "0"))
            if v > max_id:
                max_id = v
        except Exception:
            pass
    return max_id + 1

# --------- Inserciones simples ---------
def add_recurso(nombre: str, tipo: str, costo_hora: float) -> int:
    tree, root = get_tree("recursos")
    rid = next_id(root, "recurso")
    e = ET.SubElement(root, "recurso", id=str(rid))
    ET.SubElement(e, "nombre").text = nombre
    ET.SubElement(e, "tipo").text = tipo
    ET.SubElement(e, "costo_hora").text = f"{costo_hora}"
    save_tree("recursos", tree)
    return rid

def add_categoria(nombre: str, descripcion: str = "") -> int:
    tree, root = get_tree("categorias")
    cid = next_id(root, "categoria")
    e = ET.SubElement(root, "categoria", id=str(cid))
    ET.SubElement(e, "nombre").text = nombre
    ET.SubElement(e, "descripcion").text = descripcion
    save_tree("categorias", tree)
    return cid

def add_config(nombre: str, categoria_id: int, precio_base: float, recursos: List[int]) -> int:
    tree, root = get_tree("configuraciones")
    cfg_id = next_id(root, "configuracion")
    e = ET.SubElement(root, "configuracion", id=str(cfg_id))
    ET.SubElement(e, "nombre").text = nombre
    ET.SubElement(e, "categoria_id").text = str(categoria_id)
    ET.SubElement(e, "precio_base").text = f"{precio_base}"
    recs = ET.SubElement(e, "recursos")
    for r in recursos:
        ET.SubElement(recs, "recurso_id").text = str(r)
    save_tree("configuraciones", tree)
    return cfg_id

def add_cliente(nombre: str, nit: str) -> int:
    tree, root = get_tree("clientes_instancias")
    # estructura: <clientes_instancias><cliente id=""><nombre/><nit/><instancias/></cliente>...</clientes_instancias>
    cliente = ET.SubElement(root, "cliente")
    cid = next_id(root, "cliente")
    cliente.set("id", str(cid))
    ET.SubElement(cliente, "nombre").text = nombre
    ET.SubElement(cliente, "nit").text = nit
    ET.SubElement(cliente, "instancias")  # vacío
    save_tree("clientes_instancias", tree)
    return cid

def add_instancia(cliente_id: int, configuracion_id: int, estado: str, fecha_inicio: str, fecha_fin: str = None) -> int:
    tree, root = get_tree("clientes_instancias")
    cliente = root.find(f"./cliente[@id='{cliente_id}']")
    if cliente is None:
        raise ValueError("Cliente no existe")
    instancias = cliente.find("./instancias")
    iid = next_id(instancias, "instancia")
    ins = ET.SubElement(instancias, "instancia", id=str(iid))
    ET.SubElement(ins, "configuracion_id").text = str(configuracion_id)
    ET.SubElement(ins, "estado").text = estado
    ET.SubElement(ins, "fecha_inicio").text = fecha_inicio
    if fecha_fin:
        ET.SubElement(ins, "fecha_fin").text = fecha_fin
    save_tree("clientes_instancias", tree)
    return iid

def add_consumo(instancia_id: int, recurso_id: int, horas: float, fecha_hora: str) -> int:
    tree, root = get_tree("consumos")
    cid = next_id(root, "consumo")
    e = ET.SubElement(root, "consumo", id=str(cid))
    ET.SubElement(e, "instancia_id").text = str(instancia_id)
    ET.SubElement(e, "recurso_id").text = str(recurso_id)
    ET.SubElement(e, "horas").text = f"{horas}"
    ET.SubElement(e, "fecha_hora").text = fecha_hora
    ET.SubElement(e, "facturado").text = "false"
    save_tree("consumos", tree)
    return cid
