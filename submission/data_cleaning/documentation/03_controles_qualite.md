# 03. Contrôles de qualité des données

Après le nettoyage et l'harmonisation, plusieurs contrôles ont été effectués afin de vérifier la qualité des fichiers obtenus.

1. Contrôle global

Les 11 fichiers nettoyés ont été examinés pour vérifier leur disponibilité, leurs dimensions, les valeurs manquantes et les doublons complets. Les 11 fichiers ont satisfait aux contrôles réalisés.

2. Vérification finale

Un contrôle supplémentaire a porté sur le nombre de lignes, les régions, les catégories, les années et les clés d'identification. Aucun problème n'a été détecté selon les critères définis dans le script de vérification.

3. Vérification de fidélité

Les scripts de nettoyage et d'harmonisation ont été réexécutés à partir du fichier Excel original. Les résultats obtenus ont ensuite été comparés aux 11 fichiers CSV finaux.

La comparaison n'a révélé aucune différence entre les fichiers reconstruits et les fichiers finaux.

Bilan

Les 11 fichiers ont satisfait aux contrôles structurels et à la vérification de fidélité. Les rapports détaillés sont disponibles dans le dossier `results/quality_reports/`.