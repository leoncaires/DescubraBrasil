let etapa = 0;
let estadoEscolhido = "";
let categoriaEscolhida = "";
let atracoesAtuais = [];
let dados = {};
let ultimaAtracaoEscolhida = null;
let coordenadasAtuais = null;

// Gera ou recupera session_id
let session_id = localStorage.getItem("session_id");
if (!session_id) {
    session_id = Date.now().toString() + Math.random().toString(36).substring(2);
    localStorage.setItem("session_id", session_id);
}

async function initChat() {
    try {
        // Tenta obter a localização do usuário
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    coordenadasAtuais = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    console.log("Coordenadas obtidas:", coordenadasAtuais);
                },
                error => {
                    console.warn("Não foi possível obter localização:", error);
                }
            );
        }

        const res = await fetch("/dados.json?v=" + Date.now());
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        
        dados = await res.json();
        etapa = 0;
        responder();
    } catch (err) {
        console.error("Erro ao carregar dados:", err);
        document.getElementById("chat").innerHTML +=
            '<div class="bot"><strong>Erro:</strong> Dados não carregados. Verifique o arquivo dados.json</div>';
    }
}

function mostrarMapa(lat, lon, nome, mostrarHospedagens = false) {
    if (!document.getElementById('map')) {
        console.error("Elemento #map não encontrado!");
        return;
    }

    if (window.map) {
        window.map.remove();
    }

    window.map = L.map('map').setView([lat, lon], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(window.map);

    const marker = L.marker([lat, lon])
        .addTo(window.map)
        .bindPopup(`<b>${nome}</b>`)
        .openPopup();

    // Se for para mostrar hospedagens, adicionamos marcadores extras
    if (mostrarHospedagens) {
        buscarHospedagensProximas(lat, lon);
    }
}

async function buscarHospedagensProximas(lat, lon) {
    const chat = document.getElementById("chat");
    
    try {
        // Exibe mensagem de carregamento
        chat.innerHTML += `<div class="bot"><strong>Roger:</strong> Buscando hospedagens próximas...</div>`;
        
        // Codificação segura dos parâmetros
        const url = `/hospedagens_proximas?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
        const response = await fetch(url);
        
        // Tratamento de erros HTTP
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.mensagem || `Erro ${response.status}`);
        }
        
        const data = await response.json();
        
        // Limpa marcadores anteriores
        if (window.markersHospedagens) {
            window.markersHospedagens.forEach(marker => marker.remove());
        }
        window.markersHospedagens = [];
        
        // Processa resultados
        if (data.resultados && data.resultados.length > 0) {
            // Adiciona marcadores
            data.resultados.forEach(hospedagem => {
                const marker = L.marker(
                    [hospedagem.coordenadas.lat, hospedagem.coordenadas.lon],
                    {
                        icon: L.icon({
                            iconUrl: 'https://cdn-icons-png.flaticon.com/512/2838/2838694.png',
                            iconSize: [32, 32]
                        })
                    }
                )
                .addTo(window.map)
                .bindPopup(`<b>${hospedagem.nome}</b><br>Tipo: ${hospedagem.tipo}`);
                
                window.markersHospedagens.push(marker);
            });
            
            // Exibe lista no chat
            const lista = data.resultados.map(h => 
                `<li>${h.nome} (${h.distancia}m - ${h.tipo})</li>`
            ).join('');
            
            chat.innerHTML += `
                <div class="bot">
                    <strong>Roger:</strong> Encontrei ${data.resultados.length} hospedagens:
                    <ul>${lista}</ul>
                </div>
            `;
        } else {
            chat.innerHTML += `
                <div class="bot">
                    <strong>Roger:</strong> Nenhuma hospedagem encontrada neste local.
                </div>
            `;
        }
    } catch (error) {
        console.error("Erro:", error);
        chat.innerHTML += `
            <div class="bot error">
                <strong>Roger:</strong> ${error.message || 'Erro ao buscar hospedagens'}
            </div>
        `;
    } finally {
        chat.scrollTop = chat.scrollHeight;
    }
}

async function mostrarInfoClima(lat, lon) {
    try {
        const response = await fetch(`/clima_detalhado?lat=${lat}&lon=${lon}`);
        if (!response.ok) throw new Error("Erro ao buscar clima");
        
        const clima = await response.json();
        
        if (clima.error) {
            console.warn(clima.error);
            return null;
        }

        return clima;
    } catch (error) {
        console.error("Erro ao buscar clima:", error);
        return null;
    }
}

async function mostrarDetalhesAtracao(local) {
    ultimaAtracaoEscolhida = local;
    const chat = document.getElementById("chat");
    
    // Busca informações de clima se houver coordenadas
    let infoClima = null;
    if (local.lat && local.lon) {
        infoClima = await mostrarInfoClima(local.lat, local.lon);
        mostrarMapa(local.lat, local.lon, local.nome, true);
    }

    let resposta = `🗺 <strong>${local.nome}</strong><br>` +
        `📌 ${local.descricao}<br>`;
    
    // Adiciona informações de clima se disponíveis
    if (infoClima) {
        resposta += `🌤 <strong>Clima atual:</strong> ${infoClima.condicao}, ${infoClima.temperatura} (${infoClima.faixa_temperatura})<br>`;
        if (infoClima.icone) {
            resposta += `<img src="${infoClima.icone}" alt="${infoClima.condicao}" style="height: 50px;"><br>`;
        }
        resposta += `💨 Vento: ${infoClima.vento}<br>`;
        resposta += `💧 Umidade: ${infoClima.umidade}<br>`;
        resposta += `📝 <em>${infoClima.recomendacao}</em><br>`;
    } else if (local.detalhes?.clima) {
        resposta += `🌤 Clima: ${local.detalhes.clima}<br>`;
    }
    
    resposta += `🏨 Hospedagem: ${local.detalhes.hospedagem}<br>` +
        `🚗 Transporte: ${local.detalhes.transporte}<br>` +
        `📍 Endereço: ${local.detalhes.endereço}<br><br>`;
    
    if (local.lat && local.lon) {
        resposta += `<button onclick="buscarHospedagensProximas(${local.lat}, ${local.lon})" class="btn-hospedagem">🏨 Mostrar hospedagens próximas</button><br><br>`;
    }
    
    resposta += `Digite "voltar" para outras atrações ou "menu" para recomeçar.`;

    chat.innerHTML += `<div class="bot"><strong>Roger:</strong> ${resposta}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function mostrarUltimaAtracao() {
    if (ultimaAtracaoEscolhida) {
        mostrarDetalhesAtracao(ultimaAtracaoEscolhida);
    }
}

function responder(mensagemInterpretada = "") {
    const chat = document.getElementById("chat");
    let resposta = "";

    switch (etapa) {
        case 0:
            resposta = `Olá! Eu sou o Roger do Descubra Brasil. Vamos planejar sua viagem!<br>Escolha um Estado ou a Unidade Federativa:<br>` +
                `<div class="lista">${Object.keys(dados).map((e, i) => `${i + 1}. ${e}`).join('<br>')}</div>`;
            if (ultimaAtracaoEscolhida) {
                resposta += `<br><button onclick="mostrarUltimaAtracao()" class="btn-ultima">🔁 Ver última atração visitada</button>`;
            }
            etapa = 1;
            break;

        case 1:
            if (mensagemInterpretada.tipo === "estado") {
                estadoEscolhido = mensagemInterpretada.valor;
                resposta = `Ótimo! O que você quer conhecer em <strong>${estadoEscolhido}</strong>?<br>` +
                    `<div class="lista">${Object.keys(dados[estadoEscolhido]).map((c, i) => `${i + 1}. ${c}`).join('<br>')}</div>`;
                etapa = 2;
            } else {
                resposta = `Estado não reconhecido. Escolha pelo número ou nome:<br>` +
                    `<div class="lista">${Object.keys(dados).map((e, i) => `${i + 1}. ${e}`).join('<br>')}</div>`;
            }
            break;

        case 2:
            if (mensagemInterpretada.tipo === "categoria") {
                categoriaEscolhida = mensagemInterpretada.valor;

                if (!dados[estadoEscolhido] || !dados[estadoEscolhido][categoriaEscolhida]) {
                    resposta = `Categoria não encontrada. Escolha uma em <strong>${estadoEscolhido}</strong>:<br>` +
                        `<div class="lista">${Object.keys(dados[estadoEscolhido] || {}).map((c, i) => `${i + 1}. ${c}`).join('<br>')}</div>`;
                    break;
                }

                atracoesAtuais = dados[estadoEscolhido][categoriaEscolhida];
                resposta = `Ótimas opções em ${categoriaEscolhida}:<br>` +
                    `<div class="lista">${atracoesAtuais.map((a, i) => `${i + 1}. <strong>${a.nome}</strong> - ${a.descricao}`).join('<br>')}</div>` +
                    `<br>Digite o número da atração para detalhes ou "voltar" para categorias.`;
                etapa = 3;

                fetch("/salvar_recomendacao", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id, estado: estadoEscolhido, categoria: categoriaEscolhida })
                });
            } else {
                resposta = `Categoria não encontrada. Escolha uma em <strong>${estadoEscolhido}</strong>:<br>` +
                    `<div class="lista">${Object.keys(dados[estadoEscolhido]).map((c, i) => `${i + 1}. ${c}`).join('<br>')}</div>`;
            }
            break;

        case 3:
            const msg = mensagemInterpretada.valor.toLowerCase();

            if (msg === "menu") {
                etapa = 0;
                estadoEscolhido = "";
                categoriaEscolhida = "";
                return responder();
            }

            if (msg === "voltar") {
                etapa = 2;
                return responder();
            }

            if (msg === "última" || msg === "ultima") {
                mostrarUltimaAtracao();
                return;
            }

            if (!isNaN(msg)) {
                const idx = parseInt(msg) - 1;
                if (atracoesAtuais[idx]) {
                    mostrarDetalhesAtracao(atracoesAtuais[idx]);
                } else {
                    resposta = "Número inválido. Tente novamente.";
                }
            } else {
                resposta = "Opção não reconhecida. Digite um número, 'voltar' ou 'menu'.";
            }
            break;
    }

    if (resposta) {
        chat.innerHTML += `<div class="bot"><strong>Roger:</strong> ${resposta}</div>`;
        chat.scrollTop = chat.scrollHeight;
    }
}

