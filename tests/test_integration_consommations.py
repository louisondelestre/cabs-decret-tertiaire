import pytest
from cabs.calcul import calculer_cabs
from consommations.agregation import LigneConsommation


def test_site_sans_conso_reelle_manuelle_utilise_agent_consommations():
    """
    calculer_cabs() ne prend plus 'conso_reelle_kwh' en paramètre manuel :
    il reçoit les lignes de consommation brutes et appelle l'agent
    consommations lui-même pour obtenir l'agrégat réel.
    """
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "zone_climatique": "H2b",
                "tranche_altitude": "<400",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "lignes_consommation": [
            LigneConsommation("Bureaux", "eclairage", "electricite", "2025-01", 8000, "kWh", 1200),
        ],
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "CALCULÉ"
    assert resultat["conso_reelle_kwh_an"] == 8000.0


def test_site_bloque_par_agent_consommations_bloque_le_cabs():
    """Si l'agent consommations bloque (ex. fluide non couvert), calculer_cabs()
    doit bloquer aussi, jamais utiliser une valeur par défaut."""
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "zone_climatique": "H2b",
                "tranche_altitude": "<400",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "lignes_consommation": [
            LigneConsommation("Bureaux", "chauffage", "propane", "2025-01", 200, "kg", 300),
        ],
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "consommation" in resultat["raisons"][0].lower() or "propane" in resultat["raisons"][0].lower()
