# Release Notes

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] 2025-11-27

### Changements

- **Correction :** mise à jour de la gestion des erreurs lors de la sauvegarde des images chargées par les utilisateurs.
- **Optimisation :** si un utilisateur propose une image déjà présente, la sauvegarde est ignorée.
- **Optimisation :** une erreur de chargement est désormais notifiée au développeur dès sa survenue.

## [0.2.1] 2025-11-23

### Ajouts

- **Ajout :** système de pages multiples.
- **Ajout :** icônes Material Symbols (section pages & onglet de l'application).
- **Ajout :** page Nouveautés.
- **Ajout :** score s'affiche désormais directement sous les résultats.

### Changements

- **Optimisation :** mise à jour de la bibliothèque de construction d'interface Streamlit (1.22 -> 1.51).
- **Optimisation :** mise à jour de toutes les autres bibliothèques du projet.
- **Optimisation :** le système de mise en cache fonctionne désormais pour la connexion vers le bucket cloud.
- **Correction :** un oubli empêchait la sauvegarde des photographies déposées par l'utilisateur.
  
### Suppression

- **Suppression :** section Debug sous les résultats.

## [0.2.0] - 2025-11-19

### Ajouts

- **Ajout :** fonds 209SUP complet (23 391 photographies).
- **Ajout :** fonctionnalité de sauvegarde automatique des photographies déposées par l'utilisateur.

## [0.0.1] - 2025-10-29

### Ajout

- Démonstration initiale.