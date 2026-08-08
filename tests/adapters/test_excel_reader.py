from datetime import datetime

import openpyxl
import pytest

from app.adapters.excel_reader import OpenpyxlFuelLoadReader

HEADERS = [
    "Fecha de carga",
    "Fecha puente",
    "Responsable",
    "Turno",
    "Serie",
    "Coche",
    "Litros",
    "UREA",
    "Kms Odometro ",
    "Kms GPS Carga anterior",
    "Precinto NUEVO",
    "Precinto ANTERIOR",
    "TIPO DE COMBUSTIBLE",
    "CONSUMO",
    "CONSUMO LTS C/100KM)",
]


@pytest.fixture
def messy_workbook_path(tmp_path):
    """Builds a small workbook that mimics the real 'Total' sheet's messy shape."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    sheet = wb.create_sheet("Total")
    sheet.append(HEADERS)
    sheet.append(
        [
            "2026-08-01 04:04:23",  # Fecha de carga (stored as text in the real file)
            datetime(2026, 8, 1),  # Fecha puente
            "023 - MARTINEZ JOSE LUIS",  # Responsable
            "M",  # Turno
            1461,  # Serie
            76,  # Coche
            109,  # Litros
            None,  # UREA
            0,  # Kms Odometro
            447,  # Kms GPS Carga anterior
            0,  # Precinto NUEVO
            0,  # Precinto ANTERIOR
            "INFINIA",  # TIPO DE COMBUSTIBLE
            24.38,  # CONSUMO
            "||||||||||",  # CONSUMO LTS C/100KM)
        ]
    )
    # Also add another sheet before "Total" to make sure the reader targets it by name,
    # not by position -- mirrors the real workbook having 6 sheets.
    wb.create_sheet("Parque Movil", 0)

    path = tmp_path / "input_sample.xlsx"
    wb.save(path)
    return path


def test_reads_fuel_load_records_from_total_sheet(messy_workbook_path):
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(messy_workbook_path)

    assert len(records) == 1
    record = records[0]
    assert record.fecha_carga == datetime(2026, 8, 1, 4, 4, 23)
    assert record.responsable == "023 - MARTINEZ JOSE LUIS"
    assert record.serie == "1461"
    assert record.coche == "76"
    assert record.litros == 109
    assert record.kms == 0
    assert record.kms_gps == 447
    assert record.control == 0
    assert record.control_anterior == 0


def _row(fecha_carga="2026-08-01 04:04:23", serie=1461, coche=76):
    return [
        fecha_carga,
        datetime(2026, 8, 1),
        "023 - MARTINEZ JOSE LUIS",
        "M",
        serie,
        coche,
        109,
        None,
        0,
        447,
        0,
        0,
        "INFINIA",
        24.38,
        "||||||||||",
    ]


def _build_workbook(tmp_path, rows):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    sheet = wb.create_sheet("Total")
    sheet.append(HEADERS)
    for row in rows:
        sheet.append(row)
    path = tmp_path / "input_sample.xlsx"
    wb.save(path)
    return path


def test_skips_blank_spacer_rows(tmp_path):
    path = _build_workbook(
        tmp_path,
        [
            _row(),
            [None] * len(HEADERS),  # blank spacer row, as found in real spreadsheets
        ],
    )
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(path)

    assert len(records) == 1


def test_keeps_non_numeric_serie_as_text(tmp_path):
    path = _build_workbook(tmp_path, [_row(serie="TURISMO")])
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(path)

    assert records[0].serie == "TURISMO"


def test_formats_float_serie_without_spurious_decimal(tmp_path):
    path = _build_workbook(tmp_path, [_row(serie=400301.0)])
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(path)

    assert records[0].serie == "400301"


def test_keeps_non_numeric_coche_as_text(tmp_path):
    """Real data has 'Taller' (workshop) instead of a vehicle number for some loads."""
    path = _build_workbook(tmp_path, [_row(coche="Taller")])
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(path)

    assert records[0].coche == "Taller"


def test_blank_serie_becomes_empty_text_not_literal_none(tmp_path):
    """Real data has rows (usually 'Taller' loads) with no Serie value at all."""
    path = _build_workbook(tmp_path, [_row(serie=None, coche="Taller")])
    reader = OpenpyxlFuelLoadReader()

    records = reader.read(path)

    assert records[0].serie == ""
