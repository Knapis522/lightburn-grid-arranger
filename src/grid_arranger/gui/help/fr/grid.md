# Grille et placement

**Profil de disposition** — réglages enregistrés sous un nom (p. ex. « Porte-clés 3 mm ») : nombre de colonnes (ou *Automatique*), espacements, ordre de remplissage, rotation et placement. Choisir un profil dans la section **Profil de disposition** applique les valeurs ; **Enregistrer…** enregistre les réglages actuels comme profil (même nom = remplacer), **Supprimer** le supprime. Lorsque vous modifiez une valeur, le choix passe à *aucun profil* — le profil lui-même n'est pas modifié. La plaque ne fait pas partie d'un profil ; elle appartient au laser (Paramètres → Lasers).

**Colonnes** — combien d'éléments se trouvent sur une ligne. Le nombre de lignes est calculé. Avec **Automatique** coché, l'application utilise autant de colonnes que la largeur de la plaque le permet (la zone utile à l'intérieur des marges) ; le champ affiche alors le nombre calculé. Utile avec les copies et *Remplir la plaque de copies*.

**Espacement X / Y** — distance entre les contours de découpe d'éléments voisins dans les unités choisies (horizontale / verticale). Un espacement de 0 est autorisé, mais l'application signale le risque à la découpe. Saisissez les décimales comme d'habitude dans la langue de l'application (en français avec une virgule).

Si les éléments ont des **tailles différentes**, une colonne est aussi large que son élément le plus large et une ligne aussi haute que son élément le plus haut. L'espacement est alors un **minimum** — il est plus grand entre les éléments plus petits.

**Ordre de remplissage**

- *Depuis l'origine du laser* (par défaut) — l'élément n° 1 est dans le coin à l'origine du laser ; avec l'origine à droite, les lignes sont remplies de droite à gauche ; avec l'origine en bas, la première ligne est en bas et les suivantes au-dessus.
- *Ordre de lecture* — l'élément n° 1 est toujours en haut à gauche, lignes de gauche à droite.

**Placement**

- *Dans le coin de la plaque à l'origine du laser* (par défaut) — le coin de la grille côté origine se trouve dans le coin de la plaque plus la marge.
- *Au centre de la plaque*.
- *Manuellement* — saisissez les coordonnées X/Y de LightBurn (distance depuis l'origine) du coin de la grille côté origine.
- *À la position d'origine des éléments*.

Les champs **Coin X / Y** ne sont modifiables qu'en mode *Manuellement*. Dans les autres modes, ils sont grisés et affichent le coin que l'application vient de calculer (il change p. ex. avec les marges). Après le passage en *Manuellement*, ils conservent le coin actuel, la grille ne bouge donc pas et vous pouvez l'ajuster finement.

L'aperçu montre la plaque, la zone utile (en pointillés), l'origine du laser (●), les éléments déplacés avec leurs vrais motifs et textes dans les couleurs des calques et avec leurs numéros, et les objets non déplacés en gris. Les éléments en erreur sont rouges. **Afficher les motifs** dans l'en-tête de la section Éléments désactive le dessin et ne laisse que les rectangles des éléments. La molette de la souris (ou le pavé tactile) zoome en douceur, faire glisser un espace vide déplace la vue (faire glisser un élément change l'ordre), l'icône **Ajuster la vue** de la barre d'outils (Ctrl+0) ou un double-clic sur un espace vide affiche tout.

## Rotation pour économiser du matériau

L'option **Rotation** de la section Grille :

- *Angle quelconque (surface minimale)* — par défaut. Chaque élément est tourné pour que le rectangle qui l'entoure soit le plus petit possible (gain de place avec les formes inclinées ou irrégulières comme les porte-clés). Les cartes rectangulaires restent droites.
- *Par pas de 90°* — les éléments ne sont tournés que d'un quart de tour (paysage / portrait).
- *Ne pas tourner* — les éléments sont seulement déplacés.

Dans tous les modes, l'application vérifie aussi si la grille serait plus petite avec tous les éléments en paysage ou en portrait et utilise la variante la plus petite — de préférence celle qui tient sur la plaque. Si la rotation ne réduisait pas la grille, les éléments restent tels quels ; les éléments ronds ne sont jamais tournés de 90°. La rotation est visible dans l'aperçu et dans la liste des éléments. Un élément tourne autour de son centre avec ses textes et motifs ; après l'enregistrement, vérifiez la Preview dans LightBurn. Exceptions pour des éléments individuels : le bouton **Ne pas tourner** de la section Éléments.

[← Éléments](items.md) · [Suite : plaque et vérification →](board.md)
