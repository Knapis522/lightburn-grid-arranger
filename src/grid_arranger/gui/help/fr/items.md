# Sélectionner et ordonner les éléments

Après l'ouverture d'un projet (icône **Ouvrir un projet** de la barre d'outils, **Fichier → Ouvrir un projet** ou Ctrl+O), la liste affiche tous les groupes de premier niveau :

- Les éléments **cochés** sont disposés dans la grille. Le nombre devant le nom est leur position dans la grille.
- Les éléments **non cochés** sont exclus de la sortie : ils ne figurent pas dans le projet enregistré et la grille ne les prend pas en compte. Pour les laisser plutôt à leur place, choisissez **Paramètres → Enregistrement → Objets non cochés → Laisser en place** — la grille les évite alors.
- Les éléments **grisés** (« ne peut pas être déplacé ») ont été refusés — survolez-les pour voir pourquoi. Ils ne sont jamais déplacés.
- ⚠ signale un avertissement (p. ex. un texte qui ne peut pas être mesuré) — l'élément est utilisable, mais vérifiez-le dans Preview.
- **Exclure des objets :** sélectionnez des éléments dans la liste (y compris les grisés) et appuyez sur **Suppr** (ou **Édition → Exclure de la sortie**, ou clic droit). Ils passent barrés en bas de la liste et ne figurent pas dans le projet enregistré — pratique quand vous n'avez besoin que d'une partie d'un grand projet. **Édition → Restaurer les objets exclus** fait revenir ceux qui sont sélectionnés. Les copies sélectionnées sont simplement supprimées. Le projet d'origine n'est jamais modifié.
- **Renommer :** F2, double-clic ou clic droit → *Renommer l'élément…* donne à un élément votre propre nom (p. ex. « Porte-clés Pierre »). Le nom n'existe que dans l'application — dans la liste, le protocole et les noms des nouvelles pages — et n'est pas écrit dans le projet LightBurn. L'application retient les noms pour le fichier concerné.

Ordre : **saisissez un élément dans l'aperçu avec la souris et faites-le glisser à la place d'un autre élément** — un cadre vert indique où il atterrira ; **les deux éléments échangent leurs places**, tous les autres restent et la liste est renumérotée. Relâcher en dehors des éléments annule le glissement. Ou sélectionnez un élément dans la liste et utilisez **Monter / Descendre**. Un élément nouvellement coché est ajouté à la fin. **Ordre par défaut** rétablit l'ordre du fichier. **Tout sélectionner / Ne rien sélectionner** changent la sélection d'un coup.

**Rotation :** un élément tourné affiche une flèche et l'angle dans la liste (↻ sens horaire, ↺ sens antihoraire). Sélectionnez un élément en **cliquant dessus dans l'aperçu** (cadre orange) ou dans la liste ; **Ctrl+clic** en ajoute d'autres, **Échap** efface la sélection. Pour les éléments sélectionnés :

- **↺ 90° / ↻ 90°** — tourner de 90° (p. ex. pour que tous les porte-clés aient le trou en haut) ;
- **Angle de la sélection** — saisissez un angle quelconque en degrés (positif = sens horaire) ;
- **Ne pas tourner** — l'élément reste tel qu'il est dans le projet (sens du texte, fil du matériau) ;
- **Auto** — supprime l'angle manuel ; l'application tourne de nouveau l'élément elle-même.

Un angle manuel est marqué « (manuel) » dans la liste ; l'application ne le modifie jamais et il s'applique aussi avec la Rotation *Ne pas tourner*. L'angle est mesuré depuis la position dans le projet d'origine. Ouvrir un autre projet efface les angles manuels. Voir [grille](grid.md).

**Copies (remplir la plaque) :** sélectionnez des éléments et appuyez sur **Ctrl+C** puis **Ctrl+V** — une copie de chacun est ajoutée. Pour plusieurs copies à la fois, utilisez l'icône **Créer des copies** de la barre d'outils (ou **Ctrl+D**, menu Édition) et saisissez le nombre, p. ex. 5. Les copies sont ajoutées à la fin de l'ordre, sont marquées « (copie de G5) » dans la liste, reprennent l'angle manuel et peuvent être tournées et déplacées comme tout autre élément. Supprimez une copie avec **Suppr** ou en la décochant. Les copies sont écrites dans le projet enregistré comme nouveaux groupes ; le projet d'origine n'est pas modifié.

**Pièces** (champ à côté de *Angle de la sélection*) : combien de pièces de l'élément sélectionné placer — p. ex. 5 = l'original + 4 copies placées juste après (les éléments restent groupés par variante). Le diminuer supprime les copies les plus récentes, **0** n'utilise pas l'élément. Avec une copie sélectionnée, le champ modifie les pièces de son original ; la liste affiche « ×5 » à côté de l'élément.

**Remplir la plaque de copies** (icône de plaque sur la barre d'outils, **Ctrl+Maj+D**, menu Édition) : ajoute autant de copies des éléments sélectionnés qu'il en tient encore sur la plaque, la disposition passant la vérification. Avec plusieurs éléments sélectionnés, les copies alternent (A, B, A, B…). Fonctionne au mieux avec le nombre de colonnes *Automatique* ; avec un nombre de colonnes fixe, seules des lignes sont ajoutées.

L'élément numéro **1** est placé dans le coin de la grille donné par l'*Ordre de remplissage* (voir [grille](grid.md)).

[← Préparation](prepare.md) · [Suite : grille →](grid.md)
