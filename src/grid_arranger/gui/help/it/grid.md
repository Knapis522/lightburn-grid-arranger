# Griglia e posizionamento

**Profilo di disposizione** — impostazioni salvate con un nome (ad es. «Portachiavi 3 mm»): numero di colonne (o *Automatico*), spaziature, ordine di riempimento, rotazione e posizionamento. Scegliere un profilo nella sezione **Profilo di disposizione** imposta i valori; **Salva…** salva le impostazioni attuali come profilo (stesso nome = sovrascrivere), **Elimina** lo rimuove. Quando modifichi un valore, la scelta passa a *nessun profilo* — il profilo stesso non cambia. La lastra non fa parte di un profilo; appartiene al laser (Impostazioni → Laser).

**Colonne** — quanti elementi ci sono in una riga. Il numero di righe viene calcolato. Con **Automatico** spuntato l'applicazione usa tante colonne quante ne entrano nella larghezza della lastra (l'area utile all'interno dei margini); il campo mostra allora il numero calcolato. Utile insieme alle copie e a *Riempi la lastra di copie*.

**Spaziatura X / Y** — distanza tra i contorni di taglio di elementi vicini nelle unità scelte (orizzontale / verticale). Una spaziatura di 0 è consentita, ma l'applicazione avvisa del rischio durante il taglio. Inserisci i decimali come d'uso nella lingua dell'applicazione (in italiano con la virgola).

Se gli elementi hanno **dimensioni diverse**, una colonna è larga quanto il suo elemento più largo e una riga alta quanto il suo elemento più alto. La spaziatura è allora un **minimo** — tra elementi più piccoli è maggiore.

**Ordine di riempimento**

- *Dall'origine del laser* (predefinito) — l'elemento n. 1 si trova nell'angolo all'origine del laser; con l'origine a destra le righe vengono riempite da destra a sinistra; con l'origine in basso la prima riga è in basso e le successive sopra.
- *Ordine di lettura* — l'elemento n. 1 è sempre in alto a sinistra, righe da sinistra a destra.

**Posizionamento**

- *Nell'angolo della lastra all'origine del laser* (predefinito) — l'angolo della griglia lato origine si trova nell'angolo della lastra più il margine.
- *Al centro della lastra*.
- *Manualmente* — inserisci le coordinate X/Y di LightBurn (distanza dall'origine) dell'angolo della griglia lato origine.
- *Nella posizione originale degli elementi*.

I campi **Angolo X / Y** si possono modificare solo in modalità *Manualmente*. Nelle altre modalità sono in grigio e mostrano l'angolo appena calcolato dall'applicazione (cambia ad es. con i margini). Dopo il passaggio a *Manualmente* mantengono l'angolo attuale, così la griglia non si sposta e puoi regolarla con precisione.

L'anteprima mostra la lastra, l'area utile (tratteggiata), l'origine del laser (●), gli elementi spostati con la loro grafica e i loro testi reali nei colori dei livelli e con i numeri, e gli oggetti non spostati in grigio. Gli elementi con errore sono rossi. **Mostra grafica** nell'intestazione della sezione Elementi disattiva il disegno e lascia solo i rettangoli degli elementi. La rotella del mouse (o il touchpad) ingrandisce in modo fluido, trascinare uno spazio vuoto sposta la vista (trascinare un elemento cambia l'ordine), l'icona **Adatta la vista** della barra degli strumenti (Ctrl+0) o un doppio clic su uno spazio vuoto mostra tutto.

## Rotazione per risparmiare materiale

L'opzione **Rotazione** nella sezione Griglia:

- *Qualsiasi angolo (area minima)* — predefinita. Ogni elemento viene ruotato in modo che il rettangolo che lo racchiude sia il più piccolo possibile (fa risparmiare spazio con forme inclinate o irregolari come i portachiavi). I biglietti rettangolari restano dritti.
- *A passi di 90°* — gli elementi vengono ruotati solo di un quarto di giro (orizzontale / verticale).
- *Non ruotare* — gli elementi vengono solo spostati.

In tutte le modalità l'applicazione controlla anche se la griglia sarebbe più piccola con tutti gli elementi in orizzontale o in verticale e usa la variante più piccola — preferibilmente una che entri nella lastra. Se la rotazione non rimpicciolisse la griglia, gli elementi restano come sono; gli elementi rotondi non vengono mai ruotati di 90°. La rotazione è visibile nell'anteprima e nell'elenco degli elementi. Un elemento ruota attorno al proprio centro insieme a testi e grafica; dopo il salvataggio controlla la Preview in LightBurn. Eccezioni per singoli elementi: il pulsante **Non ruotare** nella sezione Elementi.

[← Elementi](items.md) · [Avanti: lastra e controllo →](board.md)
