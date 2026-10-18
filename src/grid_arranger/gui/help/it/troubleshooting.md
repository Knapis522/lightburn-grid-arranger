# Risoluzione dei problemi

**«Questa applicazione supporta solo progetti .lbrn2»** — salva il progetto in LightBurn come `.lbrn2`.

**«Versione di LightBurn non supportata»** — il progetto è stato salvato con una versione di LightBurn con cui l'applicazione non è stata verificata. L'output potrebbe non essere sicuro, perciò viene rifiutato.

**Elemento «non può essere spostato»** — passa il mouse sopra. Nella maggior parte dei casi: il gruppo non ha un contorno di taglio chiuso, qualcosa sporge dal contorno, è bloccato oppure contiene un tipo di oggetto che l'applicazione non sa ancora spostare in modo sicuro (ad es. una bitmap).

**«La geometria del testo non corrisponde alla sua posizione»** — apri il progetto in LightBurn e salvalo di nuovo.

**Il salvataggio è bloccato** — leggi gli errori (✖) sotto l'anteprima: superamento della lastra, collisione, spaziatura troppo piccola o un oggetto che non può essere misurato. Modifica colonne, spaziature, lastra o selezione.

**«Il file originale è cambiato dopo l'apertura»** — nel frattempo il progetto è stato salvato di nuovo. Riaprilo nell'applicazione.

**Windows mostra «PC protetto da Windows»** — l'applicazione non è ancora firmata digitalmente. Se il programma di installazione proviene dalle versioni di questo progetto su GitHub, fai clic su **Ulteriori informazioni → Esegui comunque**. Non disattivare l'antivirus.

**L'applicazione non si avvia o segnala un file mancante** — molto probabilmente manca la cartella `_internal` accanto a `GridArranger.exe` (ad es. è stato copiato solo l'EXE). Estrai di nuovo l'intero ZIP. Per verificare l'installazione esegui `GridArranger.exe --self-test report.json` dal prompt dei comandi; il risultato viene scritto in `report.json`.

**Segnalare un problema** — attiva Impostazioni → Salvataggio → Protocollo di salvataggio, salva di nuovo e invia il protocollo `.json` (contiene checksum e parametri, non il contenuto degli elementi) insieme ai passaggi. Invia progetti dei clienti solo con il loro permesso.

[← Introduzione](index.md)
