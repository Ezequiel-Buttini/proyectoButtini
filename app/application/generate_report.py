"""Use case: read raw fuel loads, reorder them, write the tidy report.

Depends only on the FuelLoadReader/ReportWriter protocols (dependency inversion) --
it doesn't know or care whether records come from openpyxl, a fake, or anything else.
"""

from pathlib import Path

from app.adapters.excel_reader import FuelLoadReader
from app.adapters.excel_writer import ReportWriter
from app.domain.reorder import build_report


class GenerateOrderedReport:
    def __init__(self, reader: FuelLoadReader, writer: ReportWriter):
        self._reader = reader
        self._writer = writer

    def run(self, input_path: Path, output_path: Path) -> None:
        records = self._reader.read(input_path)
        report = build_report(records)
        self._writer.write(report, output_path)
