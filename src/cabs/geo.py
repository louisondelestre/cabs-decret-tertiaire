"""
Déduction de la macro-zone climatique (H1/H2/H3) à partir d'un département.

Source : Ministère de la Transition écologique, "La répartition des
départements par zone climatique" (ecologie.gouv.fr), fondée sur l'annexe I
de l'arrêté RT2012 du 26/10/2010 modifié.

Limite importante : cette source officielle ne couvre que la macro-zone
(H1/H2/H3), jamais la sous-zone (H1a/H1b/H1c/H2a/H2b/H2c/H2d) dont les
tables CVC/USE de ce module ont besoin. La déduction automatique s'arrête
donc à la macro-zone — la sous-zone doit toujours être confirmée par
saisie manuelle (voir cabs.calcul, mode ENO-16).
"""

import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _table_departements() -> dict:
    with open(_DATA_DIR / "departements_zone_climatique.json", encoding="utf-8") as f:
        return json.load(f)["departements"]


def deduire_macro_zone(departement: str) -> str | None:
    """Retourne 'H1', 'H2' ou 'H3' pour un code département connu, sinon None."""
    return _table_departements().get(departement)
