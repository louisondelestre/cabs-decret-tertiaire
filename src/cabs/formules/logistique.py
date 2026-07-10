"""
Formules de modulation USE — catégorie Logistique/Entrepôts (6 sous-catégories).

Source : PDF utilisateur "ATDL2430864A_Annexe_I__tous_les_tableaux_Cabs_.pdf"
(Annexe I de l'arrêté modifiant l'arrêté du 10/04/2020, "Valeurs Absolues VI"),
section Logistique.
"""


def use_modulé_administration_bureaux(etalons: dict, cvc: float, T_occ: float, Surf_poste: float, Nb_h_ouvrees: float) -> float:
    """
    Sous-catégorie "Logistique - Administration et bureaux (Bureaux Standards)".
    Source : PDF, p.~465.

    USE modulé = USE_étalon × (Nb_h_ouvrées/Nb_h_ouvrées_étalon)
      × [Part_USE_variable × (T_occ/T_occ_étalon) × (Surf_poste_étalon/Surf_poste) + (1 − Part_USE_variable)]
      + 0,28 × CVC × (Nb_h_ouvrées − Nb_h_ouvrées_étalon) / Nb_h_ouvrées_étalon
    """
    dt = etalons["Nb_h_ouvrees_etalon"]
    return (
        etalons["USE_etalon"]
        * (Nb_h_ouvrees / dt)
        * (
            etalons["Part_USE_variable"] * (T_occ / etalons["T_occ_etalon"]) * (etalons["Surf_poste_etalon"] / Surf_poste)
            + (1 - etalons["Part_USE_variable"])
        )
        + 0.28 * cvc * (Nb_h_ouvrees - dt) / dt
    )


def use_modulé_froid_negatif(etalons: dict, use_zone: float, Hauteur: float, Nb_ouverture: float, Surface: float, Tcons: float, Nb_h_ouvrees: float) -> float:
    """
    Sous-catégorie "Logistique de froid négatif (référence -18°C)". Pas de CVC séparé
    ("Absence de valeur CVC - toute la consommation est considérée sur la valeur USE").
    Source : PDF, p.~495.

    USE modulé = [[(USE_zone × Hauteur) + (1,5 × Nb_ouverture)/Surface] × [1 − 0,05 × (Tcons + 18)]]
      × (Nb_h_ouvrées/Nb_h_ouvrées_étalon)
    """
    return (
        ((use_zone * Hauteur) + (etalons["ratio_kwh_par_ouverture"] * Nb_ouverture) / Surface)
        * (1 - etalons["coefficient_temperature_par_degre"] * (Tcons - etalons["Tcons_etalon"]))
        * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
    )


def use_modulé_temp_dirigee_1_8(etalons: dict, use_zone: float, Hauteur: float, Nb_ouverture: float, Surface: float, Tcons: float, Nb_h_ouvrees: float) -> float:
    """
    Sous-catégorie "Logistique ou messagerie température dirigée froid positif +1 à +8°C
    (référence +3°C)". Pas de CVC séparé. Source : PDF, p.~529.
    Même forme que le froid négatif, coefficients propres à cette sous-catégorie.
    """
    return (
        ((use_zone * Hauteur) + (etalons["ratio_kwh_par_ouverture"] * Nb_ouverture) / Surface)
        * (1 - etalons["coefficient_temperature_par_degre"] * (Tcons - etalons["Tcons_etalon"]))
        * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
    )


def use_modulé_temp_dirigee_12_17(etalons: dict, use_zone: float, Hauteur: float, Nb_ouverture: float, Surface: float, Tcons: float, Nb_h_ouvrees: float) -> float:
    """
    Sous-catégorie "Logistique ou messagerie température dirigée +12 à +17°C
    (référence +15°C)". Pas de CVC séparé. Source : PDF, p.~562.
    Même forme que les deux précédentes, coefficients propres à cette sous-catégorie.
    """
    return (
        ((use_zone * Hauteur) + (etalons["ratio_kwh_par_ouverture"] * Nb_ouverture) / Surface)
        * (1 - etalons["coefficient_temperature_par_degre"] * (Tcons - etalons["Tcons_etalon"]))
        * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
    )


def use_modulé_entrepot_temp_ambiante(
    etalons: dict, cvc: float, Surf_cond: float, Npalettes: float, Nb_h_ouvrees: float,
    HSP: float, Tcons: float, Conso_process: float, Surface: float,
) -> float:
    """
    Sous-catégorie "Entrepôt à température ambiante (évolution libre entre +12°C
    et +26°C) ou avec maintien hors-gel pour les besoins du produit".
    Source : PDF, p.~145 (NAF section H 52.10B). Branche conditionnelle Conso_process.
    """
    if Conso_process == 0:
        return (
            etalons["USE_etalon"] * (1 - Surf_cond / 100) * (
                etalons["Part_USE_variable"] * Npalettes / etalons["Npalettes_etalon"]
                + (1 - etalons["Part_USE_variable"]) * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
            )
            + Surf_cond * etalons["Variation_Surf_cond"] * Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"]
            + cvc * (
                0.1 * (Nb_h_ouvrees - etalons["Nb_h_ouvrees_etalon"]) / etalons["Nb_h_ouvrees_etalon"]
                + (HSP - etalons["HSP_etalon"]) * etalons["Variation_HSP"] / 100
            )
            + (Tcons - etalons["Tcons_etalon"]) * etalons["Variation_Tcons"]
        )
    return (
        Conso_process / Surface
        + etalons["USE_etalon"] * (1 - etalons["Part_USE_variable"]) * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
        + cvc * (
            0.1 * (Nb_h_ouvrees - etalons["Nb_h_ouvrees_etalon"]) / etalons["Nb_h_ouvrees_etalon"]
            + (HSP - etalons["HSP_etalon"]) * etalons["Variation_HSP"] / 100
        )
        + (Tcons - etalons["Tcons_etalon"]) * etalons["Variation_Tcons"]
    )


def use_modulé_entrepot_sans_maintien(
    etalons: dict, Surf_cond: float, Npalettes: float, Nb_h_ouvrees: float, Conso_process: float, Surface: float,
) -> float:
    """
    Sous-catégorie "Entrepôt ou messagerie sans besoin de maintien en température
    du produit". Source : PDF, p.~146. Structure différente de la précédente
    (pas de terme HSP/Tcons). Branche conditionnelle Conso_process.
    """
    if Conso_process == 0:
        return (
            etalons["USE_etalon"] * (1 - Surf_cond / 100) * (
                etalons["Part_USE_variable"] * Npalettes / etalons["Npalettes_etalon"]
                + (1 - etalons["Part_USE_variable"]) * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
            )
            + Surf_cond * etalons["Variation_Surf_cond"] * Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"]
        )
    return (
        Conso_process / Surface
        + etalons["USE_etalon"] * (1 - etalons["Part_USE_variable"]) * (Nb_h_ouvrees / etalons["Nb_h_ouvrees_etalon"])
    )
