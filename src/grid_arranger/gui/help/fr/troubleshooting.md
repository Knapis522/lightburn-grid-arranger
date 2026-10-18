# Résolution des problèmes

**« Cette application ne prend en charge que les projets .lbrn2 »** — enregistrez le projet dans LightBurn au format `.lbrn2`.

**« Version de LightBurn non prise en charge »** — le projet a été enregistré par une version de LightBurn avec laquelle l'application n'a pas été vérifiée. La sortie pourrait ne pas être sûre, elle est donc refusée.

**Élément « ne peut pas être déplacé »** — survolez-le. Le plus souvent : le groupe n'a pas de contour de découpe fermé, quelque chose dépasse du contour, il est verrouillé ou il contient un type d'objet que l'application ne sait pas encore déplacer en toute sécurité (p. ex. une image bitmap).

**« La géométrie du texte ne correspond pas à sa position »** — ouvrez le projet dans LightBurn et enregistrez-le à nouveau.

**L'enregistrement est bloqué** — lisez les erreurs (✖) sous l'aperçu : dépassement de la plaque, collision, espacement trop petit ou objet qui ne peut pas être mesuré. Modifiez les colonnes, les espacements, la plaque ou la sélection.

**« Le fichier d'origine a changé depuis son ouverture »** — le projet a été enregistré à nouveau entre-temps. Rouvrez-le dans l'application.

**Windows affiche « Windows a protégé votre ordinateur »** — l'application n'est pas encore signée numériquement. Si le programme d'installation provient des versions de ce projet sur GitHub, cliquez sur **Informations complémentaires → Exécuter quand même**. Ne désactivez pas votre antivirus.

**L'application ne démarre pas ou signale un fichier manquant** — le plus probable est que le dossier `_internal` manque à côté de `GridArranger.exe` (p. ex. seul l'EXE a été copié). Décompressez à nouveau tout le ZIP. Pour vérifier l'installation, exécutez `GridArranger.exe --self-test report.json` dans une invite de commandes ; le résultat est écrit dans `report.json`.

**Signaler un problème** — activez Paramètres → Enregistrement → Protocole d'enregistrement, enregistrez à nouveau et envoyez le protocole `.json` (il contient des sommes de contrôle et des paramètres, pas le contenu des éléments) ainsi que les étapes. N'envoyez des projets de clients qu'avec leur autorisation.

[← Introduction](index.md)
