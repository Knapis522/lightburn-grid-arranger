# Preparar el proyecto en LightBurn

1. **Agrupe cada elemento por separado** (Ctrl+G). Un grupo = un elemento.
2. Cada grupo necesita un **contorno de corte cerrado** que contenga todo lo demás (textos, motivos). El contorno puede tener esquinas redondeadas u otra forma — el tamaño del elemento es el rectángulo alrededor del contorno. El contorno puede ser una curva o una forma dibujada directamente en LightBurn (círculo, elipse, rectángulo, polígono); un grupo puede contener otros grupos (p. ej. un llavero: círculo con un agujero + texto).
3. Guarde el proyecto (**Save As**) como `.lbrn2`. La aplicación solo lee el archivo guardado — no ve los cambios sin guardar en LightBurn.
4. Guarde el proyecto para el láser en el que va a cortar. La aplicación reconoce el láser y su origen (arriba a la izquierda, arriba a la derecha, abajo a la izquierda o abajo a la derecha — p. ej. láseres de diodo) a partir del proyecto. **Tras cambiar de láser en LightBurn, guarde de nuevo el proyecto** y vuelva a abrirlo.

Compatible: LightBurn 2.2, proyectos `.lbrn2`, láseres con el origen en cualquier esquina. Los archivos antiguos `.lbrn` se rechazan — guarde el proyecto en LightBurn como `.lbrn2`.

## Proyecto para otro láser

Un proyecto guardado para un láser se puede preparar para otro, p. ej. de un láser con el origen arriba a la derecha para un láser con el origen arriba a la izquierda — sin cambiar de dispositivo ni voltear el diseño en LightBurn. En la sección **Proyecto**, elija en **Preparar para:** un láser del catálogo. La aplicación ofrece su plancha, llena la cuadrícula desde su origen y el archivo guardado (`…__Nombre_del_laser__grid_001.lbrn2`) queda listo para él: el archivo indica el láser de destino y los elementos se reflejan para que se vean igual en él (textos legibles).

- Catálogo de láseres: **Configuración → Láseres** (o *Gestionar láseres…* en la lista). Los láseres de los proyectos abiertos se añaden automáticamente; añada otros (p. ej. un láser de diodo) manualmente — **el nombre debe coincidir con el dispositivo en LightBurn**; elija la esquina del origen y la plancha.
- Con otro origen deben estar seleccionados **todos los elementos** y el proyecto no debe contener otros objetos (quedarían reflejados en el otro láser). Esto solo afecta a los objetos que se conservan en la salida — los objetos sin marcar y excluidos no están en la salida (opción predeterminada), así que no estorban.
- **Los ajustes de las capas (potencia, velocidad) no se convierten** — se mantienen como en el proyecto original. Abra la salida en LightBurn con el láser de destino y compruebe las capas.

## Proyecto con varias páginas

También se puede abrir un proyecto con varias páginas (**Window → Pages** en LightBurn). En la sección Proyecto elija **Página a distribuir:**; las demás páginas no cambian. De forma predeterminada se elige la página que estaba activa al guardar el proyecto.

[← Introducción](index.md) · [Siguiente: elementos →](items.md)
