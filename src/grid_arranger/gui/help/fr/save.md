# Enregistrer et vérifier dans LightBurn

L'icône **Enregistrer comme nouveau projet** de la barre d'outils (ou **Fichier → Enregistrer comme nouveau projet**, Ctrl+S) n'est active que si la disposition a passé la vérification. Une boîte d'enregistrement s'ouvre avec le nom proposé `original__grid_001.lbrn2` (puis `_002`, …) dans le dossier de l'original — **vous pouvez changer le dossier et le nom**. Après confirmation, l'application :

1. prépare un nouveau fichier dans lequel seules les positions des groupes sélectionnés (et de leurs textes) changent, les objets exclus sont retirés,
2. vérifie de façon indépendante que rien d'autre n'a changé (calques, puissance, textes, autres objets),
3. vérifie que l'original n'a pas changé depuis son ouverture,
4. enregistre un **nouveau** fichier sous le nom choisi.

**Protocole d'enregistrement** (`.json`) — un relevé indiquant à partir de quoi et comment la sortie a été créée : sommes de contrôle, laser, réglages de la grille, déplacements des éléments et résultat de la vérification (sans motifs ni textes des éléments). Utile pour le suivi ou le signalement d'un problème. **Paramètres → Enregistrement → Protocole d'enregistrement** : *Ne pas enregistrer* (par défaut), *À côté du projet enregistré* (`<nom>.json`) ou *Dans le dossier des protocoles de l'application* (ouvrez-le avec **Ouvrir le dossier des protocoles**).

**Après l'enregistrement, vous continuez à travailler sur l'original.** Le fichier enregistré est une nouvelle copie distincte ; le projet d'origine reste ouvert dans l'application, vous pouvez donc essayer une autre disposition et enregistrer une autre variante (`_002`, …). La barre de titre et la section Projet affichent *dernier enregistrement : …*. Pour continuer plutôt avec le fichier enregistré (comme « Enregistrer sous »), cochez **Continuer ici avec le fichier enregistré** dans le message d'enregistrement — il s'ouvre à la place de l'original, ses copies et rotations sont désormais figées et l'historique d'annulation recommence. L'enregistrement suivant continue alors la numérotation de l'original (`_002`, et non `__grid_001__grid_001`).

Ni les fichiers existants ni l'original ne sont jamais écrasés — si le fichier choisi (ou son protocole à côté) existe déjà, l'application demande un autre nom. En cas d'échec, aucune sortie n'est créée.

**Ensuite dans LightBurn :**

1. Ouvrez la sortie : dans le message d'enregistrement avec **Ouvrir dans LightBurn** (ou l'icône de la barre d'outils, **Fichier → Ouvrir le projet enregistré dans LightBurn**, Ctrl+L). L'application ouvre le fichier comme un double-clic dans l'Explorateur : un LightBurn en cours d'exécution remplace son projet ouvert — s'il a des modifications non enregistrées, LightBurn demande lui-même de les enregistrer ; sinon LightBurn démarre. Pour l'ouvrir manuellement, utilisez **File → Open** (pas Import — Import ne charge pas les réglages du projet).
2. Vérifiez les calques, la puissance et la vitesse.
3. Lancez la **Preview** et examinez les trajets.
4. Vérifiez la position sur la machine (**Frame**). Ensuite seulement, découpez, sous surveillance.

**Modifications non enregistrées :** si la disposition a changé depuis l'ouverture ou le dernier enregistrement, la barre de titre affiche un astérisque après le nom du projet (`karty.lbrn2*`). À la fermeture de l'application, à l'ouverture d'un autre projet ou à l'installation d'une mise à jour, l'application demande s'il faut enregistrer la disposition comme nouveau projet, l'abandonner ou annuler. Si la disposition n'a pas passé la vérification, seuls l'abandon et l'annulation sont proposés.

[← Plaque](board.md) · [Résolution des problèmes →](troubleshooting.md)
