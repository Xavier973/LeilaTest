# ── Section 07 — Géographie ───────────────────────────────

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    df_geo = df[
        df["lat_retrait"].notna() & df["lon_retrait"].notna() &
        df["lat_livraison"].notna() & df["lon_livraison"].notna()
    ].copy()

    # Filtrer hors zone Guyane
    df_geo = df_geo[
        df_geo["lat_retrait"].between(1, 8)    & df_geo["lon_retrait"].between(-56, -50) &
        df_geo["lat_livraison"].between(1, 8)  & df_geo["lon_livraison"].between(-56, -50)
    ]

    fig_map = go.Figure()
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

    fig_map.update_layout(**PLOTLY_THEME)
    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=df_geo["lat_retrait"].mean(), lon=df_geo["lon_retrait"].mean()),
            zoom=8,
        ),
        height=550,
        margin=dict(l=0, r=0, t=40, b=0),
        title="Carte des trajets — points GPS retrait & livraison",
        legend=dict(orientation="h", y=0.01, bgcolor="rgba(0,0,0,0.5)"),
    )

    # Carte de densité
    all_pts = pd.concat([
        df_geo[["lat_retrait", "lon_retrait"]].rename(
            columns={"lat_retrait": "lat", "lon_retrait": "lon"}),
        df_geo[["lat_livraison", "lon_livraison"]].rename(
            columns={"lat_livraison": "lat", "lon_livraison": "lon"}),
    ])
    fig_density = px.density_mapbox(
        all_pts, lat="lat", lon="lon", radius=12,
        title="Zones de forte activité",
        color_continuous_scale=[
            [0, "rgba(0,0,0,0)"],
            [0.3, "rgba(245,166,35,0.60)"],
            [1, COLORS["accent"]],
        ],
        mapbox_style="carto-darkmatter",
        center=dict(lat=all_pts["lat"].mean(), lon=all_pts["lon"].mean()),
        zoom=8, height=450,
    )
    fig_density.update_layout(**PLOTLY_THEME)
    fig_density.update_layout(margin=dict(l=0, r=0, t=40, b=0))

    return html.Div([
        html.H2("ANALYSE GÉOGRAPHIQUE", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        dcc.Graph(animate=False, responsive=True, style={"height": "360px"}, figure=fig_map,     config={"displayModeBar": True, "scrollZoom": True}),
        dcc.Graph(animate=False, responsive=True, style={"height": "360px"}, figure=fig_density, config={"displayModeBar": True, "scrollZoom": True}),
    ])
