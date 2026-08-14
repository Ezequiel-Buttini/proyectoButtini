from datetime import datetime
from pathlib import Path

from app.application.generate_report import GenerateOrderedReport
from app.domain.models import FuelLoadRecord


def _record(**overrides):
    defaults = dict(
        fecha_carga=datetime(2026, 8, 7, 12, 0, 0),
        fecha_puente=datetime(2026, 8, 7),
        responsable="R",
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


class FakeReader:
    """Test double: returns canned records instead of touching a real file."""

    def __init__(self, records):
        self._records = records
        self.received_path = None

    def read(self, path):
        self.received_path = path
        return self._records


class FakeWriter:
    """Test double: captures what it was asked to write instead of touching disk."""

    def __init__(self):
        self.received_rows = None
        self.received_path = None

    def write(self, rows, path):
        self.received_rows = rows
        self.received_path = path


def test_generate_ordered_report_reads_reorders_and_writes():
    early = _record(fecha_carga=datetime(2026, 8, 7, 4, 43, 7), responsable="early")
    late = _record(fecha_carga=datetime(2026, 8, 7, 15, 53, 0), responsable="late")
    reader = FakeReader([late, early])
    writer = FakeWriter()
    use_case = GenerateOrderedReport(reader=reader, writer=writer)

    input_path = Path("input.xlsx")
    output_path = Path("output.xlsx")
    use_case.run(input_path=input_path, output_path=output_path)

    assert reader.received_path == input_path
    assert writer.received_path == output_path
    assert [row.record.responsable for row in writer.received_rows] == [
        "early",
        "late",
    ]
