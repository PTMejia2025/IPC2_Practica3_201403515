# frontend/supermercado/services.py
import os
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000/api")

def api_health():
    r = requests.get(f"{BACKEND_URL}/health", timeout=30)
    r.raise_for_status()
    return r.json()

def api_init():
    r = requests.post(f"{BACKEND_URL}/init", timeout=60)
    r.raise_for_status()
    return r.json()

def api_config(fileobj):
    files = {"file": fileobj}
    r = requests.post(f"{BACKEND_URL}/config", files=files, timeout=120)
    r.raise_for_status()
    return r.json()
