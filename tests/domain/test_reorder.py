from datetime import datetime

from app.domain.models import FuelLoadRecord
from app.domain.reorder import build_report


def _record(**overrides):
    defaults = dict(
        fecha_carga=datetime(2026, 8, 7, 12, 0, 0),
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


def test_build_report_sorts_records_by_fecha_carga_ascending():
    early = _record(fecha_carga=datetime(2026, 8, 7, 4, 43, 7), responsable="A")
    late = _record(fecha_carga=datetime(2026, 8, 7, 15, 53, 0), responsable="B")

    report = build_report([late, early])

    assert [block.record.responsable for block in report.blocks] == ["A", "B"]


def test_build_report_sorts_across_different_days():
    day1 = _record(fecha_carga=datetime(2026, 8, 1, 23, 0, 0), responsable="day1")
    day7 = _record(fecha_carga=datetime(2026, 8, 7, 0, 5, 0), responsable="day7")

    report = build_report([day7, day1])

    assert [block.record.responsable for block in report.blocks] == ["day1", "day7"]


def test_block_ratio_is_kms_gps_over_litros_rounded_to_two_decimals():
    record = _record(litros=136, kms_gps=410)

    report = build_report([record])

    # 410 / 136 = 3.014705... -> 3.01, matches the reference output file
    assert report.blocks[0].kilometros_por_litro == 3.01


def test_block_ratio_is_zero_when_litros_is_zero():
    record = _record(litros=0, kms_gps=0)

    report = build_report([record])

    assert report.blocks[0].kilometros_por_litro == 0.0


def test_report_totals_sum_litros_and_kms_gps_across_all_blocks():
    records = [
        _record(litros=136, kms_gps=410),
        _record(litros=103, kms_gps=432),
    ]

    report = build_report(records)

    assert report.totals.litros == 239
    assert report.totals.kms_gps == 842
    # 842 / 239 = 3.5230... -> 3.52
    assert report.totals.kilometros_por_litro == 3.52


def test_report_totals_ratio_is_zero_when_total_litros_is_zero():
    report = build_report([_record(litros=0, kms_gps=0)])

    assert report.totals.kilometros_por_litro == 0.0
