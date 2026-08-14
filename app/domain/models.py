"""Domain models for fuel load records. Pure Python, no I/O or UI dependencies."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FuelLoadRecord:
    """A single fuel load event, exactly as extracted from the source -- raw
    values only. Consumo / Consumo Lts c/100km are NOT here: they get
    (re)computed downstream instead of trusting whatever was cached in the
    source file's formula cells.
    """

    fecha_carga: datetime
    fecha_puente: datetime
    responsable: str
    turno: str
    serie: str
    coche: str
    litros: float
    urea: float | None
    kms_odometro: float
    kms_gps_carga_anterior: float
    precinto_nuevo: float
    precinto_anterior: float
    tipo_combustible: str


@dataclass(frozen=True)
class CleanedRecord:
    """A FuelLoadRecord plus its freshly computed consumption figures, ready
    to be written out as one row of the ordered report."""

    record: FuelLoadRecord
    consumo: float
    consumo_lts_c_100km: str
