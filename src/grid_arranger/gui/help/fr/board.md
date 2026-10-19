# Plaque, marges et contrôle des collisions

La **plaque** est le rectangle de matériau en coordonnées LightBurn. Par défaut, elle se trouve à l'origine du laser (coin de la plaque X 0, Y 0). Sa taille est préremplie selon le laser enregistré dans le projet ; **Enregistrer par défaut pour ce laser** mémorise vos valeurs. Les **marges** (5 mm par défaut) sont une bande le long des bords de la plaque où rien ne peut être placé.

> La plaque dans l'application n'est pas la zone de travail de la machine. Vérifiez la position réelle du matériau et le cadrage sur la machine.

Avant l'enregistrement, l'application vérifie que :

- tous les éléments déplacés se trouvent dans la zone utile de la plaque,
- les éléments ne se chevauchent pas et respectent l'espacement,
- les éléments respectent aussi l'espacement par rapport aux groupes **non déplacés** et aux objets isolés, s'ils restent dans la sortie (Paramètres → Enregistrement) ; les objets exclus sont ignorés,
- un objet dont la taille ne peut pas être déterminée **bloque** l'enregistrement (la sécurité ne peut pas être confirmée).

Les erreurs (✖) bloquent l'enregistrement et nomment les éléments concernés. Les avertissements (⚠) non. L'application ne met jamais à l'échelle, ne tourne ni ne déplace d'elle-même les objets non sélectionnés.

La vérification travaille avec les contours du projet, pas avec le dépassement réel lors de la gravure, la compensation du trait de coupe ou le mouvement de la tête — c'est pourquoi la **Preview dans LightBurn est obligatoire**.

## Plusieurs plaques

Quand les pièces ne tiennent pas sur une plaque, l'application les répartit sur plusieurs plaques. Choisissez comment dans la section Plaque sous **Si ça ne tient pas** :

- *Répartir sur des plaques l'une après l'autre* (par défaut) — plaque 1 pleine, puis plaque 2 … ; le moins de plaques.
- *Répartir sur des plaques de façon égale* — le même nombre de pièces sur chaque plaque (p. ex. 50 → 17/17/16).
- *Répartir sur des plaques par élément* — chaque plaque ne contient que des pièces d'un seul élément (l'original et ses copies).
- *Ne pas répartir (erreur)* — comme avant : si la disposition ne tient pas, elle est bloquée.

**Compléter la dernière plaque avec des copies** ajoute des copies jusqu'à ce que la dernière plaque soit pleine (avec *par élément*, la dernière plaque de chaque élément est complétée avec des copies de cet élément).

Au-dessus de l'aperçu, des onglets montrent les plaques, comme les pages dans LightBurn ; un onglet en erreur est marqué ✖ et les messages indiquent la plaque. L'enregistrement n'est possible que si toutes les plaques passent la vérification. Toutes les plaques ont les mêmes réglages de grille et la même plaque ; les objets laissés en place (Paramètres → Enregistrement) ne sont que sur la plaque 1.

**Enregistrement :** la plaque 1 reste sur la page disposée et les plaques 2 … sont ajoutées comme nouvelles pages juste après elle (« Page 1 – plaque 2 » …). Dans LightBurn, changez de page (**Window → Pages**) et découpez une plaque après l'autre — Preview et Frame ne travaillent qu'avec la page active. Sinon, **Paramètres → Plaques → Comme fichiers séparés** enregistre un fichier par plaque (`…__plaque1.lbrn2` …). Les valeurs par défaut (mode de répartition, complément, avertissement au-delà d'un nombre de plaques) sont dans **Paramètres → Plaques**.

[← Grille](grid.md) · [Suite : enregistrement →](save.md)
