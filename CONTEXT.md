# Contexte — cabs-decret-tertiaire

## Domaine

Calcul du **Cabs** (seuil de consommation en valeur absolue du décret tertiaire / dispositif Éco Énergie Tertiaire), pour un **site** composé d'une ou plusieurs **activités**.

## Vocabulaire

- **Site** : bâtiment ou entité fonctionnelle tertiaire assujetti(e), composé d'une ou plusieurs activités.
- **Activité** : une sous-catégorie d'usage au sein d'un site (ex. "Bureaux Open Space"), avec sa propre **SConso**.
- **SConso** (surface de consommations énergétiques) : surface qui sert au calcul du Cabs — à ne jamais confondre avec la **surface plancher** (sert uniquement à l'assujettissement, hors périmètre de ce module).
- **Sous-catégorie** : classification précise d'une activité (ex. "bureaux_open_space", "entrepot_temp_ambiante"), chacune ayant sa propre formule de modulation USE et ses propres valeurs étalon.
- **Étalon** : valeur de référence réglementaire (ex. `USE_etalon`, `Nb_h_ouvrees_etalon`) publiée par arrêté, contre laquelle les valeurs réelles du site sont comparées dans la formule de modulation.
- **CVC** : composante fixe du Cabs liée au chauffage/ventilation/climatisation, lue directement dans une table croisant sous-catégorie × zone climatique × tranche d'altitude (pas de formule).
- **USE modulé** : composante variable du Cabs (usages spécifiques à l'activité), calculée par une formule propre à chaque sous-catégorie à partir des étalons et des données réelles du site.
- **Cabs unitaire** : CVC + USE modulé pour une activité donnée (kWh/m²/an).
- **Cabs pondéré** : moyenne des Cabs unitaires des activités d'un site, pondérée au prorata surfacique (SConso) — jamais un seuil plancher ni un traitement spécial pour les petites activités.
- **Échéance** : horizon réglementaire (2030 / 2040 / 2050), paramètre du calcul.
- **Blocage** : statut retourné dès qu'une activité du site relève d'une sous-catégorie, d'une combinaison zone/altitude, ou d'une échéance non couverte par une formule/donnée sourcée. Bloque **tout le site**, jamais un résultat partiel.
- **Statut prudent** : formulation du résultat qui ne dit jamais "conforme"/"non conforme" au sens réglementaire — ce module prépare des éléments, ne certifie rien (voir contexte projet plus large : dossier de préparation, jamais un audit).

## Règles non négociables

- Les formules de modulation par sous-catégorie sont du **code sourcé** (docstring citant arrêté/annexe/page), jamais des données générées ou reconstruites par analogie.
- Les valeurs étalon (nombres) sont des **données externes versionnées**, jamais codées en dur dans la logique de calcul.
- Toute activité non couverte bloque le site entier — pas de résultat approximatif.
