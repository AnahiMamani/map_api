# api_mapa/services/pindorama_service.py

import requests
from api_mapa.config import API_PINDORAMA_URL

def get_artigos():
    #Retorna a lista de artigos do backend Pindorama.
    #Se houver algum erro na requisição, retorna um dict com chave 'erro'.

    try:
        response = requests.get(f"{API_PINDORAMA_URL}/artigos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"erro": str(e)}

def get_eventos():

    #Retorna a lista de eventos do backend Pindorama.
    #Se houver algum erro na requisição, retorna um dict com chave 'erro'.

    try:
        response = requests.get(f"{API_PINDORAMA_URL}/eventos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"erro": str(e)}

def atualizar_artigo(artigo_id, payload):
    try:
        # MUDANÇA AQUI: Usa a rota silenciosa
        url = f"{API_PINDORAMA_URL}/artigos/{artigo_id}/coordenadas" 
        
        response = requests.patch(url, json=payload)
        response.raise_for_status() # Lança exceção para 4xx/5xx
        return {"sucesso": True}
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao fazer PATCH interno para Pindorama: {e}")
        return {"erro": f"Falha no PATCH interno: {e}"}
