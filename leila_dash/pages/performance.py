# ── Section 02 — Performance des trajets ─────────────────

import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # Distribution distances
    fig_dist = px.histogram(
        df, x="distance_km", nbins=40,
        title="Distribution des distances (km)",
        color_discrete_sequence=[COLORS["accent"]],
        labels={"distance_km": "Distance (km)", "count": "Nb missions"},
    )
    fig_dist.add_vline(
        x=df["distance_km"].median(), line_dash="dash",
        line_color=COLORS["accent2"],
        annotation_text=f"Médiane {df['distance_km'].median():.0f} km",
        annotation_font_color=COLORS["accent2"],
    )
    fig_dist.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # Scatter distance vs durée trajet
    df_sc = df[df["duree_trajet_min"].between(0, 600)].copy()
    fig_scatter = px.scatter(
        df_sc, x="distance_km", y="duree_trajet_min",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        title="Distance vs Durée de trajet",
        labels={
            "distance_km": "Distance (km)",
            "duree_trajet_min": "Durée trajet (min)",
            "engin_immatriculation": "Engin",
        },
        hover_data=["chauffeur", "remettant", "destinataire"],
        opacity=0.7,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=COLORS["accent2"],
    )
    fig_scatter.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # Boîtes à moustaches temps d'attente
    df_att = df[
        df["attente_chargement_min"].between(0, 240) &
        df["attente_dechargement_min"].between(0, 240)
    ].copy()
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
        html.H2("PERFORMANCE DES TRAJETS", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        html.Div([
            html.Div(dcc.Graph(figure=fig_dist, config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_box,  config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
    ])
