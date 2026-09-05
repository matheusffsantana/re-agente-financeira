from app.core.mensagens import (
    gerar_mensagem_comemorativa,
    gerar_mensagem_fora_do_escopo,
    gerar_mensagem_negociacao_esgotada,
    MENSAGENS_COMEMORATIVAS,
    MENSAGEM_FORA_ESCOPO,
    MENSAGEM_NEGOCIACAO_ESGOTADA,
)


def test_mensagem_comemorativa_esta_na_lista_quando_sem_negociacao_concluida():
    estado = {"parcelas_pagas": 0}
    mensagem = gerar_mensagem_comemorativa(estado)
    assert mensagem in MENSAGENS_COMEMORATIVAS


def test_mensagem_comemorativa_inclui_contagem_quando_ha_negociacao_concluida():
    estado = {"negociacao_concluida": {"numero_parcelas": 12}, "parcelas_pagas": 9}
    mensagem = gerar_mensagem_comemorativa(estado)
    assert "9 de 12 parcelas pagas" in mensagem


def test_mensagem_fora_do_escopo():
    assert gerar_mensagem_fora_do_escopo() == MENSAGEM_FORA_ESCOPO


def test_mensagem_negociacao_esgotada():
    assert gerar_mensagem_negociacao_esgotada() == MENSAGEM_NEGOCIACAO_ESGOTADA