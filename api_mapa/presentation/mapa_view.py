import folium
import json

from api_mapa.services.pindorama_service import get_artigos
from api_mapa.utils.map_generator_utils import (
    load_geojson,
    darken_color,
    REGIAO_COLORS,
)

def generate_map_object(initial_coords=None):
    """Função que gera um objeto mapa em representação html do Folium.
    Percorre cada artigo e demonstra ele por pop-up no mapa."""
    geojson_data = load_geojson()

    # Buscando os artigos do banco
    artigos_data = get_artigos()

    if "erro" in artigos_data:
        # Se houver erro na requisição (Rails fora do ar), use uma lista vazia ou logue o erro
        print(f"ERRO ao buscar artigos do Pindorama: {artigos_data['erro']}")
        artigos = []
    else:
        # Filtra para coordenadas validas, se for so [] ele ignora tambem
        artigos = [
            artigo for artigo in artigos_data 
            if artigo.get("coordenadas") and len(artigo["coordenadas"]) == 2
        ]

    if initial_coords is None:
        initial_coords = [-14.235, -51.9253]

    brazil_bounds = [[-34.0, -74.0], [5.5, -32.0]]

    m = folium.Map(
        location=initial_coords,
        zoom_start=4,
        tiles="OpenStreetMap",
        min_zoom=4,
        max_zoom=6,
        max_bounds=True,
    )
    m.fit_bounds(brazil_bounds)

    m.get_root().header.add_child(folium.Element('<meta charset="UTF-8">'))

    def style_function(feature):
        regiao = feature["properties"].get("regiao", "default")
        fill_color = REGIAO_COLORS.get(regiao, REGIAO_COLORS["default"])
        return {
            "fillColor": fill_color,
            "color": "#000000",
            "weight": 1,
            "fillOpacity": 0.7,
        }

    def highlight_function(feature):
        regiao = feature["properties"].get("regiao", "default")
        fill_color = REGIAO_COLORS.get(regiao, REGIAO_COLORS["default"])
        return {
            "fillColor": darken_color(fill_color),
            "color": "#000000",
            "weight": 2,
            "fillOpacity": 0.9,
        }

    popup_geojson = folium.GeoJsonPopup(
        fields=["name", "regiao"],
        aliases=["<strong>Estado:</strong> ", "<strong>Região:</strong> "],
        localize=True,
        labels=True,
        parse_html=True,
    )

    geo_layer = folium.GeoJson(
        geojson_data,
        name="Estados do Brasil",
        style_function=style_function,
        highlight_function=highlight_function,
        popup=popup_geojson,
    )
    geo_layer.add_to(m)

    icon_url = "https://leafletjs.com/examples/custom-icons/leaf-orange.png"
    artigos_layer = folium.FeatureGroup(name="Artigos")
    artigos_layer.add_to(m)

    script = f"""
        <script>
            window.artigosFolium = {json.dumps(artigos, ensure_ascii=False)};

            window.enviarArtigoParaReact = function(id) {{
                const artigo = window.artigosFolium.find(a => a.id === id);
                if (!artigo) {{
                    console.error('Artigo não encontrado XD )', id);
                    return;
                }}
                window.top.postMessage({{type: "abrirPopupArtigo", data: artigo}}, "*");
            }};
        </script>
    """
    m.get_root().html.add_child(folium.Element(script))

    for artigo in artigos:
        icon = folium.CustomIcon(icon_url, icon_size=(32, 32), icon_anchor=(16, 32))
        marker = folium.Marker(
            location=artigo["coordenadas"],
            icon=icon,
            tooltip=f"Clique para ver: {artigo['titulo']}",
        )
        marker.add_to(artigos_layer)
        marker._name = f"artigo_marker_{artigo['id']}"

    js_click_handlers = """
    <script>
        setTimeout(() => {
            for (let key in window) {
                if (key.startsWith("artigo_marker_")) {
                    const marker = window[key];
                    if (marker && marker.on) {
                        const id = parseInt(key.replace("artigo_marker_", ""));
                        marker.on("click", function() {
                            enviarArtigoParaReact(id);
                        });
                    }
                }
            }
        }, 500);
    </script>
    """
    m.get_root().html.add_child(folium.Element(js_click_handlers))

    folium.LayerControl().add_to(m)

    return m.get_root()._repr_html_()
