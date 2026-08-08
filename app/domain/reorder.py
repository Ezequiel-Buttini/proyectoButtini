"""Pure transformation logic: turn raw fuel load records into an ordered report."""

from collections.abc import Iterable

from app.domain.models import FuelLoadRecord, ReportBlock, ReportTotals


class Report:
    def __init__(self, blocks: list[ReportBlock], totals: ReportTotals):
        self.blocks = blocks
        self.totals = totals


def _ratio(kms_gps: float, litros: float) -> float:
    if litros == 0:
        return 0.0
    return round(kms_gps / litros, 2)


def _totals_for(blocks: list[ReportBlock]) -> ReportTotals:
    total_litros = sum(block.record.litros for block in blocks)
    total_kms_gps = sum(block.record.kms_gps for block in blocks)
    return ReportTotals(
        litros=total_litros,
        kms_gps=total_kms_gps,
        kilometros_por_litro=_ratio(total_kms_gps, total_litros),
    )


def build_report(records: Iterable[FuelLoadRecord]) -> Report:
    ordered = sorted(records, key=lambda record: record.fecha_carga)
    blocks = [
        ReportBlock(record=record, kilometros_por_litro=_ratio(record.kms_gps, record.litros))
        for record in ordered
    ]
    return Report(blocks=blocks, totals=_totals_for(blocks))
