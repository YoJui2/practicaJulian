# Change: preguntados-game — opción múltiple y ruleta

## What and why

El juego permitía responder en texto libre: comprobación frágil y partida poco atractiva. Este
cambio convierte la respuesta en **opción múltiple de 4 alternativas** generadas con lenguaje natural
a partir de la pregunta (sin depender del contenido del dataset): la API devuelve `options` con la
respuesta correcta y tres distractores plausibles, y la interfaz muestra cuatro botones entre los
cuales elegir.

Además corrige dos cosas de la ruleta: los rótulos «?» vivían dentro del disco que rota (quedaban
inclinados) y los colores se repetían entre sectores (demasiados sectores iguales). Los rótulos pasan
a una capa fija y cada sector usa su propio matiz.

## Alternatives considered

1. **Distractores muestreados de la base de datos** (misma categoría) — descartado: depende de que
   haya suficientes respuestas distintas guardadas y no "analiza" la pregunta.
2. **LLM externo por API** — fuera del stack declarado en `openspec/project.md`; exigiría excepción
   con ADR y API key; rechazado.
3. **Modelo local de texto de Hugging Face** (`google/flan-t5-small` vía `text2text-generation`) —
   elegido: mira la pregunta y la respuesta correcta, genera distractores creíbles en lenguaje
   natural, ya está en el stack (`transformers`), sin dependencia del dataset ni de internet en
   runtime. Costo: descarga única del modelo y algo de latencia por turno. Con fallback a opciones
   neutras si el modelo no responde.

## Out of scope

- Persistir opciones en la base de datos.
- Mas de 4 opciones, opciones con pistas/tiempo, tematicas por ronda.
- Evaluar la calidad de los distractores generados.

## Depends on

None.

## Owner

Role: `dev`. Track: **Light** (proposal + spec delta + tasks). Gates: B y C.