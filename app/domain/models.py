"""Domain models for fuel load records. Pure Python, no I/O or UI dependencies."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FuelLoadRecord:
    """A single fuel load event, already normalized from whatever source it came from."""

    fecha_carga: datetime
    responsable: str
    serie: str
    coche: str
    litros: float
    kms: float
    kms_gps: float
    control: float
    control_anterior: float


@dataclass(frozen=True)
class ReportBlock:
    """One record plus its own subtotal, ready to be rendered as a block in the report."""

    record: FuelLoadRecord
    kilometros_por_litro: float


@dataclass(frozen=True)
class ReportTotals:
    """Grand total row for the whole report."""

    litros: float
    kms_gps: float
    kilometros_por_litro: float
