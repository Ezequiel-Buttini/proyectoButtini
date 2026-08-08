"""Writes an ordered Report out to an .xlsx file, one block per fuel load record."""

from pathlib import Path
from typing import Protocol

import openpyxl

from app.domain.models import ReportBlock
from app.domain.reorder import Report

HEADER = [
    "Fecha de carga",
    "Responsable",
    "Serie",
    "Coche",
    "Litros",
    "Kms",
    "Kms GPS",
    "Control",
    "Control Anterior",
    "Ubicación",
    "Observacion",
]

_FIXED_CONTROL = "0.00 km/lt"


class ReportWriter(Protocol):
    def write(self, report: Report, path: Path) -> None: ...


def _km_lt(value: float) -> str:
    return f"{value:.2f} km/lt"


def _fecha_carga_text(block: ReportBlock) -> str:
    return block.record.fecha_carga.strftime("%Y-%m-%d %H:%M:%S")


def _data_row(block: ReportBlock) -> list:
    record = block.record
    return [
        _fecha_carga_text(block),
        record.responsable,
        record.serie,
        record.coche,
        record.litros,
        record.kms,
        record.kms_gps,
        record.control,
        record.control_anterior,
        record.ubicacion,
        record.observacion,
    ]


def _total_row(block: ReportBlock) -> list:
    record = block.record
    return [
        "",
        "TOTAL",
        record.serie,
        record.coche,
        record.litros,
        0,
        record.kms_gps,
        _FIXED_CONTROL,
        _km_lt(block.kilometros_por_litro),
        "",
        "",
    ]


def _grand_total_row(report: Report) -> list:
    return [
        "",
        "TOTAL GENERAL",
        "",
        "",
        report.totals.litros,
        0,
        report.totals.kms_gps,
        _FIXED_CONTROL,
        _km_lt(report.totals.kilometros_por_litro),
        "",
        "",
    ]


class OpenpyxlReportWriter:
    """Concrete ReportWriter backed by openpyxl."""

    def write(self, report: Report, path: Path) -> None:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(HEADER)
        for block in report.blocks:
            sheet.append(_data_row(block))
            sheet.append(_total_row(block))
        sheet.append(_grand_total_row(report))
        workbook.save(path)
