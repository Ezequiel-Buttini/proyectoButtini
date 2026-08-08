"""Reads fuel load records from the real input: a 'block report' workbook
(repeated header + one or more data rows + a TOTAL row, per vehicle), the
same shape the old tool used to produce as its own output. One data row = one
FuelLoadRecord; header/TOTAL/TOTAL GENERAL/title/blank rows are all skipped.
"""

from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol

import xlrd

from app.domain.models import FuelLoadRecord

# Column positions in the block report (0-indexed). Fecha Horario, Horario,
# Destino, Ubicacion and Observacion exist in the source but only the first
# three are intentionally dropped -- there's no reliable source data for them
# once records get resorted chronologically.
_COL_FECHA_CARGA = 0
_COL_RESPONSABLE = 1
_COL_SERIE = 5
_COL_COCHE = 6
_COL_LITROS = 7
_COL_KMS = 8
_COL_KMS_GPS = 9
_COL_CONTROL = 10
_COL_CONTROL_ANTERIOR = 11
_COL_UBICACION = 12
_COL_OBSERVACION = 13

_FECHA_CARGA_FORMAT = "%Y-%m-%d %H:%M:%S"


class FuelLoadReader(Protocol):
    def read(self, path: Path) -> list[FuelLoadRecord]: ...


def _as_float(value: object) -> float:
    return 0.0 if value in (None, "") else float(value)


def _as_text(value: object) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _try_parse_fecha_carga(value: object) -> datetime | None:
    """A row is a data row exactly when its first cell is a real timestamp --
    title/header/blank/TOTAL rows all fail to parse and get skipped."""
    try:
        return datetime.strptime(str(value).strip(), _FECHA_CARGA_FORMAT)
    except ValueError:
        return None


def _cell(row: Sequence, index: int) -> object:
    return row[index] if index < len(row) else ""


def parse_block_report_rows(rows: Iterable[Sequence]) -> list[FuelLoadRecord]:
    records = []
    for row in rows:
        fecha_carga = _try_parse_fecha_carga(_cell(row, _COL_FECHA_CARGA))
        if fecha_carga is None:
            continue
        records.append(
            FuelLoadRecord(
                fecha_carga=fecha_carga,
                responsable=_as_text(_cell(row, _COL_RESPONSABLE)),
                serie=_as_text(_cell(row, _COL_SERIE)),
                coche=_as_text(_cell(row, _COL_COCHE)),
                litros=_as_float(_cell(row, _COL_LITROS)),
                kms=_as_float(_cell(row, _COL_KMS)),
                kms_gps=_as_float(_cell(row, _COL_KMS_GPS)),
                control=_as_float(_cell(row, _COL_CONTROL)),
                control_anterior=_as_float(_cell(row, _COL_CONTROL_ANTERIOR)),
                ubicacion=_as_text(_cell(row, _COL_UBICACION)),
                observacion=_as_text(_cell(row, _COL_OBSERVACION)),
            )
        )
    return records


class XlrdFuelLoadReader:
    """Concrete FuelLoadReader for legacy .xls block reports, backed by xlrd."""

    def read(self, path: Path) -> list[FuelLoadRecord]:
        book = xlrd.open_workbook(str(path), ignore_workbook_corruption=True)
        sheet = book.sheet_by_index(0)
        rows = (sheet.row_values(row_index) for row_index in range(sheet.nrows))
        return parse_block_report_rows(rows)
