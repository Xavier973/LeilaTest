# ── Section 08 — Expérimental ─────────────────────────────
# Carte géographique filtrée :
#   - type_duree = 'journée'
#   - type_mission = 'Transport marchandises'
#   - engin_immatriculation ≠ 'CR-426-DD'

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # Filtres spécifiques à cette vue
    df_exp = df[
        (df["type_duree"] == "journée") &
        (df["type_mission"] == "Transport marchandises") &
        (df["engin_immatriculation"] != "CR-426-DD")
    ].copy()

    # Filtrer les coordonnées manquantes
    df_geo = df_exp[
        df_exp["lat_retrait"].notna() & df_exp["lon_retrait"].notna() &
        df_exp["lat_livraison"].notna() & df_exp["lon_livraison"].notna()
    ].copy()

    # Filtrer hors zone Guyane
    df_geo = df_geo[
        df_geo["lat_retrait"].between(1, 8)    & df_geo["lon_retrait"].between(-56, -50) &
        df_geo["lat_livraison"].between(1, 8)  & df_geo["lon_livraison"].between(-56, -50)
    ]

    n_missions = len(df_exp)
    n_geo = len(df_geo)

    fig_map = go.Figure()

    if n_geo > 0:
        fig_map.add_trace(go.Scattermapbox(
            lat=df_geo["lat_retrait"], lon=df_geo["lon_retrait"],
            mode="markers",
            marker=dict(size=7, color=COLORS["accent"], opacity=0.7),
            name="Retrait",
            hovertext=df_geo["remettant"],
            hovertemplate="<b>Retrait</b><br>%{hovertext}<br>%{lat:.4f}°N, %{lon:.4f}°E<extra></extra>",
        ))
        fig_map.add_trace(go.Scattermapbox(
            lat=df_geo["lat_livraison"], lon=df_geo["lon_livraison"],
            mode="markers",
            marker=dict(size=7, color=COLORS["accent3"], opacity=0.7),
            name="Livraison",
            hovertext=df_geo["destinataire"],
            hovertemplate="<b>Livraison</b><br>%{hovertext}<br>%{lat:.4f}°N, %{lon:.4f}°E<extra></extra>",
        ))

        # Lignes de trajet (échantillon 80 pour lisibilité)
        sample = df_geo.sample(min(80, len(df_geo)), random_state=42)
        lats, lons = [], []
        for _, row in sample.iterrows():
            lats += [row["lat_retrait"], row["lat_livraison"], None]
            lons += [row["lon_retrait"], row["lon_livraison"], None]

        fig_map.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="lines",
            line=dict(width=1, color=COLORS["accent2"]),
            opacity=0.3,
            name="Trajets (échantillon 80)",
            hoverinfo="skip",
        ))

        center_lat = df_geo["lat_retrait"].mean()
        center_lon = df_geo["lon_retrait"].mean()
    else:
        center_lat, center_lon = 4.5, -53.0

    fig_map.update_layout(**PLOTLY_THEME)
    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=8,
        ),
        height=800,
        margin=dict(l=0, r=0, t=40, b=0),
        title="Carte des trajets — Transport marchandises · journée · hors CR-426-DD",
        legend=dict(orientation="h", y=0.01, bgcolor="rgba(0,0,0,0.5)"),
    )

    return html.Div([
        html.H2("EXPÉRIMENTAL — TRANSPORT MARCHANDISES (JOURNÉE)", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "8px", "fontSize": "14px",
        }),
        html.Div([
            html.Span(f"{n_missions} missions filtrées", style={"color": COLORS["muted"], "fontSize": "12px", "marginRight": "16px"}),
            html.Span(f"{n_geo} avec coordonnées GPS", style={"color": COLORS["muted"], "fontSize": "12px"}),
        ], style={"marginBottom": "16px"}),
        dcc.Graph(
            id="g-exp-map",
            animate=False,
            responsive=True,
            style={"height": "80vh", "width": "100%"},
            figure=fig_map,
            config={"displayModeBar": True, "scrollZoom": True},
        ),
    ])
