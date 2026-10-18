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

[← Griglia](grid.md) · [Avanti: salvataggio →](save.md)
