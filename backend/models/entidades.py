# backend/models/entidades.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --------- Entidades de dominio ---------
@dataclass
class Recurso:
    id: int
    nombre: str
    tipo: str  # "Hardware" | "Software"
    costo_hora: float

@dataclass
class Categoria:
    id: int
    nombre: str
    descripcion: str = ""

@dataclass
class Configuracion:
    id: int
    nombre: str
    categoria_id: int
    # precio_base opcional; si tu PDF no lo usa, déjalo en 0
    precio_base: float = 0.0
    # Recursos asociados a la configuración (recurso_id -> factor/multiplicador si aplica)
    recursos: List[int] = field(default_factory=list)

@dataclass
class Cliente:
    id: int
    nombre: str
    nit: str

@dataclass
class Instancia:
    id: int
    cliente_id: int
    configuracion_id: int
    estado: str  # "Vigente" | "Cancelada"
    fecha_inicio: str  # dd/mm/yyyy
    fecha_fin: Optional[str] = None  # requerido si "Cancelada"

@dataclass
class Consumo:
    id: int
    instancia_id: int
    recurso_id: int
    # horas decimales (1.75 = 1h45m)
    horas: float
    fecha_hora: str  # dd/mm/yyyy hh:mm
    facturado: bool = False  # flag para ciclo de facturación

@dataclass
class LineaFactura:
    id: int
    factura_id: int
    instancia_id: int
    recurso_id: int
    horas: float
    monto: float

@dataclass
class Factura:
    id: int
    numero: str
    cliente_id: int
    nit: str
    fecha: str  # dd/mm/yyyy (último día del rango)
    total: float
    lineas: List[LineaFactura] = field(default_factory=list)

# --------- Utilidades ligeras ---------
DATE_RX = r'(\b\d{2}/\d{2}/\d{4}\b)'
DATETIME_RX = r'(\b\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\b)'

def parse_float(s: str, default: float = 0.0) -> float:
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return default

def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def to_dict(obj) -> Dict[str, Any]:
    if hasattr(obj, "__dict__"):
        d = obj.__dict__.copy()
        # convertir listas de dataclasses
        for k, v in d.items():
            if isinstance(v, list):
                d[k] = [to_dict(x) if hasattr(x, "__dict__") else x for x in v]
        return d
    return obj
