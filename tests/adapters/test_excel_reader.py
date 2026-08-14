"""Tests for the block-report reader: input is the .xls 'block' format
(repeated header + data row(s) + TOTAL row per vehicle), same shape as
combustible_2026-08-07.xls. Fixtures below are real rows pulled straight
from that file (values verified by cross-referencing 43/44 of them against
the matching row in 2026-08 Carga Gasoil.xlsx's 'Total' sheet).
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

# Real row: Fecha de carga=2026-08-07 23:15:33 (hour 23 -> Turno T)
ROW_NIGHT_WITH_ODOMETRO = [
    "2026-08-07 23:15:33",
    "023 - MARTINEZ JOSE LUIS",
    "2026-08-07",
    "23:00",
    "SOL DE MAYO",
    400301.0,
    3.0,
    96.0,
    66077.0,
    372.0,
    10044.0,
    10030.0,
    "",
    "",
]

# Real row: Fecha de carga=2026-08-07 04:21:46 (hour 4 -> Turno M)
ROW_MORNING = [
    "2026-08-07 04:21:46",
    "204-MANA HORACIO",
    "2026-08-07",
    "23:00",
    "SOL DE MAYO",
    1186.0,
    8.0,
    138.0,
    0.0,
    401.0,
    0.0,
    0.0,
    "",
    "",
]

# Real row: the "Cuadro Nacional" edge case -- blank Serie, invalid Fecha
# Horario ("0000-00-00" instead of a real date).
ROW_CUADRO_NACIONAL = [
    "2026-08-07 20:00:00",
    "023 - MARTINEZ JOSE LUIS",
    "0000-00-00",
    "23:00",
    "SOL DE MAYO",
    "",
    136.0,
    146.0,
    286619.0,
    0.0,
    10039.0,
    9732.0,
    "Cuadro Nacional",
    "",
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
        ROW_NIGHT_WITH_ODOMETRO,
        _total_row(),
    ]

    records = parse_block_report_rows(rows)

    assert len(records) == 1


def test_maps_kms_kmsgps_control_and_controlanterior_to_the_total_sheet_names():
    # verified against the real Total sheet: Kms->Kms Odometro,
    # Kms GPS->Kms GPS Carga anterior, Control->Precinto NUEVO,
    # Control Anterior->Precinto ANTERIOR
    records = parse_block_report_rows([HEADER_ROW, ROW_NIGHT_WITH_ODOMETRO])

    record = records[0]
    assert record.kms_odometro == 66077.0
    assert record.kms_gps_carga_anterior == 372.0
    assert record.precinto_nuevo == 10044.0
    assert record.precinto_anterior == 10030.0
    assert record.litros == 96.0
    assert record.responsable == "023 - MARTINEZ JOSE LUIS"
    assert record.serie == "400301"
    assert record.coche == "3"


def test_fecha_puente_comes_from_fecha_horario_date_part():
    records = parse_block_report_rows([HEADER_ROW, ROW_NIGHT_WITH_ODOMETRO])

    assert records[0].fecha_puente == datetime(2026, 8, 7)


def test_turno_is_derived_from_the_hour_not_read_from_the_source():
    # verified against all 255 real rows of the Total sheet: 0 mismatches
    night_records = parse_block_report_rows([HEADER_ROW, ROW_NIGHT_WITH_ODOMETRO])
    morning_records = parse_block_report_rows([HEADER_ROW, ROW_MORNING])

    assert night_records[0].turno == "T"  # hour 23
    assert morning_records[0].turno == "M"  # hour 4


def test_urea_and_tipo_combustible_are_always_blank_not_read_from_source():
    records = parse_block_report_rows([HEADER_ROW, ROW_NIGHT_WITH_ODOMETRO])

    assert records[0].urea is None
    assert records[0].tipo_combustible == ""


def test_falls_back_to_fecha_de_carga_date_when_fecha_horario_is_invalid():
    """Real edge case: 2 rows in the source have Fecha Horario = '0000-00-00'."""
    records = parse_block_report_rows([HEADER_ROW, ROW_CUADRO_NACIONAL])

    assert records[0].fecha_puente == datetime(2026, 8, 7)


def test_blank_serie_becomes_empty_text():
    records = parse_block_report_rows([HEADER_ROW, ROW_CUADRO_NACIONAL])

    assert records[0].serie == ""
    assert records[0].coche == "136"


def test_ignores_horario_destino_ubicacion_and_observacion():
    """Those 4 source columns are dropped entirely -- not part of the output."""
    records = parse_block_report_rows([HEADER_ROW, ROW_NIGHT_WITH_ODOMETRO])

    fields = vars(records[0])
    assert "horario" not in fields
    assert "destino" not in fields
    assert "ubicacion" not in fields
    assert "observacion" not in fields


def test_extracts_multiple_blocks_and_skips_grand_total_row():
    rows = [
        HEADER_ROW,
        ROW_NIGHT_WITH_ODOMETRO,
        _total_row(),
        HEADER_ROW,
        ROW_MORNING,
        _total_row(),
        [" ", " ", " ", " ", "TOTAL GENERAL", " ", " ", 239.0, 0.0, 842.0, "0.00 km/lt", "3.52 km/lt", "", ""],
    ]

    records = parse_block_report_rows(rows)

    assert len(records) == 2


def test_a_vehicle_can_load_fuel_more_than_once_in_the_same_block():
    rows = [
        HEADER_ROW,
        ROW_MORNING,
        ROW_NIGHT_WITH_ODOMETRO,
        _total_row(),
    ]

    records = parse_block_report_rows(rows)

    assert len(records) == 2
