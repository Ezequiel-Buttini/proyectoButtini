"""Reads raw fuel load records from the input: a 'block report' workbook
(.xls, repeated header + one or more data rows + a TOTAL row per vehicle,
the same shape as combustible_2026-08-07.xls). One data row = one
FuelLoadRecord; header/TOTAL/TOTAL GENERAL/title/blank rows are skipped.

Column mapping to the Total-sheet-shaped FuelLoadRecord (verified against
real data, see tests):
  Kms            -> kms_odometro
  Kms GPS        -> kms_gps_carga_anterior
  Control        -> precinto_nuevo
  Control Anterior -> precinto_anterior
  Fecha Horario  -> fecha_puente (date part; falls back to Fecha de carga's
                     own date when Fecha Horario is invalid, e.g. "0000-00-00")
  Turno          -> derived from the hour of Fecha de carga (< 13 -> "M",
                     else "T") -- the source has no Turno column at all
Horario, Destino, Ubicacion and Observacion are dropped: not part of the
output. UREA and Tipo de Combustible don't exist in this source, so they
are always blank.
"""

from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol

import xlrd

from app.domain.models import FuelLoadRecord

# Column positions in the block report (0-indexed).
_COL_FECHA_CARGA = 0
_COL_RESPONSABLE = 1
_COL_FECHA_HORARIO = 2
_COL_SERIE = 5
_COL_COCHE = 6
_COL_LITROS = 7
_COL_KMS = 8
_COL_KMS_GPS = 9
_COL_CONTROL = 10
_COL_CONTROL_ANTERIOR = 11

_FECHA_CARGA_FORMAT = "%Y-%m-%d %H:%M:%S"
_FECHA_HORARIO_FORMAT = "%Y-%m-%d"
_TURNO_CUTOFF_HOUR = 13


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


def _fecha_puente(fecha_horario: object, fecha_carga: datetime) -> datetime:
    try:
        return datetime.strptime(str(fecha_horario).strip(), _FECHA_HORARIO_FORMAT)
    except ValueError:
        # real data has rows with Fecha Horario = "0000-00-00" (invalid) --
        # fall back to Fecha de carga's own date, which is always valid.
        return datetime(fecha_carga.year, fecha_carga.month, fecha_carga.day)


def _turno(fecha_carga: datetime) -> str:
    return "M" if fecha_carga.hour < _TURNO_CUTOFF_HOUR else "T"


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
                fecha_puente=_fecha_puente(_cell(row, _COL_FECHA_HORARIO), fecha_carga),
                responsable=_as_text(_cell(row, _COL_RESPONSABLE)),
                turno=_turno(fecha_carga),
                serie=_as_text(_cell(row, _COL_SERIE)),
                coche=_as_text(_cell(row, _COL_COCHE)),
                litros=_as_float(_cell(row, _COL_LITROS)),
                urea=None,
                kms_odometro=_as_float(_cell(row, _COL_KMS)),
                kms_gps_carga_anterior=_as_float(_cell(row, _COL_KMS_GPS)),
                precinto_nuevo=_as_float(_cell(row, _COL_CONTROL)),
                precinto_anterior=_as_float(_cell(row, _COL_CONTROL_ANTERIOR)),
                tipo_combustible="",
            )
        )
    return records


class XlrdFuelLoadReader:
    """Concrete FuelLoadReader for the .xls block report, backed by xlrd."""

    def read(self, path: Path) -> list[FuelLoadRecord]:
        book = xlrd.open_workbook(str(path), ignore_workbook_corruption=True)
        sheet = book.sheet_by_index(0)
        rows = (sheet.row_values(row_index) for row_index in range(sheet.nrows))
        return parse_block_report_rows(rows)
