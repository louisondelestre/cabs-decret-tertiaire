"""
Seam public du module Cabs : calculer_cabs(site, echeance) -> dict.

Voir CONTEXT.md pour le vocabulaire du domaine.
"""

from cabs import etalons
from cabs.formules import bureaux as formules_bureaux
from cabs.formules import logistique as formules_logistique

SOUS_CATEGORIES_IMPLEMENTEES = {
    "bureaux_standards",
    "logistique_administration_bureaux",
    "logistique_froid_negatif",
    "logistique_temp_dirigee_1_8",
    "logistique_temp_dirigee_12_17",
    "entrepot_temp_ambiante",
    "entrepot_sans_maintien",
}

_SANS_CVC_SEPARE = {"logistique_froid_negatif", "logistique_temp_dirigee_1_8", "logistique_temp_dirigee_12_17"}

_FORMULES_SANS_CVC = {
    "logistique_froid_negatif": formules_logistique.use_modulé_froid_negatif,
    "logistique_temp_dirigee_1_8": formules_logistique.use_modulé_temp_dirigee_1_8,
    "logistique_temp_dirigee_12_17": formules_logistique.use_modulé_temp_dirigee_12_17,
}

_FORMULES_AVEC_CVC = {
    "bureaux_standards": lambda e, cvc, p: formules_bureaux.use_modulé(e, p["T_occ"], p["Surf_poste"], p["Nb_h_ouvrees"]),
    "logistique_administration_bureaux": lambda e, cvc, p: formules_logistique.use_modulé_administration_bureaux(
        e, cvc, p["T_occ"], p["Surf_poste"], p["Nb_h_ouvrees"]
    ),
    "entrepot_temp_ambiante": lambda e, cvc, p: formules_logistique.use_modulé_entrepot_temp_ambiante(
        e, cvc, p["Surf_cond"], p["Npalettes"], p["Nb_h_ouvrees"], p["HSP"], p["Tcons"], p["Conso_process"], p["Surface"]
    ),
    "entrepot_sans_maintien": lambda e, cvc, p: formules_logistique.use_modulé_entrepot_sans_maintien(
        e, p["Surf_cond"], p["Npalettes"], p["Nb_h_ouvrees"], p["Conso_process"], p["Surface"]
    ),
}


def calculer_cabs(site: dict, echeance: str) -> dict:
    activites = site["activites"]

    trace = []
    for activite in activites:
        resultat_activite = _calculer_activite(activite, echeance)
        if "bloquant" in resultat_activite:
            return {
                "statut": "BLOQUÉ",
                "raisons": [f"{activite['label']}: {resultat_activite['bloquant']}"],
            }
        trace.append(resultat_activite)

    s_totale = sum(a["s_conso"] for a in activites)
    for t in trace:
        poids = t["s_conso_m2"] / s_totale
        t["poids_%"] = round(poids * 100, 2)
        t["contribution_kwh_m2_an"] = round(t["cabs_unitaire_kwh_m2_an"] * poids, 2)

    cabs_pondere = sum(t["contribution_kwh_m2_an"] for t in trace)
    seuil_absolu_kwh = cabs_pondere * s_totale
    ecart_kwh = site["conso_reelle_kwh"] - seuil_absolu_kwh

    return {
        "statut": "CALCULÉ",
        "trace_par_activite": trace,
        "cabs_pondere_kwh_m2_an": round(cabs_pondere, 2),
        "seuil_absolu_kwh_an": round(seuil_absolu_kwh, 0),
        "conso_reelle_kwh_an": site["conso_reelle_kwh"],
        "ecart_kwh": round(ecart_kwh, 0),
        "statut_prudent": (
            "ÉCART — indicatif, non opposable, hors validation par un auditeur qualifié — "
            + ("AU-DESSUS du seuil" if ecart_kwh > 0 else "SOUS le seuil")
        ),
        "hypotheses": {"echeance": echeance},
    }


def _calculer_activite(activite: dict, echeance: str) -> dict:
    sous_cat = activite["sous_categorie"]
    p = activite["params"]

    if sous_cat not in SOUS_CATEGORIES_IMPLEMENTEES:
        return {"bloquant": f"sous-catégorie '{sous_cat}' non implémentée en V1"}

    if sous_cat in _SANS_CVC_SEPARE:
        use_zone = etalons.use_zone_lookup(sous_cat, activite["zone_climatique"], activite["tranche_altitude"], echeance)
        if use_zone is None:
            return {
                "bloquant": (
                    f"USE indisponible pour {sous_cat}/{activite['zone_climatique']}/"
                    f"{activite['tranche_altitude']}/{echeance}"
                )
            }
        etalons_activite = etalons.etalons_logistique_use_zone()[sous_cat]
        use = _FORMULES_SANS_CVC[sous_cat](
            etalons_activite, use_zone, p["Hauteur"], p["Nb_ouverture"], p["Surface"], p["Tcons"], p["Nb_h_ouvrees"]
        )
        cvc = 0.0
    else:
        cvc = etalons.cvc_lookup(sous_cat, activite["zone_climatique"], activite["tranche_altitude"], echeance)
        if cvc is None:
            return {
                "bloquant": (
                    f"CVC indisponible pour {sous_cat}/{activite['zone_climatique']}/"
                    f"{activite['tranche_altitude']}/{echeance}"
                )
            }
        etalons_activite = (
            etalons.etalons_bureaux() if sous_cat == "bureaux_standards" else etalons.etalons_logistique()
        )[sous_cat]
        use = _FORMULES_AVEC_CVC[sous_cat](etalons_activite, cvc, p)

    cabs_unitaire = cvc + use

    return {
        "activite": activite["label"],
        "sous_categorie": sous_cat,
        "s_conso_m2": activite["s_conso"],
        "cvc_kwh_m2_an": cvc,
        "use_modulé_kwh_m2_an": round(use, 2),
        "cabs_unitaire_kwh_m2_an": round(cabs_unitaire, 2),
    }
