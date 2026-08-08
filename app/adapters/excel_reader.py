"""Reads fuel load records from the messy input workbook (the 'Total' sheet)."""

from datetime import datetime
from pathlib import Path
from typing import Protocol

import openpyxl

from app.domain.models import FuelLoadRecord

SHEET_NAME = "Total"

# Real headers have stray whitespace (e.g. "Kms Odometro "), so we match by
# stripped text rather than exact position.
_COLUMN_FECHA_CARGA = "fecha de carga"
_COLUMN_RESPONSABLE = "responsable"
_COLUMN_SERIE = "serie"
_COLUMN_COCHE = "coche"
_COLUMN_LITROS = "litros"
_COLUMN_KMS = "kms odometro"
_COLUMN_KMS_GPS = "kms gps carga anterior"
_COLUMN_CONTROL = "precinto nuevo"
_COLUMN_CONTROL_ANTERIOR = "precinto anterior"


class FuelLoadReader(Protocol):
    def read(self, path: Path) -> list[FuelLoadRecord]: ...


def _normalize(header: object) -> str:
    return str(header).strip().lower()


def _as_float(value: object) -> float:
    return float(value) if value is not None else 0.0


def _as_text(value: object) -> str:
    return "" if value is None else str(value)


def _parse_fecha_carga(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d %H:%M:%S")


class OpenpyxlFuelLoadReader:
    """Concrete FuelLoadReader backed by openpyxl."""

    def read(self, path: Path) -> list[FuelLoadRecord]:
        workbook = openpyxl.load_workbook(path, data_only=True)
        sheet = workbook[SHEET_NAME]

        rows = sheet.iter_rows(values_only=True)
        header = [_normalize(cell) for cell in next(rows)]
        column_index = {name: header.index(name) for name in header}

        records = []
        for row in rows:
            if row[column_index[_COLUMN_FECHA_CARGA]] is None:
                continue
            records.append(
                FuelLoadRecord(
                    fecha_carga=_parse_fecha_carga(row[column_index[_COLUMN_FECHA_CARGA]]),
                    responsable=_as_text(row[column_index[_COLUMN_RESPONSABLE]]),
                    serie=_as_text(row[column_index[_COLUMN_SERIE]]),
                    coche=_as_text(row[column_index[_COLUMN_COCHE]]),
                    litros=_as_float(row[column_index[_COLUMN_LITROS]]),
                    kms=_as_float(row[column_index[_COLUMN_KMS]]),
                    kms_gps=_as_float(row[column_index[_COLUMN_KMS_GPS]]),
                    control=_as_float(row[column_index[_COLUMN_CONTROL]]),
                    control_anterior=_as_float(row[column_index[_COLUMN_CONTROL_ANTERIOR]]),
                )
            )
        return records
