# ProyectoButtini

App de escritorio en Python que toma el Excel de carga de combustible tal
como lo exporta el sistema actual (`.xls`, formato "por bloques": un
encabezado repetido + fila de datos + fila TOTAL por cada carga) y
devuelve un Excel prolijo en formato de tabla plana (mismas columnas que
la hoja "Total" de `Carga Gasoil.xlsx`): ordenado cronológicamente, sin
duplicados, y con `Consumo` / `Consumo Lts c/100km` calculados
correctamente. No guarda nada de forma permanente: procesa el archivo en
memoria y listo.

## Estructura

```
app/
  domain/                  # Logica de reordenamiento. Python puro, sin
    models.py              # dependencias de openpyxl/xlrd ni de la UI --
    reorder.py             # se testea con datos en memoria, sin abrir archivos.
  adapters/
    excel_reader.py        # Lee el Excel .xls de entrada (formato de bloques).
    excel_writer.py         # Escribe el Excel .xlsx ordenado de salida (tabla plana).
  application/
    generate_report.py     # Caso de uso: orquesta reader -> reorder -> writer.
  ui/
    main_window.py          # Ventana PySide6 (un boton). Sin logica propia.
  main.py                   # Entrypoint de la app.
tests/                      # Un modulo de test por cada capa de arriba.
requirements.txt
pytest.ini
```

Arquitectura en capas con inversión de dependencias: `domain` no sabe que
existen Excel ni una interfaz gráfica; `application` depende de
abstracciones (`FuelLoadReader` / `ReportWriter`), no de openpyxl/xlrd
directamente. Esto permite testear toda la lógica de negocio sin abrir
archivos reales ni levantar la ventana.

## Instalación

Requiere Python 3.10+ (probado con 3.12 y 3.14 en Windows). Ninguna
dependencia (`openpyxl`, `xlrd`, `PySide6`, `pytest`) necesita compilar
nada nativo, así que no debería haber problemas de wheels.

```powershell
cd C:\Programas\ProyectoButtini
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Correr los tests

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

Deberías ver todos los tests en verde (uno por cada comportamiento de
`domain`, `adapters` y `application`).

## Probar la app con un Excel real

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.main
```

Se abre una ventana con un solo botón: **"Elegir Excel y generar
reporte"**.

1. Click en el botón.
2. En el diálogo, elegí el Excel de entrada. Tiene que ser un **`.xls`**
   (Excel 97-2003) con la forma de "bloques": encabezado repetido
   (Fecha de carga, Responsable, Fecha Horario, Horario, Destino, Serie,
   Coche, Litros, Kms, Kms GPS, Control, Control Anterior, Ubicación,
   Observacion) seguido de una o más filas de datos y una fila `TOTAL`
   por vehículo.
3. Al confirmar, la app procesa el archivo y muestra un cartel "Listo"
   con la ruta del archivo generado.
4. El archivo de salida se guarda **en la misma carpeta que el de
   entrada**, como `.xlsx`, con el mismo nombre + `_ordenado`. Ej: si
   elegís `combustible_2026-08-07.xls`, se genera
   `combustible_2026-08-07_ordenado.xlsx` al lado.
5. Abrí ese `_ordenado.xlsx` y verificá que:
   - Tenga las 15 columnas de la hoja "Total" (Fecha de carga, Fecha
     puente, Responsable, Turno, Serie, Coche, Litros, UREA, Kms
     Odometro, Kms GPS Carga anterior, Precinto Nuevo, Precinto
     Anterior, Tipo de Combustible, Consumo, Consumo Lts c/100km), en
     una tabla plana (sin bloques ni filas TOTAL).
   - Las filas estén en orden cronológico (fecha/hora ascendente).
   - `Consumo` tenga un valor con sentido en cada fila (no 0, salvo que
     `Kms GPS Carga anterior` sea 0) y `Consumo Lts c/100km` sea una
     barra de `||` de largo proporcional a `Consumo`.

### Si algo falla

Si el botón tira un error, la app lo muestra completo en un cartel (no
falla en silencio). Un caso esperado de error: si el archivo no tiene la
forma de bloques esperada, la app puede no encontrar ningún registro.

## Columnas derivadas o calculadas

El archivo de entrada (formato de bloques) no tiene todas las columnas de
la salida. Estas se completan así:

| Columna de salida | Cómo se obtiene |
|---|---|
| Fecha puente | Fecha (sin hora) de "Fecha Horario" del bloque; si ese valor es inválido (pasa en 2 registros reales, viene como `"0000-00-00"`), se usa la fecha de "Fecha de carga" |
| Turno | Derivado: hora de "Fecha de carga" < 13 → `M`, si no → `T` (verificado contra las 255 filas reales de `Carga Gasoil.xlsx`, 0 discrepancias) |
| Kms Odometro | = "Kms" del bloque |
| Kms GPS Carga anterior | = "Kms GPS" del bloque |
| Precinto Nuevo | = "Control" del bloque |
| Precinto Anterior | = "Control Anterior" del bloque |
| UREA | no existe en la entrada, siempre vacío |
| Tipo de Combustible | no existe en la entrada, siempre vacío |
| Consumo | `Litros / Kms GPS Carga anterior * 100`, redondeado a 2 decimales; `0` si `Kms GPS Carga anterior` es `0` |
| Consumo Lts c/100km | el caracter `"||"` repetido `floor(Consumo)` veces (barra visual, igual fórmula `=REPT("||", Consumo)` que usa `Carga Gasoil.xlsx` para su propia columna del mismo nombre) |

Las columnas `Horario`, `Destino`, `Ubicación` y `Observacion` del
archivo de entrada se descartan: no forman parte de la salida.

## Qué NO hace todavía (fuera de alcance de esta primera etapa)

- No filtra por fecha ni por responsable: procesa el archivo entero de una.
- No valida el archivo antes de procesarlo más allá de lo que ya cubren
  los tests.
- Solo acepta `.xls` (formato de bloques) como entrada.
- No hay mapeos configurables ni histórico guardado: cada corrida es
  independiente.

## Metodología

Este proyecto sigue TDD estricto (Red-Green-Refactor): cada
funcionalidad nueva se implementa escribiendo primero el test que define
el comportamiento esperado (Red), después el código mínimo para pasarlo
(Green), y por último se evalúa si conviene refactorizar. El mapeo de
columnas (Turno derivado por hora, Kms/Kms GPS/Control/Control Anterior,
la fórmula de Consumo) se verificó cruzando filas reales entre
`combustible_2026-08-07.xls` y `2026-08 Carga Gasoil.xlsx` antes de
programar nada, y varios de esos casos reales quedaron como fixtures de
test.
