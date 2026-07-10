"""
Seam public du module Cabs : calculer_cabs(site, echeance) -> dict.

Voir CONTEXT.md pour le vocabulaire du domaine.
"""

from cabs import etalons
from cabs.formules import bureaux as formules_bureaux

SOUS_CATEGORIES_IMPLEMENTEES = {"bureaux_standards"}


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
    cabs_pondere = sum(t["cabs_unitaire_kwh_m2_an"] * (t["s_conso_m2"] / s_totale) for t in trace)
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
    if sous_cat not in SOUS_CATEGORIES_IMPLEMENTEES:
        return {"bloquant": f"sous-catégorie '{sous_cat}' non implémentée en V1"}

    cvc = etalons.cvc_lookup(sous_cat, activite["zone_climatique"], activite["tranche_altitude"], echeance)
    if cvc is None:
        return {
            "bloquant": (
                f"CVC indisponible pour {sous_cat}/{activite['zone_climatique']}/"
                f"{activite['tranche_altitude']}/{echeance}"
            )
        }

    etalons_activite = etalons.etalons_bureaux()[sous_cat]
    use = formules_bureaux.use_modulé(
        etalons_activite,
        activite["params"]["T_occ"],
        activite["params"]["Surf_poste"],
        activite["params"]["Nb_h_ouvrees"],
    )
    cabs_unitaire = cvc + use

    return {
        "activite": activite["label"],
        "sous_categorie": sous_cat,
        "s_conso_m2": activite["s_conso"],
        "cvc_kwh_m2_an": cvc,
        "use_modulé_kwh_m2_an": round(use, 2),
        "cabs_unitaire_kwh_m2_an": round(cabs_unitaire, 2),
    }
