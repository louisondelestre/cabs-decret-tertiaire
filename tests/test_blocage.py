from cabs.calcul import calculer_cabs


def test_sous_categorie_non_implementee_bloque_le_site_entier():
    site = {
        "activites": [
            {
                "label": "Surface de vente",
                "sous_categorie": "commerce_gsa_hypermarche",
                "s_conso": 4000,
                "zone_climatique": "H1a",
                "tranche_altitude": "<400",
                "params": {},
            },
            {
                "label": "Bureaux admin",
                "sous_categorie": "bureaux_standards",
                "s_conso": 200,
                "zone_climatique": "H2b",
                "tranche_altitude": "<400",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            },
        ],
        "conso_reelle_kwh": 500000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "commerce_gsa_hypermarche" in resultat["raisons"][0]
    # aucun résultat partiel pondéré sur la seule activité Bureaux couverte
    assert "trace_par_activite" not in resultat


def test_zone_altitude_non_couverte_bloque():
    site = {
        "activites": [
            {
                "label": "Bureaux",
                "sous_categorie": "bureaux_standards",
                "s_conso": 800,
                "zone_climatique": "H3",
                "tranche_altitude": ">1600",
                "params": {"T_occ": 50, "Surf_poste": 20, "Nb_h_ouvrees": 3500},
            }
        ],
        "conso_reelle_kwh": 90000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"


def test_echeance_non_couverte_bloque():
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

    resultat = calculer_cabs(site, echeance="2040")

    assert resultat["statut"] == "BLOQUÉ"
