# Preparare il progetto in LightBurn

1. **Raggruppa ogni elemento separatamente** (Ctrl+G). Un gruppo = un elemento.
2. Ogni gruppo deve avere un **contorno di taglio chiuso** che contenga tutto il resto (testi, grafica). Il contorno può avere angoli arrotondati o un'altra forma — la dimensione dell'elemento è il rettangolo attorno al contorno. Il contorno può essere una curva o una forma disegnata direttamente in LightBurn (cerchio, ellisse, rettangolo, poligono); un gruppo può contenere altri gruppi (ad es. un portachiavi: cerchio con foro + testo).
3. Salva il progetto (**Save As**) come `.lbrn2`. L'applicazione legge solo il file salvato — non vede le modifiche non salvate in LightBurn.
4. Salva il progetto per il laser su cui taglierai. L'applicazione riconosce dal progetto il laser e la sua origine (in alto a sinistra, in alto a destra, in basso a sinistra o in basso a destra — ad es. laser a diodo). **Dopo aver cambiato laser in LightBurn, salva di nuovo il progetto** e riaprilo.

Supportati: LightBurn 2.2, progetti `.lbrn2`, laser con l'origine in qualsiasi angolo. I vecchi file `.lbrn` vengono rifiutati — salva il progetto in LightBurn come `.lbrn2`.

## Progetto per un altro laser

Un progetto salvato per un laser può essere preparato per un altro, ad es. da un laser con l'origine in alto a destra per un laser con l'origine in alto a sinistra — senza cambiare dispositivo né capovolgere il disegno in LightBurn. Nella sezione **Progetto** scegli in **Prepara per:** un laser del catalogo. L'applicazione propone la sua lastra, riempie la griglia dalla sua origine e il file salvato (`…__Nome_laser__grid_001.lbrn2`) è già pronto per esso: il file indica il laser di destinazione e gli elementi sono specchiati in modo da apparire uguali su di esso (testi leggibili).

- Catalogo dei laser: **Impostazioni → Laser** (oppure *Gestisci laser…* nell'elenco). I laser dei progetti aperti vengono aggiunti automaticamente; aggiungi gli altri (ad es. un laser a diodo) manualmente — **il nome deve corrispondere al dispositivo in LightBurn**; scegli l'angolo dell'origine e la lastra.
- Con un'altra origine devono essere selezionati **tutti gli elementi** e il progetto non deve contenere altri oggetti (sull'altro laser resterebbero specchiati). Questo riguarda solo gli oggetti mantenuti nell'output — gli oggetti non spuntati ed esclusi non sono nell'output (impostazione predefinita), quindi non sono d'ostacolo.
- **Le impostazioni dei livelli (potenza, velocità) non vengono convertite** — restano come nel progetto originale. Apri l'output in LightBurn con il laser di destinazione e controlla i livelli.

## Progetto con più pagine

Si può aprire anche un progetto con più pagine (**Window → Pages** in LightBurn). Nella sezione Progetto scegli **Pagina da disporre:**; le altre pagine restano invariate. Per impostazione predefinita viene scelta la pagina attiva al salvataggio del progetto.

[← Introduzione](index.md) · [Avanti: elementi →](items.md)
