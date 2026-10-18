# Selezionare e ordinare gli elementi

Dopo aver aperto un progetto (icona **Apri progetto** della barra degli strumenti, **File → Apri progetto** o Ctrl+O) l'elenco mostra tutti i gruppi di primo livello:

- Gli elementi **spuntati** vengono disposti nella griglia. Il numero prima del nome è la loro posizione nella griglia.
- Gli elementi **non spuntati** sono esclusi dall'output: non saranno nel progetto salvato e la griglia non ne tiene conto. Se preferisci lasciarli al loro posto, scegli **Impostazioni → Salvataggio → Oggetti non spuntati → Lascia al proprio posto** — la griglia li eviterà.
- Gli elementi **grigi** («non può essere spostato») sono stati rifiutati — passa il mouse sopra per vedere il motivo. Non vengono mai spostati.
- ⚠ indica un avviso (ad es. un testo che non può essere misurato) — l'elemento si può usare, ma controllalo in Preview.
- **Escludere oggetti:** seleziona gli elementi nell'elenco (anche quelli grigi) e premi **Canc** (oppure **Modifica → Escludi dall'output**, o clic destro). Passano barrati in fondo all'elenco e non saranno nel progetto salvato — utile quando ti serve solo una parte di un progetto grande. **Modifica → Ripristina oggetti esclusi** riporta quelli selezionati. Le copie selezionate vengono semplicemente rimosse. Il progetto originale non cambia mai.

Ordine: **afferra un elemento nell'anteprima con il mouse e trascinalo al posto di un altro elemento** — una cornice verde indica dove finirà; **i due elementi si scambiano di posto**, tutti gli altri restano e l'elenco viene rinumerato. Rilasciare fuori dagli elementi annulla il trascinamento. Oppure seleziona un elemento nell'elenco e usa **Su / Giù**. Un elemento appena spuntato viene aggiunto alla fine. **Ordine predefinito** ripristina l'ordine del file. **Seleziona tutto / Deseleziona tutto** cambiano la selezione in una volta.

**Rotazione:** un elemento ruotato mostra nell'elenco una freccia e l'angolo (↻ senso orario, ↺ antiorario). Seleziona un elemento **facendo clic su di esso nell'anteprima** (cornice arancione) o nell'elenco; **Ctrl+clic** ne aggiunge altri, **Esc** annulla la selezione. Per gli elementi selezionati:

- **↺ 90° / ↻ 90°** — ruota di 90° (ad es. perché tutti i portachiavi abbiano il foro in alto);
- **Angolo della selezione** — inserisci un angolo qualsiasi in gradi (positivo = senso orario);
- **Non ruotare** — l'elemento resta com'è nel progetto (direzione del testo, venatura del materiale);
- **Auto** — rimuove l'angolo manuale; l'applicazione torna a ruotare l'elemento da sola.

Un angolo manuale è indicato con «(manuale)» nell'elenco; l'applicazione non lo modifica mai e vale anche con la Rotazione *Non ruotare*. L'angolo è misurato dalla posizione nel progetto originale. L'apertura di un altro progetto cancella gli angoli manuali. Vedi [griglia](grid.md).

**Copie (riempire la lastra):** seleziona gli elementi e premi **Ctrl+C** e **Ctrl+V** — viene aggiunta una copia di ciascuno. Per più copie alla volta usa l'icona **Crea copie** della barra degli strumenti (oppure **Ctrl+D**, menu Modifica) e inserisci il numero, ad es. 5. Le copie vengono aggiunte alla fine dell'ordine, sono indicate con «(copia di G5)» nell'elenco, ereditano l'angolo manuale e si possono ruotare e spostare come qualsiasi altro elemento. Rimuovi una copia con **Canc** o togliendo la spunta. Le copie vengono scritte nel progetto salvato come nuovi gruppi; il progetto originale non cambia.

**Pezzi** (campo accanto ad *Angolo della selezione*): quanti pezzi dell'elemento selezionato posizionare — ad es. 5 = l'originale + 4 copie subito dopo (gli elementi restano raggruppati per variante). Ridurlo rimuove le copie più recenti, **0** esclude l'elemento. Con una copia selezionata, il campo cambia i pezzi del suo originale; l'elenco mostra «×5» accanto all'elemento.

**Riempi la lastra di copie** (icona della lastra sulla barra degli strumenti, **Ctrl+Maiusc+D**, menu Modifica): aggiunge tante copie degli elementi selezionati quante ne entrano ancora nella lastra con una disposizione che supera il controllo. Con più elementi selezionati, le copie si alternano (A, B, A, B…). Funziona meglio con il numero di colonne *Automatico*; con un numero fisso di colonne si aggiungono solo righe.

L'elemento numero **1** si trova nell'angolo della griglia indicato dall'*Ordine di riempimento* (vedi [griglia](grid.md)).

[← Preparazione](prepare.md) · [Avanti: griglia →](grid.md)
