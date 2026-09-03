from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.core.estado import estado_inicial, avaliar_transicao
from app.core.mensagens import gerar_mensagem_comemorativa, MENSAGEM_FORA_ESCOPO
from app.data.repositorio import carregar_perfil_cliente
from app.llm.prompts import montar_system_prompt, PROMPT_CLASSIFICACAO_ESCOPO
from app.llm.client import gerar_resposta, classificar_estruturado
from app.websocket.manager import manager



app = FastAPI(title="Rê - Agente Financeira")

# Estado em memória por cliente (em produção, seria um banco de dados/cache)
estados_ativos: dict[str, dict] = {}


def obter_ou_criar_estado(cliente_id: str) -> dict:
    """
    Devolve o estado do cliente se já estiver em memória; senão, carrega o
    perfil dos dados mockados e cria um estado novo.
    """
    if cliente_id not in estados_ativos:
        perfil = carregar_perfil_cliente(cliente_id)
        estados_ativos[cliente_id] = estado_inicial(perfil)
    return estados_ativos[cliente_id]


@app.websocket("/ws/{cliente_id}")
async def canal_cliente(websocket: WebSocket, cliente_id: str):
    await manager.conectar(cliente_id, websocket)
    estado = obter_ou_criar_estado(cliente_id)
    try:
        while True:
            mensagem_cliente = await websocket.receive_text()

            # 1. Verificação de escopo (nunca deixar o LLM improvisar fora do propósito)
            classificacao = classificar_estruturado(
                PROMPT_CLASSIFICACAO_ESCOPO.format(mensagem=mensagem_cliente)
            )
            if classificacao["escopo"] == "fora_escopo":
                await websocket.send_text(MENSAGEM_FORA_ESCOPO)
                continue

            # 2. Monta o prompt com a fase atual e os dados do cliente
            system_prompt = montar_system_prompt(estado["fase"], estado)

            # 3. Gera a resposta em linguagem natural
            resposta = gerar_resposta(system_prompt, mensagem_cliente)
            await websocket.send_text(resposta)

    except WebSocketDisconnect:
        manager.desconectar(cliente_id)


async def notificar_pagamento(cliente_id: str):
    """
    Chamado externamente (hoje, manualmente para teste; no futuro, por um webhook
    do banco) quando uma parcela é confirmada como paga.
    """
    estado = obter_ou_criar_estado(cliente_id)
    estado["fase"] = avaliar_transicao(estado, "parcela_paga")
    mensagem = gerar_mensagem_comemorativa(estado)
    await manager.enviar_para_cliente(cliente_id, mensagem)