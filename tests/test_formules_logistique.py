import pytest
from cabs.formules import logistique


def test_administration_bureaux_cas_etalon_egale_use_etalon():
    """Au point étalon exact (T_occ, Surf_poste, Nb_h_ouvrees = étalon), USE_modulé
    doit valoir USE_étalon (le terme 0,28*CVC*(...) s'annule car Nb_h_ouvrées = étalon)."""
    etalons = {"USE_etalon": 50, "Part_USE_variable": 0.77, "Nb_h_ouvrees_etalon": 3120,
               "Surf_poste_etalon": 18, "T_occ_etalon": 70}
    resultat = logistique.use_modulé_administration_bureaux(etalons, cvc=50, T_occ=70, Surf_poste=18, Nb_h_ouvrees=3120)
    assert resultat == pytest.approx(50, abs=0.01)


def test_froid_negatif_cas_etalon_egale_use_zone():
    """Au point étalon (Hauteur=1, Nb_ouverture=0, Tcons=Tcons_étalon, Nb_h_ouvrées=étalon),
    USE_modulé doit valoir USE_zone (les termes correctifs valent 1)."""
    etalons = {"Hauteur_etalon": 1, "Tcons_etalon": -18, "Nb_ouverture_etalon": 0,
               "Nb_h_ouvrees_etalon": 8760, "ratio_kwh_par_ouverture": 1.5,
               "coefficient_temperature_par_degre": 0.05}
    resultat = logistique.use_modulé_froid_negatif(
        etalons, use_zone=52.8, Hauteur=1, Nb_ouverture=0, Surface=1000, Tcons=-18, Nb_h_ouvrees=8760
    )
    assert resultat == pytest.approx(52.8, abs=0.01)


def test_temp_dirigee_1_8_cas_etalon_egale_use_zone():
    etalons = {"Hauteur_etalon": 1, "Tcons_etalon": 3, "Nb_ouverture_etalon": 0,
               "Nb_h_ouvrees_etalon": 8760, "ratio_kwh_par_ouverture": 0.8,
               "coefficient_temperature_par_degre": 0.037}
    resultat = logistique.use_modulé_temp_dirigee_1_8(
        etalons, use_zone=26.4, Hauteur=1, Nb_ouverture=0, Surface=1000, Tcons=3, Nb_h_ouvrees=8760
    )
    assert resultat == pytest.approx(26.4, abs=0.01)


def test_temp_dirigee_12_17_cas_etalon_egale_use_zone():
    etalons = {"Hauteur_etalon": 1, "Tcons_etalon": 15, "Nb_ouverture_etalon": 0,
               "Nb_h_ouvrees_etalon": 8760, "ratio_kwh_par_ouverture": 0.3,
               "coefficient_temperature_par_degre": 0.02}
    resultat = logistique.use_modulé_temp_dirigee_12_17(
        etalons, use_zone=10, Hauteur=1, Nb_ouverture=0, Surface=1000, Tcons=15, Nb_h_ouvrees=8760
    )
    assert resultat == pytest.approx(10, abs=0.01)


ETALONS_TEMP_AMBIANTE = {
    "USE_etalon": 8, "Part_USE_variable": 0.6, "Nb_h_ouvrees_etalon": 3744,
    "Npalettes_etalon": 165, "Tcons_etalon": 12, "Variation_Tcons": 4.4,
    "HSP_etalon": 9, "Variation_HSP": 5, "Variation_Surf_cond": 0.6,
}


def test_entrepot_temp_ambiante_cas_etalon_conso_process_zero():
    resultat = logistique.use_modulé_entrepot_temp_ambiante(
        ETALONS_TEMP_AMBIANTE, cvc=16, Surf_cond=0, Npalettes=165, Nb_h_ouvrees=3744,
        HSP=9, Tcons=12, Conso_process=0, Surface=1000,
    )
    assert resultat == pytest.approx(8, abs=0.01)


def test_entrepot_temp_ambiante_branche_conso_process_positif():
    resultat = logistique.use_modulé_entrepot_temp_ambiante(
        ETALONS_TEMP_AMBIANTE, cvc=16, Surf_cond=0, Npalettes=165, Nb_h_ouvrees=3744,
        HSP=9, Tcons=12, Conso_process=100000, Surface=1000,
    )
    # Conso_process/Surface=100 + USE_etalon*(1-0.6)*1 = 100+3.2 = 103.2 (termes CVC/Tcons nuls au point étalon)
    assert resultat == pytest.approx(103.2, abs=0.01)


ETALONS_SANS_MAINTIEN = {
    "USE_etalon": 1, "Part_USE_variable": 0.63, "Nb_h_ouvrees_etalon": 380,
    "Npalettes_etalon": 17, "Variation_Surf_cond": 0.06,
}


def test_entrepot_sans_maintien_cas_etalon_conso_process_zero():
    resultat = logistique.use_modulé_entrepot_sans_maintien(
        ETALONS_SANS_MAINTIEN, Surf_cond=0, Npalettes=17, Nb_h_ouvrees=380, Conso_process=0, Surface=1000,
    )
    assert resultat == pytest.approx(1, abs=0.01)


def test_entrepot_sans_maintien_branche_conso_process_positif():
    resultat = logistique.use_modulé_entrepot_sans_maintien(
        ETALONS_SANS_MAINTIEN, Surf_cond=0, Npalettes=17, Nb_h_ouvrees=380, Conso_process=50000, Surface=1000,
    )
    # Conso_process/Surface=50 + USE_etalon*(1-0.63)*1 = 50+0.37 = 50.37
    assert resultat == pytest.approx(50.37, abs=0.01)
