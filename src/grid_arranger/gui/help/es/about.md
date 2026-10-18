# Versión, archivos admitidos y datos

- Versión de la aplicación: **Ayuda → Acerca de**.
- Verificado con: LightBurn 2.2.00, proyectos `.lbrn2`, láseres con el origen en cualquier esquina (arriba a la izquierda y arriba a la derecha en láseres reales, abajo a la izquierda y abajo a la derecha con dispositivos de prueba de LightBurn).
- La aplicación funciona **sin conexión** y no controla el láser. La única conexión a Internet es la búsqueda de actualizaciones en GitHub (sin ningún dato sobre sus proyectos); se puede desactivar en **Configuración → Actualizaciones**.
- **Configuración** (elemento de la barra de menús, icono de engranaje, Ctrl+,) abre una ventana aparte con las páginas *General*, *Láseres* (catálogo de láseres — vea [Proyecto para otro láser](prepare.md)), *Guardado* (objetos sin marcar, protocolo de guardado) y *Actualizaciones*. Los cambios se aplican con **Aceptar** o **Aplicar**; **Cancelar** cierra la ventana sin cambios (tras *Aplicar*, el botón se llama **Cerrar**).
- **Idioma:** **Configuración → General → Idioma** — Automático (según Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Cada idioma aparece con su propio nombre.
- **Panel de distribución:** **Configuración → General → Panel de distribución** — las secciones Proyecto, Elementos, Cuadrícula, Colocación y Plancha a la izquierda o a la derecha de la vista previa.
- Apariencia: **Configuración → General → Apariencia** (automática según Windows; claro = toda la aplicación clara; oscuro = controles oscuros, la vista previa de la plancha sigue clara).
- **Unidades:** **Configuración → General → Unidades** — milímetros o pulgadas (como en LightBurn). Solo cambian la visualización y la introducción de valores; el cálculo y el proyecto guardado siempre están en milímetros, así que cambiar de unidades no mueve nada.
- Las secciones del panel lateral (Proyecto, Elementos, Cuadrícula, …) se pueden contraer haciendo clic en su cabecera; el estado se recuerda.
- La configuración (idioma, apariencia, unidades, lado del panel, planchas predeterminadas por láser, catálogo de láseres, perfiles) se guarda en el perfil de usuario de Windows, no en el proyecto.
- Instalación: ejecute `GridArranger-Setup-….exe` (no se necesitan derechos de administrador; la aplicación aparece en el menú Inicio). Alternativa sin instalación: descomprima el ZIP y ejecute `GridArranger.exe` — debe quedarse junto a la carpeta `_internal`.
- **Actualizaciones:** con la búsqueda automática activada (**Configuración → Actualizaciones**), la aplicación ofrece una nueva versión en cada inicio; en cualquier momento también con el botón **Buscar actualizaciones** en **Configuración → Actualizaciones** (o Ayuda → Buscar actualizaciones). Siempre se ofrece la versión más reciente, con los cambios desde su versión. Puede instalarla (la aplicación se cierra, instala la nueva versión y se vuelve a iniciar), recordarla más tarde u omitir la versión — se volverá a ofrecer una más reciente. No se instala nada sin su consentimiento; el instalador descargado se verifica con una suma de comprobación antes de ejecutarse. Las versiones preliminares (de prueba) solo se ofrecen con «Incluir versiones preliminares» activado.
- Un proyecto también se puede abrir arrastrando un archivo `.lbrn2` sobre `GridArranger.exe`.
- Una copia del ZIP se actualiza manualmente: descomprima la nueva versión en una carpeta nueva; la configuración se conserva.

> Nota: esta traducción se ha realizado automáticamente y aún debe revisarla un hablante nativo.

[← Introducción](index.md)
