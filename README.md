# cabs-decret-tertiaire

Calcul du Cabs (décret tertiaire / dispositif Éco Énergie Tertiaire, méthode valeur absolue) pour des sites tertiaires multi-activités : bureaux et logistique/entrepôts (6 sous-catégories).

Dépend de [`consommations-decret-tertiaire`](../consommations-decret-tertiaire) pour la consommation réelle des sites.

## Installation

```bash
pip install -e ../consommations-decret-tertiaire   # dépendance locale
```

## Utilisation

```python
from cabs.calcul import calculer_cabs
from consommations.agregation import LigneConsommation

site = {
    "activites": [
        {
            "label": "Bureaux",
            "sous_categorie": "bureaux_standards",
            "s_conso": 1000,               # surface de consommations énergétiques (m2)
            "zone_climatique": "H2b",       # ou "departement": "44" pour déduction auto (macro-zone)
            "tranche_altitude": "<400",
            "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
        }
    ],
    "lignes_consommation": [
        LigneConsommation("Bureaux", "eclairage", "electricite", "2025-01", 8000, "kWh", 1200),
    ],
}

resultat = calculer_cabs(site, echeance="2030")
print(resultat["statut"])                  # "CALCULÉ" ou "BLOQUÉ"
print(resultat["cabs_pondere_kwh_m2_an"])
print(resultat["statut_prudent"])          # jamais "conforme/non conforme"
```

Voir `CONTEXT.md` pour le vocabulaire du domaine et les règles non négociables.

## Sous-catégories couvertes

- Bureaux (Standards cloisonnés)
- Logistique : Administration/bureaux, froid négatif, +1 à +8°C, +12 à +17°C, entrepôt température ambiante, entrepôt sans maintien

Toute autre sous-catégorie, ou combinaison zone/altitude non couverte par la table, bloque explicitement.

## Limites connues

- L'altitude reste saisie manuellement (`tranche_altitude`) — pas d'intégration API IGN.
- Les coefficients de conversion fluide → kWh (repo consommations) utilisent des valeurs usuelles publiques, à recroiser avec l'ADEME Base Carbone pour un usage réglementaire strict.
- Commerce et Hôtellerie ne sont pas encore implémentés.

## Tests

```bash
python3 -m pytest tests/ -v
```

## Suivi

Linear, équipe Enorka : PRD ENO-15, tickets ENO-16 à ENO-20.
