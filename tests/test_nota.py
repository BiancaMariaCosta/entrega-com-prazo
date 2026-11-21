# =====================================================================
# CRITÉRIOS DE ACEITAÇÃO (copiados da Issue #1)
# =====================================================================
# RF-001  Dado nota 8.0 e prazo 20/11/2026 23:59:00
#         Quando a entrega ocorre exatamente às 23:59:00
#         Então a entrega é aceita, com nota final 8.0, desconto 0%, 0 dias de atraso
#         e situação DENTRO_DO_PRAZO
# RF-002  Dado nota 10.0
#         Quando a entrega ocorre 1 s, 24 h e 24 h + 1 s após o prazo
#         Então os dias de atraso são 1, 1 e 2, e as notas finais são 9.0, 9.0 e 8.0
# RF-003  Dado nota 10.0
#         Quando a entrega ocorre 4 dias + 1 s e exatamente 5 dias após o prazo
#         Então o desconto é 50% nos dois casos e a nota final é 5.0
# RF-004  Dado nota 10.0
#         Quando a entrega ocorre 5 dias + 1 s após o prazo
#         Então a entrega é rejeitada: aceita = False, nota final e desconto ausentes (None),
#         situação REJEITADA e 6 dias de atraso
# RF-005  Dado nota 10.0, justificativa aprovada e novo prazo 7 dias após o prazo original
#         Quando a entrega ocorre 6 dias após o prazo original
#         Então a nota final é 10.0, o desconto é 0% e o prazo considerado é o novo prazo
# RF-006  Dado nota 10.0, justificativa aprovada e novo prazo 3 dias após o prazo original
#         Quando a entrega ocorre 1 hora após o novo prazo
#         Então o desconto é 10%, a nota final é 9.0 e há 1 dia de atraso contado do novo prazo
# RF-007  Dado justificativa aprovada
#         Quando o novo prazo não é informado, ou é igual ao prazo original
#         Então a função lança ValueError
# RF-008  Dado justificativa não aprovada e um novo prazo 7 dias após o prazo original
#         Quando a entrega ocorre 1 hora após o prazo original
#         Então o novo prazo é ignorado: desconto 10% e prazo considerado igual ao original
# RF-009  Dado nota 7.0
#         Quando a entrega ocorre 2 horas após o prazo
#         Então o resultado traz o momento da entrega, o prazo considerado, 1 dia de atraso,
#         desconto 10%, nota final 6.3 e situação ATRASADA
# RF-010  Dada nota -0.1, 10.01, "8", True, NaN ou infinito
#         Quando a função é chamada
#         Então a função lança ValueError
# RF-011  Dado nota 8.35 com 1 dia de atraso (8.35 x 0,90 = 7.515)
#         e nota 9.15 com 3 dias de atraso (9.15 x 0,70 = 6.405)
#         Quando a função calcula a nota final
#         Então as notas finais são 7.52 e 6.41
# RF-012  Dado prazo sem fuso horário e entrega com fuso horário
#         Quando a função é chamada
#         Então a função lança ValueError
# RF-013  Dado prazo em texto ("2026-11-20"), ou justificativa_aprovada "sim",
#         ou justificativa aprovada com novo prazo em texto
#         Quando a função é chamada
#         Então a função lança ValueError
# RNF-001 Dado o Codespace padrão da turma
#         Quando a função é chamada 10.000 vezes seguidas
#         Então o tempo total é menor que 1 segundo
# RNF-002 Dada toda nota de 0.00 a 10.00 em passos de 0.25 e atrasos de 0 a 5 dias
#         Quando a função é chamada para cada combinação (246 casos)
#         Então 100% das notas finais são iguais ao cálculo decimal exato com 2 casas
# RNF-003 Dada a mesma entrada
#         Quando a função é chamada 1.000 vezes seguidas
#         Então os 1.000 resultados são idênticos
# =====================================================================

import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

import pytest

import src.nota as nota

PRAZO = datetime(2026, 11, 20, 23, 59, 0)
UM_SEGUNDO = timedelta(seconds=1)
UMA_HORA = timedelta(hours=1)
UM_DIA = timedelta(days=1)


def test_rf001_entrega_no_limite_recebe_nota_integral():
    r = nota.calcular_nota_final(8.0, PRAZO, PRAZO, False, None)
    assert r.aceita is True
    assert r.nota_final == 8.0
    assert r.desconto_percentual == 0
    assert r.dias_atraso == 0
    assert r.situacao == "DENTRO_DO_PRAZO"


def test_rf002_desconto_de_10_por_cento_por_dia_iniciado():
    r1 = nota.calcular_nota_final(10.0, PRAZO, PRAZO + UM_SEGUNDO, False, None)
    r2 = nota.calcular_nota_final(10.0, PRAZO, PRAZO + UM_DIA, False, None)
    r3 = nota.calcular_nota_final(10.0, PRAZO, PRAZO + UM_DIA + UM_SEGUNDO, False, None)
    assert (r1.dias_atraso, r1.nota_final) == (1, 9.0)
    assert (r2.dias_atraso, r2.nota_final) == (1, 9.0)
    assert (r3.dias_atraso, r3.nota_final) == (2, 8.0)


