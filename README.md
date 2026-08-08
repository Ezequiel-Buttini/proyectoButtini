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
    excel_reader.py        # Lee la hoja "Total" del Excel de entrada.
    excel_writer.py         # Escribe el Excel ordenado de salida.
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

Requiere **Python 3.12** (no usar 3.14: todavía no tiene wheels
precompilados para varias dependencias en Windows y falla la instalación).

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
2. En el diálogo, elegí el Excel de entrada (debe tener una hoja llamada
   **"Total"** con las columnas: Fecha de carga, Responsable, Serie, Coche,
   Litros, Kms Odometro, Kms GPS Carga anterior, Precinto NUEVO, Precinto
   ANTERIOR).
3. Al confirmar, la app procesa el archivo y muestra un cartel "Listo"
   con la ruta del archivo generado.
4. El archivo de salida se guarda **en la misma carpeta que el de
   entrada**, con el mismo nombre + `_ordenado`. Ej: si elegís
   `2026-08 Carga Gasoil.xlsx`, se genera
   `2026-08 Carga Gasoil_ordenado.xlsx` al lado.
5. Abrí ese `_ordenado.xlsx` y verificá que:
   - Las filas estén en orden cronológico (fecha/hora ascendente).
   - Cada carga tenga su propio bloque: encabezado + fila de datos + fila
     `TOTAL` con el ratio km/lt de esa carga.
   - Al final haya una fila `TOTAL GENERAL` con la suma de litros y km
     GPS de todo el archivo.

### Si algo falla

Si el botón tira un error, la app lo muestra completo en un cartel (no
falla en silencio). Un caso esperado de error: si el Excel elegido no
tiene una hoja llamada "Total" con esas columnas, la app no va a poder
procesarlo (por ahora está atado a ese formato específico).

## Qué NO hace todavía (fuera de alcance de esta primera etapa)

- No filtra por fecha ni por responsable: procesa el archivo entero de una.
- No valida el archivo antes de procesarlo más allá de lo que ya cubren
  los tests.
- Las columnas `Ubicación` y `Observacion` del Excel de salida siempre
  quedan vacías (esa información no está en el Excel de entrada).
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
