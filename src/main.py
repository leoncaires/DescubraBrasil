from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import unicodedata
import re
import os
from api.openweather_api import obter_clima
from api.tourism_api import buscar_atracoes, buscar_hospedagens

API_RESPONSE_FORMAT = {
    "status": "sucesso|erro",
    "codigo": 200,
    "mensagem": "",
    "dados": {}
}

app = Flask(__name__, static_folder='interface', template_folder='interface')
CORS(app)

# Configurações
app.config['JSON_AS_ASCII'] = False  # Para manter caracteres especiais

# Estados e siglas
ESTADOS = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
    "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará",
    "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima",
    "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
]

SIGLAS_ESTADOS = {
    "ac": "Acre", "al": "Alagoas", "ap": "Amapá", "am": "Amazonas",
    "ba": "Bahia", "ce": "Ceará", "df": "Distrito Federal", "es": "Espírito Santo",
    "go": "Goiás", "ma": "Maranhão", "mt": "Mato Grosso", "ms": "Mato Grosso do Sul",
    "mg": "Minas Gerais", "pa": "Pará", "pb": "Paraíba", "pr": "Paraná",
    "pe": "Pernambuco", "pi": "Piauí", "rj": "Rio de Janeiro", "rn": "Rio Grande do Norte",
    "rs": "Rio Grande do Sul", "ro": "Rondônia", "rr": "Roraima", "sc": "Santa Catarina",
    "sp": "São Paulo", "se": "Sergipe", "to": "Tocantins"
}

CATEGORIAS = [
    "Parques naturais",
    "Litoral",
    "Cultura e história",
    "Museus",
    "Gastronomia"
]

# Palavras-chave para categorias
palavras_chave = {
    "Parques naturais": ["parque", "trilha", "cachoeira", "natureza", "mata", "floresta"],
    "Litoral": ["praias", "litoral", "mar", "costa", "praia"],
    "Cultura e história": ["historia", "cultura", "igreja", "monumento", "centro historico"],
    "Museus": ["museu", "exposicao", "arte"],
    "Gastronomia": ["comida", "culinaria", "restaurante", "gastronomia", "prato tipico"]
}

# Memória para recomendações
recomendacoes = {}

# Carrega os dados


def carregar_dados():
    try:
        caminho_json = os.path.join(app.static_folder, 'dados.json')
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados.json: {str(e)}")
        return {}


dados_recomendacoes = carregar_dados()

# Normalização de texto


def normalizar(texto):
    return unicodedata.normalize('NFD', texto.lower()).encode('ascii', 'ignore').decode('utf-8')

# Interpretador de mensagens


def interpretar_mensagem_ia(mensagem):
    mensagem = normalizar(mensagem)
    resultado = {"estado": None, "categoria": None}

    # Busca por estado
    for sigla, estado_nome in SIGLAS_ESTADOS.items():
        if mensagem == sigla or mensagem == normalizar(estado_nome):
            resultado["estado"] = estado_nome
            break
        elif re.search(rf'\b{sigla}\b', mensagem) or re.search(rf'\b{normalizar(estado_nome)}\b', mensagem):
            resultado["estado"] = estado_nome
            break

    # Tokeniza a mensagem
    mensagem_tokens = re.findall(r'\b\w+\b', mensagem)

    # Busca por palavras-chave de categoria
    for categoria, palavras in palavras_chave.items():
        palavras_normalizadas = [normalizar(p) for p in palavras]
        if any(p in mensagem_tokens for p in palavras_normalizadas):
            resultado["categoria"] = categoria
            break

    # Fallback: nome exato da categoria
    if not resultado["categoria"]:
        for cat in CATEGORIAS:
            if mensagem == normalizar(cat):
                resultado["categoria"] = cat
                break

    return resultado


# Rotas


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/dados.json')
def dados():
    return send_from_directory(app.static_folder, 'dados.json')


@app.route('/mensagem', methods=['POST'])
def mensagem():
    dados = request.get_json()
    mensagem_original = dados.get('mensagem', '').strip()
    mensagem_usuario = normalizar(mensagem_original)
    session_id = dados.get('session_id')

    if not session_id:
        return jsonify({"erro": "Sessão não identificada"}), 400

    # Comando especial: repetir última recomendação
    if mensagem_usuario in ["ultima", "última"]:
        ultima = recomendacoes.get(session_id)
        if not ultima:
            return jsonify({"valor": "Nenhuma recomendação anterior encontrada"})

        estado = ultima["estado"]
        categoria = ultima["categoria"]
        atracoes = dados_recomendacoes.get(estado, {}).get(categoria, [])

        if not atracoes:
            return jsonify({"valor": "Nenhuma atração encontrada para esta recomendação"})

        return jsonify({
            "tipo": "recomendar",
            "valor": {
                "estado": estado,
                "categoria": categoria,
                "titulo": atracoes[0]["nome"],
                "descricao": atracoes[0]["descricao"]
            }
        })

    # Verifica se é estado
    for sigla, nome_estado in SIGLAS_ESTADOS.items():
        if mensagem_usuario == sigla or mensagem_usuario == normalizar(nome_estado):
            return jsonify({"tipo": "estado", "valor": nome_estado})

    # Verifica se é categoria
    for cat in CATEGORIAS:
        if mensagem_usuario == normalizar(cat):
            return jsonify({"tipo": "categoria", "valor": cat})

    # Comandos simples
    if mensagem_usuario in ["menu", "voltar"] or mensagem_usuario.isdigit():
        return jsonify({"valor": mensagem_usuario})

    # Interpretação com IA (reconhece estado e/ou categoria)
    interpretacao = interpretar_mensagem_ia(mensagem_usuario)

    if interpretacao["estado"] and interpretacao["categoria"]:
        estado = interpretacao["estado"]
        categoria = interpretacao["categoria"]
        atracoes = dados_recomendacoes.get(estado, {}).get(categoria, [])

        if atracoes:
            recomendacoes[session_id] = {
                "estado": estado,
                "categoria": categoria
            }
            return jsonify({
                "tipo": "recomendar",
                "valor": {
                    "estado": estado,
                    "categoria": categoria,
                    "titulo": atracoes[0]["nome"],
                    "descricao": atracoes[0]["descricao"]
                }
            })

    elif interpretacao["estado"]:
        # Apenas o estado identificado
        return jsonify({
            "tipo": "estado",
            "valor": interpretacao["estado"]
        })

    elif interpretacao["categoria"]:
        # Apenas a categoria identificada
        return jsonify({
            "tipo": "categoria",
            "valor": interpretacao["categoria"]
        })

    return jsonify({"valor": "Não entendi. Tente mencionar um estado e uma categoria."})


