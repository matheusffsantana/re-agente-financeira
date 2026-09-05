from dotenv import load_dotenv
load_dotenv()

import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.core.estado import estado_inicial, avaliar_transicao
from app.core.calculo import sugerir_melhor_parcelamento
from app.core.mensagens import gerar_mensagem_comemorativa, MENSAGEM_FORA_ESCOPO
from app.data.repositorio import carregar_perfil_cliente, carregar_produtos_financeiros
from app.llm.prompts import montar_system_prompt, PROMPT_CLASSIFICACAO_ESCOPO
from app.llm.client import gerar_resposta, classificar_estruturado
from app.websocket.manager import manager

app = FastAPI(title="Rê - Agente Financeira")

estados_ativos: dict[str, dict] = {}


def obter_ou_criar_estado(cliente_id: str) -> dict:
    if cliente_id not in estados_ativos:
        perfil = carregar_perfil_cliente(cliente_id)
        estados_ativos[cliente_id] = estado_inicial(perfil)
    return estados_ativos[cliente_id]


def gerar_proposta_negociacao(estado: dict) -> dict | None:
    """
    Usa o motor de cálculo para montar uma proposta de parcelamento real,
    baseada nos dados do cliente e nas regras de negociação disponíveis.
    """
    produtos = carregar_produtos_financeiros()
    produto_parcelamento = produtos["negociacao"][0]

    return sugerir_melhor_parcelamento(
        saldo_devedor=estado["saldo_devedor"],
        juros_ao_mes=produto_parcelamento["juros_ao_mes"],
        renda_mensal=estado["renda_mensal"],
        max_parcelas=produto_parcelamento["max_parcelas"],
    )


@app.websocket("/ws/{cliente_id}")
async def canal_cliente(websocket: WebSocket, cliente_id: str):
    await manager.conectar(cliente_id, websocket)
    estado = obter_ou_criar_estado(cliente_id)

    await websocket.send_json({"tipo": "estado", "fase": estado["fase"]})
    if estado["fase"] == "negociacao":
        proposta = gerar_proposta_negociacao(estado)
        if proposta is not None:
            await websocket.send_json({"tipo": "proposta", "proposta": proposta})

    try:
        while True:
            dado_bruto = await websocket.receive_text()
            dado = json.loads(dado_bruto)

            if dado["tipo"] == "decisao":
                nova_fase = avaliar_transicao(estado, dado["evento"])
                estado["fase"] = nova_fase
                await websocket.send_json({"tipo": "estado", "fase": nova_fase})

                if nova_fase == "negociacao":
                    proposta = gerar_proposta_negociacao(estado)
                    if proposta is not None:
                        await websocket.send_json({"tipo": "proposta", "proposta": proposta})

            elif dado["tipo"] == "mensagem":
                mensagem_cliente = dado["texto"]

                try:
                    classificacao = classificar_estruturado(
                        PROMPT_CLASSIFICACAO_ESCOPO.format(mensagem=mensagem_cliente)
                    )
                except (json.JSONDecodeError, KeyError):
                    classificacao = {"escopo": "dentro_escopo"}

                if classificacao["escopo"] == "fora_escopo":
                    await websocket.send_json({"tipo": "mensagem", "autor": "re", "texto": MENSAGEM_FORA_ESCOPO})
                    continue

                system_prompt = montar_system_prompt(estado["fase"], estado)
                resposta = gerar_resposta(system_prompt, mensagem_cliente)
                await websocket.send_json({"tipo": "mensagem", "autor": "re", "texto": resposta})

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