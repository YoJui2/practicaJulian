# Declaración del proyecto

## Qué es este sistema

Juego web de preguntas para dos personas que comparten el mismo dispositivo y navegador. Cada participante juega por turnos, la interfaz representa la selección mediante una ruleta clásica y la aplicación administra el puntaje de la partida. El frontend está construido con React y obtiene cada pregunta desde la API FastAPI local, que a su vez consulta PostgreSQL.

La prioridad funcional es que la ruleta, el turno activo, la pregunta solicitada y el puntaje siempre coincidan. El navegador no accede directamente a la base de datos y nunca se inventa o completa una pregunta si la API falla.

## Alcance de esta versión

Incluye:

- Partida local para dos jugadores en el mismo navegador.
- Ruleta clásica animada, turnos alternados, preguntas, respuestas y puntaje.
- Consulta de una pregunta por su identificador cuando el juego la necesita.
- Pantallas de carga, error y reintento para cuando falla la API.
- Interfaz responsive en español.

No incluye todavía:

- Multijugador entre dispositivos, salas, chat ni sincronización en tiempo real.
- Cuentas de usuario, autenticación, ranking persistente ni guardado de partida.
- Administración o edición de preguntas desde el frontend.
- Publicación en producción.

## Runtime y lenguajes

| | |
|---|---|
| Lenguaje y versión | TypeScript 5.x en modo estricto para el frontend; Python >=3.11,<3.15 para la API |
| Runtime del frontend | Node.js >=20.19 y npm |
| Fijado por | `package-lock.json` para React; `poetry.lock` para Python; imagen `postgres:15` para la base |
| Un comando para compilar | `npm run build` |
| Un comando para probar | `npm test` |
| Un comando para lint y formato | `npm run quality` |
| Un comando para verificar tipos | `npm run typecheck` |
| Cobertura | Mínimo 80% en statements, branches, functions y lines del código frontend; la lógica de juego y los cambios de comportamiento deben tener cobertura integral |

Los scripts anteriores son los comandos públicos del workspace y deben vivir en la raíz para no obligar a recordar si se está trabajando sobre el frontend o la API. El primer scaffold del frontend debe crearlos. Python no requiere una fase de compilación separada.

## Frameworks y librerías

- **Frontend / UI**: React con TypeScript y Vite. React administra la interfaz; los componentes no realizan consultas HTTP directamente.
- **Estado**: `useReducer` y Context de React para el estado de partida. No se incorpora Redux u otra librería global sin un cambio de especificación y su ADR.
- **Estilos**: CSS Modules, custom properties de CSS y animación de la ruleta con CSS. No se usa un framework visual que imponga sus propios colores o componentes.
- **Cliente HTTP**: `fetch` encapsulado en un cliente de API tipado. El punto de entrada a la API se configura con `VITE_API_BASE_URL`.
- **Web / API**: FastAPI. Valida la entrada, consulta los datos y define la respuesta de preguntas.
- **Acceso a datos**: SQLAlchemy, exclusivamente en la API. PostgreSQL nunca se expone al navegador.
- **Trabajo en segundo plano**: no hay colas ni tareas asíncronas en esta versión.
- **Calidad**: ESLint y Prettier para el frontend; pytest para la API existente.
- **Testing frontend**: Vitest, React Testing Library y user-event. Las respuestas de red se prueban como datos controlados o mediante un mock del cliente, sin exigir PostgreSQL en cada prueba de componente.
- **Testing de la API**: pytest conserva sus niveles unitario, integración, validación y calidad de datos. Las pruebas de integración sustituyen PostgreSQL por SQLite en memoria.

## Contrato de preguntas

La ruta real definida actualmente por FastAPI es **plural**:

```http
GET http://localhost:8000/questions/{question_id}
Accept: application/json
```

Respuesta de ejemplo:

```json
{
  "id": 42,
  "question": "¿Cuál es la capital de Argentina?",
  "answer": "Buenos Aires",
  "category": "Geografía",
  "source": null
}
```

El cliente representa esa respuesta con esta forma:

```ts
interface QuestionDto {
  id: number
  question: string
  answer: string
  category: string | null
  source: string | null
}
```

Reglas de integración:

- React solicita `question_id` en el momento en que la ruleta determina la pregunta; no descarga un lote de respuestas para mostrarlas por adelantado.
- Una respuesta es válida solo si contiene un `id` numérico y textos no vacíos para `question` y `answer`.
- `category` y `source` pueden ser `null` y la interfaz debe seguir funcionando.
- Un body `{ "error": "Pregunta no encontrada" }` no se trata como una pregunta válida.
- Los errores de red, API o formato conservan el turno activo, muestran un mensaje accionable y permiten reintentar sin cambiar el puntaje.
- Como React y FastAPI se ejecutan en orígenes distintos durante el desarrollo, la API debe habilitar CORS para el origen del servidor de Vite, inicialmente `http://localhost:5173`.

La correspondencia entre una posición de la ruleta y un `question_id` se define en la especificación de la capacidad de juego; esta declaración solo fija el contrato de consulta.

## Datastores

| Store | Contiene | Migraciones ejecutadas por |
|---|---|---|
| PostgreSQL 15 | Preguntas y sus categorizaciones | Actualmente `Base.metadata.create_all` durante el arranque de la API; no hay herramienta de migraciones |
| SQLite en memoria | Datos aislados para tests de integración | Fixtures de pytest |

`admin` / `admin123` y `questions_db` son credenciales de desarrollo local definidas en `docker-compose.yml`; no son secretos de producción y no deben reutilizarse fuera de ese entorno. La versión actual no modifica el esquema de PostgreSQL. Cualquier cambio de esquema requiere una especificación y la incorporación explícita de migraciones.

## Identidad y autorización

