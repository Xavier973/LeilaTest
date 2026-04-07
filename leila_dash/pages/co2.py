# ── Section 06 — Impact CO₂ ───────────────────────────────

import plotly.express as px
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # CO₂ par engin
    co2_eng = df.groupby("engin_immatriculation").agg(
        co2_total=("co2_kg", "sum"),
        missions=("mission_id", "count"),
        km=("distance_km", "sum"),
    ).reset_index()
    co2_eng["co2_par_mission"] = co2_eng["co2_total"] / co2_eng["missions"]
    co2_eng["co2_par_km"]      = co2_eng["co2_total"] / co2_eng["km"]

    co2_eng_sorted = co2_eng.sort_values("co2_total", ascending=False)
    fig_co2_eng = px.bar(
        co2_eng_sorted,
        x="engin_immatriculation", y="co2_total",
        title="CO₂ estimé total par engin (kg) — facteurs ADEME",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        labels={"engin_immatriculation": "Engin", "co2_total": "CO₂ total (kg)"},
        text=co2_eng_sorted["co2_total"].round(0).astype(int),
    )
    fig_co2_eng.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_co2_eng.update_layout(
        **PLOTLY_THEME, showlegend=False,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # CO₂ par chauffeur
    co2_ch = df.groupby("chauffeur").agg(
        co2_total=("co2_kg", "sum"),
        missions=("mission_id", "count"),
    ).reset_index().sort_values("co2_total", ascending=True)

    fig_co2_ch = px.bar(
        co2_ch, x="co2_total", y="chauffeur",
        orientation="h", title="CO₂ estimé par chauffeur (kg)",
        color="co2_total",
        color_continuous_scale=[
            [0, COLORS["accent3"]], [0.5, COLORS["accent2"]], [1, COLORS["accent"]],
        ],
        labels={"co2_total": "CO₂ (kg)", "chauffeur": ""},
    )
    fig_co2_ch.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                              xaxis=dict(gridcolor=COLORS["border"]))

    # Évolution hebdomadaire CO₂
    co2_wk = df.groupby("semaine")["co2_kg"].sum().reset_index()
    fig_co2_trend = px.area(
        co2_wk, x="semaine", y="co2_kg",
        title="Évolution hebdomadaire des émissions CO₂ estimées (kg)",
        labels={"semaine": "Semaine", "co2_kg": "CO₂ (kg)"},
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig_co2_trend.update_traces(fillcolor="rgba(232,69,69,0.20)", line_color=COLORS["accent"])
    fig_co2_trend.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    note = html.Div([
        html.Span("⚠ ", style={"color": COLORS["accent2"]}),
        html.Span(
            "Estimation indicative basée sur les facteurs ADEME : "
            "Porteur 8x4 → 0,90 kg/km · Tracteur 6x4 → 0,75 kg/km · Tracteur 4x2 → 0,65 kg/km. "
            "Aucune donnée carburant disponible dans ce dump.",
            style={"color": COLORS["muted"], "fontSize": "11px",
                   "fontFamily": "'Courier New', monospace"},
        ),
    ], style={"marginBottom": "16px"})

    return html.Div([
        html.H2("IMPACT ENVIRONNEMENTAL", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "12px", "fontSize": "14px",
        }),
        note,
        html.Div([
            html.Div(dcc.Graph(animate=False, responsive=False, style={"height": "360px", "width": "100%"}, figure=fig_co2_eng, config={"displayModeBar": False, "responsive": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(animate=False, responsive=False, style={"height": "360px", "width": "100%"}, figure=fig_co2_ch,  config={"displayModeBar": False, "responsive": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(animate=False, responsive=False, style={"height": "360px", "width": "100%"}, figure=fig_co2_trend, config={"displayModeBar": False, "responsive": False}),
    ])
