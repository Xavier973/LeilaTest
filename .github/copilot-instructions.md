# LEILA Transport Dashboard — Contexte projet Copilot

## Vue d'ensemble
Dashboard **Dash/Plotly** pour un test technique de recrutement Data/BI Analyst chez **MÉTHODES CODE** (éditeur du SaaS LEILA).  
Date de rendu : **8 avril 2026**.

---

## Base de données
- **MariaDB local** · base : `snfAnonymise`
- Connexion via **SQLAlchemy + pymysql**
- **Source unique : vue `v_missions`** — ne jamais lire les tables brutes directement depuis le dashboard

```python
DB_USER     = "root"
DB_PASSWORD = ""
DB_HOST     = "127.0.0.1"
DB_PORT     = 3306
DB_NAME     = "snfAnonymise"
```

---

## Vue v_missions — colonnes disponibles

| Colonne | Type | Description |
|---|---|---|
| `mission_id` | int | Clé primaire |
| `statut` | str | COLLECTE / COMPILE / CORRECTION |
| `type_mission` | str | Transport marchandises / Location à la journée / Location au voyage |
| `mission_debut` | datetime | Début mission |
| `mission_fin` | datetime | Fin mission |
| `engin_immatriculation` | str | TR-789-XY · HB-316-CS · PO-456-AB · VH-234-CD · GR-256-CQ · CR-426-DD |
| `engin_type` | str | Porteur 8x4 / Tracteur 6x4 / Tracteur 4x2 |
| `engin_marque` | str | MAN / DAF / SCANIA |
| `engin_modele` | str | |
| `engin_contenance_t` | float | Capacité en tonnes |
| `chauffeur_nom` | str | |
| `chauffeur_prenom` | str | NB : OVAL JOHAN = AUVAL JOHAN (doublon saisie) |
| `remettant` | str | Expéditeur (anonymisé ENTITY-XXXX) |
| `remettant_activite` | str | Carrière / Magasin / Usine / BTP… |
| `destinataire` | str | Destinataire (anonymisé ENTITY-XXXX) |
| `destinataire_activite` | str | |
| `km_depart` | int | Kilométrage compteur au retrait |
| `km_arrivee` | int | Kilométrage compteur à la livraison |
| `distance_km` | int | km_arrivee - km_depart (filtré 1–300 km) |
| `attente_chargement_min` | int | Durée étape retrait (min) |
| `duree_trajet_min` | int | Durée trajet retrait→livraison (min) |
| `attente_dechargement_min` | int | Durée étape livraison (min) |
| `duree_totale_min` | int | Durée totale mission (min) |
| `lat_retrait` | float | GPS latitude point retrait |
| `lon_retrait` | float | GPS longitude point retrait |
| `lat_livraison` | float | GPS latitude point livraison |
| `lon_livraison` | float | GPS longitude point livraison |
| `marchandises` | str | GROUP_CONCAT des libellés (ex: "Palette agglo 10, Palette agglo 15") |
| `poids_net_total_t` | float | Somme poids net (tonnes) |
| `poids_brut_total_t` | float | Somme poids brut (tonnes) |

---

## Données clés

- **734 missions validées** · Jan–Mars 2026 (11 semaines)
- **6 engins** réels (1 créé par formulaire, sans missions)
- **Distance** : médiane 27 km · moyenne 42,1 km · total 30 920 km
- **Poids** : 20% de nulls → utiliser `COALESCE(..., 0)` ou filtrer selon contexte
- **GPS** : 1–2% de nulls → toujours filtrer `IS NOT NULL` avant carte
- **Coordonnées valides Guyane** : lat ∈ [1, 8] · lon ∈ [-56, -50]
- **Table Location vide** → type "Location" non représenté dans le dashboard

---

## Anomalies connues à gérer

- `OVAL JOHAN` = `AUVAL JOHAN` → fusionner avec `.replace()`
- `BROWN Wetch` → graphie anormale (1 seule mission), laisser tel quel
- `CR-426-DD` → 1 seule mission dans la période
- Durées négatives sur `duree_trajet_min` → filtrer avec `.clip(lower=0)` ou `BETWEEN 0 AND 600`
- `marchandises` = chaîne GROUP_CONCAT → `.str.split(', ').explode()` pour analyser

---

## Estimation CO₂ (facteurs ADEME)

```python
CO2_FACTEURS = {
    "Porteur 8x4":  0.900,  # kg CO₂ / km
    "Tracteur 6x4": 0.750,
    "Tracteur 4x2": 0.650,
}
```
Aucune donnée carburant disponible — estimation uniquement.

---

## Structure du dashboard (7 sections)

1. **Vue d'ensemble** — KPIs globaux, activité hebdomadaire
2. **Performance trajets** — distances, durées, temps d'attente
3. **Chauffeurs & Engins** — missions par chauffeur, utilisation engins, heatmap semaine×engin
4. **Expéditeurs / Destinataires** — top acteurs, comparaison temps d'attente
5. **Marchandises** — top libellés, évolution mensuelle
6. **Impact CO₂** — estimation par engin et chauffeur (ADEME)
7. **Géographie** — carte points GPS + lignes trajets + densité zones

---

## Stack technique

```
dash>=2.16.0
plotly>=5.20.0
pandas>=2.0.0
sqlalchemy>=2.0.0
pymysql>=1.1.0
```
