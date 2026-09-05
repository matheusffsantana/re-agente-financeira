from app.core.estado import estado_inicial, avaliar_transicao, MAX_TENTATIVAS_NEGOCIACAO


def perfil_exemplo(**overrides):
    base = {
        "cliente_id": "cli_teste",
        "fase": "diagnostico",
        "saldo_devedor": 5000,
        "renda_mensal": 3000,
    }
    base.update(overrides)
    return base


def test_diagnostico_avanca_para_negociacao_com_saldo_devedor():
    estado = estado_inicial(perfil_exemplo())
    nova_fase = avaliar_transicao(estado, evento="nenhum")
    assert nova_fase == "negociacao"


def test_negociacao_aceita_vai_para_aguardando_banco():
    estado = estado_inicial(perfil_exemplo(fase="negociacao"))
    nova_fase = avaliar_transicao(estado, evento="proposta_aceita_pelo_cliente")
    assert nova_fase == "aguardando_banco"


def test_negociacao_esgota_apos_maximo_de_tentativas():
    estado = estado_inicial(perfil_exemplo(fase="negociacao", tentativas_negociacao=MAX_TENTATIVAS_NEGOCIACAO - 1))
    nova_fase = avaliar_transicao(estado, evento="proposta_recusada")
    assert nova_fase == "negociacao_esgotada"


def test_negociacao_esgotada_reinicia_apos_atendimento_humano():
    estado = estado_inicial(perfil_exemplo(fase="negociacao_esgotada", tentativas_negociacao=MAX_TENTATIVAS_NEGOCIACAO))
    nova_fase = avaliar_transicao(estado, evento="atendimento_humano_concluido")
    assert nova_fase == "negociacao"
    assert estado["tentativas_negociacao"] == 0


def test_banco_confirma_avanca_para_organizacao():
    estado = estado_inicial(perfil_exemplo(fase="aguardando_banco"))
    nova_fase = avaliar_transicao(estado, evento="banco_confirmou")
    assert nova_fase == "organizacao"


def test_banco_recusa_volta_para_negociacao():
    estado = estado_inicial(perfil_exemplo(fase="aguardando_banco"))
    nova_fase = avaliar_transicao(estado, evento="banco_recusou")
    assert nova_fase == "negociacao"


def test_nova_divida_durante_organizacao_regride_para_negociacao():
    estado = estado_inicial(perfil_exemplo(fase="organizacao", saldo_devedor=0))
    nova_fase = avaliar_transicao(estado, evento="nova_divida")
    assert nova_fase == "negociacao"


def test_parcela_paga_que_completa_meta_avanca_para_investimento_na_mesma_chamada():
    estado = estado_inicial(perfil_exemplo(
        fase="organizacao", saldo_devedor=0, reserva_atual=5000, meta_reserva=5000
    ))
    nova_fase = avaliar_transicao(estado, evento="parcela_paga")
    assert nova_fase == "investimento"
    assert estado["parcelas_pagas"] == 1


def test_parcela_paga_sem_completar_meta_continua_em_organizacao():
    estado = estado_inicial(perfil_exemplo(fase="organizacao", saldo_devedor=0, reserva_atual=1000, meta_reserva=5000))
    nova_fase = avaliar_transicao(estado, evento="parcela_paga")
    assert nova_fase == "organizacao"
    assert estado["parcelas_pagas"] == 1


def test_usar_reserva_durante_investimento_regride_para_organizacao():
    estado = estado_inicial(perfil_exemplo(fase="investimento", saldo_devedor=0, reserva_atual=5000))
    nova_fase = avaliar_transicao(estado, evento="usou_reserva_emergencia")
    assert nova_fase == "organizacao"
    assert estado["reserva_atual"] == 0