# Plaque, marges et contrôle des collisions

La **plaque** est le rectangle de matériau en coordonnées LightBurn. Par défaut, elle se trouve à l'origine du laser (coin de la plaque X 0, Y 0). Sa taille est préremplie selon le laser enregistré dans le projet ; **Enregistrer par défaut pour ce laser** mémorise vos valeurs. Les **marges** (5 mm par défaut) sont une bande le long des bords de la plaque où rien ne peut être placé.

> La plaque dans l'application n'est pas la zone de travail de la machine. Vérifiez la position réelle du matériau et le cadrage sur la machine.

Avant l'enregistrement, l'application vérifie que :

- tous les éléments déplacés se trouvent dans la zone utile de la plaque,
- les éléments ne se chevauchent pas et respectent l'espacement,
- les éléments respectent aussi l'espacement par rapport aux groupes **non déplacés** et aux objets isolés,
- un objet dont la taille ne peut pas être déterminée **bloque** l'enregistrement (la sécurité ne peut pas être confirmée).

Les erreurs (✖) bloquent l'enregistrement et nomment les éléments concernés. Les avertissements (⚠) non. L'application ne met jamais à l'échelle, ne tourne ni ne déplace d'elle-même les objets non sélectionnés.

La vérification travaille avec les contours du projet, pas avec le dépassement réel lors de la gravure, la compensation du trait de coupe ou le mouvement de la tête — c'est pourquoi la **Preview dans LightBurn est obligatoire**.

[← Grille](grid.md) · [Suite : enregistrement →](save.md)
