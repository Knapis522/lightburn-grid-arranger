# Salvare e controllare in LightBurn

L'icona **Salva come nuovo progetto** della barra degli strumenti (oppure **File → Salva come nuovo progetto**, Ctrl+S) è attiva solo quando la disposizione ha superato il controllo. Si apre una finestra di salvataggio con il nome proposto `originale__grid_001.lbrn2` (poi `_002`, …) nella cartella dell'originale — **puoi cambiare la cartella e il nome**. Dopo la conferma, l'applicazione:

1. prepara un nuovo file in cui cambiano solo le posizioni dei gruppi selezionati (e dei loro testi), gli oggetti esclusi vengono rimossi,
2. verifica in modo indipendente che nient'altro sia cambiato (livelli, potenza, testi, altri oggetti),
3. verifica che l'originale non sia cambiato dall'apertura,
4. salva un file **nuovo** con il nome scelto.

**Protocollo di salvataggio** (`.json`) — un registro di da cosa e come è stato creato l'output: checksum, laser, impostazioni della griglia, spostamenti degli elementi e risultato del controllo (senza grafica né testi degli elementi). Utile per la tracciabilità o per segnalare un problema. **Impostazioni → Salvataggio → Protocollo di salvataggio**: *Non salvare* (predefinito), *Accanto al progetto salvato* (`<nome>.json`) oppure *Nella cartella dei protocolli dell'applicazione* (aprila lì con **Apri la cartella dei protocolli**).

**Dopo il salvataggio continui a lavorare sull'originale.** Il file salvato è una nuova copia separata; il progetto originale resta aperto nell'applicazione, così puoi provare un'altra disposizione e salvare un'altra variante (`_002`, …). La barra del titolo e la sezione Progetto mostrano *ultimo salvataggio come …*. Per continuare invece con il file salvato (come «Salva con nome»), spunta **Continua qui con il file salvato** nel messaggio di salvataggio — si apre al posto dell'originale, le sue copie e rotazioni sono ormai fisse e la cronologia di annullamento riparte. Il salvataggio successivo prosegue allora la numerazione dell'originale (`_002`, non `__grid_001__grid_001`).

I file esistenti e l'originale non vengono mai sovrascritti — se il file scelto (o il suo protocollo accanto) esiste già, l'applicazione chiede un altro nome. In caso di errore non viene creato alcun output.

**Poi in LightBurn:**

1. Apri l'output: nel messaggio di salvataggio con **Apri in LightBurn** (oppure l'icona della barra degli strumenti, **File → Apri il progetto salvato in LightBurn**, Ctrl+L). L'applicazione apre il file come un doppio clic in Esplora file: un LightBurn in esecuzione sostituisce il progetto aperto — se ha modifiche non salvate, LightBurn chiede da solo di salvarle; altrimenti LightBurn si avvia. Per aprirlo manualmente usa **File → Open** (non Import — Import non carica le impostazioni del progetto).
2. Controlla livelli, potenza e velocità.
3. Avvia la **Preview** ed esamina i percorsi.
4. Controlla la posizione sulla macchina (**Frame**). Solo allora taglia, sotto sorveglianza.

[← Lastra](board.md) · [Risoluzione dei problemi →](troubleshooting.md)
