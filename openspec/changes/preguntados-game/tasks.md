# preguntados-game — tasks

1. **Backend: generar opciones con lenguaje natural** — `app/options.py`: `build_options(question,
   answer)` usa `pipeline("text2text-generation", model="google/flan-t5-small")` (carga diferida,
   una vez) para generar 3 distractores en español a partir de la pregunta; limpieza de la salida,
   dedupe contra la respuesta correcta, mezcla final y relleno con opciones neutras si el modelo
   falla. «GET /questions/{id}» en `app/main.py` devuelve `options`. El pipeline se expone como punto
   de mockeo (`_get_generator`). Tests unitarios en `tests/unit/test_options.py` e integración en
   `tests/test_integration.py` con el generador falso en `tests/conftest.py` (fixture autouse).
2. **Frontend: contrato** — `frontend/src/api/questions.ts`: `options: string[]` en el DTO y en
   `isQuestion` (lista no vacía, sin valores vacíos, incluye `answer`). Tests en `questions.test.ts`.
3. **Frontend: elegir opción** — `frontend/src/App.tsx`: reemplazar el input de texto por cuatro
   botones de opción que resuelven el turno; mantener puntaje y retroalimentación. Tests en
   `App.test.tsx` (acierta, falla, reintento) por interacción de botón.
4. **Frontend: rótulos de ruleta** — `frontend/src/components/Wheel.tsx` y `Wheel.module.css`: mover
   los rótulos a una capa estática fuera del disco rotatorio (glifo vertical siempre).
5. **Frontend: variedad de colores** — `frontend/src/components/Wheel.tsx`: un matiz HSL distinto por
   sector (sin repetir gama).