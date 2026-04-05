# ── Connexion MariaDB & chargement des données ────────────

import pandas as pd
from sqlalchemy import create_engine, text
from config import CO2_FACTEURS

DB_USER     = "root"
DB_PASSWORD = ""
DB_HOST     = "127.0.0.1"
DB_PORT     = 3306
DB_NAME     = "leila_test"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"charset": "utf8mb4"},
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

    # Estimation CO₂ (facteurs ADEME kg CO₂/km)
    df["co2_kg"] = df.apply(
        lambda r: r["distance_km"] * CO2_FACTEURS.get(r["engin_type"], 0.75),
        axis=1,
    )

    return df


# Chargement unique au démarrage
df = load_data()
