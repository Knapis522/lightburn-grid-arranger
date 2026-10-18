# Cuadrícula y colocación

**Perfil de distribución** — ajustes guardados con un nombre (p. ej. «Llaveros 3 mm»): número de columnas (o *Automático*), separaciones, orden de llenado, rotación y colocación. Elegir un perfil en la sección **Perfil de distribución** aplica los valores; **Guardar…** guarda los ajustes actuales como perfil (mismo nombre = sobrescribir), **Eliminar** lo borra. Cuando cambia un valor, la elección pasa a *sin perfil* — el perfil en sí no cambia. La plancha no forma parte de un perfil; pertenece al láser (Configuración → Láseres).

**Columnas** — cuántos elementos hay en una fila. El número de filas se calcula. Con **Automático** marcado, la aplicación usa tantas columnas como quepan en el ancho de la plancha (el área útil dentro de los márgenes); el campo muestra entonces el número calculado. Útil junto con las copias y *Llenar la plancha con copias*.

**Separación X / Y** — distancia entre los contornos de corte de elementos vecinos en las unidades elegidas (horizontal / vertical). Se permite una separación de 0, pero la aplicación advierte del riesgo al cortar. Introduzca los decimales como es habitual en el idioma de la aplicación (en español con coma).

Si los elementos tienen **tamaños distintos**, una columna es tan ancha como su elemento más ancho y una fila tan alta como su elemento más alto. La separación es entonces un **mínimo** — es mayor entre elementos más pequeños.

**Orden de llenado**

- *Desde el origen del láser* (predeterminado) — el elemento n.º 1 está en la esquina junto al origen del láser; con el origen a la derecha, las filas se llenan de derecha a izquierda; con el origen abajo, la primera fila está abajo y las siguientes encima.
- *Orden de lectura* — el elemento n.º 1 está siempre arriba a la izquierda, filas de izquierda a derecha.

**Colocación**

- *En la esquina de la plancha junto al origen del láser* (predeterminado) — la esquina de la cuadrícula junto al origen está en la esquina de la plancha más el margen.
- *En el centro de la plancha*.
- *Manualmente* — introduzca las coordenadas X/Y de LightBurn (distancia desde el origen) de la esquina de la cuadrícula junto al origen.
- *En la posición original de los elementos*.

Los campos **Esquina X / Y** solo se pueden editar en el modo *Manualmente*. En los demás modos aparecen en gris y muestran la esquina que la aplicación acaba de calcular (cambia, p. ej., con los márgenes). Al pasar a *Manualmente* conservan la esquina actual, así que la cuadrícula no se mueve y puede ajustarla con precisión.

La vista previa muestra la plancha, el área útil (discontinua), el origen del láser (●), los elementos movidos con sus motivos y textos reales en los colores de las capas y con sus números, y los objetos no movidos en gris. Los elementos con error aparecen en rojo. **Mostrar motivos** en la cabecera de la sección Elementos desactiva el dibujo y deja solo los rectángulos de los elementos. La rueda del ratón (o el panel táctil) amplía de forma continua, arrastrar un espacio vacío desplaza la vista (arrastrar un elemento cambia el orden), el icono **Ajustar la vista** de la barra de herramientas (Ctrl+0) o un doble clic en un espacio vacío lo muestra todo.

## Rotación para ahorrar material

La opción **Rotación** de la sección Cuadrícula:

- *Cualquier ángulo (superficie mínima)* — predeterminado. Cada elemento se gira para que el rectángulo que lo rodea sea lo más pequeño posible (ahorra espacio con formas inclinadas o irregulares como llaveros). Las tarjetas rectangulares quedan rectas.
- *En pasos de 90°* — los elementos solo se giran un cuarto de vuelta (horizontal / vertical).
- *No girar* — los elementos solo se mueven.

En todos los modos, la aplicación comprueba además si la cuadrícula sería más pequeña con todos los elementos en horizontal o en vertical y usa la variante más pequeña — preferiblemente una que quepa en la plancha. Si girar no hiciera más pequeña la cuadrícula, los elementos quedan como están; los elementos redondos nunca se giran 90°. La rotación se ve en la vista previa y en la lista de elementos. Un elemento gira alrededor de su centro junto con sus textos y motivos; después de guardar, compruebe la Preview en LightBurn. Excepciones para elementos concretos: el botón **No girar** de la sección Elementos.

[← Elementos](items.md) · [Siguiente: plancha y comprobación →](board.md)
