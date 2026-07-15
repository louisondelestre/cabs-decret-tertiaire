"""
Seam public du module Cabs : calculer_cabs(site, echeance) -> dict.

Voir CONTEXT.md pour le vocabulaire du domaine.
"""

from cabs import etalons
from cabs import geo
from cabs.formules import bureaux as formules_bureaux
from cabs.formules import logistique as formules_logistique
from consommations.agregation import verifier_et_agreger

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


def _resoudre_conso_reelle(site: dict):
    """
    Résout la consommation réelle annuelle du site (kWh énergie finale).
    Priorité à l'agent "analyse des consommations" si des lignes brutes sont
    fournies (site['lignes_consommation']) ; fallback rétro-compatible sur
    'conso_reelle_kwh' pour les sites qui la passent déjà calculée.
    Si l'agent consommations bloque, le calcul Cabs bloque aussi — jamais
    de valeur par défaut.
    Note : on suppose que toutes les lignes fournies appartiennent à ce site
    (un seul "zone" au sens de l'agent consommations = ce site) ; l'agrégat
    est sommé sur toutes les zones retournées par prudence si plusieurs
    apparaissent.
    """
    if "lignes_consommation" in site:
        lignes = site["lignes_consommation"]
        mois_attendus = sorted({ligne.mois for ligne in lignes})
        resultat = verifier_et_agreger(lignes, mois_attendus)
        if resultat["statut"] == "BLOQUÉ":
            return None, {
                "statut": "BLOQUÉ",
                "raisons": [f"agent consommations: {r}" for r in resultat["raisons"]],
            }
        return sum(resultat["agregat_annuel_kwh_par_site"].values()), None
    return site["conso_reelle_kwh"], None


def calculer_cabs(site: dict, echeance: str) -> dict:
    activites = site["activites"]

    conso_reelle_kwh, blocage_conso = _resoudre_conso_reelle(site)
    if blocage_conso is not None:
        return blocage_conso

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
    ecart_kwh = conso_reelle_kwh - seuil_absolu_kwh

    return {
        "statut": "CALCULÉ",
        "trace_par_activite": trace,
        "cabs_pondere_kwh_m2_an": round(cabs_pondere, 2),
        "seuil_absolu_kwh_an": round(seuil_absolu_kwh, 0),
        "conso_reelle_kwh_an": conso_reelle_kwh,
        "ecart_kwh": round(ecart_kwh, 0),
        "statut_prudent": (
            "ÉCART — indicatif, non opposable, hors validation par un auditeur qualifié — "
            + ("AU-DESSUS du seuil" if ecart_kwh > 0 else "SOUS le seuil")
        ),
        "hypotheses": {"echeance": echeance},
    }


def _resoudre_zone(activite: dict) -> dict:
    """
    Résout la zone climatique d'une activité. La saisie manuelle explicite
    (zone_climatique, ENO-16) est toujours prioritaire. À défaut, si un
    département est fourni, la macro-zone (H1/H2/H3) est déduite depuis la
    source officielle — mais comme cette source ne couvre pas la sous-zone
    exacte (H1a/H1b/H1c/H2a/H2b/H2c/H2d) requise par les tables CVC/USE, le
    calcul bloque toujours dans ce cas et demande une confirmation manuelle
    de la sous-zone, en indiquant la macro-zone déduite pour aider l'utilisateur.
    """
    if "zone_climatique" in activite:
        return {"zone_climatique": activite["zone_climatique"]}

    departement = activite.get("departement")
    if departement is None:
        return {"bloquant": "ni zone_climatique ni département fournis — saisie manuelle requise"}

    macro_zone = geo.deduire_macro_zone(departement)
    if macro_zone is None:
        return {"bloquant": f"département '{departement}' non résolu dans la table officielle — saisie manuelle de la zone requise"}

    if macro_zone == "H3":
        # H3 n'est pas subdivisée (zone homogène) — pas d'ambiguïté de sous-zone à lever.
        return {"zone_climatique": "H3"}

    return {
        "bloquant": (
            f"macro-zone déduite du département {departement} : {macro_zone} — mais la source officielle "
            f"ne précise pas la sous-zone exacte ({macro_zone}a/{macro_zone}b/...) requise pour le calcul ; "
            "merci de confirmer la sous-zone climatique en saisie manuelle (zone_climatique)"
        )
    }


def _calculer_activite(activite: dict, echeance: str) -> dict:
    sous_cat = activite["sous_categorie"]
    p = activite["params"]

    if sous_cat not in SOUS_CATEGORIES_IMPLEMENTEES:
        return {"bloquant": f"sous-catégorie '{sous_cat}' non implémentée en V1"}

    resolution = _resoudre_zone(activite)
    if "bloquant" in resolution:
        return resolution
    zone_climatique = resolution["zone_climatique"]
    activite = {**activite, "zone_climatique": zone_climatique}

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
