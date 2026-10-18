# Uloženie a kontrola v LightBurne

Ikona **Uložiť ako nový projekt** na paneli nástrojov (alebo **Súbor → Uložiť ako nový projekt**, Ctrl+S) je aktívna, len keď rozloženie prešlo kontrolou. Otvorí sa okno na uloženie: navrhnutý je názov `pôvodný__grid_001.lbrn2` (ďalej `_002`, …) v priečinku originálu — **priečinok aj názov môžete zmeniť**. Po potvrdení aplikácia:

1. pripraví nový súbor, v ktorom sa zmenia len polohy vybraných skupín (a ich textov),
2. nezávisle overí, že sa nič iné nezmenilo (vrstvy, výkony, texty, ostatné objekty),
3. overí, že sa originál od otvorenia nezmenil,
4. uloží **nový** súbor pod zvoleným názvom.

**Protokol uloženia** (`.json`) — záznam o tom, z čoho a ako výstup vznikol: kontrolné súčty, laser, nastavenie mriežky, posuny výrobkov a výsledok kontroly (žiadne motívy ani texty výrobkov). Hodí sa na dohľadanie alebo nahlásenie chyby. **Nastavenia → Ukladanie → Protokol uloženia**: *Neukladať* (predvolené), *Vedľa uloženého projektu* (`<názov>.json`) alebo *Do priečinka protokolov aplikácie* (otvoríte ho tamtiež položkou **Otvoriť priečinok protokolov**).

**Po uložení pracujete ďalej s originálom.** Uložený súbor je samostatná nová kópia; v aplikácii zostáva otvorený pôvodný projekt, takže môžete skúsiť iné rozloženie a uložiť ďalšiu variantu (`_002`, …). Titulok okna aj sekcia Projekt ukazujú *naposledy uložené ako …*. Ak chcete namiesto toho pokračovať s uloženým súborom (ako „Uložiť ako“), zaškrtnite v hlásení o uložení **Pokračovať v aplikácii s uloženým súborom** — otvorí sa namiesto originálu, kópie a otočenia v ňom už sú napevno a krok späť začína znova. Ďalšie uloženie potom pokračuje v číselnom rade originálu (`_002`, nie `__grid_001__grid_001`).

Existujúce súbory ani originál sa nikdy neprepisujú — ak zvolený súbor (alebo jeho protokol vedľa neho) už existuje, aplikácia požiada o iný názov. Pri akejkoľvek chybe nevznikne žiadny výstup.

**Potom v LightBurne:**

1. Otvorte výstup: v hlásení o uložení tlačidlom **Otvoriť v LightBurne** (alebo ikonou na paneli nástrojov, **Súbor → Otvoriť uložený projekt v LightBurne**, Ctrl+L). Aplikácia súbor otvorí rovnako ako dvojklik v Prieskumníkovi: bežiaci LightBurn nahradí otvorený projekt — ak má neuložené zmeny, sám sa spýta na uloženie; inak sa LightBurn spustí. Ručne otvárajte cez **File → Open** (nie Import — Import nenačíta nastavenia projektu).
2. Skontrolujte vrstvy, výkony a rýchlosti.
3. Spustite **Preview** a prezrite dráhy.
4. Overte polohu na stroji (**Frame**). Až potom režte, pod dohľadom.

[← Doska](board.md) · [Riešenie problémov →](troubleshooting.md)
