# ProyectoButtini

App de escritorio en Python que toma el Excel desordenado de carga de
combustible (una hoja llena de columnas e info que no se usa) y devuelve
un Excel prolijo, ordenado cronológicamente. No guarda nada de forma
permanente: procesa el archivo en memoria y listo.

## Estructura

```
app/
  domain/                  # Logica de reordenamiento. Python puro, sin
    models.py              # dependencias de openpyxl ni de la UI -- se
    reorder.py             # testea con datos en memoria, sin abrir archivos.
  adapters/
    excel_reader.py        # Lee el Excel .xls de entrada (formato de bloques).
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
   (formato Excel 97-2003, el que exporta el sistema viejo) con la forma
   de "bloques": un encabezado repetido (Fecha de carga, Responsable,
   Fecha Horario, Horario, Destino, Serie, Coche, Litros, Kms, Kms GPS,
   Control, Control Anterior, Ubicación, Observacion) seguido de una o
   más filas de datos y una fila `TOTAL` por cada vehículo.
3. Al confirmar, la app procesa el archivo y muestra un cartel "Listo"
   con la ruta del archivo generado.
4. El archivo de salida se guarda **en la misma carpeta que el de
   entrada**, como `.xlsx`, con el mismo nombre + `_ordenado`. Ej: si
   elegís `combustible_2026-08-07.xls`, se genera
   `combustible_2026-08-07_ordenado.xlsx` al lado.
5. Abrí ese `_ordenado.xlsx` y verificá que:
   - Las filas estén en orden cronológico (fecha/hora ascendente) — el
     archivo de entrada normalmente viene agrupado por vehículo, no por
     hora, así que el orden va a cambiar bastante respecto al original.
   - Cada carga tenga su propio bloque: encabezado + fila de datos + fila
     `TOTAL` con el ratio km/lt de esa carga.
   - Al final haya una fila `TOTAL GENERAL` con la suma de litros y km
     GPS de todo el archivo.

### Si algo falla

Si el botón tira un error, la app lo muestra completo en un cartel (no
falla en silencio). Casos esperados de error:
- El diálogo solo deja elegir `.xls` — si tu archivo es `.xlsx`, no va a
  aparecer en la lista (todavía no está soportado ese formato para la
  entrada).
- Si el archivo no tiene la forma de bloques esperada (encabezados +
  filas de datos + TOTAL), la app puede no encontrar ningún registro o
  fallar al leer una fecha.

## Qué NO hace todavía (fuera de alcance de esta primera etapa)

- No filtra por fecha ni por responsable: procesa el archivo entero de una.
- No valida el archivo antes de procesarlo más allá de lo que ya cubren
  los tests.
- Solo acepta `.xls` como entrada (no `.xlsx`) — es el formato en el que
  llega el archivo real hoy.
- Las columnas `Fecha Horario`, `Horario` y `Destino` del Excel de
  entrada se descartan (no hay forma confiable de mantenerlas una vez
  reordenado todo cronológicamente). `Ubicación` y `Observacion` sí se
  conservan cuando el archivo de entrada las trae cargadas.
- No hay mapeos configurables ni histórico guardado: cada corrida es
  independiente.

## Metodología

Este proyecto sigue TDD estricto (Red-Green-Refactor): cada
funcionalidad nueva se implementa escribiendo primero el test que define
el comportamiento esperado (Red), después el código mínimo para pasarlo
(Green), y por último se evalúa si conviene refactorizar. Varios casos
reales del Excel de agosto (por ejemplo, `Coche` con el valor de texto
"Taller" en vez de un número) se detectaron probando contra el archivo
real y se incorporaron como tests de regresión antes de arreglarlos.
