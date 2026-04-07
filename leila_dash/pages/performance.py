# ── Section 02 — Performance des trajets ─────────────────

import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # ── Répartition journée / overnight / multi-jour ──────
    type_counts = df["type_duree"].value_counts().reset_index()
    type_counts.columns = ["type_duree", "count"]
    color_map = {
        "journée":    COLORS["accent3"],
        "overnight":  COLORS["accent2"],
        "multi-jour": COLORS["accent"],
    }
    fig_type = px.pie(
        type_counts, names="type_duree", values="count",
        title="Répartition des missions par type de durée",
        color="type_duree",
        color_discrete_map=color_map,
        hole=0.45,
    )
    fig_type.update_traces(textfont_color=COLORS["text"], textinfo="percent+label")
    fig_type.update_layout(**PLOTLY_THEME, showlegend=False)

    # ── Distribution distances ─────────────────────────────
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

    # ── Scatter distance vs durée (missions journée uniquement) ──
    df_sc = df[
        (df["type_duree"] == "journée") &
        df["duree_trajet_min"].between(0, 600)
    ].copy()
    pct_journee = len(df_sc) / len(df) * 100
    fig_scatter = px.scatter(
        df_sc, x="distance_km", y="duree_trajet_min",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        title=f"Distance vs Durée de trajet — missions journée ({pct_journee:.0f}% du total)",
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

    # ── Boîtes à moustaches temps d'attente ───────────────
    df_att = df[
        (df["type_duree"] == "journée") &
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
        title="Temps d'attente — missions journée (min)",
        **PLOTLY_THEME,
        yaxis=dict(title="Minutes", gridcolor=COLORS["border"]),
    )

    note_overnight = html.Div([
        html.Span("ℹ ", style={"color": COLORS["accent3"]}),
        html.Span(
            "Les missions 'overnight' (chargement la veille, livraison le lendemain matin) "
            "et 'multi-jour' sont exclues des graphiques de durée car leur "
            "duree_totale_min inclut le stationnement nocturne non travaillé.",
            style={"color": COLORS["muted"], "fontSize": "11px",
                   "fontFamily": "'Courier New', monospace"},
        ),
    ], style={
        "background": COLORS["card"], "border": f"1px solid {COLORS['accent3']}33",
        "borderRadius": "6px", "padding": "10px 14px", "marginBottom": "16px",
    })

    return html.Div([
        html.H2("PERFORMANCE DES TRAJETS", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "12px", "fontSize": "14px",
        }),
        note_overnight,
        html.Div([
            html.Div(dcc.Graph(id="g-perf-type",    animate=False, responsive=True, style={"height": "360px", "width": "100%"}, figure=fig_type,    config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(id="g-perf-dist",    animate=False, responsive=True, style={"height": "360px", "width": "100%"}, figure=fig_dist,    config={"displayModeBar": False}), style={"flex": "2"}),
        ], style={"display": "flex", "gap": "16px"}),
        html.Div([
            html.Div(dcc.Graph(id="g-perf-scatter", animate=False, responsive=True, style={"height": "360px", "width": "100%"}, figure=fig_scatter, config={"displayModeBar": False}), style={"flex": "2"}),
            html.Div(dcc.Graph(id="g-perf-box",     animate=False, responsive=True, style={"height": "360px", "width": "100%"}, figure=fig_box,     config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])

