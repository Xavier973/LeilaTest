# ── Section 01 — Vue d'ensemble ───────────────────────────

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import dcc, html, dash_table

from config import COLORS, PLOTLY_THEME
from components import kpi_card


def layout(df, df_form_missions, df_km_anomalies):
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
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis=dict(title="Semaine", gridcolor=COLORS["border"]),
        yaxis=dict(title="Nb missions", gridcolor=COLORS["border"]),
        yaxis2=dict(title="Km total", gridcolor=COLORS["border"]),
    )
    fig_weekly.update_layout(margin=dict(l=40, r=20, t=40, b=80))

    # Répartition par type de formulaire : priorité à la table brute, fallback v_missions.
    if (
        df_form_missions is not None
        and not df_form_missions.empty
        and {"mission", "count"}.issubset(set(df_form_missions.columns))
    ):
        pie_data = df_form_missions.copy()
    else:
        pie_data = (
            df.groupby("type_mission")
            .size()
            .reset_index(name="count")
            .rename(columns={"type_mission": "mission"})
        )

    fig_form = px.pie(
        pie_data,
        values="count",
        names="mission",
        title="Répartition par type de formulaire",
        color_discrete_sequence=[COLORS["accent"], COLORS["accent2"], COLORS["accent3"]],
        hole=0.55,
    )
    fig_form.update_layout(**PLOTLY_THEME)
    fig_form.update_traces(textfont_color=COLORS["text"])

    # ── Anomalies kilométrage (toutes causes, tables brutes) ────
    nb_anomalies = len(df_km_anomalies)
    alert_color  = COLORS["danger"] if nb_anomalies > 0 else COLORS["success"]
    alert_label  = f"⚠ {nb_anomalies}" if nb_anomalies > 0 else "✓ 0"

    anomaly_section = html.Div([
        html.H3("ALERTES KILOMÉTRAGE — ENREGISTREMENTS ABERRANTS", style={
            "color": alert_color, "fontFamily": "'Courier New', monospace",
            "letterSpacing": "2px", "fontSize": "12px", "marginBottom": "8px",
        }),
        html.P(
            f"{nb_anomalies} enregistrement(s) suspect(s) détecté(s) dans les tables brutes "
            "(inclut les entrées exclues de v_missions : distance hors 1–300 km, GPS identiques, vitesse > 130 km/h).",
            style={"color": COLORS["text"], "fontSize": "12px", "marginBottom": "10px"},
        ),
        dash_table.DataTable(
            data=df_km_anomalies.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df_km_anomalies.columns],
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": COLORS["card"],
                "color": alert_color,
                "fontWeight": "bold",
                "fontFamily": "'Courier New', monospace",
                "fontSize": "11px",
                "borderBottom": f"1px solid {alert_color}",
            },
            style_cell={
                "backgroundColor": COLORS["bg"],
                "color": COLORS["text"],
                "fontFamily": "'Courier New', monospace",
                "fontSize": "11px",
                "border": f"1px solid {COLORS['border']}",
                "padding": "6px 10px",
                "whiteSpace": "normal",
                "maxWidth": "300px",
            },
            style_data_conditional=[{
                "if": {"column_id": "Anomalie"},
                "color": alert_color,
                "fontWeight": "bold",
            }],
            sort_action="native",
            filter_action="native",
            page_size=10,
        ) if nb_anomalies > 0 else html.P(
            "✓ Aucune anomalie kilométrique détectée.",
            style={"color": COLORS["success"], "fontStyle": "italic", "fontSize": "12px"},
        ),
    ], style={
        "backgroundColor": COLORS["card"],
        "border": f"1px solid {alert_color}",
        "borderRadius": "6px",
        "padding": "16px",
        "marginTop": "20px",
    })

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
            kpi_card("Alertes km",             alert_label,             "anomalies brutes", alert_color),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "20px"}),
        html.Div([
            html.Div(dcc.Graph(animate=False, responsive=True, style={"height": "360px"},figure=fig_weekly, config={"displayModeBar": False}), style={"flex": "2"}),
            html.Div(dcc.Graph(animate=False, responsive=True, style={"height": "360px"},figure=fig_form,   config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        anomaly_section,
    ])
