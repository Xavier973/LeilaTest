# LEILA Transport Dashboard

Dashboard analytique Dash/Plotly pour le test technique **Data/BI Analyst — MÉTHODES CODE** (éditeur du SaaS LEILA).

**Période analysée :** Janvier – Mars 2026 (11 semaines)

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
python leila_dash/app.py
```

Accès : [http://127.0.0.1:8100](http://127.0.0.1:8100)

> Les paramètres de connexion sont pilotés par variables d'environnement (voir `.env.example`).

---

## Mise en ligne (leilatest.data-service.fr)

Configuration recommandée : **Ubuntu + Nginx + Gunicorn + systemd + Let's Encrypt**.

### Docker Compose

Cette option exécute l'application dans un conteneur, tout en gardant **Nginx + Certbot sur l'hôte**
pour publier `leilatest.data-service.fr`.

#### 1) Préparer les variables d'environnement

```bash
cd /home/ubuntu/LeilaTest
sudo mkdir -p /etc/leila
sudo cp .env.example /etc/leila/leilatest.env
sudo nano /etc/leila/leilatest.env
```

Valeurs minimales :

```dotenv
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=snfAnonymise
LEILA_DEBUG=false
LEILA_HOST=127.0.0.1
LEILA_PORT=8100
GUNICORN_WORKERS=3
```

#### 3) Lancer l'application avec Compose

```bash
cd /home/ubuntu/LeilaTest
docker compose up -d --build
docker compose ps
```

#### 4) Configurer Nginx pour le domaine

```bash
sudo cp deploy/nginx.leilatest.data-service.fr.conf /etc/nginx/sites-available/leilatest.data-service.fr
sudo ln -sf /etc/nginx/sites-available/leilatest.data-service.fr /etc/nginx/sites-enabled/leilatest.data-service.fr
sudo nginx -t
sudo systemctl reload nginx
```

#### 5) Activer HTTPS

```bash
sudo certbot --nginx -d leilatest.data-service.fr
```

#### 6) Vérifier

```bash
docker compose logs --tail=100 leila-dashboard
curl -I http://127.0.0.1:8100
curl -I https://leilatest.data-service.fr
```

---

## Architecture des données

### Pipeline de chargement

Le dashboard repose sur **4 requêtes SQL** exécutées au démarrage ([data.py](leila_dash/data.py)) :

| # | Fonction | Tables sources | Utilisée par |
|---|----------|---------------|--------------|
| 1 | `SELECT * FROM v_missions` | Vue unifiée (7 tables) | **Toutes les pages** |
| 2 | `load_carburant()` — agrégation Gasoil | MouvementStock, Formulaire, Entite, Engin | Impact économique |
| 3 | `load_formulaire_missions()` — COUNT par type | Formulaire (brut) | Vue d'ensemble (camembert) |
| 4 | `load_km_anomalies()` — records non filtrés | Formulaire, Entite, Engin, Retrait, Livraison, Personne | Vue d'ensemble (table anomalies) |

> Les requêtes #3 et #4 interrogent les tables brutes (hors `v_missions`) pour capturer des données que la vue exclut intentionnellement.

### Composants par page

| Page | Composant | Source |
|------|-----------|--------|
| **Vue d'ensemble** | KPIs, activité hebdomadaire | `df` ← `v_missions` |
| | Camembert types de missions | `df_form_missions` ← requête #3 |
| | Table anomalies km | `df_km_anomalies` ← requête #4 |
| **Performance trajets** | Histogramme distances, scatter, boxplots attentes | `df` ← `v_missions` |
| **Chauffeurs & Engins** | Missions/km par chauffeur, heatmap, % nuitées | `df` ← `v_missions` |
| **Expéditeurs / Destinataires** | Top remettants, destinataires, temps d'attente | `df` ← `v_missions` |
| **Marchandises** | Top 15, évolution mensuelle | `df` ← `v_missions` (colonne GROUP_CONCAT éclatée en Python) |
| **Impact CO₂** | CO₂ par véhicule, chauffeur, tendance | `df` ← `v_missions` + facteurs ADEME ([config.py](leila_dash/config.py)) |
| **Géographie** | Carte GPS (points + routes) | `df` ← `v_missions` (filtré GPS valides Guyane) |
| **Impact économique** | Coût carburant réel, consommation L/100km | `df_carburant` ← requête #2 |
| | Coût horaire, coût par chauffeur/mission | `df` ← `v_missions` + estimations Python |

---

## Structure du projet

```
Leila_Test/
├── leila_dash/
│   ├── app.py           # Point d'entrée — python app.py
│   ├── dash_app.py      # Instance dash.Dash() partagée
│   ├── config.py        # Couleurs, thème Plotly, constantes métier
│   ├── data.py          # Connexion MariaDB, load_data(), DataFrame
│   ├── components.py    # Composants HTML réutilisables (card, kpi_card)
│   ├── layout.py        # Structure de la page (header, nav, contenu)
│   ├── callbacks.py     # Callback de navigation entre sections
│   └── pages/
│       ├── overview.py       # 01 — Vue d'ensemble
│       ├── performance.py    # 02 — Performance des trajets
│       ├── chauffeurs.py     # 03 — Chauffeurs & Engins
│       ├── acteurs.py        # 04 — Expéditeurs / Destinataires
│       ├── marchandises.py   # 05 — Marchandises
│       ├── co2.py            # 06 — Impact CO₂
│       ├── geo.py            # 07 — Géographie
│       └── economie.py       # 08 — Impact économique
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
| 8 | **Impact économique** | Coût carburant, coût horaire, coût total par engin et chauffeur (barème CNR) |

---

## Données clés

| Indicateur | Valeur |
|---|---|
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

---

