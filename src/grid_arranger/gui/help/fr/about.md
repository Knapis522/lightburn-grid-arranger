# Version, fichiers pris en charge et données

- Version de l'application : **Aide → À propos**.
- Vérifié avec : LightBurn 2.2.00, projets `.lbrn2`, lasers dont l'origine est dans n'importe quel coin (en haut à gauche et en haut à droite sur de vrais lasers, en bas à gauche et en bas à droite avec des appareils de test LightBurn).
- L'application fonctionne **hors ligne** et ne pilote pas le laser. La seule connexion Internet est la recherche de mises à jour sur GitHub (sans aucune donnée sur vos projets) ; elle peut être désactivée dans **Paramètres → Mises à jour**.
- **Paramètres** (élément de la barre de menus, icône d'engrenage, Ctrl+,) ouvre une fenêtre distincte avec les pages *Général*, *Lasers* (catalogue des lasers — voir [Projet pour un autre laser](prepare.md)), *Enregistrement* (objets non cochés, protocole d'enregistrement) et *Mises à jour*. Les modifications prennent effet avec **OK** ou **Appliquer** ; **Annuler** ferme la fenêtre sans modification (après *Appliquer*, le bouton s'appelle **Fermer**).
- **Paramètres → Plaques :** mode de répartition par défaut sur plusieurs plaques, complément de la dernière plaque, avertissement au-delà d'un nombre de plaques et enregistrement comme pages ou fichiers séparés — voir [Plusieurs plaques](board.md).
- **Langue :** **Paramètres → Général → Langue** — Automatique (selon Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Chaque langue est affichée sous son propre nom.
- **Panneau de disposition :** **Paramètres → Général → Panneau de disposition** — les sections Projet, Éléments, Grille, Placement et Plaque à gauche ou à droite de l'aperçu.
- Apparence : **Paramètres → Général → Apparence** (automatique selon Windows ; clair = toute l'application claire ; sombre = commandes sombres, l'aperçu de la plaque reste clair).
- **Unités :** **Paramètres → Général → Unités** — millimètres ou pouces (comme dans LightBurn). Seuls l'affichage et la saisie des valeurs changent ; le calcul et le projet enregistré sont toujours en millimètres, changer d'unités ne déplace donc rien.
- Les sections du panneau latéral (Projet, Éléments, Grille, …) peuvent être repliées en cliquant sur leur en-tête ; l'état est mémorisé.
- Les paramètres (langue, apparence, unités, côté du panneau, plaques par défaut par laser, catalogue des lasers, profils) sont enregistrés dans le profil utilisateur Windows, pas dans le projet.
- Installation : exécutez `GridArranger-Setup-….exe` (aucun droit d'administrateur nécessaire ; l'application apparaît dans le menu Démarrer). Solution sans installation : décompressez le ZIP et lancez `GridArranger.exe` — il doit rester à côté du dossier `_internal`.
- **Mises à jour :** avec la recherche automatique activée (**Paramètres → Mises à jour**), l'application propose une nouvelle version à chaque démarrage ; à tout moment aussi avec le bouton **Rechercher des mises à jour** dans **Paramètres → Mises à jour** (ou Aide → Rechercher des mises à jour). La version la plus récente est toujours proposée, avec les changements depuis votre version. Vous pouvez l'installer (l'application se ferme, installe la nouvelle version et redémarre), demander un rappel plus tard ou ignorer la version — une version plus récente sera de nouveau proposée. Rien n'est installé sans votre accord ; le programme d'installation téléchargé est vérifié par une somme de contrôle avant son exécution. Les versions préliminaires (de test) ne sont proposées que si « Inclure les versions préliminaires » est activé.
- Un projet peut aussi être ouvert en déposant un fichier `.lbrn2` sur `GridArranger.exe`.
- Une copie issue du ZIP se met à jour manuellement : décompressez la nouvelle version dans un nouveau dossier ; les paramètres sont conservés.

> Remarque : cette traduction a été réalisée automatiquement et doit encore être relue par un locuteur natif.

[← Introduction](index.md)
