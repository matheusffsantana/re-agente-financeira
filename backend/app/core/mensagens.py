import random

MENSAGENS_COMEMORATIVAS = [
    "Mais uma parcela paga! Você está construindo um histórico novo, parabéns.",
    "Cada pagamento desses é um passo real rumo à sua liberdade financeira.",
    "Você está cada vez mais perto de fechar essa negociação. Continue assim.",
]

MENSAGEM_FORA_ESCOPO = "Desculpe, não posso ajudar com isso. Vamos focar em suas finanças."

MENSAGEM_NEGOCIACAO_ESGOTADA = "Você atingiu o limite de tentativas de negociação. Por favor, aguarde atendimento humano."

def gerar_mensagem_comemorativa(estado: dict) -> str:
    """
    Retorna uma mensagem comemorativa aleatória.
    """
    mensagem = random.choice(MENSAGENS_COMEMORATIVAS)
    total_parcelas = estado.get("negociacao_concluida", {}).get("numero_parcelas")
    pagas = estado.get("parcelas_pagas", 0)
    if total_parcelas:
        return f"{mensagem} ({pagas} de {total_parcelas} parcelas pagas)."
    return mensagem

def gerar_mensagem_fora_do_escopo() -> str:
    """
    Retorna uma mensagem indicando que a solicitação está fora do escopo.
    """
    return MENSAGEM_FORA_ESCOPO

def gerar_mensagem_negociacao_esgotada() -> str:
    """
    Retorna uma mensagem indicando que as tentativas de negociação foram esgotadas.
    """
    return MENSAGEM_NEGOCIACAO_ESGOTADA

