import requests
from urllib.parse import quote

# Configuração da API
OPENTRIPMAP_API_KEY = "5ae2e3f221c38a28845f05b67dcb916137225bca3ebc5d73127ab338"
BASE_URL = "https://api.opentripmap.com/0.1/en/places/radius"


def buscar_atracoes(lat, lon, raio=5000, limite=5, tipos=None):
    """
    Busca atrações turísticas próximas usando a API OpenTripMap

    Args:
        lat (float): Latitude
        lon (float): Longitude
        raio (int): Raio de busca em metros (padrão: 10km)
        limite (int): Número máximo de resultados (padrão: 5)
        tipos (list): Lista de tipos de lugares (opcional)

    Returns:
        list: Lista de atrações formatadas ou None em caso de erro
    """
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": raio,
        "lon": lon,
        "lat": lat,
        "limit": limite,
        "apikey": OPENTRIPMAP_API_KEY,
        "rate": 2,
        "format": "json"
    }

    if tipos:
        params['kinds'] = ','.join(tipos)

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()

        atracoes = resposta.json()
        return formatar_atracoes(atracoes)

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de atrações: {str(e)}")
        return None


def formatar_atracoes(atracoes):
    """
    Formata os dados das atrações para um formato mais amigável

    Args:
        atracoes (list): Lista de atrações brutas da API

    Returns:
        list: Lista de atrações formatadas
    """
    formatadas = []

    for atracao in atracoes:
        formatada = {
            'nome': atracao.get('name', 'Nome não disponível'),
            'tipo': atracao.get('kinds', 'Tipo não disponível').split(',')[0],
            'distancia': atracao.get('dist', 0),
            'pontuacao': atracao.get('rate', 'Não avaliado'),
            'coordenadas': {
                'lat': atracao.get('point', {}).get('lat'),
                'lon': atracao.get('point', {}).get('lon')
            }
        }

        # Adiciona link para mais informações se disponível
        if 'xid' in atracao:
            formatada['mais_info'] = f"https://opentripmap.com/en/card/{atracao['xid']}"

        formatadas.append(formatada)

    return formatadas


def buscar_hospedagens(lat, lon, raio=5000, limite=10):
    """
    Busca hospedagens com tratamento robusto de erros e validação
    """
    try:
        # Validação das coordenadas
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Coordenadas fora do intervalo válido")

        # Parâmetros da requisição
        params = {
            "lat": lat,
            "lon": lon,
            "radius": raio,
            "limit": limite,
            "apikey": OPENTRIPMAP_API_KEY,
            "format": "json",
            "kinds": "accomodations"  # <-- Corrigido aqui
        }

        # Headers para melhor compatibilidade
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }

        # Requisição com timeout e verificação de SSL
        resposta = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=15,
            verify=True
        )

        # Tratamento de erros HTTP
        resposta.raise_for_status()

        # Processamento da resposta
        dados = resposta.json()

        if not isinstance(dados, list):
            print(f"Resposta inesperada da API: {dados}")
            return []

        # Formatação dos resultados
        resultados = []
        for item in dados:
            try:
                resultado = {
                    'nome': item.get('name', 'Sem nome'),
                    'tipo': 'Hospedagem',
                    'distancia': item.get('dist', 0),
                    'coordenadas': {
                        'lat': item.get('point', {}).get('lat', lat),
                        'lon': item.get('point', {}).get('lon', lon)
                    },
                    'xid': item.get('xid', '')
                }

                if resultado['xid']:
                    resultado['detalhes_url'] = f"https://opentripmap.com/en/card/{resultado['xid']}"

                resultados.append(resultado)
            except (KeyError, TypeError) as e:
                print(f"Erro ao processar item: {e}")
                continue

        return resultados

    except requests.exceptions.HTTPError as e:
        error_msg = f"Erro na API: {e.response.status_code}"
        if e.response.status_code == 400:
            error_msg += f"\nDetalhes: {e.response.text}"
        print(error_msg)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {str(e)}")
        return None
    except ValueError as e:
        print(f"Erro de validação: {str(e)}")
        return None