- **Cómo se identifica una petición**: esta versión no tiene identidad ni usuarios registrados.
- **Dónde se autoriza**: la API no requiere autenticación y solo expone las operaciones existentes. El cliente no envía credenciales.
- **Jugador frente a servicio**: los dos jugadores son participantes de una sesión local del navegador; PostgreSQL y FastAPI no reciben una identidad de jugador.
- **Auditoría**: no se auditan partidas ni turnos. La puntuación y el progreso viven en memoria en el navegador y se reinician al recargar.

No se debe simular autorización en el frontend como sustituto de una futura autorización del servidor.

## Secretos

- Las variables `VITE_*` se incorporan al bundle del navegador y nunca contienen secretos.
- `VITE_API_BASE_URL` solo contiene una URL pública.
- Las credenciales de PostgreSQL se mantienen en configuración local fuera del código del frontend.
- Las credenciales de desarrollo de Docker no se usan en staging ni producción.
- Ningún token, contraseña de base ni clave de servicio se escribe en componentes, logs, errores visibles, fixtures o artefactos.

## Límites de servicios

| Servicio | Es dueño de | Habla con | Sobre |
|---|---|---|---|
| Aplicación React | Ruleta, turnos, puntaje, estado visual, solicitud y presentación de preguntas | API FastAPI por HTTP desde el navegador | Puerto de desarrollo de Vite |
| API FastAPI | Validación, consulta de preguntas y contrato HTTP | PostgreSQL mediante SQLAlchemy | `http://localhost:8000` |
| PostgreSQL | Persistencia de preguntas y categorizaciones | API FastAPI | Puerto local `5432` |

Los límites son obligatorios: React conoce la API, FastAPI conoce la base y la base no conoce el juego.

## Despliegue

- **Objetivo actual**: ejecución local. Vite sirve el frontend, Uvicorn sirve la API y Docker Compose ejecuta PostgreSQL.
- **Pipeline**: fuera del alcance de esta versión.
- **Firma de artefactos e infraestructura como código**: fuera del alcance hasta que exista un objetivo de despliegue aprobado.
- **Persistencia local**: el volumen `postgres_data` conserva las preguntas; reiniciar PostgreSQL no debe implicar borrarlas.

Cualquier decisión sobre publicación, dominios, HTTPS, CI/CD o infraestructura requiere un ADR porque cambia el alcance y los límites de servicio.

## Observabilidad

- FastAPI conserva sus logs HTTP estándar.
- React registra errores técnicos únicamente en la consola de desarrollo y muestra errores útiles al usuario sin exponer datos internos.
- La aplicación no envía telemetría, tokens ni respuestas de preguntas a servicios externos.
- No hay métricas ni identificadores de correlación en esta versión. Incorporarlos requiere una especificación observable.

## Convenciones del proyecto

### Interfaz y ruleta

- La ruleta conserva una rueda segmentada con la secuencia clásica roja, amarilla, azul, violeta y verde, repetida de manera uniforme alrededor del círculo.
- Los separadores y detalles usan acentos dorados; el fondo usa tonos oscuros; los textos principales son blancos o de alto contraste.
- Los colores se declaran una sola vez como custom properties de CSS. Los componentes no inventan variantes ni usan valores hexadecimales dispersos.
- El resultado que determina la ruleta se calcula antes de la animación. La posición final, la solicitud HTTP y la pregunta presentada deben corresponder al mismo sector.
- El estado no depende solamente del color: sector activo, respuesta y turno también tienen texto, forma o icono.
- La animación respeta `prefers-reduced-motion` y mantiene siempre un resultado final determinista.
- El diseño se prueba, como mínimo, para 360 px de ancho, escritorio y zoom del navegador al 200 %.

### Estructura y nombres

- El frontend vive en `frontend/` y sigue capas `components/`, `features/game/`, `services/api/`, `styles/` y `types/`.
- Los componentes son presentacionales o coordinadores de UI. Las llamadas HTTP quedan en `services/api/` y las reglas de partida en `features/game/`.
- La API conserva su estructura Python actual en `app/` y sus pruebas en `tests/`.
- Se usan nombres en inglés para código, tipos y commits; los textos visibles de la interfaz se escriben en español.
- Las funciones que transforman el estado de la partida son puras y testeables sin renderizar React.

### Flujo de partida y errores

- El flujo principal es explícito: inicio → giro → carga de pregunta → respuesta → revelación y puntaje → siguiente turno o fin.
- La respuesta correcta no se muestra antes de que el jugador termine su turno.
- La UI no contiene datos de pregunta inventados ni valores de reemplazo fijados en el código.
- El error de una consulta se presenta cerca de la acción afectada y ofrece reintentar; no borra el puntaje ni cambia silenciosamente de jugador.
- La aplicación tiene en cuenta estados de carga y vacío para evitar dobles clics y solicitudes duplicadas.

### API y contratos

- El frontend consume DTOs, no modelos internos de SQLAlchemy.
- Los nombres de propiedades JSON se conservan exactamente como los entrega FastAPI.
- Un cambio incompatible del contrato requiere primero una delta de especificación y una decisión sobre versionado.
- La base de la URL tiene un valor configurable y nunca se concatena a mitad de un componente.

### Ramas y cambios

- Las ramas y los commits siguen la nomenclatura de `AGENTS.md` y hacen referencia al nombre real del cambio OpenSpec.
- La trazabilidad vive en OpenSpec, ramas, commits y releases; no se agregan referencias de cambios ni de gates en comentarios del código.
- Cada comportamiento nuevo incluye sus tests en el mismo cambio.
- No se añaden dependencias, frameworks visuales, librerías de estado o servicios externos fuera de esta declaración sin escalarlo y registrar la excepción mediante un ADR.

## Excepciones registradas

Ninguna.
