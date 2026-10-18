# Plancha, márgenes y control de colisiones

La **plancha** es el rectángulo de material en coordenadas de LightBurn. De forma predeterminada se encuentra en el origen del láser (esquina de la plancha X 0, Y 0). Su tamaño se rellena según el láser guardado en el proyecto; **Guardar como predeterminado para este láser** recuerda sus valores. Los **márgenes** (5 mm de forma predeterminada) son una franja a lo largo de los bordes de la plancha donde no se puede colocar nada.

> La plancha en la aplicación no es el área de trabajo de la máquina. Compruebe en la máquina la posición real del material y el encuadre.

Antes de guardar, la aplicación comprueba que:

- todos los elementos movidos están dentro del área útil de la plancha,
- los elementos no se solapan y mantienen la separación,
- los elementos mantienen la separación también respecto a los grupos **no movidos** y los objetos sueltos,
- un objeto cuyo tamaño no se puede determinar **bloquea** el guardado (no se puede confirmar la seguridad).

Los errores (✖) bloquean el guardado y nombran los elementos afectados. Los avisos (⚠) no. La aplicación nunca escala, gira ni mueve por sí misma los objetos no seleccionados.

La comprobación trabaja con los contornos del proyecto, no con el sobrerrecorrido real al grabar, la compensación del ancho de corte ni el movimiento del cabezal — por eso la **Preview en LightBurn es obligatoria**.

[← Cuadrícula](grid.md) · [Siguiente: guardado →](save.md)
