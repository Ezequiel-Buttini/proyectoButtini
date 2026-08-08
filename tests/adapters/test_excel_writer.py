from datetime import datetime

import openpyxl

from app.adapters.excel_writer import OpenpyxlReportWriter
from app.domain.models import FuelLoadRecord
from app.domain.reorder import build_report

EXPECTED_HEADER = [
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


def _record(**overrides):
    defaults = dict(
        fecha_carga=datetime(2026, 8, 7, 20, 55, 48),
        responsable="023 - MARTINEZ JOSE LUIS",
        serie="1644",
        coche="1",
        litros=136,
        kms=0,
        kms_gps=410,
        control=0,
        control_anterior=0,
    )
    defaults.update(overrides)
    return FuelLoadRecord(**defaults)


def test_writes_header_data_and_total_row_for_a_single_block(tmp_path):
    report = build_report([_record()])
    path = tmp_path / "output.xlsx"

    OpenpyxlReportWriter().write(report, path)

    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    assert rows[0] == tuple(EXPECTED_HEADER)
    assert rows[1] == (
        "2026-08-07 20:55:48",
        "023 - MARTINEZ JOSE LUIS",
        "1644",
        "1",
        136,
        0,
        410,
        0,
        0,
        None,
        None,
    )
    assert rows[2] == (
        None,
        "TOTAL",
        "1644",
        "1",
        136,
        0,
        410,
        "0.00 km/lt",
        "3.01 km/lt",
        None,
        None,
    )


def test_writes_grand_total_row_after_all_blocks(tmp_path):
    report = build_report(
        [
            _record(coche="1", litros=136, kms_gps=410),
            _record(coche="2", litros=103, kms_gps=432),
        ]
    )
    path = tmp_path / "output.xlsx"

    OpenpyxlReportWriter().write(report, path)

    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    # header + (data + total) * 2 blocks + grand total = 1 + 4 + 1 = 6 rows
    assert len(rows) == 6
    assert rows[-1] == (
        None,
        "TOTAL GENERAL",
        None,
        None,
        239,
        0,
        842,
        "0.00 km/lt",
        "3.52 km/lt",
        None,
        None,
    )
