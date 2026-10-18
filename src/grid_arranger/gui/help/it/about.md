# Versione, file supportati e dati

- Versione dell'applicazione: **Guida → Informazioni**.
- Verificato con: LightBurn 2.2.00, progetti `.lbrn2`, laser con l'origine in qualsiasi angolo (in alto a sinistra e in alto a destra su laser reali, in basso a sinistra e in basso a destra con dispositivi di prova LightBurn).
- L'applicazione funziona **offline** e non controlla il laser. L'unica connessione a Internet è la verifica degli aggiornamenti su GitHub (senza alcun dato sui tuoi progetti); si può disattivare in **Impostazioni → Aggiornamenti**.
- **Impostazioni** (voce della barra dei menu, icona a ingranaggio, Ctrl+,) apre una finestra separata con le pagine *Generale*, *Laser* (catalogo dei laser — vedi [Progetto per un altro laser](prepare.md)), *Salvataggio* e *Aggiornamenti*. Le modifiche hanno effetto con **OK** o **Applica**; **Annulla** chiude la finestra senza modifiche (dopo *Applica* il pulsante si chiama **Chiudi**).
- **Lingua:** **Impostazioni → Generale → Lingua** — Automatico (secondo Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Ogni lingua è indicata con il proprio nome.
- **Pannello di disposizione:** **Impostazioni → Generale → Pannello di disposizione** — le sezioni Progetto, Elementi, Griglia, Posizionamento e Lastra a sinistra o a destra dell'anteprima.
- Aspetto: **Impostazioni → Generale → Aspetto** (automatico secondo Windows; chiaro = tutta l'applicazione chiara; scuro = comandi scuri, l'anteprima della lastra resta chiara).
- **Unità:** **Impostazioni → Generale → Unità** — millimetri o pollici (come in LightBurn). Cambiano solo la visualizzazione e l'inserimento dei valori; il calcolo e il progetto salvato sono sempre in millimetri, quindi cambiare unità non sposta nulla.
- Le sezioni del pannello laterale (Progetto, Elementi, Griglia, …) si possono comprimere facendo clic sulla loro intestazione; lo stato viene memorizzato.
- Le impostazioni (lingua, aspetto, unità, lato del pannello, lastre predefinite per laser, catalogo dei laser, profili) vengono salvate nel profilo utente di Windows, non nel progetto.
- Installazione: esegui `GridArranger-Setup-….exe` (non servono diritti di amministratore; l'applicazione compare nel menu Start). In alternativa senza installazione: estrai lo ZIP ed esegui `GridArranger.exe` — deve restare accanto alla cartella `_internal`.
- **Aggiornamenti:** con la verifica automatica attiva (**Impostazioni → Aggiornamenti**) l'applicazione propone una nuova versione a ogni avvio; in qualsiasi momento anche con il pulsante **Verifica aggiornamenti** in **Impostazioni → Aggiornamenti** (oppure Guida → Verifica aggiornamenti). Viene sempre proposta la versione più recente, con le modifiche rispetto alla tua versione. Puoi installarla (l'applicazione si chiude, installa la nuova versione e si riavvia), ricevere un promemoria più tardi o saltare la versione — ne verrà proposta di nuovo una più recente. Nulla viene installato senza il tuo consenso; il programma di installazione scaricato viene verificato con un checksum prima dell'esecuzione. Le versioni preliminari (di prova) vengono proposte solo con «Includi le versioni preliminari» attivo.
- Un progetto si può aprire anche trascinando un file `.lbrn2` su `GridArranger.exe`.
- Una copia dallo ZIP si aggiorna manualmente: estrai la nuova versione in una nuova cartella; le impostazioni vengono mantenute.

> Nota: questa traduzione è stata realizzata automaticamente e deve ancora essere revisionata da un madrelingua.

[← Introduzione](index.md)
