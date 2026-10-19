# Guardar y comprobar en LightBurn

El icono **Guardar como proyecto nuevo** de la barra de herramientas (o **Archivo → Guardar como proyecto nuevo**, Ctrl+S) solo está activo cuando la distribución ha superado la comprobación. Se abre un cuadro de guardado con el nombre propuesto `original__grid_001.lbrn2` (luego `_002`, …) en la carpeta del original — **puede cambiar la carpeta y el nombre**. Tras confirmar, la aplicación:

1. prepara un archivo nuevo en el que solo cambian las posiciones de los grupos seleccionados (y de sus textos), se quitan los objetos excluidos,
2. comprueba de forma independiente que no ha cambiado nada más (capas, potencia, textos, otros objetos),
3. comprueba que el original no ha cambiado desde que se abrió,
4. guarda un archivo **nuevo** con el nombre elegido.

**Protocolo de guardado** (`.json`) — un registro de a partir de qué y cómo se creó la salida: sumas de comprobación, láser, ajustes de la cuadrícula, desplazamientos de los elementos y resultado de la comprobación (sin motivos ni textos de los elementos). Útil para el seguimiento o para informar de un problema. **Configuración → Guardado → Protocolo de guardado**: *No guardar* (predeterminado), *Junto al proyecto guardado* (`<nombre>.json`) o *En la carpeta de protocolos de la aplicación* (ábrala allí con **Abrir la carpeta de protocolos**).

**Después de guardar, sigue trabajando con el original.** El archivo guardado es una copia nueva independiente; el proyecto original sigue abierto en la aplicación, así que puede probar otra distribución y guardar otra variante (`_002`, …). La barra de título y la sección Proyecto muestran *último guardado como …*. Para continuar en su lugar con el archivo guardado (como «Guardar como»), marque **Seguir trabajando aquí con el archivo guardado** en el mensaje de guardado — se abre en lugar del original, sus copias y rotaciones quedan fijas y el historial de deshacer empieza de nuevo. El siguiente guardado continúa entonces la numeración del original (`_002`, no `__grid_001__grid_001`).

Ni los archivos existentes ni el original se sobrescriben nunca — si el archivo elegido (o su protocolo junto a él) ya existe, la aplicación pide otro nombre. Si algo falla, no se crea ninguna salida.

**Después, en LightBurn:**

1. Abra la salida: en el mensaje de guardado con **Abrir en LightBurn** (o el icono de la barra de herramientas, **Archivo → Abrir el proyecto guardado en LightBurn**, Ctrl+L). La aplicación abre el archivo como un doble clic en el Explorador: un LightBurn en ejecución sustituye su proyecto abierto — si tiene cambios sin guardar, LightBurn pregunta por sí mismo; si no, LightBurn se inicia. Para abrirlo manualmente use **File → Open** (no Import — Import no carga los ajustes del proyecto).
2. Compruebe las capas, la potencia y la velocidad.
3. Ejecute la **Preview** y revise los recorridos.
4. Compruebe la posición en la máquina (**Frame**). Solo entonces corte, bajo supervisión.

**Cambios sin guardar:** si la distribución ha cambiado desde que se abrió o se guardó por última vez, la barra de título muestra un asterisco tras el nombre del proyecto (`karty.lbrn2*`). Al cerrar la aplicación, abrir otro proyecto o instalar una actualización, la aplicación pregunta si guardar la distribución como proyecto nuevo, descartarla o cancelar. Si la distribución no superó la comprobación, solo ofrece descartar o cancelar.

[← Plancha](board.md) · [Solución de problemas →](troubleshooting.md)
