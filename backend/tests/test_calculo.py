import pytest
from app.core.calculo import (
    simular_parcelamento,
    simular_desconto_a_vista,
    calcular_comprometimento_renda,
    proposta_e_saudavel,
    sugerir_melhor_parcelamento,
)


def test_simular_parcelamento_sem_juros_divide_igualmente():
    assert simular_parcelamento(saldo_devedor=1000, juros_ao_mes=0, numero_parcelas=10) == 100


def test_simular_parcelamento_numero_parcelas_invalido_levanta_erro():
    with pytest.raises(ValueError):
        simular_parcelamento(saldo_devedor=1000, juros_ao_mes=0.02, numero_parcelas=0)


def test_simular_desconto_a_vista():
    assert simular_desconto_a_vista(saldo_devedor=1000, percentual_desconto=0.25) == 750


def test_calcular_comprometimento_renda():
    assert calcular_comprometimento_renda(valor_parcela=900, renda_mensal=3000) == 0.3


def test_calcular_comprometimento_renda_renda_invalida_levanta_erro():
    with pytest.raises(ValueError):
        calcular_comprometimento_renda(valor_parcela=100, renda_mensal=0)


def test_proposta_no_limite_e_saudavel():
    assert proposta_e_saudavel(valor_parcela=900, renda_mensal=3000) is True


def test_proposta_acima_do_limite_nao_e_saudavel():
    assert proposta_e_saudavel(valor_parcela=1200, renda_mensal=3000) is False


def test_sugerir_melhor_parcelamento_encontra_opcao_saudavel():
    sugestao = sugerir_melhor_parcelamento(saldo_devedor=10000, juros_ao_mes=0.019, renda_mensal=3200, max_parcelas=12)
    assert sugestao is not None
    assert sugestao["comprometimento_renda"] <= 0.30


def test_sugerir_melhor_parcelamento_retorna_none_quando_nao_cabe():
    sugestao = sugerir_melhor_parcelamento(saldo_devedor=100000, juros_ao_mes=0.05, renda_mensal=1000, max_parcelas=3)
    assert sugestao is None