async function enviarMensagem() {
    const input = document.getElementById("mensagem");
    const msg = input.value.trim();
    if (!msg) return;

    const chat = document.getElementById("chat");
    chat.innerHTML += `<div class="user"><strong>Você:</strong> ${msg}</div>`;
    input.value = "";

    const num = parseInt(msg);
    if (!isNaN(num)) {
        let interpretado = { valor: msg };

        if (etapa === 1) {
            const estadosLista = Object.keys(dados);
            if (num > 0 && num <= estadosLista.length) {
                interpretado = { tipo: "estado", valor: estadosLista[num - 1] };
            }
        } else if (etapa === 2) {
            const categoriasLista = Object.keys(dados[estadoEscolhido] || {});
            if (num > 0 && num <= categoriasLista.length) {
                interpretado = { tipo: "categoria", valor: categoriasLista[num - 1] };
            }
        }

        responder(interpretado);
        return;
    }

    try {
        const resposta = await fetch("/mensagem", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: msg, session_id })
        });
        const interpretado = await resposta.json();

        if (interpretado.tipo === "recomendar") {
            const r = interpretado.valor;
            estadoEscolhido = r.estado;
            categoriaEscolhida = r.categoria;
            atracoesAtuais = dados[estadoEscolhido]?.[categoriaEscolhida] || [];

            etapa = 3;
            chat.innerHTML += `<div class="bot"><strong>Roger:</strong> Encontrei algo legal para você em <strong>${estadoEscolhido} - ${categoriaEscolhida}</strong>:<br>` +
                `<strong>${r.titulo}</strong><br>${r.descricao}<br>` +
                `<br>Veja mais opções ou digite o número para detalhes.</div>`;

            chat.innerHTML += `<div class="bot"><strong>Roger:</strong> Outras opções em <strong>${categoriaEscolhida}</strong>:<br>` +
                `<div class="lista">${atracoesAtuais.map((a, i) => `${i + 1}. <strong>${a.nome}</strong> - ${a.descricao}`).join('<br>')}</div>` +
                `<br>Digite o número da atração para detalhes ou "voltar" para categorias.</div>`;

            chat.scrollTop = chat.scrollHeight;
            return;
        }

        responder(interpretado);
    } catch (error) {
        console.error("Erro:", error);
        chat.innerHTML += '<div class="bot"><strong>Erro:</strong> Falha na conexão</div>';
    }
}

window.onload = function () {
    initChat();

    const mapElement = document.getElementById("map");
    if (mapElement) {
        // Mapa inicial com visão do Brasil
        window.map = L.map('map').setView([-15.7797, -47.9297], 4);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(window.map);
    } else {
        console.error("#map não encontrado no DOM");
    }
};

document.getElementById("mensagem").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        enviarMensagem();
    }
});