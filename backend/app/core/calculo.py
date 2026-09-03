"""
Motor de simulação financeira. Determinístico — nunca passa pelo LLM.
"""

LIMITE_COMPROMETIMENTO_RENDA = 0.30  # 30% da renda mensal


def simular_parcelamento(saldo_devedor: float, juros_ao_mes: float, numero_parcelas: int) -> float:
    """
    Calcula o valor de cada parcela usando a fórmula de juros compostos
    """
    if numero_parcelas <= 0:
        raise ValueError("O numero de parcelas deve ser maior que zero.")
    if juros_ao_mes == 0:
        return saldo_devedor / numero_parcelas
    fator = (1 + juros_ao_mes) ** numero_parcelas
    parcela = saldo_devedor * (juros_ao_mes * fator) / (fator - 1)
    return parcela


def simular_desconto_a_vista(saldo_devedor: float, percentual_desconto: float) -> float:
    """
    Retorna o valor final para quitação à vista, com o desconto aplicado.
    """
    return saldo_devedor * (1 - percentual_desconto)


def calcular_comprometimento_renda(valor_parcela: float, renda_mensal: float) -> float:
    """
    Retorna a fração da renda mensal que a parcela representa (ex.: 0.25 = 25%).
    Deve levantar ValueError se renda_mensal <= 0.
    """
    if renda_mensal <= 0:
        raise ValueError("A renda mensal deve ser um valor positivo.")
    return valor_parcela / renda_mensal


def proposta_e_saudavel(valor_parcela: float, renda_mensal: float) -> bool:
    """
    Retorna True se o comprometimento de renda da parcela está dentro do limite
    definido em LIMITE_COMPROMETIMENTO_RENDA.
    """
    return calcular_comprometimento_renda(valor_parcela, renda_mensal) <= LIMITE_COMPROMETIMENTO_RENDA


def sugerir_melhor_parcelamento(saldo_devedor: float, juros_ao_mes: float, renda_mensal: float, max_parcelas: int) -> dict | None:
    """
    Testa, de 1 até max_parcelas, o menor número de parcelas cujo valor respeita o
    limite saudável de comprometimento de renda. Retorna um dicionário com
    numero_parcelas, valor_parcela e comprometimento_renda, ou None se nem o
    parcelamento máximo couber no orçamento.
    """
    for numero_parcelas in range(1, max_parcelas + 1):
        valor_parcela = simular_parcelamento(saldo_devedor, juros_ao_mes, numero_parcelas)
        comprometimento = calcular_comprometimento_renda(valor_parcela, renda_mensal)
        if proposta_e_saudavel(valor_parcela, renda_mensal):
            return {
                "numero_parcelas": numero_parcelas,
                "valor_parcela": valor_parcela,
                "comprometimento_renda": comprometimento
            }