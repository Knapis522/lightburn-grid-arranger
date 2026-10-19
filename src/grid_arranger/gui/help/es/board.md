# Plancha, márgenes y control de colisiones

La **plancha** es el rectángulo de material en coordenadas de LightBurn. De forma predeterminada se encuentra en el origen del láser (esquina de la plancha X 0, Y 0). Su tamaño se rellena según el láser guardado en el proyecto; **Guardar como predeterminado para este láser** recuerda sus valores. Los **márgenes** (5 mm de forma predeterminada) son una franja a lo largo de los bordes de la plancha donde no se puede colocar nada.

> La plancha en la aplicación no es el área de trabajo de la máquina. Compruebe en la máquina la posición real del material y el encuadre.

Antes de guardar, la aplicación comprueba que:

- todos los elementos movidos están dentro del área útil de la plancha,
- los elementos no se solapan y mantienen la separación,
- los elementos mantienen la separación también respecto a los grupos **no movidos** y los objetos sueltos, si permanecen en la salida (Configuración → Guardado); los objetos excluidos se ignoran,
- un objeto cuyo tamaño no se puede determinar **bloquea** el guardado (no se puede confirmar la seguridad).

Los errores (✖) bloquean el guardado y nombran los elementos afectados. Los avisos (⚠) no. La aplicación nunca escala, gira ni mueve por sí misma los objetos no seleccionados.

La comprobación trabaja con los contornos del proyecto, no con el sobrerrecorrido real al grabar, la compensación del ancho de corte ni el movimiento del cabezal — por eso la **Preview en LightBurn es obligatoria**.

## Varias planchas

Cuando las piezas no caben en una plancha, la aplicación las reparte en varias planchas. Elija cómo en la sección Plancha, en **Si no cabe**:

- *Repartir en planchas una tras otra* (predeterminado) — plancha 1 llena, luego plancha 2 …; el menor número de planchas.
- *Repartir en planchas por igual* — el mismo número de piezas en cada plancha (p. ej. 50 → 17/17/16).
- *Repartir en planchas por elemento* — cada plancha contiene solo piezas de un elemento (el original y sus copias).
- *No repartir (error)* — como antes: si la distribución no cabe, queda bloqueada.

**Completar la última plancha con copias** añade copias hasta llenar la última plancha (con *por elemento*, la última plancha de cada elemento se completa con copias de ese elemento).

Sobre la vista previa, unas pestañas muestran las planchas, como las páginas en LightBurn; una pestaña con error se marca con ✖ y los mensajes indican la plancha. Solo se puede guardar cuando todas las planchas superan la comprobación. Todas las planchas tienen los mismos ajustes de cuadrícula y la misma plancha; los objetos que se dejan en su sitio (Configuración → Guardado) están solo en la plancha 1.

Con varias planchas, la lista Elementos muestra las piezas de la plancha mostrada (numeradas en ella) y debajo los objetos sin marcar y excluidos; las copias añadidas automáticamente aparecen en gris. **Ctrl+A** resalta todos los elementos — con varias planchas, solo los de la plancha mostrada.

**Guardado:** la plancha 1 se queda en la página distribuida y las planchas 2 … se añaden como páginas nuevas justo después («Página 1 – plancha 2» …). En LightBurn, cambie de página (**Window → Pages**) y corte una plancha tras otra — Preview y Frame trabajan solo con la página activa. Como alternativa, **Configuración → Planchas → Como archivos separados** guarda un archivo por plancha (`…__plancha1.lbrn2` …). Los valores predeterminados (modo de reparto, completar, aviso por encima de un número de planchas) están en **Configuración → Planchas**.

[← Cuadrícula](grid.md) · [Siguiente: guardado →](save.md)
