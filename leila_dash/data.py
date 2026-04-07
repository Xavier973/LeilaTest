# ── Connexion MariaDB & chargement des données ────────────

import os

import pandas as pd
from pandas.errors import DatabaseError as PandasDatabaseError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from config import CO2_FACTEURS

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "snfAnonymise")

db_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD or None,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(
    db_url,
    connect_args={"charset": "utf8mb4"},
    pool_pre_ping=True,
    pool_recycle=280,
)


def load_data() -> pd.DataFrame:
    """Charge v_missions depuis MariaDB et enrichit le DataFrame."""
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM v_missions"), conn)

    df["mission_debut"] = pd.to_datetime(df["mission_debut"])
    df["mission_fin"]   = pd.to_datetime(df["mission_fin"])
    df["semaine"]       = df["mission_debut"].dt.isocalendar().week.astype(int)
    df["mois"]          = df["mission_debut"].dt.to_period("M").astype(str)
    df["jour"]          = df["mission_debut"].dt.date
    df["chauffeur"]     = (
        df["chauffeur_nom"].str.strip() + " " + df["chauffeur_prenom"].str.strip()
    )

    # Fusion AUVAL/OVAL (doublon de saisie confirmé)
    df["chauffeur"] = df["chauffeur"].replace({"OVAL JOHAN": "AUVAL JOHAN"})

    # Compatibilité : type_duree peut ne pas exister si la vue n'a pas été recréée
    if "type_duree" not in df.columns:
        df["type_duree"] = df["duree_totale_min"].apply(
            lambda m: "journée" if m <= 600 else ("overnight" if m <= 1440 else "multi-jour")
        )
    if "duree_active_min" not in df.columns:
        df["duree_active_min"] = df["duree_totale_min"]

    # Estimation CO₂ (facteurs ADEME kg CO₂/km)
    df["co2_kg"] = df.apply(
        lambda r: r["distance_km"] * CO2_FACTEURS.get(r["engin_type"], 0.75),
        axis=1,
    )

    return df


def load_carburant() -> pd.DataFrame:
    """Charge les pleins carburant (Gasoil) par engin depuis mouvementstock."""
    sql = text("""
        SELECT
            e.identifiant                       AS engin_immatriculation,
            e.type                              AS engin_type,
            e.marque,
            COUNT(DISTINCT m.id)                AS nb_pleins,
            ROUND(SUM(m.quantite), 1)           AS total_litres,
            ROUND(AVG(m.quantite), 1)           AS moy_litres_par_plein
        FROM MouvementStock m
        JOIN Formulaire f  ON f.id             = m.formulaireId
        JOIN Entite ent    ON ent.formulaireId = f.id
                           AND ent.fonction    = 'EQ-5003'
        JOIN Engin e       ON e.entiteId       = ent.id
        WHERE m.produit = 'Gasoil'
        GROUP BY e.identifiant, e.type, e.marque
        ORDER BY total_litres DESC
    """)
    try:
        with engine.connect() as conn:
            return pd.read_sql(sql, conn)
    except (SQLAlchemyError, PandasDatabaseError):
        # Certaines bases de test ne contiennent pas les tables stock/carburant.
        return pd.DataFrame(
            columns=[
                "engin_immatriculation",
                "engin_type",
                "marque",
                "nb_pleins",
                "total_litres",
                "moy_litres_par_plein",
            ]
        )


