# Lastra, margini e controllo delle collisioni

La **lastra** è il rettangolo di materiale in coordinate LightBurn. Per impostazione predefinita si trova all'origine del laser (angolo della lastra X 0, Y 0). Le sue dimensioni sono precompilate in base al laser salvato nel progetto; **Salva come predefinito per questo laser** memorizza i tuoi valori. I **margini** (predefiniti 5 mm) sono una fascia lungo i bordi della lastra in cui non si può posizionare nulla.

> La lastra nell'applicazione non è l'area di lavoro della macchina. Verifica sulla macchina la posizione reale del materiale e l'inquadratura.

Prima del salvataggio l'applicazione verifica che:

- tutti gli elementi spostati si trovino nell'area utile della lastra,
- gli elementi non si sovrappongano e rispettino la spaziatura,
- gli elementi rispettino la spaziatura anche rispetto ai gruppi **non spostati** e agli oggetti sciolti, se restano nell'output (Impostazioni → Salvataggio); gli oggetti esclusi vengono ignorati,
- un oggetto la cui dimensione non può essere determinata **blocchi** il salvataggio (la sicurezza non può essere confermata).

Gli errori (✖) bloccano il salvataggio e indicano gli elementi interessati. Gli avvisi (⚠) no. L'applicazione non ridimensiona, non ruota e non sposta mai da sola gli oggetti non selezionati.

Il controllo lavora con i contorni del progetto, non con l'overscan reale durante l'incisione, la compensazione della larghezza di taglio o il movimento della testa — per questo la **Preview in LightBurn è obbligatoria**.

## Più lastre

Quando i pezzi non entrano in una lastra, l'applicazione li divide su più lastre. Scegli come nella sezione Lastra, in **Se non ci sta**:

- *Dividi su più lastre una dopo l'altra* (predefinito) — lastra 1 piena, poi lastra 2 …; il minor numero di lastre.
- *Dividi su più lastre in modo uniforme* — lo stesso numero di pezzi su ogni lastra (ad es. 50 → 17/17/16).
- *Dividi su più lastre per elemento* — ogni lastra contiene solo pezzi di un elemento (l'originale e le sue copie).
- *Non dividere (errore)* — come prima: se la disposizione non ci sta, è bloccata.

**Completa l'ultima lastra con copie** aggiunge copie finché l'ultima lastra è piena (con *per elemento*, l'ultima lastra di ogni elemento viene completata con copie dello stesso elemento).

Sopra l'anteprima le schede mostrano le lastre, come le pagine in LightBurn; una scheda con errore è contrassegnata da ✖ e i messaggi indicano la lastra. Si può salvare solo quando tutte le lastre superano il controllo. Tutte le lastre hanno le stesse impostazioni della griglia e la stessa lastra; gli oggetti lasciati al loro posto (Impostazioni → Salvataggio) sono solo sulla lastra 1.

Con più lastre, l'elenco Elementi mostra i pezzi della lastra visualizzata (numerati su di essa) e sotto gli oggetti non spuntati ed esclusi; le copie aggiunte automaticamente sono grigie. **Ctrl+A** evidenzia tutti gli elementi — con più lastre solo quelli della lastra visualizzata.

**Salvataggio:** la lastra 1 resta sulla pagina disposta e le lastre 2 … vengono aggiunte come nuove pagine subito dopo («Pagina 1 – lastra 2» …). In LightBurn cambia pagina (**Window → Pages**) e taglia una lastra alla volta — Preview e Frame lavorano solo con la pagina attiva. In alternativa **Impostazioni → Lastre → Come file separati** salva un file per lastra (`…__lastra1.lbrn2` …). I valori predefiniti (modo di divisione, completamento, avviso oltre un numero di lastre) sono in **Impostazioni → Lastre**.

[← Griglia](grid.md) · [Avanti: salvataggio →](save.md)
