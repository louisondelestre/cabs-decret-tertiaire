"""
Chargement des tables de données étalon (valeurs numériques uniquement).

Ces tables sont des données externes versionnées, pas de la logique de
calcul — les formules de modulation vivent dans cabs/formules/.
"""

import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _charger_json(nom_fichier: str) -> dict:
    with open(_DATA_DIR / nom_fichier, encoding="utf-8") as f:
        return json.load(f)


def etalons_bureaux() -> dict:
    """Retourne le dict sous_categorie -> valeurs étalon pour les bureaux."""
    return _charger_json("etalons_bureaux.json")["sous_categories"]


def etalons_logistique() -> dict:
    """Sous-catégories logistique dont l'étalon USE est une constante (pas dépendante de la zone)."""
    return _charger_json("etalons_logistique.json")["sous_categories"]


def etalons_logistique_use_zone() -> dict:
    """Sous-catégories logistique dont l'étalon USE dépend de la zone climatique (pas de CVC séparé)."""
    return _charger_json("etalons_logistique.json")["sous_categories_use_zone"]


def cvc_bureaux() -> list[dict]:
    """Retourne la liste des entrées CVC bureaux (sous_categorie, zone, altitude, échéance, valeur)."""
    return _charger_json("cvc_bureaux.json")["entries"]


def cvc_logistique() -> list[dict]:
    return _charger_json("cvc_logistique.json")["entries"]


def use_zone_logistique() -> list[dict]:
    return _charger_json("use_zone_logistique.json")["entries"]


def cvc_lookup(sous_categorie: str, zone_climatique: str, tranche_altitude: str, echeance: str) -> float | None:
    """Cherche la valeur CVC pour la combinaison exacte demandée, ou None si absente de la table."""
    for entree in cvc_bureaux() + cvc_logistique():
        if (
            entree["sous_categorie"] == sous_categorie
            and entree["zone_climatique"] == zone_climatique
            and entree["tranche_altitude"] == tranche_altitude
            and entree["echeance"] == echeance
        ):
            return entree["cvc_kwh_m2_an"]
    return None


def use_zone_lookup(sous_categorie: str, zone_climatique: str, tranche_altitude: str, echeance: str) -> float | None:
    """Cherche la valeur USE-par-zone (sous-catégories logistique sans CVC séparé), ou None si absente."""
    for entree in use_zone_logistique():
        if (
            entree["sous_categorie"] == sous_categorie
            and entree["zone_climatique"] == zone_climatique
            and entree["tranche_altitude"] == tranche_altitude
            and entree["echeance"] == echeance
        ):
            return entree["use_zone_kwh_m2_an"]
    return None
