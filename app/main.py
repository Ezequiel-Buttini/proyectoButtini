"""Entrypoint: wires concrete adapters and launches the desktop UI."""

import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> None:
    application = QApplication(sys.argv)
    window = MainWindow()
    window.resize(420, 160)
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
