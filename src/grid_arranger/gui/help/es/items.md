# Seleccionar y ordenar los elementos

Tras abrir un proyecto (icono **Abrir proyecto** de la barra de herramientas, **Archivo → Abrir proyecto** o Ctrl+O), la lista muestra todos los grupos de nivel superior:

- Los elementos **marcados** se distribuyen en la cuadrícula. El número delante del nombre es su posición en la cuadrícula.
- Los elementos **sin marcar** se quedan donde están y la aplicación se asegura de que la cuadrícula no los toque.
- Los elementos **grises** («no se puede mover») se han rechazado — pase el ratón por encima para ver el motivo. Nunca se mueven.
- ⚠ indica un aviso (p. ej. un texto que no se puede medir) — el elemento se puede usar, pero compruébelo en Preview.

Orden: **tome un elemento en la vista previa con el ratón y arrástrelo al lugar de otro elemento** — un marco verde indica dónde caerá; **los dos elementos intercambian sus posiciones**, los demás se quedan y la lista se renumera. Soltar fuera de los elementos cancela el arrastre. O seleccione un elemento en la lista y use **Subir / Bajar**. Un elemento recién marcado se añade al final. **Orden predeterminado** restaura el orden del archivo. **Seleccionar todo / No seleccionar nada** cambian la selección de una vez.

**Rotación:** un elemento girado muestra en la lista una flecha y el ángulo (↻ sentido horario, ↺ antihorario). Seleccione un elemento **haciendo clic en él en la vista previa** (marco naranja) o en la lista; **Ctrl+clic** añade más, **Esc** borra la selección. Para los elementos seleccionados:

- **↺ 90° / ↻ 90°** — girar 90° (p. ej. para que todos los llaveros tengan el agujero arriba);
- **Ángulo de la selección** — introduzca cualquier ángulo en grados (positivo = sentido horario);
- **No girar** — el elemento queda como en el proyecto (dirección del texto, veta del material);
- **Auto** — quita el ángulo manual; la aplicación vuelve a girar el elemento por sí misma.

Un ángulo manual aparece marcado «(manual)» en la lista; la aplicación nunca lo cambia y también se aplica con la Rotación *No girar*. El ángulo se mide desde la posición en el proyecto original. Abrir otro proyecto borra los ángulos manuales. Vea [cuadrícula](grid.md).

**Copias (llenar la plancha):** seleccione elementos y pulse **Ctrl+C** y **Ctrl+V** — se añade una copia de cada uno. Para varias copias a la vez, use el icono **Crear copias** de la barra de herramientas (o **Ctrl+D**, menú Edición) e introduzca el número, p. ej. 5. Las copias se añaden al final del orden, aparecen marcadas «(copia de G5)» en la lista, heredan el ángulo manual y se pueden girar y mover como cualquier otro elemento. Quite una copia con **Supr** o desmarcándola. Las copias se escriben en el proyecto guardado como grupos nuevos; el proyecto original no cambia.

**Piezas** (campo junto a *Ángulo de la selección*): cuántas piezas del elemento seleccionado colocar — p. ej. 5 = el original + 4 copias justo detrás (los elementos siguen agrupados por variante). Reducirlo quita las copias más recientes, **0** deja fuera el elemento. Con una copia seleccionada, el campo cambia las piezas de su original; la lista muestra «×5» junto al elemento.

**Llenar la plancha con copias** (icono de plancha en la barra de herramientas, **Ctrl+Mayús+D**, menú Edición): añade tantas copias de los elementos seleccionados como aún quepan en la plancha con una distribución que supere la comprobación. Con varios elementos seleccionados, las copias se alternan (A, B, A, B…). Funciona mejor con el número de columnas *Automático*; con un número fijo de columnas solo se añaden filas.

El elemento número **1** se coloca en la esquina de la cuadrícula que indica el *Orden de llenado* (vea [cuadrícula](grid.md)).

[← Preparación](prepare.md) · [Siguiente: cuadrícula →](grid.md)
