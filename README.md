# ProyectoButtini

App de escritorio en Python que toma el Excel desordenado de carga de
combustible (`2026-08 Carga Gasoil.xlsx`, hoja "Total") y devuelve un
Excel prolijo: mismas columnas, ordenado cronológicamente, sin
duplicados, y con `Consumo` / `Consumo Lts c/100km` recalculados
correctamente. No guarda nada de forma permanente: procesa el archivo en
memoria y listo.

## Estructura

```
app/
  domain/                  # Logica de reordenamiento. Python puro, sin
    models.py              # dependencias de openpyxl ni de la UI -- se
    reorder.py             # testea con datos en memoria, sin abrir archivos.
  adapters/
    excel_reader.py        # Lee la hoja "Total" del Excel de entrada (.xlsx).
    excel_writer.py         # Escribe el Excel .xlsx ordenado de salida.
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
abstracciones (`FuelLoadReader` / `ReportWriter`), no de openpyxl
directamente. Esto permite testear toda la lógica de negocio sin abrir
archivos reales ni levantar la ventana.

## Instalación

Requiere Python 3.10+ (probado con 3.12 y 3.14 en Windows). Ninguna
dependencia (`openpyxl`, `PySide6`, `pytest`) necesita compilar nada
nativo, así que no debería haber problemas de wheels.

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
2. En el diálogo, elegí el Excel de entrada. Tiene que ser un `.xlsx`
   con una hoja llamada **"Total"** con las columnas: Fecha de carga,
   Fecha puente, Responsable, Turno, Serie, Coche, Litros, UREA, Kms
   Odometro, Kms GPS Carga anterior, Precinto NUEVO, Precinto ANTERIOR,
   Tipo de Combustible, Consumo, Consumo Lts c/100km (las últimas dos se
   ignoran al leer -- se recalculan de cero).
3. Al confirmar, la app procesa el archivo y muestra un cartel "Listo"
   con la ruta del archivo generado.
4. El archivo de salida se guarda **en la misma carpeta que el de
   entrada**, con el mismo nombre + `_ordenado`. Ej: si elegís
   `2026-08 Carga Gasoil.xlsx`, se genera
   `2026-08 Carga Gasoil_ordenado.xlsx` al lado.
5. Abrí ese `_ordenado.xlsx` y verificá que:
   - Tenga las mismas 15 columnas que el original, en el mismo orden.
   - Las filas estén en orden cronológico (fecha/hora ascendente).
   - `Consumo` tenga un valor con sentido en cada fila (no 0, salvo que
     `Kms GPS Carga anterior` sea 0) y `Consumo Lts c/100km` sea una
     barra de `||` de largo proporcional a `Consumo`.

### Si algo falla

Si el botón tira un error, la app lo muestra completo en un cartel (no
falla en silencio). Un caso esperado de error: si el archivo no tiene una
hoja llamada "Total" con esas columnas, la app no va a poder procesarlo.

## Fórmulas recalculadas

`Consumo` y `Consumo Lts c/100km` **no** se copian del Excel de entrada
(esos valores pueden venir en 0 o rotos) -- se recalculan siempre, con la
misma fórmula que ya usa el Excel original (verificada contra la fórmula
real de la celda, no solo el valor cacheado):

- `Consumo = Litros / Kms GPS Carga anterior * 100`, o `0` si `Kms GPS
  Carga anterior` es `0` (igual que el `=IFERROR(...)` del original).
- `Consumo Lts c/100km` = el caracter `"||"` repetido `floor(Consumo)`
  veces (igual que el `=REPT("||", Consumo)` del original -- Excel trunca
  el conteo, no redondea).

## Qué NO hace todavía (fuera de alcance de esta primera etapa)

- No filtra por fecha ni por responsable: procesa el archivo entero de una.
- No valida el archivo antes de procesarlo más allá de lo que ya cubren
  los tests.
- Solo acepta `.xlsx` como entrada, con la hoja "Total" tal como la
  produce el sistema actual.
- No hay mapeos configurables ni histórico guardado: cada corrida es
  independiente.

## Metodología

Este proyecto sigue TDD estricto (Red-Green-Refactor): cada
funcionalidad nueva se implementa escribiendo primero el test que define
el comportamiento esperado (Red), después el código mínimo para pasarlo
(Green), y por último se evalúa si conviene refactorizar. Varios casos
reales del Excel de agosto (por ejemplo, `Coche` con el valor de texto
"Taller" en vez de un número, o la fórmula exacta de `Consumo`) se
confirmaron probando contra el archivo real antes de programarlos.
