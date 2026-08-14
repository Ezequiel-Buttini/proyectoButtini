"""Reads raw fuel load records from the 'Total' sheet of the source workbook
(2026-08 Carga Gasoil.xlsx-shaped). Never reads the source's own Consumo /
Consumo Lts c/100km cells -- those are formula results we don't trust and
recompute fresh in the domain layer instead.
"""

from datetime import datetime
from pathlib import Path
from typing import Protocol

import openpyxl

from app.domain.models import FuelLoadRecord

SHEET_NAME = "Total"

# Real headers have stray whitespace (e.g. "Kms Odometro "), so columns are
# matched by stripped/lowercased text rather than position.
_COLUMN_FECHA_CARGA = "fecha de carga"
_COLUMN_FECHA_PUENTE = "fecha puente"
_COLUMN_RESPONSABLE = "responsable"
_COLUMN_TURNO = "turno"
_COLUMN_SERIE = "serie"
_COLUMN_COCHE = "coche"
_COLUMN_LITROS = "litros"
_COLUMN_UREA = "urea"
_COLUMN_KMS_ODOMETRO = "kms odometro"
_COLUMN_KMS_GPS = "kms gps carga anterior"
_COLUMN_PRECINTO_NUEVO = "precinto nuevo"
_COLUMN_PRECINTO_ANTERIOR = "precinto anterior"
_COLUMN_TIPO_COMBUSTIBLE = "tipo de combustible"


class FuelLoadReader(Protocol):
    def read(self, path: Path) -> list[FuelLoadRecord]: ...


def _normalize(header: object) -> str:
    return str(header).strip().lower()


def _as_float(value: object) -> float:
    return float(value) if value is not None else 0.0


def _as_optional_float(value: object) -> float | None:
    return None if value is None else float(value)


def _as_text(value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


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

        def cell(row, column_name):
            return row[column_index[column_name]]

        records = []
        for row in rows:
            if cell(row, _COLUMN_FECHA_CARGA) is None:
                continue
            records.append(
                FuelLoadRecord(
                    fecha_carga=_parse_fecha_carga(cell(row, _COLUMN_FECHA_CARGA)),
                    fecha_puente=cell(row, _COLUMN_FECHA_PUENTE),
                    responsable=_as_text(cell(row, _COLUMN_RESPONSABLE)),
                    turno=_as_text(cell(row, _COLUMN_TURNO)),
                    serie=_as_text(cell(row, _COLUMN_SERIE)),
                    coche=_as_text(cell(row, _COLUMN_COCHE)),
                    litros=_as_float(cell(row, _COLUMN_LITROS)),
                    urea=_as_optional_float(cell(row, _COLUMN_UREA)),
                    kms_odometro=_as_float(cell(row, _COLUMN_KMS_ODOMETRO)),
                    kms_gps_carga_anterior=_as_float(cell(row, _COLUMN_KMS_GPS)),
                    precinto_nuevo=_as_float(cell(row, _COLUMN_PRECINTO_NUEVO)),
                    precinto_anterior=_as_float(cell(row, _COLUMN_PRECINTO_ANTERIOR)),
                    tipo_combustible=_as_text(cell(row, _COLUMN_TIPO_COMBUSTIBLE)),
                )
            )
        return records