@app.route('/salvar_recomendacao', methods=['POST'])
def salvar_recomendacao():
    dados = request.get_json()
    if not all(key in dados for key in ["session_id", "estado", "categoria"]):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400

    recomendacoes[dados["session_id"]] = {
        "estado": dados["estado"],
        "categoria": dados["categoria"]
    }
    return jsonify({"status": "ok"})


@app.route('/hospedagens_proximas', methods=['GET'])
def hospedagens_proximas():
    try:
        # Validação rigorosa dos parâmetros
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Coordenadas fora do intervalo válido")

    except (TypeError, ValueError) as e:
        return jsonify({
            "status": "erro",
            "codigo": 400,
            "mensagem": "Parâmetros inválidos",
            "detalhes": str(e),
            "ajuda": "Use /hospedagens_proximas?lat=-23.55&lon=-46.63"
        }), 400

    # Busca hospedagens com tratamento de erro
    hospedagens = buscar_hospedagens(lat, lon)

    if hospedagens is None:
        return jsonify({
            "status": "erro",
            "codigo": 502,
            "mensagem": "Serviço temporariamente indisponível"
        }), 502

    if not hospedagens:
        return jsonify({
            "status": "sucesso",
            "codigo": 200,
            "mensagem": "Nenhuma hospedagem encontrada",
            "resultados": []
        }), 200

    return jsonify({
        "status": "sucesso",
        "codigo": 200,
        "resultados": hospedagens
    })


@app.route('/clima_detalhado', methods=['GET'])
def clima_detalhado():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    clima_info = obter_clima(lat, lon)
    if not clima_info:
        return jsonify({"error": "Não foi possível obter dados do clima"}), 500

    # Formatação mais amigável para o chatbot
    resposta = {
        "cidade": clima_info.get('cidade'),
        "condicao": clima_info.get('condicao'),
        "temperatura": f"{clima_info.get('temperatura')}°C",
        "sensacao_termica": f"Sensação térmica de {clima_info.get('sensacao_termica')}°C",
        "faixa_temperatura": f"Mínima de {clima_info.get('temperatura_min')}°C e máxima de {clima_info.get('temperatura_max')}°C",
        "umidade": f"{clima_info.get('umidade')}%",
        "vento": f"{clima_info.get('vento_velocidade')} km/h",
        "icone": clima_info.get('icone'),
        "recomendacao": gerar_recomendacao_clima(clima_info)
    }

    return jsonify(resposta)


def gerar_recomendacao_clima(dados_clima):
    """
    Gera uma recomendação com base nas condições climáticas

    Args:
        dados_clima (dict): Dados formatados do clima

    Returns:
        str: Recomendação baseada no clima
    """
    temperatura = dados_clima.get('temperatura')
    condicao = dados_clima.get('condicao', '').lower()

    if not temperatura:
        return "Confira o clima antes de sair!"

    recomendacoes = []

    if temperatura > 30:
        recomendacoes.append(
            "Está muito quente! Leve roupas leves e use protetor solar.")
    elif temperatura > 20:
        recomendacoes.append(
            "Temperatura agradável. Ótimo para passeios ao ar livre!")
    elif temperatura > 10:
        recomendacoes.append("Está fresco. Leve um casaco.")
    else:
        recomendacoes.append("Está frio! Vista-se bem aquecido.")

    if 'chuva' in condicao:
        recomendacoes.append("Leve um guarda-chuva ou capa de chuva.")
    elif 'sol' in condicao:
        recomendacoes.append(
            "Dias de sol são ótimos para fotos! Não esqueça o óculos de sol.")
    elif 'nublado' in condicao:
        recomendacoes.append(
            "Céu nublado, mas ótimo para caminhadas sem muito calor.")

    return " ".join(recomendacoes)


@app.route('/clima', methods=['GET'])
def clima():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    clima_info = obter_clima(lat, lon)
    if not clima_info:
        return jsonify({"error": "Não foi possível obter dados do clima"}), 500

    return jsonify(clima_info)


@app.route('/atracoes_proximas', methods=['GET'])
def atracoes_proximas():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    atracoes = buscar_atracoes(lat, lon)
    if not atracoes:
        return jsonify({"error": "Nenhuma atração próxima encontrada"}), 404

    return jsonify(atracoes)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
