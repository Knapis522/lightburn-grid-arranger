# Préparer le projet dans LightBurn

1. **Groupez chaque élément séparément** (Ctrl+G). Un groupe = un élément.
2. Chaque groupe doit avoir un **contour de découpe fermé** contenant tout le reste (textes, motifs). Le contour peut avoir des coins arrondis ou une autre forme — la taille de l'élément est le rectangle autour du contour. Le contour peut être une courbe ou une forme dessinée directement dans LightBurn (cercle, ellipse, rectangle, polygone) ; un groupe peut contenir d'autres groupes (p. ex. un porte-clés : cercle avec un trou + texte).
3. Enregistrez le projet (**Save As**) au format `.lbrn2`. L'application lit uniquement le fichier enregistré — elle ne voit pas les modifications non enregistrées dans LightBurn.
4. Enregistrez le projet pour le laser sur lequel vous découperez. L'application reconnaît le laser et son origine (en haut à gauche, en haut à droite, en bas à gauche ou en bas à droite — p. ex. lasers à diode) à partir du projet. **Après avoir changé de laser dans LightBurn, enregistrez à nouveau le projet** et rouvrez-le.

Pris en charge : LightBurn 2.2, projets `.lbrn2`, lasers dont l'origine est dans n'importe quel coin. Les anciens fichiers `.lbrn` sont refusés — enregistrez le projet dans LightBurn au format `.lbrn2`.

## Projet pour un autre laser

Un projet enregistré pour un laser peut être préparé pour un autre, p. ex. d'un laser avec l'origine en haut à droite vers un laser avec l'origine en haut à gauche — sans changer d'appareil ni retourner le dessin dans LightBurn. Dans la section **Projet**, choisissez **Préparer pour :** un laser du catalogue. L'application propose sa plaque, remplit la grille depuis son origine, et le fichier enregistré (`…__Nom_du_laser__grid_001.lbrn2`) est prêt pour lui : le fichier indique le laser cible et les éléments sont mis en miroir pour avoir le même aspect sur celui-ci (textes lisibles).

- Catalogue des lasers : **Paramètres → Lasers** (ou *Gérer les lasers…* dans la liste). Les lasers des projets ouverts sont ajoutés automatiquement ; ajoutez les autres (p. ex. un laser à diode) manuellement — **le nom doit correspondre à l'appareil dans LightBurn** ; choisissez le coin de l'origine et la plaque.
- Avec une autre origine, **tous les éléments** doivent être sélectionnés et le projet ne doit pas contenir d'autres objets (ils resteraient en miroir sur l'autre laser). Cela ne concerne que les objets conservés dans la sortie — les objets non cochés et exclus ne figurent pas dans la sortie (par défaut) et ne gênent donc pas.
- **Les réglages des calques (puissance, vitesse) ne sont pas convertis** — ils restent ceux du projet d'origine. Ouvrez la sortie dans LightBurn avec le laser cible et vérifiez les calques.

## Projet avec plusieurs pages

Un projet avec plusieurs pages (**Window → Pages** dans LightBurn) peut aussi être ouvert. Dans la section Projet, choisissez **Page à disposer :** ; les autres pages restent inchangées. Par défaut, c'est la page active lors de l'enregistrement du projet qui est choisie.

[← Introduction](index.md) · [Suite : éléments →](items.md)
