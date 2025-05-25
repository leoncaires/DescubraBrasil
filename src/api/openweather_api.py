import requests
from datetime import datetime

OPENWEATHER_API_KEY = "57305e645e155cafb64187b91e065767"


def obter_clima(lat, lon):
    """
    Obtém dados climáticos atuais usando a API OpenWeatherMap

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Dados climáticos formatados ou None em caso de erro
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()

        dados_clima = resposta.json()
        return formatar_clima(dados_clima)

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição do clima: {str(e)}")
        return None


def formatar_clima(dados_clima):
    """
    Formata os dados climáticos para um formato mais amigável

    Args:
        dados_clima (dict): Dados brutos da API

    Returns:
        dict: Dados climáticos formatados
    """
    if not dados_clima:
        return None

    clima_principal = dados_clima.get('weather', [{}])[0]
    principais = dados_clima.get('main', {})
    vento = dados_clima.get('wind', {})
    sistema = dados_clima.get('sys', {})

    formatado = {
        'condicao': clima_principal.get('description', 'Condição não disponível').capitalize(),
        'temperatura': principais.get('temp'),
        'sensacao_termica': principais.get('feels_like'),
        'temperatura_min': principais.get('temp_min'),
        'temperatura_max': principais.get('temp_max'),
        'umidade': principais.get('humidity'),
        'pressao': principais.get('pressure'),
        'vento_velocidade': vento.get('speed'),
        'vento_direcao': vento.get('deg'),
        'nascer_sol': datetime.fromtimestamp(sistema.get('sunrise')).strftime('%H:%M') if sistema.get('sunrise') else None,
        'por_do_sol': datetime.fromtimestamp(sistema.get('sunset')).strftime('%H:%M') if sistema.get('sunset') else None,
        'visibilidade': dados_clima.get('visibility'),
        'nuvens': dados_clima.get('clouds', {}).get('all'),
        'cidade': dados_clima.get('name', 'Local desconhecido'),
        'pais': sistema.get('country'),
        'icone': f"https://openweathermap.org/img/wn/{clima_principal.get('icon')}@2x.png" if clima_principal.get('icon') else None,
        'atualizacao': datetime.fromtimestamp(dados_clima.get('dt')).strftime('%d/%m/%Y %H:%M') if dados_clima.get('dt') else None
    }

    return formatado
