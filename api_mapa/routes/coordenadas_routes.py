from flask import Blueprint, request, jsonify
from api_mapa.services.coordenada_service import gerar_coordenada_para_artigo
from api_mapa.services.pindorama_service import get_artigos

coordenadas_bp = Blueprint("coordenadas", __name__)

@coordenadas_bp.route("/gerar", methods=["POST"])
def gerar_coordenada():
    data = request.get_json()

    if not data or "id" not in data:
        return jsonify({"erro": "Campo 'id' do artigo é obrigatório"}), 400

    artigo_id = data["id"]

    # Buscar todos artigos
    artigos = get_artigos()
    if "erro" in artigos:
        return jsonify(artigos), 400

    # Encontrar o artigo específico
    artigo = next((a for a in artigos if a["id"] == artigo_id), None)

    if not artigo:
        return jsonify({"erro": f"Artigo {artigo_id} não encontrado"}), 404

    # Gerar coordenada
    resultado = gerar_coordenada_para_artigo(artigo, artigos)

    if "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({
    "mensagem": "Coordenada gerada com sucesso",
    **resultado
    }), 200

@coordenadas_bp.route("/teste", methods=["GET"])
def testar_conexao():
    artigos = get_artigos()
    return jsonify(artigos)
