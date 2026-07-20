"""
Interface locale (Streamlit) pour le calcul du Cabs.

Lancer avec : streamlit run app_cabs.py
Prérequis : depuis le dossier cabs-decret-tertiaire, avec le package
consommations installé (pip install -e ../consommations-decret-tertiaire).
"""

import streamlit as st
import pandas as pd

from cabs.calcul import calculer_cabs
from consommations.agregation import LigneConsommation

st.set_page_config(page_title="Calcul Cabs — décret tertiaire", layout="wide")

st.title("Calcul du Cabs — décret tertiaire")
st.caption(
    "Cet outil prépare des éléments de calcul. Il ne certifie et ne signe jamais une "
    "conformité réglementaire — cette validation reste du ressort d'un professionnel qualifié."
)

SOUS_CATEGORIES = {
    "Bureaux": "bureaux_standards",
    "Logistique - Administration et bureaux": "logistique_administration_bureaux",
    "Logistique - froid négatif": "logistique_froid_negatif",
    "Logistique - température dirigée +1 à +8°C": "logistique_temp_dirigee_1_8",
    "Logistique - température dirigée +12 à +17°C": "logistique_temp_dirigee_12_17",
    "Entrepôt - température ambiante": "entrepot_temp_ambiante",
    "Entrepôt - sans maintien en température": "entrepot_sans_maintien",
}

if "nb_activites" not in st.session_state:
    st.session_state.nb_activites = 1

st.header("1. Activités du site")

col_add, col_remove = st.columns([1, 1])
if col_add.button("+ Ajouter une activité"):
    st.session_state.nb_activites += 1
if col_remove.button("- Retirer la dernière activité") and st.session_state.nb_activites > 1:
    st.session_state.nb_activites -= 1

activites = []
for i in range(st.session_state.nb_activites):
    with st.expander(f"Activité {i + 1}", expanded=True):
        label = st.text_input("Nom de l'activité", value=f"Activité {i + 1}", key=f"label_{i}")
        sous_cat_label = st.selectbox("Sous-catégorie", list(SOUS_CATEGORIES.keys()), key=f"souscat_{i}")
        sous_categorie = SOUS_CATEGORIES[sous_cat_label]
        s_conso = st.number_input(
            "Surface de consommations énergétiques (SConso, m²) — pas la surface plancher",
            min_value=1.0, value=1000.0, key=f"sconso_{i}",
        )

        col_zone, col_dept = st.columns(2)
        mode_zone = col_zone.radio("Zone climatique", ["Saisie manuelle", "Déduire du département"], key=f"mode_zone_{i}")
        activite = {"label": label, "sous_categorie": sous_categorie, "s_conso": s_conso}
        if mode_zone == "Saisie manuelle":
            activite["zone_climatique"] = col_dept.selectbox(
                "Zone (H1a...H3)",
                ["H1a", "H1b", "H1c", "H2a", "H2b", "H2c", "H2d", "H3"],
                key=f"zone_{i}",
            )
        else:
            activite["departement"] = col_dept.text_input("Code département (ex. 44)", key=f"dept_{i}")

        activite["tranche_altitude"] = st.selectbox(
            "Tranche d'altitude", ["<400", "400-800", "800-1200", "1200-1600", ">1600"], key=f"alt_{i}"
        )

        st.markdown("**Paramètres de modulation**")
        params = {}
        if sous_categorie in ("bureaux_standards", "logistique_administration_bureaux"):
            c1, c2, c3 = st.columns(3)
            params["T_occ"] = c1.number_input("Taux d'occupation (%)", value=50.0, key=f"tocc_{i}")
            params["Surf_poste"] = c2.number_input("Surface par poste (m²)", value=18.0, key=f"surfposte_{i}")
            params["Nb_h_ouvrees"] = c3.number_input("Heures ouvrées / an", value=3120.0, key=f"nbh_{i}")
        elif sous_categorie in ("logistique_froid_negatif", "logistique_temp_dirigee_1_8", "logistique_temp_dirigee_12_17"):
            c1, c2, c3 = st.columns(3)
            params["Hauteur"] = c1.number_input("Hauteur (facteur, 1 = étalon)", value=1.0, key=f"hauteur_{i}")
            params["Nb_ouverture"] = c2.number_input("Nombre d'ouvertures", value=0.0, key=f"ouv_{i}")
            params["Tcons"] = c3.number_input("Température de consigne (°C)", value=-18.0, key=f"tcons_{i}")
            params["Nb_h_ouvrees"] = st.number_input("Heures ouvrées / an", value=8760.0, key=f"nbh_{i}")
            params["Surface"] = s_conso
        else:  # entrepôts
            c1, c2, c3 = st.columns(3)
            params["Surf_cond"] = c1.number_input("Surface conditionnée (%)", value=0.0, key=f"surfcond_{i}")
            params["Npalettes"] = c2.number_input("Nombre de palettes / m² / an", value=150.0, key=f"npal_{i}")
            params["Nb_h_ouvrees"] = c3.number_input("Heures ouvrées / an", value=3744.0, key=f"nbh_{i}")
            if sous_categorie == "entrepot_temp_ambiante":
                c4, c5 = st.columns(2)
                params["HSP"] = c4.number_input("Hauteur sous plafond (m)", value=9.0, key=f"hsp_{i}")
                params["Tcons"] = c5.number_input("Température de consigne (°C)", value=12.0, key=f"tcons_{i}")
            params["Conso_process"] = st.number_input("Consommation process (kWh, 0 si aucune)", value=0.0, key=f"process_{i}")
            params["Surface"] = s_conso

        activite["params"] = params
        activites.append(activite)

st.header("2. Consommation réelle (import CSV)")
st.caption("Colonnes attendues : zone, poste, fluide, mois (YYYY-MM), quantite, unite, montant_eur")
fichier_csv = st.file_uploader("Fichier CSV des consommations", type=["csv"])

st.header("3. Échéance")
echeance = st.selectbox("Échéance réglementaire", ["2030", "2040", "2050"])

if st.button("Calculer le Cabs", type="primary"):
    if fichier_csv is None:
        st.warning("Merci d'importer un fichier CSV de consommations avant de calculer.")
    else:
        df = pd.read_csv(fichier_csv)
        lignes = [
            LigneConsommation(
                zone=row["zone"], poste=row["poste"], fluide=row["fluide"], mois=str(row["mois"]),
                quantite=row["quantite"], unite=row["unite"], montant_eur=row["montant_eur"],
            )
            for _, row in df.iterrows()
        ]

        site = {"activites": activites, "lignes_consommation": lignes}
        resultat = calculer_cabs(site, echeance=echeance)

        if resultat["statut"] == "BLOQUÉ":
            st.error("Calcul bloqué :")
            for raison in resultat["raisons"]:
                st.write(f"- {raison}")
        else:
            st.success(resultat["statut_prudent"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Seuil Cabs pondéré", f"{resultat['cabs_pondere_kwh_m2_an']} kWh/m²/an")
            c2.metric("Seuil absolu du site", f"{resultat['seuil_absolu_kwh_an']:,.0f} kWh/an")
            c3.metric("Consommation réelle", f"{resultat['conso_reelle_kwh_an']:,.0f} kWh/an")
            st.metric("Écart", f"{resultat['ecart_kwh']:,.0f} kWh")

            st.subheader("Détail par activité")
            st.dataframe(pd.DataFrame(resultat["trace_par_activite"]))

            with st.expander("Hypothèses de calcul"):
                st.json(resultat.get("hypotheses", {}))
