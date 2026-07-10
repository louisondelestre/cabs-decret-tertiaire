"""
Formule de modulation USE — catégorie Bureaux (sous-catégories Standards
cloisonnés, Open Space, Flex Office).

Source : Arrêté du 24 novembre 2020 modifiant l'arrêté du 10 avril 2020,
Annexe II (Légifrance, article JORFARTI000042994835).
"""


def use_modulé(etalons: dict, T_occ: float, Surf_poste: float, Nb_h_ouvrees: float) -> float:
    """
    USE modulé (kWh/m²/an) = USE_étalon × [0,05 + 0,95 × (T_occ / T_occ_étalon)
      × (Surf_poste_étalon / Surf_poste) × (Nb_h_ouvrées / DT_étalon)
      + 0,28 × (Nb_h_ouvrées − DT_étalon) / DT_étalon]

    `etalons` doit contenir : USE_etalon, T_occ_etalon, Surf_poste_etalon,
    Nb_h_ouvrees_etalon (= DT_étalon).
    """
    dt_etalon = etalons["Nb_h_ouvrees_etalon"]
    return etalons["USE_etalon"] * (
        0.05
        + 0.95
        * (T_occ / etalons["T_occ_etalon"])
        * (etalons["Surf_poste_etalon"] / Surf_poste)
        * (Nb_h_ouvrees / dt_etalon)
        + 0.28 * (Nb_h_ouvrees - dt_etalon) / dt_etalon
    )
