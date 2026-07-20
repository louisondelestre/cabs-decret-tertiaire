from consommations.agregation import verifier_et_agreger, LigneConsommation

lignes = [
    LigneConsommation(
        zone="Siège Paris",       # site/bâtiment — jamais deviné, à renseigner
        poste="eclairage",         # type d'usage — jamais deviné
        fluide="electricite",      # electricite, gaz, fioul, bois, reseau_chaleur_froid
        mois="2025-01",            # format YYYY-MM
        quantite=1000,
        unite="kWh",
        montant_eur=150,
    ),
    LigneConsommation("Siège Paris", "chauffage", "gaz", "2025-01", 2000, "kWh", 180),
]

resultat = verifier_et_agreger(lignes, mois_attendus=["2025-01"])

if resultat["statut"] == "BLOQUÉ":
    print("Bloqué :", resultat["raisons"])
else:
    print("Agrégat annuel kWh par site :", resultat["agregat_annuel_kwh_par_site"])
    print("Doublons détectés :", resultat["doublons_detectes"])
    print("Mois manquants :", resultat["mois_manquants"])
    print("Couverture temporelle (%) :", resultat["couverture_temporelle_%"])
    print("Bascules de fluide détectées :", resultat["bascules_fluide_detectees"])