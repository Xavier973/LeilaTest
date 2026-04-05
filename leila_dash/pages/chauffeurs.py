# ── Section 03 — Chauffeurs & Engins ─────────────────────

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
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

    fig_eng = px.bar(
        eng, x="engin_immatriculation", y="missions",
        title="Missions par engin",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        labels={"engin_immatriculation": "Engin", "missions": "Nb missions"},
        text="missions",
    )
    fig_eng.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_eng.update_layout(
        **PLOTLY_THEME, showlegend=False,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # Heatmap semaine × engin
    wk_eng = df.groupby(["semaine", "engin_immatriculation"]).size().reset_index(name="missions")
    fig_heatmap = px.density_heatmap(
        wk_eng, x="semaine", y="engin_immatriculation", z="missions",
        title="Intensité d'utilisation par engin et semaine",
        color_continuous_scale=[
            [0, COLORS["card"]],
            [0.3, "rgba(232,69,69,0.53)"],
            [1, COLORS["accent"]],
        ],
        labels={"semaine": "Semaine", "engin_immatriculation": "Engin", "missions": "Missions"},
    )
    fig_heatmap.update_layout(**PLOTLY_THEME)

    return html.Div([
        html.H2("CHAUFFEURS & ENGINS", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        html.Div([
            html.Div(dcc.Graph(figure=fig_ch,  config={"displayModeBar": False}), style={"flex": "2"}),
            html.Div(dcc.Graph(figure=fig_eng, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_heatmap, config={"displayModeBar": False}),
    ])
