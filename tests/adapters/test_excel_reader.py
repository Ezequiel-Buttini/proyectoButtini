"""Tests for the block-report parser: header/data/TOTAL/TOTAL GENERAL rows,
exactly as xlrd hands them back (all numbers as float, blanks as "").
"""

from datetime import datetime

from app.adapters.excel_reader import parse_block_report_rows

HEADER_ROW = [
    "Fecha de carga",
    "Responsable",
    "Fecha Horario",
    "Horario",
    "Destino",
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


def _data_row(
    fecha_carga="2026-08-07 20:55:48",
    responsable="023 - MARTINEZ JOSE LUIS",
    serie=1644.0,
    coche=1.0,
    litros=136.0,
    kms=0.0,
    kms_gps=410.0,
    control=0.0,
    control_anterior=0.0,
    ubicacion="",
    observacion="",
):
    return [
        fecha_carga,
        responsable,
        "2026-08-07",
        "23:00",
        "SOL DE MAYO",
        serie,
        coche,
        litros,
        kms,
        kms_gps,
        control,
        control_anterior,
        ubicacion,
        observacion,
    ]


def _total_row(coche=1.0, litros=136.0, kms_gps=410.0, ratio="3.01 km/lt"):
    return [" ", " ", " ", " ", "TOTAL", " ", coche, litros, 0.0, kms_gps, "0.00 km/lt", ratio, "", ""]


def _blank_row():
    return [""] * len(HEADER_ROW)


def test_extracts_one_record_per_data_row_ignoring_headers_and_totals():
    rows = [
        ["DETALLE DE CARGA DE COMBUSTIBLES entre el 2026-08-07 y el 2026-08-07"],
        _blank_row(),
        _blank_row(),
        HEADER_ROW,
        _data_row(),
        _total_row(),
    ]

    records = parse_block_report_rows(rows)

    assert len(records) == 1
    record = records[0]
    assert record.fecha_carga == datetime(2026, 8, 7, 20, 55, 48)
    assert record.responsable == "023 - MARTINEZ JOSE LUIS"
    assert record.serie == "1644"
    assert record.coche == "1"
    assert record.litros == 136
    assert record.kms == 0
    assert record.kms_gps == 410
    assert record.control == 0
    assert record.control_anterior == 0


def test_extracts_multiple_blocks_and_skips_grand_total_row():
    rows = [
        HEADER_ROW,
        _data_row(coche=1.0, litros=136.0),
        _total_row(coche=1.0, litros=136.0),
        HEADER_ROW,
        _data_row(coche=2.0, litros=103.0),
        _total_row(coche=2.0, litros=103.0),
        [" ", " ", " ", " ", "TOTAL GENERAL", " ", " ", 239.0, 0.0, 842.0, "0.00 km/lt", "3.52 km/lt", "", ""],
    ]

    records = parse_block_report_rows(rows)

    assert [r.coche for r in records] == ["1", "2"]


def test_keeps_non_numeric_serie_and_coche_as_text():
    rows = [HEADER_ROW, _data_row(serie="TURISMO", coche="Taller")]

    records = parse_block_report_rows(rows)

    assert records[0].serie == "TURISMO"
    assert records[0].coche == "Taller"


def test_blank_serie_becomes_empty_text():
    rows = [HEADER_ROW, _data_row(serie="")]

    records = parse_block_report_rows(rows)

    assert records[0].serie == ""


def test_passes_through_ubicacion_and_observacion_when_present():
    rows = [HEADER_ROW, _data_row(ubicacion="Cuadro Nacional", observacion="")]

    records = parse_block_report_rows(rows)

    assert records[0].ubicacion == "Cuadro Nacional"
    assert records[0].observacion == ""


def test_a_vehicle_can_load_fuel_more_than_once_in_the_same_block():
    rows = [
        HEADER_ROW,
        _data_row(fecha_carga="2026-08-07 04:43:07", coche=11.0),
        _data_row(fecha_carga="2026-08-07 15:53:00", coche=11.0),
        _total_row(coche=11.0),
    ]

    records = parse_block_report_rows(rows)

    assert len(records) == 2
