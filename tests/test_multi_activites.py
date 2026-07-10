import pytest
from cabs.calcul import calculer_cabs


def _activite_bureaux(label, s_conso, T_occ, Surf_poste, Nb_h_ouvrees):
    return {
        "label": label,
        "sous_categorie": "bureaux_standards",
        "s_conso": s_conso,
        "zone_climatique": "H2b",
        "tranche_altitude": "<400",
        "params": {"T_occ": T_occ, "Surf_poste": Surf_poste, "Nb_h_ouvrees": Nb_h_ouvrees},
    }


def test_ponderation_surfacique_sur_trois_activites_de_poids_differents():
    """
    3 activités Bureaux de même sous-catégorie mais de paramètres différents
    (donc de Cabs unitaire différent) et de SConso différentes. Le Cabs
    pondéré du site doit être la moyenne des Cabs unitaires pondérée par
    SConso (prorata surfacique), pas une moyenne simple.
    Valeurs de référence calculées indépendamment : A=88.46, B=100.0,
    C=95.27 kWh/m²/an ; pondéré attendu ≈ 96.91 kWh/m²/an.
    Une moyenne simple donnerait (88.46+100+95.27)/3 ≈ 94.58 — différent,
    ce qui permet de détecter une pondération implémentée par erreur comme
    une moyenne simple.
    """
    site = {
        "activites": [
            _activite_bureaux("A", s_conso=1000, T_occ=50, Surf_poste=20, Nb_h_ouvrees=3500),
            _activite_bureaux("B", s_conso=3000, T_occ=70, Surf_poste=18, Nb_h_ouvrees=3120),
            _activite_bureaux("C", s_conso=500, T_occ=70, Surf_poste=18, Nb_h_ouvrees=2880),
        ],
        "conso_reelle_kwh": 400000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "CALCULÉ"
    assert resultat["cabs_pondere_kwh_m2_an"] == pytest.approx(96.91, abs=0.05)
    # discriminant : différent d'une moyenne simple
    moyenne_simple = (88.46 + 100.0 + 95.27) / 3
    assert resultat["cabs_pondere_kwh_m2_an"] != pytest.approx(moyenne_simple, abs=0.05)


def test_trace_par_activite_affiche_poids_et_contribution():
    site = {
        "activites": [
            _activite_bureaux("A", s_conso=1000, T_occ=50, Surf_poste=20, Nb_h_ouvrees=3500),
            _activite_bureaux("B", s_conso=3000, T_occ=70, Surf_poste=18, Nb_h_ouvrees=3120),
        ],
        "conso_reelle_kwh": 300000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    ligne_a = next(t for t in resultat["trace_par_activite"] if t["activite"] == "A")
    assert ligne_a["poids_%"] == pytest.approx(25.0, abs=0.01)
    assert "contribution_kwh_m2_an" in ligne_a


def test_activite_bloquante_bloque_le_site_meme_avec_dautres_activites_couvertes():
    site = {
        "activites": [
            _activite_bureaux("A", s_conso=1000, T_occ=50, Surf_poste=20, Nb_h_ouvrees=3500),
            {
                "label": "Commerce",
                "sous_categorie": "commerce_gsa_hypermarche",
                "s_conso": 500,
                "zone_climatique": "H2b",
                "tranche_altitude": "<400",
                "params": {},
            },
        ],
        "conso_reelle_kwh": 300000,
    }

    resultat = calculer_cabs(site, echeance="2030")

    assert resultat["statut"] == "BLOQUÉ"
    assert "trace_par_activite" not in resultat
