from cabs.calcul import calculer_cabs
from cabs.geo import deduire_macro_zone


def test_deduction_macro_zone_departements_connus_trois_zones():
    """Source officielle : ecologie.gouv.fr, répartition des départements par zone climatique."""
    assert deduire_macro_zone("44") == "H2"   # Loire-Atlantique
    assert deduire_macro_zone("75") == "H1"   # Paris
    assert deduire_macro_zone("13") == "H3"   # Bouches-du-Rhône


def test_deduction_macro_zone_departement_inconnu_retourne_none():
    assert deduire_macro_zone("999") is None


def test_activite_avec_departement_sans_zone_bloque_et_demande_sous_zone():
    """
    La source officielle ne couvre que la macro-zone (H1/H2/H3), jamais la
    sous-zone (H1a/H1b/H1c/H2a/H2b/H2c/H2d) nécessaire aux tables CVC/USE.
    Le calcul doit donc toujours bloquer dans ce cas et demander une saisie
    manuelle de la sous-zone exacte — jamais deviner laquelle.
    """
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "departement": "44",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "H2" in resultat["raisons"][0]
    assert "sous-zone" in resultat["raisons"][0]


def test_activite_avec_departement_inconnu_bloque_avec_message_departement_non_resolu():
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "departement": "999",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "département" in resultat["raisons"][0].lower()


def test_zone_climatique_manuelle_reste_prioritaire_sur_departement():
    """Le mode saisie manuelle (ENO-16) reste utilisable en fallback explicite,
    y compris si un département est aussi fourni (la saisie manuelle gagne)."""
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "zone_climatique": "H2b",
                "tranche_altitude": "<400",
                "departement": "44",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "CALCULÉ"


def test_departement_zone_h3_resolu_directement_sans_blocage():
    """H3 n'est pas subdivisée (zone homogène, pas de a/b/c/d) : la déduction
    peut donc résoudre directement 'H3' sans ambiguïté de sous-zone. Il n'existe
    pas d'entrée CVC H3 dans la table bureaux du prototype -> reste bloqué,
    mais pour une raison différente (CVC manquant, pas sous-zone ambiguë)."""
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 1000,
                "departement": "13",  # Bouches-du-Rhône -> H3
                "tranche_altitude": "<400",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "sous-zone" not in resultat["raisons"][0]
    assert "CVC indisponible" in resultat["raisons"][0]
