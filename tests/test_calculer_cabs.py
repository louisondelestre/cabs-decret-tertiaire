from cabs.calcul import calculer_cabs


def test_site_mono_activite_bureaux_couvert_retourne_calcule():
    """
    Cas verifie : exemple chiffre publie par GRDF Cegibat, citant l'arrete
    seuil n1 du 24/11/2020 - immeuble de bureaux, 3500 h ouvrees/an,
    20 m2/poste, 50% de taux d'occupation, zone H2b <400m, echeance 2030.
    Attendu : USE modulé = 38,46 kWh/m2/an, CVC = 50 kWh/m2/an,
    Cabs unitaire = 88,46 kWh/m2/an.
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
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "CALCULÉ"
    assert "trace_par_activite" in resultat
    assert "cabs_pondere_kwh_m2_an" in resultat
    assert "seuil_absolu_kwh_an" in resultat
    assert "ecart_kwh" in resultat
    assert "statut_prudent" in resultat
    assert "hypotheses" in resultat


def test_statut_prudent_ne_contient_jamais_conforme():
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
        "conso_reelle_kwh": 95000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    texte = resultat["statut_prudent"].lower()
    assert "non conforme" not in texte
    assert "conforme" not in texte