def test_rf003_desconto_nao_passa_de_50_por_cento():
    r1 = nota.calcular_nota_final(10.0, PRAZO, PRAZO + 4 * UM_DIA + UM_SEGUNDO, False, None)
    r2 = nota.calcular_nota_final(10.0, PRAZO, PRAZO + 5 * UM_DIA, False, None)
    for r in (r1, r2):
        assert r.desconto_percentual == 50
        assert r.nota_final == 5.0


def test_rf004_entrega_apos_5_dias_e_rejeitada():
    r = nota.calcular_nota_final(10.0, PRAZO, PRAZO + 5 * UM_DIA + UM_SEGUNDO, False, None)
    assert r.aceita is False
    assert r.nota_final is None
    assert r.desconto_percentual is None
    assert r.situacao == "REJEITADA"
    assert r.dias_atraso == 6


def test_rf005_justificativa_aprovada_dentro_do_novo_prazo_sem_desconto():
    novo = PRAZO + 7 * UM_DIA
    r = nota.calcular_nota_final(10.0, PRAZO, PRAZO + 6 * UM_DIA, True, novo)
    assert r.aceita is True
    assert r.nota_final == 10.0
    assert r.desconto_percentual == 0
    assert r.prazo_considerado == novo


def test_rf006_justificativa_aprovada_apos_novo_prazo_conta_atraso_do_novo_prazo():
    novo = PRAZO + 3 * UM_DIA
    r = nota.calcular_nota_final(10.0, PRAZO, novo + UMA_HORA, True, novo)
    assert r.desconto_percentual == 10
    assert r.nota_final == 9.0
    assert r.dias_atraso == 1
    assert r.prazo_considerado == novo


def test_rf007_justificativa_sem_novo_prazo_valido_gera_erro():
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, PRAZO, PRAZO, True, None)
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, PRAZO, PRAZO, True, PRAZO)


def test_rf008_novo_prazo_sem_justificativa_aprovada_e_ignorado():
    r = nota.calcular_nota_final(10.0, PRAZO, PRAZO + UMA_HORA, False, PRAZO + 7 * UM_DIA)
    assert r.desconto_percentual == 10
    assert r.prazo_considerado == PRAZO


def test_rf009_resultado_traz_dados_para_registro():
    entrega = PRAZO + 2 * UMA_HORA
    r = nota.calcular_nota_final(7.0, PRAZO, entrega, False, None)
    assert r.entregue_em == entrega
    assert r.prazo_considerado == PRAZO
    assert r.dias_atraso == 1
    assert r.desconto_percentual == 10
    assert r.nota_final == 6.3
    assert r.situacao == "ATRASADA"


def test_rf010_nota_invalida_gera_erro():
    for invalida in (-0.1, 10.01, "8", True, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            nota.calcular_nota_final(invalida, PRAZO, PRAZO, False, None)


def test_rf011_arredondamento_duas_casas_metade_para_cima():
    r1 = nota.calcular_nota_final(8.35, PRAZO, PRAZO + UMA_HORA, False, None)
    r2 = nota.calcular_nota_final(9.15, PRAZO, PRAZO + 2 * UM_DIA + UMA_HORA, False, None)
    assert r1.nota_final == 7.52
    assert r2.nota_final == 6.41


def test_rf012_fusos_misturados_geram_erro():
    entrega_com_fuso = datetime(2026, 11, 20, 23, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, PRAZO, entrega_com_fuso, False, None)


def test_rf013_tipos_incorretos_geram_erro():
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, "2026-11-20", PRAZO, False, None)
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, PRAZO, PRAZO, "sim", None)
    with pytest.raises(ValueError):
        nota.calcular_nota_final(10.0, PRAZO, PRAZO, True, "2026-11-27")


def test_rnf001_desempenho_10000_chamadas_em_menos_de_1_segundo():
    inicio = time.perf_counter()
    for i in range(10_000):
        nota.calcular_nota_final(9.5, PRAZO, PRAZO + (i % 6) * UM_DIA, False, None)
    assert time.perf_counter() - inicio < 1.0


def test_rnf002_precisao_exata_em_todas_as_combinacoes():
    casos = 0
    for passo in range(41):  # 0.00, 0.25, ..., 10.00
        n = passo * 0.25
        for dias in range(6):  # 0 a 5 dias de atraso
            r = nota.calcular_nota_final(n, PRAZO, PRAZO + dias * UM_DIA, False, None)
            esperado = (Decimal(str(n)) * Decimal(100 - 10 * dias) / Decimal(100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            assert Decimal(str(r.nota_final)) == esperado
            casos += 1
    assert casos == 246


def test_rnf003_mesma_entrada_gera_sempre_o_mesmo_resultado():
    resultados = {
        nota.calcular_nota_final(8.0, PRAZO, PRAZO + 2 * UM_DIA, False, None)
        for _ in range(1000)
    }
    assert len(resultados) == 1