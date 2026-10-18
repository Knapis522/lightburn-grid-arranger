# Solución de problemas

**«Esta aplicación solo admite proyectos .lbrn2»** — guarde el proyecto en LightBurn como `.lbrn2`.

**«Versión de LightBurn no admitida»** — el proyecto se guardó con una versión de LightBurn con la que la aplicación no se ha verificado. La salida podría no ser segura, por eso se rechaza.

**Elemento «no se puede mover»** — pase el ratón por encima. Lo más habitual: el grupo no tiene un contorno de corte cerrado, algo sobresale del contorno, está bloqueado o contiene un tipo de objeto que la aplicación todavía no puede mover de forma segura (p. ej. un mapa de bits).

**«La geometría del texto no coincide con su posición»** — abra el proyecto en LightBurn y guárdelo de nuevo.

**El guardado está bloqueado** — lea los errores (✖) bajo la vista previa: plancha sobrepasada, colisión, separación demasiado pequeña o un objeto que no se puede medir. Cambie las columnas, las separaciones, la plancha o la selección.

**«El archivo original ha cambiado desde que se abrió»** — el proyecto se guardó de nuevo entretanto. Ábralo otra vez en la aplicación.

**Windows muestra «Windows protegió su PC»** — la aplicación todavía no está firmada digitalmente. Si el instalador procede de las versiones de este proyecto en GitHub, haga clic en **Más información → Ejecutar de todas formas**. No desactive el antivirus.

**La aplicación no se inicia o indica que falta un archivo** — lo más probable es que falte la carpeta `_internal` junto a `GridArranger.exe` (p. ej. se copió solo el EXE). Descomprima de nuevo todo el ZIP. Para comprobar la instalación, ejecute `GridArranger.exe --self-test report.json` en una ventana de comandos; el resultado se escribe en `report.json`.

**Informar de un problema** — active Configuración → Guardado → Protocolo de guardado, guarde de nuevo y envíe el protocolo `.json` (contiene sumas de comprobación y parámetros, no el contenido de los elementos) junto con los pasos. Envíe proyectos de clientes solo con su permiso.

[← Introducción](index.md)