def load_km_anomalies() -> pd.DataFrame:
    """Charge tous les enregistrements kilométrage aberrants depuis les tables brutes,
    y compris ceux filtrés par v_missions (distance hors 1-300 km, GPS identiques)."""
    sql = text("""
        SELECT
            f.id                                            AS mission_id,
            f.debut                                         AS mission_debut,
            e.identifiant                                   AS engin,
            e.type                                          AS engin_type,
            CONCAT(p.nom, ' ', p.prenom)                   AS chauffeur,
            r.kilometrageDebut                              AS km_depart,
            l.kilometrageDebut                              AS km_arrivee,
            (l.kilometrageDebut - r.kilometrageDebut)       AS distance_km,
            TIMESTAMPDIFF(MINUTE, r.dateFin, l.dateDebut)  AS duree_trajet_min,
            r.gpsLatitude                                   AS lat_retrait,
            r.gpsLongitude                                  AS lon_retrait,
            l.gpsLatitude                                   AS lat_livraison,
            l.gpsLongitude                                  AS lon_livraison
        FROM Formulaire f
        JOIN Entite   ent ON ent.formulaireId = f.id AND ent.fonction = 'EQ-5003'
        JOIN Engin    e   ON e.entiteId       = ent.id
        JOIN Retrait  r   ON r.enginId        = e.id
        JOIN Livraison l  ON l.enginId        = e.id
        JOIN Personne p   ON p.enginId        = e.id
        WHERE f.mission IN ('Transport marchandises', 'Location à la journée', 'Location au voyage')
    """)
    with engine.connect() as conn:
        raw = pd.read_sql(sql, conn)

    raw["chauffeur"] = raw["chauffeur"].replace({"OVAL JOHAN": "AUVAL JOHAN"})
    raw["mission_debut"] = pd.to_datetime(raw["mission_debut"])

    rows = []
    for _, r in raw.iterrows():
        dist = r["distance_km"]
        dur  = r["duree_trajet_min"]

        # Catégorisation des anomalies
        if dist is None or pd.isna(dist):
            motif = "Kilométrage manquant"
        elif dist <= 0:
            motif = "Distance nulle ou négative (km_arrivée ≤ km_départ)"
        elif dist > 300:
            motif = f"Distance hors limite ({dist:.0f} km > 300 km)"
        elif dist < 1:
            motif = f"Distance < 1 km ({dist:.1f} km)"
        elif (
            r["lat_retrait"] is not None and not pd.isna(r["lat_retrait"]) and
            r["lat_livraison"] is not None and not pd.isna(r["lat_livraison"]) and
            r["lat_retrait"] == r["lat_livraison"] and
            r["lon_retrait"] == r["lon_livraison"] and
            dist > 100
        ):
            motif = f"GPS identiques + distance suspecte ({dist:.0f} km)"
        elif dur is not None and not pd.isna(dur) and dur > 0:
            vitesse = dist / dur * 60
            if vitesse > 130:
                motif = f"Vitesse impliquée {vitesse:.0f} km/h > 130 km/h"
            else:
                continue  # Enregistrement sain
        elif dur is not None and not pd.isna(dur) and dur <= 0:
            motif = f"Durée trajet nulle ou négative ({dur:.0f} min)"
        else:
            continue

        rows.append({
            "ID":              r["mission_id"],
            "Date":            r["mission_debut"].strftime("%d/%m/%Y %H:%M"),
            "Chauffeur":       r["chauffeur"],
            "Engin":           r["engin"],
            "Type engin":      r["engin_type"],
            "km départ":       r["km_depart"],
            "km arrivée":      r["km_arrivee"],
            "Distance (km)":   dist,
            "Durée trajet (min)": dur,
            "Anomalie":        motif,
        })

    return pd.DataFrame(rows)


def load_formulaire_missions() -> pd.DataFrame:
    """Compte le nombre de formulaires par type de mission (table brute)."""
    sql = text("""
        SELECT mission, COUNT(*) AS count
        FROM Formulaire
        GROUP BY mission
        ORDER BY count DESC
    """)
    try:
        with engine.connect() as conn:
            return pd.read_sql(sql, conn)
    except (SQLAlchemyError, PandasDatabaseError):
        return pd.DataFrame(columns=["mission", "count"])


# Chargement unique au démarrage
df = load_data()
df_carburant = load_carburant()
df_form_missions = load_formulaire_missions()
df_km_anomalies = load_km_anomalies()
