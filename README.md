# ProyectoButtini

Web app full-stack con arquitectura en 3 capas, backend y frontend separados por carpetas.

## Estructura

```
proyectoButtini/
  backend/            # FastAPI + MongoDB
    app/
      api/            # Capa de presentacion: routers HTTP
      services/       # Capa de logica de negocio
      repositories/   # Capa de acceso a datos (Mongo)
      models/         # Esquemas / entidades de dominio
      core/           # Configuracion y conexion a base de datos
      main.py
    tests/
      unit/
      integration/
  frontend/           # React + Vite + TypeScript
    src/
      components/
      pages/
      services/       # Clientes HTTP hacia el backend
```

El backend sigue una arquitectura en capas con inyeccion de dependencias:
`api` depende de `services`, `services` depende de una abstraccion de
`repositories` (no de Mongo directamente), lo que permite testear la
logica de negocio sin una base de datos real.

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Tests (TDD: correlos antes de tocar codigo)
pytest

# Levantar el servidor
uvicorn app.main:app --reload
```

Variables de entorno (`.env` en `backend/`, opcional):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=proyecto_buttini
```

## Frontend

```bash
cd frontend
npm install

# Tests
npm test

# Servidor de desarrollo (proxea /health hacia http://localhost:8000)
npm run dev
```

## Metodologia

Este proyecto sigue TDD (Red-Green-Refactor): cada funcionalidad nueva se
implementa escribiendo primero el test que define el comportamiento
esperado, luego el codigo minimo para pasarlo, y por ultimo se evalua si
conviene refactorizar.
