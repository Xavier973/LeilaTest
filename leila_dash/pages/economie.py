# ── Section 08 — Impact économique ───────────────────────

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from config import COLORS, PLOTLY_THEME

PRIX_GASOIL_EUR = 1.60   # €/L — prix public Guyane (source : prix-carburants.gouv.fr)
COUT_HORAIRE_EUR = 55.0  # €/h — coût complet poids lourd chauffeur+amortissement (barème CNR)


def _kpi(label, value, unit="", color=None):
    return html.Div([
        html.Div(label, style={
            "color": COLORS["muted"], "fontSize": "10px",
            "fontFamily": "'Courier New', monospace", "letterSpacing": "1px",
            "marginBottom": "4px",
        }),
        html.Div([
            html.Span(value, style={
                "color": color or COLORS["accent2"], "fontSize": "26px",
                "fontWeight": "700", "fontFamily": "'Courier New', monospace",
            }),
            html.Span(f" {unit}", style={"color": COLORS["muted"], "fontSize": "12px"}),
        ]),
    ], style={
        "background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
        "borderRadius": "6px", "padding": "16px 20px", "flex": "1",
    })


def layout(df: pd.DataFrame, df_carburant: pd.DataFrame = None):
    carburant_reel_disponible = df_carburant is not None and not df_carburant.empty

    # ── Agrégation km missions par engin ──────────────────
    km_engin = (
        df.groupby("engin_immatriculation")
        .agg(km_missions=("distance_km", "sum"), nb_missions=("mission_id", "count"))
        .reset_index()
    )

    # ── Fusion carburant × km ──────────────────────────────
    if carburant_reel_disponible:
        merged = df_carburant.merge(km_engin, on="engin_immatriculation", how="left")
        # km estimés total = km missions × 2 (trajets à vide inclus)
        merged["km_total_estime"] = merged["km_missions"] * 2
        merged["cout_carburant_eur"] = merged["total_litres"] * PRIX_GASOIL_EUR
        merged["l_pour_100km"] = (
            merged["total_litres"] / merged["km_total_estime"].replace(0, pd.NA) * 100
        ).round(1)
        merged["cout_par_km_eur"] = (
            merged["cout_carburant_eur"] / merged["km_total_estime"].replace(0, pd.NA)
        ).round(3)
    else:
        # Fallback : conso moyenne par type d'engin (L/100 km) pour garder des indicateurs exploitables.
        conso_par_type = {"Porteur 8x4": 45.0, "Tracteur 6x4": 42.0, "Tracteur 4x2": 35.0}
        engin_types = (
            df[["engin_immatriculation", "engin_type"]]
            .drop_duplicates(subset=["engin_immatriculation"])
        )
        merged = km_engin.merge(engin_types, on="engin_immatriculation", how="left")
        merged["l_pour_100km"] = merged["engin_type"].map(conso_par_type).fillna(40.0)
        merged["km_total_estime"] = merged["km_missions"] * 2
        merged["total_litres"] = (merged["km_total_estime"] * merged["l_pour_100km"] / 100).round(1)
        merged["cout_carburant_eur"] = (merged["total_litres"] * PRIX_GASOIL_EUR).round(1)
        merged["cout_par_km_eur"] = (
            merged["cout_carburant_eur"] / merged["km_total_estime"].replace(0, pd.NA)
        ).round(3)

    # ── Coût par mission — missions journée uniquement ────────
    df_cout = df[df["type_duree"] == "journée"].copy()
    nb_exclus = len(df) - len(df_cout)
    df_cout["cout_carburant_estime"] = df_cout.apply(
        lambda r: (
            r["distance_km"]
            * merged.loc[
                merged["engin_immatriculation"] == r["engin_immatriculation"],
                "l_pour_100km",
            ].values[0]
            / 100
            * PRIX_GASOIL_EUR
            if r["engin_immatriculation"] in merged["engin_immatriculation"].values
            and pd.notna(
                merged.loc[
                    merged["engin_immatriculation"] == r["engin_immatriculation"],
                    "l_pour_100km",
                ].values[0]
            )
            else 0
        ),
        axis=1,
    )
    df_cout["cout_horaire_estime"] = df_cout["duree_totale_min"].clip(lower=0) / 60 * COUT_HORAIRE_EUR
    df_cout["cout_total_estime"] = df_cout["cout_carburant_estime"] + df_cout["cout_horaire_estime"]

    # ── KPIs globaux ──────────────────────────────────────
    total_carburant = merged["cout_carburant_eur"].sum()
    total_cout = df_cout["cout_total_estime"].sum()
    km_total = merged["km_total_estime"].sum()
    cout_km_moy = total_cout / km_total if km_total > 0 else 0
    l100_moy = merged["l_pour_100km"].mean()

    # ── Fig 1 : Coût carburant par engin ──────────────────
    merged_sorted = merged.sort_values("cout_carburant_eur", ascending=False)
    fig_cout_eng = px.bar(
        merged_sorted,
        x="engin_immatriculation", y="cout_carburant_eur",
        title="Coût carburant estimé par engin (€)",
        color="engin_immatriculation",
        color_discrete_map=COLORS["engins"],
        labels={"engin_immatriculation": "Engin", "cout_carburant_eur": "Coût (€)"},
        text=merged_sorted["cout_carburant_eur"].round(0).astype(int),
    )
    fig_cout_eng.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_cout_eng.update_layout(
        **PLOTLY_THEME, showlegend=False,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # ── Fig 2 : L/100km par engin avec benchmark ──────────
    benchmarks = {"Porteur 8x4": 45, "Tracteur 6x4": 42, "Tracteur 4x2": 35}
    merged["benchmark_l100"] = merged["engin_type"].map(benchmarks)

    fig_conso = go.Figure()
    for _, row in merged.iterrows():
        color = COLORS["engins"].get(row["engin_immatriculation"], COLORS["accent2"])
        fig_conso.add_trace(go.Bar(
            x=[row["engin_immatriculation"]],
            y=[row["l_pour_100km"]],
            name=row["engin_immatriculation"],
            marker_color=color,
            text=[f"{row['l_pour_100km']} L" if pd.notna(row["l_pour_100km"]) else "N/A"],
            textposition="outside",
        ))
    # Ligne benchmark par type
    for _, row in merged.iterrows():
        if pd.notna(row.get("benchmark_l100")):
            fig_conso.add_shape(
                type="line",
                x0=row["engin_immatriculation"], x1=row["engin_immatriculation"],
                y0=0, y1=row["benchmark_l100"],
                line=dict(color=COLORS["accent"], dash="dot", width=2),
            )
    fig_conso.update_layout(
        **PLOTLY_THEME,
        title="Consommation L/100km estimée (trajets à vide inclus) — ligne pointillée = benchmark type",
        showlegend=False,
        xaxis=dict(title="Engin", gridcolor=COLORS["border"]),
        yaxis=dict(title="L/100km", gridcolor=COLORS["border"]),
        barmode="group",
    )

    # ── Fig 3 : Scatter distance vs durée par chauffeur ───
    df_scatter = df_cout[df_cout["duree_totale_min"].between(0, 600)].copy()
    fig_scatter = px.scatter(
        df_scatter,
        x="distance_km", y="duree_totale_min",
        color="chauffeur",
        size="cout_total_estime",
        hover_data=["engin_immatriculation", "cout_total_estime", "poids_net_total_t"],
        title="Distance vs Durée par chauffeur — taille = coût estimé (€)",
        labels={
            "distance_km": "Distance (km)",
            "duree_totale_min": "Durée totale (min)",
            "chauffeur": "Chauffeur",
        },
        opacity=0.75,
    )
    fig_scatter.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    # ── Fig 4 : Coût total + coût/mission par chauffeur ──────
    cout_ch = (
        df_cout.groupby("chauffeur")
        .agg(
            cout_total=("cout_total_estime", "sum"),
            cout_carb=("cout_carburant_estime", "sum"),
            cout_heure=("cout_horaire_estime", "sum"),
            nb_missions=("mission_id", "count"),
        )
        .reset_index()
    )
    cout_ch["cout_par_mission"] = (cout_ch["cout_total"] / cout_ch["nb_missions"]).round(0)
    cout_ch_sorted = cout_ch.sort_values("cout_total", ascending=True)

    fig_cout_ch = go.Figure()
    fig_cout_ch.add_trace(go.Bar(
        y=cout_ch_sorted["chauffeur"], x=cout_ch_sorted["cout_carb"],
        name="Carburant", orientation="h",
        marker_color=COLORS["accent2"],
    ))
    fig_cout_ch.add_trace(go.Bar(
        y=cout_ch_sorted["chauffeur"], x=cout_ch_sorted["cout_heure"],
        name="Horaire (CNR)", orientation="h",
        marker_color=COLORS["accent3"],
    ))
    fig_cout_ch.update_layout(
        **PLOTLY_THEME,
        title="Coût total estimé par chauffeur (€) — carburant + horaire",
        barmode="stack",
        xaxis=dict(title="€", gridcolor=COLORS["border"]),
        yaxis=dict(title=""),
    )

    # Coût moyen par mission (comparaison équitable)
    cout_ch_mission = cout_ch.sort_values("cout_par_mission", ascending=True)
    fig_cout_mission = px.bar(
        cout_ch_mission,
        x="cout_par_mission", y="chauffeur", orientation="h",
        title="Coût moyen par mission (€) — comparaison équitable",
        color="cout_par_mission",
        color_continuous_scale=[
            [0, COLORS["accent3"]], [0.5, COLORS["accent2"]], [1, COLORS["accent"]],
        ],
        text=cout_ch_mission["cout_par_mission"].apply(lambda x: f"{x:.0f} €"),
        labels={"cout_par_mission": "€/mission", "chauffeur": ""},
        hover_data={"nb_missions": True, "cout_total": True},
    )
    fig_cout_mission.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_cout_mission.update_layout(
        **PLOTLY_THEME, coloraxis_showscale=False,
        xaxis=dict(title="€ / mission", gridcolor=COLORS["border"]),
    )

    source_carburant = (
        "litres réels (MouvementStock)"
        if carburant_reel_disponible
        else "estimation par type d'engin (aucun relevé carburant disponible)"
    )

    # ── Note méthodologique ───────────────────────────────
    note = html.Div([
        html.Span("⚠ ESTIMATIONS — ", style={"color": COLORS["accent2"], "fontWeight": "700"}),
        html.Span(
            f"Carburant : {source_carburant} × {PRIX_GASOIL_EUR} €/L (prix Guyane, source prix-carburants.gouv.fr). "
            f"Km totaux : km missions × 2 (trajets à vide estimés). "
            f"Coût horaire : {COUT_HORAIRE_EUR} €/h (barème CNR poids lourds). "
            f"Missions overnight et multi-jour exclues ({nb_exclus} missions) — durée non fiable (stationnement nocturne inclus). "
            "Les coûts de maintenance, pneumatiques et assurances ne sont pas inclus.",
            style={"color": COLORS["muted"], "fontSize": "11px",
                   "fontFamily": "'Courier New', monospace"},
        ),
    ], style={
        "background": COLORS["card"], "border": f"1px solid {COLORS['accent2']}33",
        "borderRadius": "6px", "padding": "12px 16px", "marginBottom": "20px",
    })

    return html.Div([
        html.H2("IMPACT ÉCONOMIQUE", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "12px", "fontSize": "14px",
        }),
        note,

        # KPIs
        html.Div([
            _kpi("COÛT CARBURANT TOTAL", f"{total_carburant:,.0f}", "€"),
            _kpi("COÛT TOTAL ESTIMÉ", f"{total_cout:,.0f}", "€", COLORS["accent"]),
            _kpi("COÛT / KM MOYEN", f"{cout_km_moy:.2f}", "€/km"),
            _kpi("CONSO. MOYENNE", f"{l100_moy:.1f}" if pd.notna(l100_moy) else "N/A", "L/100km"),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "20px"}),

        # Graphiques ligne 1
        html.Div([
            html.Div(dcc.Graph(figure=fig_cout_eng, config={"displayModeBar": False}),
                     style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_conso, config={"displayModeBar": False}),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # Graphiques ligne 2
        html.Div([
            html.Div(dcc.Graph(figure=fig_cout_ch,      config={"displayModeBar": False}),
                     style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_cout_mission, config={"displayModeBar": False}),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # Graphique ligne 3
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
    ])
