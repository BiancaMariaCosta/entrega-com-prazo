"""Cálculo da nota final de uma entrega com desconto por atraso (Issue #1)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

DESCONTO_POR_DIA = 10      # pontos percentuais por dia iniciado de atraso (regra 3)
DESCONTO_MAXIMO = 50       # teto do desconto, em % (regra 4)
LIMITE_DIAS_ATRASO = 5     # acima disso a entrega é rejeitada (regra 5)
NOTA_MINIMA = 0
NOTA_MAXIMA = 10
UM_DIA = timedelta(days=1)


@dataclass(frozen=True)
class ResultadoNota:
    """Resultado do cálculo, com os dados que o sistema precisa registrar (regra 8)."""

    aceita: bool
    nota_final: float | None
    desconto_percentual: int | None
    dias_atraso: int
    entregue_em: datetime
    prazo_considerado: datetime
    situacao: str  # "DENTRO_DO_PRAZO", "ATRASADA" ou "REJEITADA"


def _validar_nota(nota: int | float | Decimal) -> None:
    if isinstance(nota, bool) or not isinstance(nota, (int, float, Decimal)):
        raise ValueError("nota deve ser um número (int ou float), não booleano")
    if isinstance(nota, float) and not math.isfinite(nota):
        raise ValueError("nota não pode ser NaN nem infinito")
    if isinstance(nota, Decimal) and not nota.is_finite():
        raise ValueError("nota não pode ser NaN nem infinito")
    if not NOTA_MINIMA <= nota <= NOTA_MAXIMA:
        raise ValueError(f"nota deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}")


def _validar_datas(*datas) -> None:
    for d in datas:
        if not isinstance(d, datetime):
            raise ValueError("prazo, entrega e novo_prazo devem ser datetime")
    com_fuso = {d.utcoffset() is not None for d in datas}
    if len(com_fuso) > 1:
        raise ValueError("as datas devem ser todas com fuso horário ou todas sem")


def _tempo_decorrido(inicio: datetime, fim: datetime) -> timedelta:
    """Tempo real entre dois instantes; com fuso, compara em UTC (86.400 s por dia)."""
    if inicio.utcoffset() is not None:
        inicio = inicio.astimezone(timezone.utc)
        fim = fim.astimezone(timezone.utc)
    return fim - inicio


def _dias_iniciados(atraso: timedelta) -> int:
    """Conta períodos de 24 h iniciados: 1 segundo de atraso já conta 1 dia."""
    if atraso <= timedelta(0):
        return 0
    dias_completos, resto = divmod(atraso, UM_DIA)
    return dias_completos + (1 if resto else 0)


def calcular_nota_final(
    nota: int | float | Decimal,
    prazo: datetime,
    entrega: datetime,
    justificativa_aprovada: bool = False,
    novo_prazo: datetime | None = None,
) -> ResultadoNota:
    _validar_nota(nota)
    _validar_datas(prazo, entrega)
    if not isinstance(justificativa_aprovada, bool):
        raise ValueError("justificativa_aprovada deve ser True ou False")

    prazo_considerado = prazo
    if justificativa_aprovada:
        if novo_prazo is None:
            raise ValueError("justificativa aprovada exige novo_prazo")
        _validar_datas(prazo, entrega, novo_prazo)
        if _tempo_decorrido(prazo, novo_prazo) <= timedelta(0):
            raise ValueError("novo_prazo deve ser posterior ao prazo original")
        prazo_considerado = novo_prazo

    dias = _dias_iniciados(_tempo_decorrido(prazo_considerado, entrega))

    if dias > LIMITE_DIAS_ATRASO:
        return ResultadoNota(
            aceita=False,
            nota_final=None,
            desconto_percentual=None,
            dias_atraso=dias,
            entregue_em=entrega,
            prazo_considerado=prazo_considerado,
            situacao="REJEITADA",
        )

    desconto = min(dias * DESCONTO_POR_DIA, DESCONTO_MAXIMO)
    fator = Decimal(100 - desconto) / Decimal(100)
    final = (Decimal(str(nota)) * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return ResultadoNota(
        aceita=True,
        nota_final=float(final),
        desconto_percentual=desconto,
        dias_atraso=dias,
        entregue_em=entrega,
        prazo_considerado=prazo_considerado,
        situacao="DENTRO_DO_PRAZO" if dias == 0 else "ATRASADA",
    )