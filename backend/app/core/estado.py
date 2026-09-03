FASES = ["diagnostico", "negociacao", "aguardando_banco", "organizacao", "investimento"]
MAX_TENTATIVAS_NEGOCIACAO = 3


def estado_inicial(perfil_cliente: dict) -> dict:
    """
    Inicializa o estado do cliente a partir do perfil.
    """
    return {
        "cliente_id": perfil_cliente.get("cliente_id"),
        "fase": perfil_cliente.get("fase", "diagnostico"),
        "saldo_devedor": perfil_cliente.get("saldo_devedor", 0),
        "renda_mensal": perfil_cliente.get("renda_mensal", 0),
        "reserva_atual": perfil_cliente.get("reserva_atual", 0),
        "meta_reserva": perfil_cliente.get("meta_reserva", 0),
        "tentativas_negociacao": perfil_cliente.get("tentativas_negociacao", 0),
        "parcelas_pagas": perfil_cliente.get("parcelas_pagas", 0),
    }


def avaliar_transicao(estado: dict, evento: str) -> str:
    """
    Avalia a transição de fase com base no estado e no evento.
    """
    fase = estado["fase"]

    # diagnostico -> negociação

    if fase == "diagnostico" and estado["saldo_devedor"] > 0:
        return "negociacao"

    # negociação

    if fase == "negociacao":
        if evento == "proposta_aceita_pelo_cliente":
            return "aguardando_banco"
        elif evento == "proposta_recusada":
            estado["tentativas_negociacao"] += 1
            if estado["tentativas_negociacao"] >= MAX_TENTATIVAS_NEGOCIACAO:
                return "negociacao_esgotada"
            return "negociacao"

    # negociação esgotada

    if fase == "negociacao_esgotada":
        if evento == "atendimento_humano_concluido":
            estado["tentativas_negociacao"] = 0  # segunda chance começa do zero
            return "negociacao"

    # aguardando banco

    if fase == "aguardando_banco":
        if evento == "banco_confirmou":
            return "organizacao"
        elif evento == "banco_recusou":
            return "negociacao"

    # organização

    if fase == "organizacao":
        if evento == "nova_divida":
            return "negociacao"
        if evento == "parcela_paga":
            estado["parcelas_pagas"] += 1
            # sem "return" aqui — deixa cair na checagem abaixo, no mesmo evento
        if estado["saldo_devedor"] <= 0 and estado["reserva_atual"] >= estado["meta_reserva"]:
            return "investimento"


    # investimento

    if fase == "investimento":
        if evento == "usou_reserva_emergencia":
            estado["reserva_atual"] = 0
            return "organizacao"

    return fase