import pytest
from cabs.calcul import calculer_cabs


def _site(sous_categorie, params, zone="H2b", altitude="<400"):
    return {
        "activites": [
            {
                "label": "Zone",
                "sous_categorie": sous_categorie,
                "s_conso": 1000,
                "zone_climatique": zone,
                "tranche_altitude": altitude,
                "params": params,
            }
        ],
        "conso_reelle_kwh": 100000,
    }


def test_administration_bureaux_mono_activite_calcule():
    site = _site("logistique_administration_bureaux", {"T_occ": 70, "Surf_poste": 18, "Nb_h_ouvrees": 3120})
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_froid_negatif_mono_activite_calcule():
    site = _site("logistique_froid_negatif", {"Hauteur": 1, "Nb_ouverture": 0, "Surface": 1000, "Tcons": -18, "Nb_h_ouvrees": 8760})
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_temp_dirigee_1_8_mono_activite_calcule():
    site = _site("logistique_temp_dirigee_1_8", {"Hauteur": 1, "Nb_ouverture": 0, "Surface": 1000, "Tcons": 3, "Nb_h_ouvrees": 8760})
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_temp_dirigee_12_17_mono_activite_calcule():
    site = _site("logistique_temp_dirigee_12_17", {"Hauteur": 1, "Nb_ouverture": 0, "Surface": 1000, "Tcons": 15, "Nb_h_ouvrees": 8760})
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_entrepot_temp_ambiante_mono_activite_calcule():
    site = _site("entrepot_temp_ambiante", {
        "Surf_cond": 0, "Npalettes": 165, "Nb_h_ouvrees": 3744, "HSP": 9, "Tcons": 12,
        "Conso_process": 0, "Surface": 1000,
    })
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_entrepot_sans_maintien_mono_activite_calcule():
    site = _site("entrepot_sans_maintien", {"Surf_cond": 0, "Npalettes": 17, "Nb_h_ouvrees": 380, "Conso_process": 0, "Surface": 1000})
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "CALCULÉ"


def test_zone_non_couverte_bloque_pour_categorie_logistique():
    site = _site("logistique_froid_negatif", {"Hauteur": 1, "Nb_ouverture": 0, "Surface": 1000, "Tcons": -18, "Nb_h_ouvrees": 8760}, zone="H3", altitude=">1600")
    resultat = calculer_cabs(site, echeance="2030")
    assert resultat["statut"] == "BLOQUÉ"
