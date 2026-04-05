# LEILA Transport Dashboard

Dashboard analytique Dash/Plotly pour le test technique **Data/BI Analyst — MÉTHODES CODE** (éditeur du SaaS LEILA).

**Période analysée :** Janvier – Mars 2026 (11 semaines) · **734 missions validées**

---

## Prérequis

- Python 3.10+
- MariaDB local avec la base `snfAnonymise` importée depuis `Leila_Mise-en-conditions_dump.sql`

---

## Installation

```bash
# 1. Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Installer les dépendances
pip install -r requirements.txt
```

---

## Mise en place de la base de données

```bash
# Importer le dump dans MariaDB
mysql -u root snfAnonymise < Leila_Mise-en-conditions_dump.sql

# Créer la vue v_missions (source unique du dashboard)
mysql -u root snfAnonymise < create_view_v_missions.sql
```

La vue `v_missions` applique les filtres qualité suivants :

- Missions de type `Transport marchandises`, `Location à la journée`, `Location au voyage`
- Distance comprise entre 1 et 300 km (exclusion des erreurs de saisie compteur)
- Exclusion des missions avec GPS retrait = GPS livraison et distance > 100 km

---

## Lancement

```bash
python leila_dash/leila_dashboard.py
```

Accès : [http://127.0.0.1:8100](http://127.0.0.1:8100)

> Adapter les paramètres de connexion dans `leila_dash/leila_dashboard.py` si nécessaire (lignes `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`).

---

## Structure du projet

```
Leila_Test/
├── leila_dash/
│   └── leila_dashboard.py      # Application Dash principale
├── create_view_v_missions.sql  # Script de création de la vue SQL
├── requirements.txt
└── README.md
```

---

## Sections du dashboard (7 axes)

| # | Section | Contenu |
|---|---|---|
| 1 | **Vue d'ensemble** | KPIs globaux, activité hebdomadaire, répartition par type de mission |
| 2 | **Performance trajets** | Distribution des distances et durées, temps d'attente chargement/déchargement |
| 3 | **Chauffeurs & Engins** | Missions par chauffeur, taux d'utilisation engins, heatmap semaine × engin |
| 4 | **Expéditeurs / Destinataires** | Top acteurs, comparaison des temps d'attente |
| 5 | **Marchandises** | Top libellés, évolution mensuelle des volumes |
| 6 | **Impact CO₂** | Estimation par engin et chauffeur (facteurs ADEME) |
| 7 | **Géographie** | Carte GPS trajets, densité des zones retrait/livraison |

---

## Données clés

| Indicateur | Valeur |
|---|---|
| Missions validées | 734 |
| Engins actifs | 6 |
| Chauffeurs | 7 |
| Distance médiane | 27 km |
| Distance moyenne | 42,1 km |
| Kilométrage total | 30 920 km |

**Flotte :** TR-789-XY · HB-316-CS · PO-456-AB · VH-234-CD · GR-256-CQ · CR-426-DD  
**Types :** Porteur 8x4 / Tracteur 6x4 / Tracteur 4x2 — **Marques :** MAN · DAF · SCANIA

---

## Estimation CO₂ (facteurs ADEME)

| Type véhicule | Facteur |
|---|---|
| Porteur 8x4 | 0,900 kg CO₂/km |
| Tracteur 6x4 | 0,750 kg CO₂/km |
| Tracteur 4x2 | 0,650 kg CO₂/km |

Aucune donnée carburant disponible dans le dump — estimation par type de véhicule uniquement.

---

## Anomalies connues

- **OVAL JOHAN = AUVAL JOHAN** : doublon de saisie, fusionné dans le code
- **Table `Location` vide** : le formulaire TRP2 (location à la journée) n'est pas exploitable
- **20% de nulls sur les poids** : missions sans pesée — traités avec `COALESCE(..., 0)`
- **1–2% de nulls GPS** : filtrés avant affichage cartographique
