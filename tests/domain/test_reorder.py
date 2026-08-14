from datetime import datetime

from app.domain.models import FuelLoadRecord
from app.domain.reorder import build_report


def _record(**overrides):
    defaults = dict(
        fecha_carga=datetime(2026, 8, 7, 12, 0, 0),
        fecha_puente=datetime(2026, 8, 7),
        responsable="023 - MARTINEZ JOSE LUIS",
        turno="M",
        serie="1644",
        coche="1",
        litros=136,
        urea=None,
        kms_odometro=0,
        kms_gps_carga_anterior=410,
        precinto_nuevo=0,
        precinto_anterior=0,
        tipo_combustible="INFINIA",
    )
    defaults.update(overrides)
    return FuelLoadRecord(**defaults)


def test_sorts_records_by_fecha_carga_ascending():
    early = _record(fecha_carga=datetime(2026, 8, 7, 4, 43, 7), responsable="A")
    late = _record(fecha_carga=datetime(2026, 8, 7, 15, 53, 0), responsable="B")

    rows = build_report([late, early])

    assert [row.record.responsable for row in rows] == ["A", "B"]


def test_sorts_across_different_days():
    day1 = _record(fecha_carga=datetime(2026, 8, 1, 23, 0, 0), responsable="day1")
    day7 = _record(fecha_carga=datetime(2026, 8, 7, 0, 5, 0), responsable="day7")

    rows = build_report([day7, day1])

    assert [row.record.responsable for row in rows] == ["day1", "day7"]


def test_consumo_is_litros_over_kms_gps_times_100():
    record = _record(litros=148, kms_gps_carga_anterior=488)

    rows = build_report([record])

    # matches the real Excel formula =IFERROR((Litros/KmsGPS)*100,0), verified
    # against the real file: 148/488*100 = 30.327868852459016
    assert rows[0].consumo == 148 / 488 * 100


def test_consumo_is_zero_when_kms_gps_is_zero():
    record = _record(litros=135, kms_gps_carga_anterior=0)

    rows = build_report([record])

    assert rows[0].consumo == 0.0


def test_consumo_lts_c_100km_is_a_bar_of_pipe_pairs_truncated_not_rounded():
    # consumo = 148/488*100 = 30.327... -> Excel's REPT truncates to 30, not 31
    record = _record(litros=148, kms_gps_carga_anterior=488)

    rows = build_report([record])

    assert rows[0].consumo_lts_c_100km == "||" * 30


def test_consumo_lts_c_100km_is_empty_when_consumo_is_zero():
    record = _record(litros=135, kms_gps_carga_anterior=0)

    rows = build_report([record])

    assert rows[0].consumo_lts_c_100km == ""


def test_removes_exact_duplicate_records():
    record = _record()
    identical_copy = _record()

    rows = build_report([record, identical_copy])

    assert len(rows) == 1


def test_keeps_records_that_only_differ_in_one_field():
    record = _record(litros=136)
    different = _record(litros=200)

    rows = build_report([record, different])

    assert len(rows) == 2
