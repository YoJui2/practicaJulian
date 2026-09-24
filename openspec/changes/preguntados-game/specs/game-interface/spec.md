# game-interface — spec delta (opción múltiple, opciones generadas, ruleta)

(Delta para el cambio `preguntados-game`. Solo lo que cambia.)

## Answering

- La respuesta deja de ser texto libre: el jugador elige entre **cuatro opciones** mostradas como
  botones. Una de ellas es la respuesta correcta.
- Elegir la opción correcta otorga 10 puntos y revela el resultado; elegir una incorrecta no suma
  puntos y revela cuál era la respuesta correcta. El turno avanza igual en ambos casos.
- La respuesta correcta no aparece señalizada antes de que el jugador elija.

### Acceptance criteria

- Given una pregunta con `options` devuelto por la API, la interfaz muestra exactamente cuatro
  botones de opción. *(authored)*
- Given el jugador elige la opción correcta, el puntaje del jugador activo aumenta en 10 y se muestra
  «¡Correcto!». *(authored)*
- Given el jugador elige una opción incorrecta, no cambia el puntaje y se muestra la respuesta
  correcta junto a la opción elegida. *(authored)*

## API contract — GET /questions/{id}

- La respuesta del detalle de una pregunta incluye `options: string[]`: la respuesta correcta y tres
  distractores generados en lenguaje natural a partir de la pregunta mediante un modelo local de
  texto.
- Las opciones no se leen de la base de datos: son cuatro siempre, distintas, no vacías, e incluyen
  `answer`. Si el modelo no responde, se rellenan con opciones neutras (ninguna coincide con
  `answer`).

### Acceptance criteria

- Given una sola pregunta en el catálogo, la respuesta de `GET /questions/{id}` devuelve exactamente
  cuatro `options` distintas, no vacías, que incluyen `answer`. *(authored)*
- Las `options` no dependen de las preguntas o respuestas almacenadas (se generan de la pregunta
  actual). *(authored)*
- La lista de `options` no repite elementos y su orden es aleatorio (la respuesta correcta no queda
  siempre en la misma posición). *(authored)*

## Wheel (ruleta)

- Los rótulos de sector («?») se renderizan en una capa que **no rota** con el disco, de modo que el
  glifo queda siempre vertical durante y después del giro.
- Cada sector usa un **matiz propio** (un color por sector, sin repetir la misma gama), para que la
  variedad aumente con los sectores.

### Acceptance criteria

- Given la ruleta en cualquier estado (reposo o girando), cada rótulo de sector se dibuja vertical,
  sin inclinación derivada de `transform: rotate`. *(authored)*
- Given una ruleta de N sectores, los N sectores usan colores distintos (un matiz HSL por sector, sin
  repeticiones). *(authored)*