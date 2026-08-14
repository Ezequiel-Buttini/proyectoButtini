"""Pure transformation logic: sort, dedupe and (re)compute consumption for
the raw fuel load records. Doesn't know about Excel or the UI.
"""

from collections.abc import Iterable

from app.domain.models import CleanedRecord, FuelLoadRecord


def _consumo(litros: float, kms_gps_carga_anterior: float) -> float:
    """Reproduces the source file's own formula:
    =IFERROR((Litros/KmsGPS)*100, 0), rounded to 2 decimals -- verified
    against real rows from both source files."""
    if kms_gps_carga_anterior == 0:
        return 0.0
    return round(litros / kms_gps_carga_anterior * 100, 2)


def _consumo_lts_c_100km(consumo: float) -> str:
    """Reproduces =REPT("||", Consumo). Excel's REPT truncates its count to
    an integer (verified: floor matches 246/246 rows, round only 133/246)."""
    return "||" * int(consumo)


def build_report(records: Iterable[FuelLoadRecord]) -> list[CleanedRecord]:
    ordered = sorted(records, key=lambda record: record.fecha_carga)
    deduplicated = list(dict.fromkeys(ordered))
    rows = []
    for record in deduplicated:
        consumo = _consumo(record.litros, record.kms_gps_carga_anterior)
        rows.append(
            CleanedRecord(
                record=record,
                consumo=consumo,
                consumo_lts_c_100km=_consumo_lts_c_100km(consumo),
            )
        )
    return rows
