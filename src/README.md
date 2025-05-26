# 🚀 Descubra Brasil - Sistema Inteligente de Recomendações Turísticas

**Resumo:** Chatbot interativo que utiliza processamento de linguagem natural e geolocalização para recomendar atrações turísticas no Brasil, integrando dados climáticos em tempo real e opções de hospedagem próximas.

---

## 🎯 Objetivo

Desenvolver um sistema que:
- Interpreta requisições em linguagem natural sobre destinos turísticos
- Oferece recomendações baseadas em estado e categoria
- Exibe localizações em mapas interativos
- Fornece informações práticas (clima, hospedagens) via APIs externas
- Demonstra aplicação prática de conceitos de NLP e arquitetura de software

---

## 👨‍💻 Tecnologias Utilizadas

### Backend (Python)
- **Flask**: Microframework para API web
- **Unicode normalization**: Pré-processamento de texto
- **Expressões regulares**: Interpretação de padrões
- **APIs RESTful**: OpenWeather (clima) e TourismAPI (hospedagens)

### Frontend (JavaScript)
- **Leaflet.js**: Biblioteca para mapas interativos
- **Web Fetch API**: Comunicação com o backend
- **LocalStorage**: Persistência de sessão

### Estrutura de Dados
- **JSON hierárquico**: Armazenamento de atrações por estado/categoria
- **Dicionários de palavras-chave**: Categorização automática

---
```
📦 descubra-brasil
├── 📁 api
│ ├── openweather_api.py # Integração com API de clima
│ └── tourism_api.py # Busca de hospedagens/atrações
├── 📁 interface
│ ├── index.html # Interface do chat
│ ├── styles.css # Estilos CSS
│ ├── app.js # Lógica frontend
│ └── dados.json # Database de atrações
├── main.py # Servidor principal
├── README.md # Este arquivo
└── requirements.txt # Dependências Python
```

---

## ⚙️ Como Executar

### ✅ Rodando Localmente

1. Clone o repositório:

```
   ```bash
   git clone https://github.com/leoncaires/DescubraBrasil.git
   cd descubra-brasil
```

2. Crie o ambiente virtual e ative:

```
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

3. Instale as dependências:

```
pip install -r requirements.txt
```

4. Execute a aplicação:

```
python main.py
```

---

## 📸 Demonstrações

Inclua aqui prints, gifs ou vídeos mostrando a interface ou o funcionamento do sistema:

- Tela inicial
- Exemplo de funcionalidade
- Resultados esperados

![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)

---

## 👥 Equipe

| Nome | GitHub |
|------|--------|
| Leonel Santos Caires | [@leoncaires](https://github.com/leoncaires) |
| Elton Dos Santos Rodrigues| [@elton-sr](https://github.com/elton-sr) |

---

## 🧠 Disciplinas Envolvidas

- Estrutura de Dados I
- Teoria dos Grafos
- Linguagens Formais e Autômatos

---

## 🏫 Informações Acadêmicas

- Universidade: **Universidade Braz Cubas**
- Curso: **Ciência da Computação**
- Semestre: 2º 
- Período: Manhã / Noite
- Professora orientadora: **Dra. Andréa Ono Sakai**
- Evento: **Mostra de Tecnologia 1º Semestre de 2025**
- Local: Laboratório 12
- Datas: 05 e 06 de junho de 2025

---

## 📄 Licença


