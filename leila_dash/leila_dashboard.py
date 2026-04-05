"""
LEILA Transport Dashboard — Data/BI Analyst Test Technique
==========================================================
Connexion : MariaDB (snfAnonymise) → vue v_missions
Lancer    : python leila_dashboard.py
Accès     : http://127.0.0.1:8100
"""

# ── Dépendances ────────────────────────────────────────────
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ── Connexion MariaDB ──────────────────────────────────────
# Adapter les paramètres à votre environnement local
DB_USER     = "root"
DB_PASSWORD = ""          # ou votre mot de passe
DB_HOST     = "127.0.0.1"
DB_PORT     = 3306
DB_NAME     = "leila_test"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"charset": "utf8mb4"}
)

# ── Chargement données ─────────────────────────────────────
def load_data():
    """Charge v_missions depuis MariaDB et enrichit le DataFrame."""
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM v_missions"), conn)

    # Nettoyage / enrichissement
    df["mission_debut"] = pd.to_datetime(df["mission_debut"])
    df["mission_fin"]   = pd.to_datetime(df["mission_fin"])
    df["semaine"]       = df["mission_debut"].dt.isocalendar().week.astype(int)
    df["mois"]          = df["mission_debut"].dt.to_period("M").astype(str)
    df["jour"]          = df["mission_debut"].dt.date
    df["chauffeur"]     = df["chauffeur_nom"].str.strip() + " " + df["chauffeur_prenom"].str.strip()

    # Fusion AUVAL/OVAL (doublon de saisie confirmé)
    df["chauffeur"] = df["chauffeur"].replace({
        "OVAL JOHAN": "AUVAL JOHAN",
        "AUVAL JOHAN": "AUVAL JOHAN",
    })

    # Estimation CO₂ (facteurs ADEME kg CO₂/km par type de véhicule)
    CO2_FACTEURS = {
        "Porteur 8x4":   0.900,
        "Tracteur 6x4":  0.750,
        "Tracteur 4x2":  0.650,
    }
    df["co2_kg"] = df.apply(
        lambda r: r["distance_km"] * CO2_FACTEURS.get(r["engin_type"], 0.75),
        axis=1
    )

    return df


df = load_data()

# ── Palette & style ───────────────────────────────────────
COLORS = {
    "bg":        "#0F1117",
    "card":      "#1A1D27",
    "border":    "#2A2D3E",
    "accent":    "#E84545",
    "accent2":   "#F5A623",
    "accent3":   "#4ECDC4",
    "text":      "#E8E8F0",
    "muted":     "#7B7D8E",
    "engins": {
        "TR-789-XY": "#E84545",
        "HB-316-CS": "#F5A623",
        "PO-456-AB": "#4ECDC4",
        "VH-234-CD": "#A78BFA",
        "GR-256-CQ": "#34D399",
        "CR-426-DD": "#F472B6",
    }
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'Courier New', monospace", color=COLORS["text"], size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=[COLORS["accent"], COLORS["accent2"], COLORS["accent3"],
              "#A78BFA", "#34D399", "#F472B6"],
)

def card(children, style=None):
    s = {
        "background": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "8px",
        "padding": "20px",
        "marginBottom": "16px",
    }
    if style:
        s.update(style)
    return html.Div(children, style=s)

def kpi_card(label, value, sub="", color=COLORS["accent"]):
    return html.Div([
        html.Div(label, style={"color": COLORS["muted"], "fontSize": "11px",
                               "fontFamily": "'Courier New', monospace",
                               "letterSpacing": "2px", "textTransform": "uppercase"}),
        html.Div(value, style={"color": color, "fontSize": "32px",
                               "fontWeight": "700", "fontFamily": "'Courier New', monospace",
                               "lineHeight": "1.1", "marginTop": "6px"}),
        html.Div(sub,   style={"color": COLORS["muted"], "fontSize": "11px", "marginTop": "4px"}),
    ], style={
        "background": COLORS["card"],
        "border":     f"1px solid {color}33",
        "borderLeft": f"3px solid {color}",
        "borderRadius": "6px",
        "padding": "16px 20px",
        "flex": "1",
        "minWidth": "140px",
    })

# ── Sections du dashboard ─────────────────────────────────

