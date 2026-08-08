from datetime import datetime
from pathlib import Path

from app.application.generate_report import GenerateOrderedReport
from app.domain.models import FuelLoadRecord


def _record(**overrides):
    defaults = dict(
        fecha_carga=datetime(2026, 8, 7, 12, 0, 0),
        responsable="R",
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
        self.received_report = None
        self.received_path = None

    def write(self, report, path):
        self.received_report = report
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
    assert [block.record.responsable for block in writer.received_report.blocks] == [
        "early",
        "late",
    ]
