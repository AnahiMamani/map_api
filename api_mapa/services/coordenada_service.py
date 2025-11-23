# api_mapa/services/coordenada_service.py

import random
from api_mapa.services.pindorama_service import get_artigos, atualizar_artigo
from api_mapa.utils.geo_utils import (
    obter_limites_da_cidade,
    gerar_ponto_dentro_da_area,
    distancia_entre_pontos
)

DISTANCIA_MIN_KM = 5


def gerar_coordenadas_para_artigos():
    """
    Gera coordenadas para todos os artigos SEM coordenadas.
    Retorna relatório da operação.
    """
    artigos = get_artigos()

    if "erro" in artigos:
        return artigos

    relatorio = {
        "total_artigos": len(artigos),
        "gerados": 0,
        "ignorados": 0,
        "erros": []
    }

    # Agrupa coordenadas já existentes por cidade
    coordenadas_existentes = {}

    for artigo in artigos:
        local = artigo["local"]
        if local not in coordenadas_existentes:
            coordenadas_existentes[local] = []

        if artigo["coordenadas"]:
            lat, lon = artigo["coordenadas"]
            coordenadas_existentes[local].append({"lat": lat, "lon": lon})

    # Gerar coordenadas para quem não tem
    for artigo in artigos:
        if artigo["coordenadas"]:
            relatorio["ignorados"] += 1
            continue

        local = artigo["local"]
        bbox = obter_limites_da_cidade(local)

        if not bbox:
            relatorio["erros"].append({
                "id": artigo["id"],
                "motivo": f"Bounding box não definido para '{local}'"
            })
            continue

        nova_coord = gerar_coordenada_valida(bbox, coordenadas_existentes[local])

        if not nova_coord:
            relatorio["erros"].append({
                "id": artigo["id"],
                "motivo": "Não foi possível gerar coordenada válida"
            })
            continue

        # Salvar nos registros existentes
        coordenadas_existentes[local].append(nova_coord)

        # Enviar PATCH para API Pindorama
        atualizar_artigo(artigo["id"], {
            "coordenadas": [nova_coord["lat"], nova_coord["lon"]]
        })

        relatorio["gerados"] += 1

    return relatorio

def gerar_coordenada_valida(bbox, coords_existentes):
    """
    Gera nova coordenada garantindo:
    - ficar dentro do bounding box
    - não estar a <5km de outra coordenada da mesma cidade
    - não duplicar pontos
    """

    for _ in range(100):  # evita loop infinito
        ponto = gerar_ponto_dentro_da_area(bbox)

        valido = True

        for c in coords_existentes:
            dist = distancia_entre_pontos(
                ponto["lat"], ponto["lon"],
                c["lat"], c["lon"]
            )
            if dist < DISTANCIA_MIN_KM:
                valido = False
                break

        if valido:
            return ponto

    return None

def gerar_coordenada_para_artigo(artigo, artigos):
    
    """
    Gera coordenada para UM artigo específico.
    """
    local = artigo["local"]
    bbox = obter_limites_da_cidade(local)

    if not bbox:
        return {"erro": f"Bounding box não definido para '{local}'"}

    coords_existentes = [
        {"lat": a["coordenadas"][0], "lon": a["coordenadas"][1]}
        for a in artigos
        if a["local"] == local and a["coordenadas"]
    ]

    nova_coord = gerar_coordenada_valida(bbox, coords_existentes)

    if not nova_coord:
        return {"erro": "Não foi possível gerar coordenada válida"}

    # Atualiza
    atualizar_artigo(artigo["id"], {
        "coordenadas": [nova_coord["lat"], nova_coord["lon"]]
    })

    return {
        "id": artigo["id"],
        "local": local,
        "coordenada": nova_coord
    }
