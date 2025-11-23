# config.py (CORRIGIDO)
import os

# ⚠️ CORREÇÃO AQUI: Usa os.getenv() para carregar a variável de ambiente.
# Se a variável NÃO for encontrada, ele usará o segundo parâmetro como valor padrão.
# Neste caso, usamos a URL do Docker Compose como padrão, o que é seguro para local.

API_PINDORAMA_URL = os.getenv("API_PINDORAMA_URL", "http://api-pindorama-web:3000")

# Recomendado: Imprimir o valor para verificar se está carregando corretamente
print(f"Usando API Pindorama URL: {API_PINDORAMA_URL}")
