# api_mapa/utils/geo_utils.py

import json
import random
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CITY_BOUNDS_FILE = DATA_DIR / "city_bounds.json"


def obter_limites_da_cidade(local: str):
    """Carrega o bounding box da cidade no arquivo city_bounds.json."""
    if not CITY_BOUNDS_FILE.exists():
        raise FileNotFoundError("Arquivo city_bounds.json não encontrado em /data")

    with open(CITY_BOUNDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get(local)


def gerar_ponto_dentro_da_area(bbox):
    """Gera coordenada aleatória dentro de um bounding box."""
    lat_min, lat_max = bbox["lat_min"], bbox["lat_max"]
    lon_min, lon_max = bbox["lon_min"], bbox["lon_max"]

    lat = random.uniform(lat_min, lat_max)
    lon = random.uniform(lon_min, lon_max)

    return {"lat": round(lat, 6), "lon": round(lon, 6)}


def distancia_entre_pontos(lat1, lon1, lat2, lon2):
    """Distância em quilômetros (Haversine)."""

    R = 6371  # raio da Terra em km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c