def section_overview(df):
    # KPIs globaux
    total_km     = df["distance_km"].sum()
    total_co2    = df["co2_kg"].sum() / 1000  # tonnes
    moy_dist     = df["distance_km"].median()
    moy_duree    = df["duree_trajet_min"].median()
    nb_chauffeurs = df["chauffeur"].nunique()
    nb_engins    = df["engin_immatriculation"].nunique()

    # Activité hebdomadaire
    weekly = df.groupby("semaine").agg(
        missions=("mission_id", "count"),
        km_total=("distance_km", "sum")
    ).reset_index()

    fig_weekly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_weekly.add_trace(go.Bar(
        x=weekly["semaine"], y=weekly["missions"],
        name="Missions", marker_color=COLORS["accent"],
        opacity=0.85
    ), secondary_y=False)
    fig_weekly.add_trace(go.Scatter(
        x=weekly["semaine"], y=weekly["km_total"],
        name="Km total", mode="lines+markers",
        line=dict(color=COLORS["accent2"], width=2),
        marker=dict(size=5)
    ), secondary_y=True)
    fig_weekly.update_layout(
        title="Activité hebdomadaire — missions & kilométrage",
        **PLOTLY_THEME,
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(title="Semaine", gridcolor=COLORS["border"]),
        yaxis=dict(title="Nb missions", gridcolor=COLORS["border"]),
        yaxis2=dict(title="Km total", gridcolor=COLORS["border"]),
    )

    # Répartition par type mission
    type_counts = df["type_mission"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig_type = px.pie(
        type_counts, values="count", names="type",
        title="Répartition par type de mission",
        color_discrete_sequence=[COLORS["accent"], COLORS["accent2"], COLORS["accent3"]],
        hole=0.55,
    )
    fig_type.update_layout(**PLOTLY_THEME)
    fig_type.update_traces(textfont_color=COLORS["text"])

    return html.Div([
        html.H2("VUE D'ENSEMBLE", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        html.Div([
            kpi_card("Missions validées",  f"{len(df):,}", f"Jan–Mars 2026"),
            kpi_card("Km parcourus",       f"{total_km:,.0f}", "total",       COLORS["accent2"]),
            kpi_card("CO₂ estimé",         f"{total_co2:.1f} t", "ADEME",     COLORS["accent3"]),
            kpi_card("Distance médiane",   f"{moy_dist:.0f} km", "par mission"),
            kpi_card("Durée médiane trajet", f"{moy_duree:.0f} min", "hors attente", COLORS["accent2"]),
            kpi_card("Chauffeurs actifs",  str(nb_chauffeurs), ""),
            kpi_card("Engins actifs",      str(nb_engins), "sur 6 immat.", COLORS["accent3"]),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "20px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_weekly, config={"displayModeBar": False}),
                     style={"flex": "2"}),
            html.Div(dcc.Graph(figure=fig_type,   config={"displayModeBar": False}),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])


def section_performance(df):
    # Distribution distances
    fig_dist = px.histogram(
        df, x="distance_km", nbins=40,
        title="Distribution des distances (km)",
        color_discrete_sequence=[COLORS["accent"]],
        labels={"distance_km": "Distance (km)", "count": "Nb missions"},
    )
    fig_dist.add_vline(x=df["distance_km"].median(), line_dash="dash",
                       line_color=COLORS["accent2"],
                       annotation_text=f"Médiane {df['distance_km'].median():.0f} km",
                       annotation_font_color=COLORS["accent2"])
    fig_dist.update_layout(**PLOTLY_THEME,
                           xaxis=dict(gridcolor=COLORS["border"]),
                           yaxis=dict(gridcolor=COLORS["border"]))

    # Scatter distance vs durée trajet
    df_sc = df[df["duree_trajet_min"].between(0, 600)].copy()
    fig_scatter = px.scatter(
        df_sc, x="distance_km", y="duree_trajet_min",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        title="Distance vs Durée de trajet",
        labels={"distance_km": "Distance (km)", "duree_trajet_min": "Durée trajet (min)",
                "engin_immatriculation": "Engin"},
        hover_data=["chauffeur", "remettant", "destinataire"],
        opacity=0.7,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=COLORS["accent2"],
    )
    fig_scatter.update_layout(**PLOTLY_THEME,
                              xaxis=dict(gridcolor=COLORS["border"]),
                              yaxis=dict(gridcolor=COLORS["border"]))

    # Boîtes à moustaches temps d'attente
    df_att = df[df["attente_chargement_min"].between(0, 240) &
                df["attente_dechargement_min"].between(0, 240)].copy()
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=df_att["attente_chargement_min"], name="Chargement",
        marker_color=COLORS["accent"], boxmean=True,
    ))
    fig_box.add_trace(go.Box(
        y=df_att["attente_dechargement_min"], name="Déchargement",
        marker_color=COLORS["accent3"], boxmean=True,
    ))
    fig_box.update_layout(
        title="Temps d'attente chargement / déchargement (min)",
        **PLOTLY_THEME,
        yaxis=dict(title="Minutes", gridcolor=COLORS["border"]),
    )

    return html.Div([
        html.H2("PERFORMANCE DES TRAJETS", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_dist,    config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_box,     config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
    ])


def section_chauffeurs(df):
    # Missions & km par chauffeur
    ch = df.groupby("chauffeur").agg(
        missions=("mission_id", "count"),
        km_total=("distance_km", "sum"),
        km_moyen=("distance_km", "mean"),
        duree_moy=("duree_trajet_min", "median"),
    ).reset_index().sort_values("missions", ascending=True)

    fig_ch = make_subplots(rows=1, cols=2,
                            subplot_titles=["Missions par chauffeur", "Km total par chauffeur"])
    fig_ch.add_trace(go.Bar(
        x=ch["missions"], y=ch["chauffeur"], orientation="h",
        marker_color=COLORS["accent"], name="Missions",
    ), row=1, col=1)
    fig_ch.add_trace(go.Bar(
        x=ch["km_total"], y=ch["chauffeur"], orientation="h",
        marker_color=COLORS["accent2"], name="Km total",
    ), row=1, col=2)
    fig_ch.update_layout(
        title="Performance chauffeurs", showlegend=False,
        **PLOTLY_THEME,
        yaxis=dict(gridcolor=COLORS["border"]),
        xaxis=dict(gridcolor=COLORS["border"]),
        xaxis2=dict(gridcolor=COLORS["border"]),
    )

    # Utilisation engins
    eng = df.groupby("engin_immatriculation").agg(
        missions=("mission_id", "count"),
        km_total=("distance_km", "sum"),
        km_moyen=("distance_km", "mean"),
    ).reset_index().sort_values("missions", ascending=False)

    colors_eng = [COLORS["engins"].get(i, COLORS["accent"]) for i in eng["engin_immatriculation"]]

    fig_eng = px.bar(
        eng, x="engin_immatriculation", y="missions",
        title="Missions par engin",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        labels={"engin_immatriculation": "Engin", "missions": "Nb missions"},
        text="missions",
    )
    fig_eng.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_eng.update_layout(**PLOTLY_THEME,
                          showlegend=False,
                          xaxis=dict(gridcolor=COLORS["border"]),
                          yaxis=dict(gridcolor=COLORS["border"]))

    # Activité hebdo par engin
    wk_eng = df.groupby(["semaine", "engin_immatriculation"]).size().reset_index(name="missions")
    fig_heatmap = px.density_heatmap(
        wk_eng, x="semaine", y="engin_immatriculation", z="missions",
        title="Intensité d'utilisation par engin et semaine",
        color_continuous_scale=[[0, COLORS["card"]], [0.3, COLORS["accent"]+"88"], [1, COLORS["accent"]]],
        labels={"semaine": "Semaine", "engin_immatriculation": "Engin", "missions": "Missions"},
    )
    fig_heatmap.update_layout(**PLOTLY_THEME)

    return html.Div([
        html.H2("CHAUFFEURS & ENGINS", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_ch,  config={"displayModeBar": False}), style={"flex": "2"}),
            html.Div(dcc.Graph(figure=fig_eng, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_heatmap, config={"displayModeBar": False}),
    ])


def section_acteurs(df):
    # Top remettants et destinataires par volume de missions
    top_rmt = df.groupby("remettant").agg(
        missions=("mission_id", "count"),
        att_moy=("attente_chargement_min", "median"),
    ).reset_index().sort_values("missions", ascending=False).head(12)

    top_dst = df.groupby("destinataire").agg(
        missions=("mission_id", "count"),
        att_moy=("attente_dechargement_min", "median"),
    ).reset_index().sort_values("missions", ascending=False).head(12)

    fig_rmt = px.bar(
        top_rmt.sort_values("missions"), x="missions", y="remettant",
        orientation="h", title="Top remettants — volume missions",
        color="att_moy",
        color_continuous_scale=[[0, COLORS["accent3"]], [1, COLORS["accent"]]],
        labels={"missions": "Nb missions", "remettant": "", "att_moy": "Attente moy (min)"},
        text="missions",
    )
    fig_rmt.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_rmt.update_layout(**PLOTLY_THEME,
                          coloraxis_showscale=True,
                          xaxis=dict(gridcolor=COLORS["border"]))

    fig_dst = px.bar(
        top_dst.sort_values("missions"), x="missions", y="destinataire",
        orientation="h", title="Top destinataires — volume missions",
        color="att_moy",
        color_continuous_scale=[[0, COLORS["accent3"]], [1, COLORS["accent"]]],
        labels={"missions": "Nb missions", "destinataire": "", "att_moy": "Attente moy (min)"},
        text="missions",
    )
    fig_dst.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_dst.update_layout(**PLOTLY_THEME,
                          coloraxis_showscale=True,
                          xaxis=dict(gridcolor=COLORS["border"]))

    # Comparaison temps d'attente remettant vs destinataire
    rmt_att = df.groupby("remettant")["attente_chargement_min"].median().reset_index()
    rmt_att.columns = ["acteur", "attente_min"]
    rmt_att["role"] = "Remettant"
    dst_att = df.groupby("destinataire")["attente_dechargement_min"].median().reset_index()
    dst_att.columns = ["acteur", "attente_min"]
    dst_att["role"] = "Destinataire"
    att_df = pd.concat([rmt_att, dst_att])
    att_df = att_df[att_df["attente_min"].between(0, 240)]

    fig_att = px.box(
        att_df, x="role", y="attente_min", color="role",
        title="Distribution temps d'attente : remettants vs destinataires",
        color_discrete_map={"Remettant": COLORS["accent"], "Destinataire": COLORS["accent3"]},
        labels={"attente_min": "Attente médiane (min)", "role": ""},
    )
    fig_att.update_layout(**PLOTLY_THEME, showlegend=False,
                          yaxis=dict(gridcolor=COLORS["border"]))

    return html.Div([
        html.H2("EXPÉDITEURS & DESTINATAIRES", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_rmt, config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_dst, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_att, config={"displayModeBar": False}),
    ])


def section_marchandises(df):
    # Nettoyer les libellés de marchandises (multi-valeurs séparées par virgule)
    mch = (df["marchandises"]
           .dropna()
           .str.split(",")
           .explode()
           .str.strip()
           .value_counts()
           .reset_index())
    mch.columns = ["marchandise", "count"]
    mch = mch.head(15)

    fig_mch = px.bar(
        mch.sort_values("count"), x="count", y="marchandise",
        orientation="h", title="Top 15 marchandises transportées",
        color="count",
        color_continuous_scale=[[0, COLORS["accent"]+"44"], [1, COLORS["accent"]]],
        labels={"count": "Nb occurrences", "marchandise": ""},
        text="count",
    )
    fig_mch.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_mch.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                          xaxis=dict(gridcolor=COLORS["border"]))

    # Évolution mensuelle par famille de marchandise
    df_m = df[df["marchandises"].notna()].copy()
    df_m["marchandise_principale"] = df_m["marchandises"].str.split(",").str[0].str.strip()
    top_mch = df_m["marchandise_principale"].value_counts().head(6).index.tolist()
    df_m2 = df_m[df_m["marchandise_principale"].isin(top_mch)]
    monthly = df_m2.groupby(["mois", "marchandise_principale"]).size().reset_index(name="missions")

    fig_trend = px.line(
        monthly, x="mois", y="missions", color="marchandise_principale",
        title="Évolution mensuelle — top 6 marchandises",
        markers=True,
        labels={"mois": "Mois", "missions": "Nb missions", "marchandise_principale": "Marchandise"},
    )
    fig_trend.update_layout(**PLOTLY_THEME,
                             xaxis=dict(gridcolor=COLORS["border"]),
                             yaxis=dict(gridcolor=COLORS["border"]))

    return html.Div([
        html.H2("ANALYSE MARCHANDISES", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_mch,   config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_trend, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])


def section_co2(df):
    # CO₂ par engin
    co2_eng = df.groupby("engin_immatriculation").agg(
        co2_total=("co2_kg", "sum"),
        missions=("mission_id", "count"),
        km=("distance_km", "sum"),
    ).reset_index()
    co2_eng["co2_par_mission"] = co2_eng["co2_total"] / co2_eng["missions"]
    co2_eng["co2_par_km"]      = co2_eng["co2_total"] / co2_eng["km"]

    fig_co2_eng = px.bar(
        co2_eng.sort_values("co2_total", ascending=False),
        x="engin_immatriculation", y="co2_total",
        title="CO₂ estimé total par engin (kg) — facteurs ADEME",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        labels={"engin_immatriculation": "Engin", "co2_total": "CO₂ total (kg)"},
        text=co2_eng.sort_values("co2_total", ascending=False)["co2_total"].round(0).astype(int),
    )
    fig_co2_eng.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_co2_eng.update_layout(**PLOTLY_THEME, showlegend=False,
                               xaxis=dict(gridcolor=COLORS["border"]),
                               yaxis=dict(gridcolor=COLORS["border"]))

    # CO₂ par chauffeur
    co2_ch = df.groupby("chauffeur").agg(
        co2_total=("co2_kg", "sum"),
        missions=("mission_id", "count"),
    ).reset_index().sort_values("co2_total", ascending=True)

    fig_co2_ch = px.bar(
        co2_ch, x="co2_total", y="chauffeur",
        orientation="h", title="CO₂ estimé par chauffeur (kg)",
        color="co2_total",
        color_continuous_scale=[[0, COLORS["accent3"]], [0.5, COLORS["accent2"]], [1, COLORS["accent"]]],
        labels={"co2_total": "CO₂ (kg)", "chauffeur": ""},
    )
    fig_co2_ch.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                              xaxis=dict(gridcolor=COLORS["border"]))

    # Évolution CO₂ hebdomadaire
    co2_wk = df.groupby("semaine")["co2_kg"].sum().reset_index()
    fig_co2_trend = px.area(
        co2_wk, x="semaine", y="co2_kg",
        title="Évolution hebdomadaire des émissions CO₂ estimées (kg)",
        labels={"semaine": "Semaine", "co2_kg": "CO₂ (kg)"},
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig_co2_trend.update_traces(fillcolor=COLORS["accent"]+"33", line_color=COLORS["accent"])
    fig_co2_trend.update_layout(**PLOTLY_THEME,
                                 xaxis=dict(gridcolor=COLORS["border"]),
                                 yaxis=dict(gridcolor=COLORS["border"]))

    note = html.Div([
        html.Span("⚠ ", style={"color": COLORS["accent2"]}),
        html.Span(
            "Estimation indicative basée sur les facteurs ADEME : Porteur 8x4 → 0,90 kg/km · "
            "Tracteur 6x4 → 0,75 kg/km · Tracteur 4x2 → 0,65 kg/km. "
            "Aucune donnée carburant disponible dans ce dump.",
            style={"color": COLORS["muted"], "fontSize": "11px",
                   "fontFamily": "'Courier New', monospace"}
        )
    ], style={"marginBottom": "16px"})

    return html.Div([
        html.H2("IMPACT ENVIRONNEMENTAL", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "12px", "fontSize": "14px"}),
        note,
        html.Div([
            html.Div(dcc.Graph(figure=fig_co2_eng, config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_co2_ch,  config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_co2_trend, config={"displayModeBar": False}),
    ])


def section_geo(df):
    df_geo = df[
        df["lat_retrait"].notna() & df["lon_retrait"].notna() &
        df["lat_livraison"].notna() & df["lon_livraison"].notna()
    ].copy()

    # Filtrer les coordonnées aberrantes (hors zone Guyane approx)
    # Guyane : lat ~2–6N, lon ~-55 à -51W
    df_geo = df_geo[
        df_geo["lat_retrait"].between(1, 8) &
        df_geo["lon_retrait"].between(-56, -50) &
        df_geo["lat_livraison"].between(1, 8) &
        df_geo["lon_livraison"].between(-56, -50)
    ]

    # Points de retrait
    fig_map = go.Figure()

    fig_map.add_trace(go.Scattermapbox(
        lat=df_geo["lat_retrait"], lon=df_geo["lon_retrait"],
        mode="markers",
        marker=dict(size=6, color=COLORS["accent"], opacity=0.6),
        name="Point retrait",
        hovertemplate="<b>Retrait</b><br>%{lat:.4f}, %{lon:.4f}<br>" +
                      "<extra>%{customdata}</extra>",
        customdata=df_geo["remettant"],
    ))

    fig_map.add_trace(go.Scattermapbox(
        lat=df_geo["lat_livraison"], lon=df_geo["lon_livraison"],
        mode="markers",
        marker=dict(size=6, color=COLORS["accent3"], opacity=0.6),
        name="Point livraison",
        hovertemplate="<b>Livraison</b><br>%{lat:.4f}, %{lon:.4f}<br>" +
                      "<extra>%{customdata}</extra>",
        customdata=df_geo["destinataire"],
    ))

    # Lignes de trajet (sample 80 missions pour lisibilité)
    sample = df_geo.sample(min(80, len(df_geo)), random_state=42)
    for _, row in sample.iterrows():
        fig_map.add_trace(go.Scattermapbox(
            lat=[row["lat_retrait"], row["lon_retrait"], None],
            lon=[row["lon_retrait"], row["lon_livraison"], None],
            mode="lines",
            line=dict(width=1, color=COLORS["accent2"]),
            opacity=0.25,
            showlegend=False,
            hoverinfo="skip",
        ))

    # Correction : les lignes de trajet doivent utiliser lat/lon correctement
    fig_map2 = go.Figure()
    fig_map2.add_trace(go.Scattermapbox(
        lat=df_geo["lat_retrait"], lon=df_geo["lon_retrait"],
        mode="markers",
        marker=dict(size=7, color=COLORS["accent"], opacity=0.7),
        name="Retrait",
        hovertext=df_geo["remettant"],
        hovertemplate="<b>Retrait</b><br>%{hovertext}<br>%{lat:.4f}°N, %{lon:.4f}°E<extra></extra>",
    ))
    fig_map2.add_trace(go.Scattermapbox(
        lat=df_geo["lat_livraison"], lon=df_geo["lon_livraison"],
        mode="markers",
        marker=dict(size=7, color=COLORS["accent3"], opacity=0.7),
        name="Livraison",
        hovertext=df_geo["destinataire"],
        hovertemplate="<b>Livraison</b><br>%{hovertext}<br>%{lat:.4f}°N, %{lon:.4f}°E<extra></extra>",
    ))

    # Ajouter les lignes de trajet
    lats, lons = [], []
    for _, row in sample.iterrows():
        lats += [row["lat_retrait"], row["lat_livraison"], None]
        lons += [row["lon_retrait"], row["lon_livraison"], None]

    fig_map2.add_trace(go.Scattermapbox(
        lat=lats, lon=lons,
        mode="lines",
        line=dict(width=1, color=COLORS["accent2"]),
        opacity=0.3,
        name="Trajets (échantillon 80)",
        hoverinfo="skip",
    ))

    fig_map2.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=df_geo["lat_retrait"].mean(), lon=df_geo["lon_retrait"].mean()),
            zoom=8,
        ),
        **PLOTLY_THEME,
        height=550,
        margin=dict(l=0, r=0, t=40, b=0),
        title="Carte des trajets — points GPS retrait & livraison",
        legend=dict(orientation="h", y=0.01, bgcolor="rgba(0,0,0,0.5)"),
    )

    # Densité des zones d'activité
    all_pts = pd.concat([
        df_geo[["lat_retrait", "lon_retrait"]].rename(columns={"lat_retrait": "lat", "lon_retrait": "lon"}),
        df_geo[["lat_livraison", "lon_livraison"]].rename(columns={"lat_livraison": "lat", "lon_livraison": "lon"}),
    ])

    fig_density = px.density_mapbox(
        all_pts, lat="lat", lon="lon", radius=12,
        title="Zones de forte activité",
        color_continuous_scale=[[0, "rgba(0,0,0,0)"], [0.3, COLORS["accent2"]+"99"], [1, COLORS["accent"]]],
        mapbox_style="carto-darkmatter",
        center=dict(lat=all_pts["lat"].mean(), lon=all_pts["lon"].mean()),
        zoom=8, height=450,
    )
    fig_density.update_layout(**PLOTLY_THEME, margin=dict(l=0, r=0, t=40, b=0))

    return html.Div([
        html.H2("ANALYSE GÉOGRAPHIQUE", style={"color": COLORS["accent"],
                "fontFamily": "'Courier New', monospace",
                "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px"}),
        dcc.Graph(figure=fig_map2,    config={"displayModeBar": True, "scrollZoom": True}),
        dcc.Graph(figure=fig_density, config={"displayModeBar": True, "scrollZoom": True}),
    ])


# ── Layout principal ───────────────────────────────────────
NAV_ITEMS = [
    ("overview",      "01 — Vue d'ensemble"),
    ("performance",   "02 — Performance"),
    ("chauffeurs",    "03 — Chauffeurs & Engins"),
    ("acteurs",       "04 — Expéditeurs / Dest."),
    ("marchandises",  "05 — Marchandises"),
    ("co2",           "06 — Impact CO₂"),
    ("geo",           "07 — Géographie"),
]

app = dash.Dash(
    __name__,
    title="LEILA Transport — Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div([
    # ── En-tête ──
    html.Div([
        html.Div([
            html.Span("LEILA", style={
                "color": COLORS["accent"], "fontSize": "22px",
                "fontWeight": "900", "fontFamily": "'Courier New', monospace",
                "letterSpacing": "4px",
            }),
            html.Span(" · TRANSPORT", style={
                "color": COLORS["muted"], "fontSize": "13px",
                "fontFamily": "'Courier New', monospace", "letterSpacing": "3px",
            }),
        ]),
        html.Div("Plateau des Guyanes · Jan–Mars 2026", style={
            "color": COLORS["muted"], "fontSize": "11px",
            "fontFamily": "'Courier New', monospace",
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "padding": "14px 28px",
        "borderBottom": f"1px solid {COLORS['border']}",
        "background": COLORS["card"],
        "position": "sticky", "top": "0", "zIndex": "100",
    }),

    # ── Corps principal ──
    html.Div([
        # ── Navigation latérale ──
        html.Div([
            html.Div(
                html.Button(
                    label,
                    id=f"nav-{key}",
                    n_clicks=0,
                    style={
                        "display": "block", "width": "100%", "textAlign": "left",
                        "background": "none", "border": "none",
                        "borderLeft": f"2px solid {COLORS['border']}",
                        "padding": "10px 16px",
                        "color": COLORS["muted"],
                        "fontFamily": "'Courier New', monospace",
                        "fontSize": "11px", "letterSpacing": "1px",
                        "cursor": "pointer",
                    }
                )
            ) for key, label in NAV_ITEMS
        ] + [
            html.Div(style={"height": "1px", "background": COLORS["border"], "margin": "16px 0"}),
            html.Div([
                html.Div("SOURCE", style={"color": COLORS["muted"], "fontSize": "9px",
                                          "fontFamily": "'Courier New', monospace",
                                          "letterSpacing": "2px", "marginBottom": "6px"}),
                html.Div(f"{len(df)} missions validées", style={
                    "color": COLORS["text"], "fontSize": "11px",
                    "fontFamily": "'Courier New', monospace",
                }),
                html.Div("MariaDB · snfAnonymise", style={
                    "color": COLORS["muted"], "fontSize": "10px",
                    "fontFamily": "'Courier New', monospace",
                }),
                html.Div("Vue : v_missions", style={
                    "color": COLORS["muted"], "fontSize": "10px",
                    "fontFamily": "'Courier New', monospace",
                }),
            ], style={"padding": "0 16px"}),
        ], style={
            "width": "180px", "minWidth": "180px",
            "padding": "24px 0",
            "borderRight": f"1px solid {COLORS['border']}",
            "position": "sticky", "top": "53px",
            "height": "calc(100vh - 53px)",
            "overflowY": "auto",
        }),

        # ── Contenu dynamique ──
        html.Div(
            id="page-content",
            style={"flex": "1", "padding": "28px", "overflowY": "auto"},
        ),
    ], style={"display": "flex", "minHeight": "calc(100vh - 53px)"}),

], style={"background": COLORS["bg"], "minHeight": "100vh", "color": COLORS["text"]})


# ── Callbacks navigation ───────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    [Input(f"nav-{key}", "n_clicks") for key, _ in NAV_ITEMS],
    prevent_initial_call=False,
)
def render_page(*args):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == 0:
        # Page par défaut
        return section_overview(df)

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    key = button_id.replace("nav-", "")

    sections = {
        "overview":     section_overview,
        "performance":  section_performance,
        "chauffeurs":   section_chauffeurs,
        "acteurs":      section_acteurs,
        "marchandises": section_marchandises,
        "co2":          section_co2,
        "geo":          section_geo,
    }
    return sections.get(key, section_overview)(df)


# ── Lancement ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  LEILA Transport Dashboard")
    print(f"  {len(df)} missions chargées depuis MariaDB")
    print("  http://127.0.0.1:8100")
    print("=" * 55)
    app.run(debug=True, host="127.0.0.1", port=8100)
