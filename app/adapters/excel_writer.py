"""Writes the cleaned, ordered rows out to a flat .xlsx -- same column
schema as the source (Fecha de carga ... Consumo Lts c/100km), one row per
record, no block/TOTAL structure.
"""

from pathlib import Path
from typing import Protocol

import openpyxl

from app.domain.models import CleanedRecord

HEADER = [
    "Fecha de carga",
    "Fecha puente",
    "Responsable",
    "Turno",
    "Serie",
    "Coche",
    "Litros",
    "UREA",
    "Kms Odometro",
    "Kms GPS Carga anterior",
    "Precinto Nuevo",
    "Precinto Anterior",
    "Tipo de Combustible",
    "Consumo",
    "Consumo Lts c/100km",
]


class ReportWriter(Protocol):
    def write(self, rows: list[CleanedRecord], path: Path) -> None: ...


def _fecha_carga_text(cleaned_row: CleanedRecord) -> str:
    return cleaned_row.record.fecha_carga.strftime("%Y-%m-%d %H:%M:%S")


def _row(cleaned_row: CleanedRecord) -> list:
    record = cleaned_row.record
    return [
        _fecha_carga_text(cleaned_row),
        record.fecha_puente,
        record.responsable,
        record.turno,
        record.serie,
        record.coche,
        record.litros,
        record.urea,
        record.kms_odometro,
        record.kms_gps_carga_anterior,
        record.precinto_nuevo,
        record.precinto_anterior,
        record.tipo_combustible,
        cleaned_row.consumo,
        cleaned_row.consumo_lts_c_100km,
    ]


class OpenpyxlReportWriter:
    """Concrete ReportWriter backed by openpyxl."""

    def write(self, rows: list[CleanedRecord], path: Path) -> None:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(HEADER)
        for cleaned_row in rows:
            sheet.append(_row(cleaned_row))
        workbook.save(path)
