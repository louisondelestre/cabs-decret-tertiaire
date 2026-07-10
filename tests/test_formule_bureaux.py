import pytest
from cabs.formules.bureaux import use_modulé


def test_use_modulé_cas_grdf_verifie():
    """
    Source : GRDF Cegibat, exemple chiffré arrêté seuil n°1 du 24/11/2020.
    3500 h ouvrées/an, 20 m²/poste, 50% occupation -> USE modulé = 38,46 kWh/m²/an.
    """
    etalons = {
        "USE_etalon": 50,
        "T_occ_etalon": 70,
        "Surf_poste_etalon": 18,
        "Nb_h_ouvrees_etalon": 3120,
    }

    resultat = use_modulé(etalons, T_occ=50, Surf_poste=20, Nb_h_ouvrees=3500)

    assert resultat == pytest.approx(38.46, abs=0.01)
