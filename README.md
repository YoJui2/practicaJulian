# Preguntados

Juego web de preguntas para dos jugadores en el mismo navegador. Incluye una ruleta clásica animada, turnos alternados, puntaje y conexión con la API de preguntas existente.

## Requisitos

- Docker Desktop.
- Poetry.
- Node.js 20.19 o superior.
- PostgreSQL iniciado mediante Docker Compose.

## Primera instalación

1. Abrir Docker Desktop.
2. Instalar las dependencias de Python:

   ```bat
   poetry install
   ```

3. Instalar las dependencias del frontend:

   ```bat
   instalar-frontend.bat
   ```

4. Levantar PostgreSQL:

   ```bat
   docker compose up -d db
   ```

5. Cargar las preguntas una sola vez si la base está vacía:

   ```bat
   poetry run python -m app.load_data
   ```

   El cargador de OpenTriviaQA lee el dataset completo y descarta las preguntas
   inválidas, de más de 70 caracteres o de verdadero/falso. La API de juego
   también omite preguntas existentes que no cumplan esos criterios.

## Levantar el juego

La forma recomendada en Windows es ejecutar:

```bat
iniciar-juego.bat
```

El script abre FastAPI en una ventana y el frontend en la otra. Después entrar a:

- Juego: <http://localhost:5173>
- API: <http://localhost:8000>
- Documentación de la API: <http://localhost:8000/docs>

Para detener el juego, presionar `Ctrl+C` en la ventana del frontend y cerrar la ventana de la API. PostgreSQL puede detenerse con:

```bat
docker compose stop db
```

## Levantar manualmente

Si `node` y `npm` ya están disponibles en el `PATH`, abrir dos terminales en `D:\PracticasJulian`.

**Terminal 1 — PostgreSQL y API:**

```bat
docker compose up -d db
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**

```bat
cd frontend
npm install
npm run dev
```

El frontend usa `http://localhost:8000` y Vite queda fijado al puerto `5173`. FastAPI habilita CORS únicamente para `http://localhost:5173`.

## Probar los cambios

Para ejecutar formato, lint, tipos, tests y compilación del frontend, y después los tests de FastAPI:

```bat
verificar.bat
```

Comandos individuales cuando `npm` esté en el `PATH`:

```bat
npm --prefix frontend run quality
npm --prefix frontend run build
poetry run pytest
```

## Estructura principal

```text
app/                  API FastAPI y modelos SQLAlchemy
frontend/             Aplicación React + TypeScript + Vite
frontend/src/api/     Cliente HTTP y validación de respuestas
frontend/src/game/    Utilidades de respuestas y números aleatorios
frontend/src/components/  Ruleta
openspec/project.md   Declaración técnica del proyecto
tests/                Tests de la API
```

## Problemas frecuentes

- **`No se pudo conectar con la API`**: confirmar que `http://localhost:8000/docs` responda.
- **La pregunta no existe**: la base probablemente no tiene cargadas las preguntas. Ejecutar `poetry run python -m app.load_data`.
- **Puerto 5173 ocupado**: el puerto está fijado intencionalmente porque FastAPI solo permite CORS para ese origen. Liberar el puerto antes de iniciar.
- **Docker no responde**: abrir Docker Desktop y volver a ejecutar `docker compose up -d db`.
