"""Thin PySide6 window: picks a file, runs the use case, reports the result.

No business logic lives here on purpose -- everything testable already lives in
app.domain / app.adapters / app.application, exercised without ever importing Qt.
"""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app.adapters.excel_reader import OpenpyxlFuelLoadReader
from app.adapters.excel_writer import OpenpyxlReportWriter
from app.application.generate_report import GenerateOrderedReport

WINDOW_TITLE = "Ordenar carga de combustible"
OUTPUT_SUFFIX = "_ordenado"


def _default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}{OUTPUT_SUFFIX}.xlsx")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)

        self._status_label = QLabel("Elegí el Excel de cargas de combustible a ordenar.")
        self._status_label.setWordWrap(True)

        pick_button = QPushButton("Elegir Excel y generar reporte")
        pick_button.clicked.connect(self._on_pick_file)

        layout = QVBoxLayout()
        layout.addWidget(self._status_label)
        layout.addWidget(pick_button)
        self.setLayout(layout)

    def _on_pick_file(self) -> None:
        input_path_str, _ = QFileDialog.getOpenFileName(
            self, "Elegir Excel de entrada", "", "Excel (*.xlsx)"
        )
        if not input_path_str:
            return

        input_path = Path(input_path_str)
        output_path = _default_output_path(input_path)
        use_case = GenerateOrderedReport(
            reader=OpenpyxlFuelLoadReader(), writer=OpenpyxlReportWriter()
        )

        try:
            use_case.run(input_path=input_path, output_path=output_path)
        except Exception as error:  # surfaced to the user, not swallowed
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{error}")
            return

        self._status_label.setText(f"Listo. Archivo generado en:\n{output_path}")
        QMessageBox.information(self, "Listo", f"Reporte generado en:\n{output_path}")
