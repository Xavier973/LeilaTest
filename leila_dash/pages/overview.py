# ── Section 01 — Vue d'ensemble ───────────────────────────

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import dcc, html

from config import COLORS, PLOTLY_THEME
from components import kpi_card


def layout(df):
    total_km      = df["distance_km"].sum()
    total_co2     = df["co2_kg"].sum() / 1000  # tonnes
    moy_dist      = df["distance_km"].median()
    moy_duree     = df["duree_trajet_min"].median()
    nb_chauffeurs = df["chauffeur"].nunique()
    nb_engins     = df["engin_immatriculation"].nunique()

    # Activité hebdomadaire
    weekly = df.groupby("semaine").agg(
        missions=("mission_id", "count"),
        km_total=("distance_km", "sum"),
    ).reset_index()

    fig_weekly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_weekly.add_trace(go.Bar(
        x=weekly["semaine"], y=weekly["missions"],
        name="Missions", marker_color=COLORS["accent"], opacity=0.85,
    ), secondary_y=False)
    fig_weekly.add_trace(go.Scatter(
        x=weekly["semaine"], y=weekly["km_total"],
        name="Km total", mode="lines+markers",
        line=dict(color=COLORS["accent2"], width=2),
        marker=dict(size=5),
    ), secondary_y=True)
    fig_weekly.update_layout(
        title="Activité hebdomadaire — missions & kilométrage",
        **PLOTLY_THEME,
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(title="Semaine", gridcolor=COLORS["border"]),
        yaxis=dict(title="Nb missions", gridcolor=COLORS["border"]),
        yaxis2=dict(title="Km total", gridcolor=COLORS["border"]),
    )

    # Répartition par type de mission
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
        html.H2("VUE D'ENSEMBLE", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        html.Div([
            kpi_card("Missions validées",      f"{len(df):,}",          "Jan–Mars 2026"),
            kpi_card("Km parcourus",           f"{total_km:,.0f}",      "total",            COLORS["accent2"]),
            kpi_card("CO₂ estimé",             f"{total_co2:.1f} t",    "ADEME",            COLORS["accent3"]),
            kpi_card("Distance médiane",       f"{moy_dist:.0f} km",    "par mission"),
            kpi_card("Durée médiane trajet",   f"{moy_duree:.0f} min",  "hors attente",     COLORS["accent2"]),
            kpi_card("Chauffeurs actifs",      str(nb_chauffeurs),      ""),
            kpi_card("Engins actifs",          str(nb_engins),          "sur 6 immat.",     COLORS["accent3"]),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "20px"}),
        html.Div([
            html.Div(dcc.Graph(figure=fig_weekly, config={"displayModeBar": False}), style={"flex": "2"}),
            html.Div(dcc.Graph(figure=fig_type,   config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])
