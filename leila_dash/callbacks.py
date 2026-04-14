# ── Callbacks de navigation et filtres ───────────────────

import dash
from dash import Input, Output, State

from dash_app import app
from config import NAV_ITEMS
from data import df, df_carburant, df_form_missions, df_km_anomalies

import pages.overview     as overview
import pages.performance  as performance
import pages.chauffeurs   as chauffeurs
import pages.acteurs      as acteurs
import pages.marchandises as marchandises
import pages.co2          as co2
import pages.economie     as economie
import pages.geo          as geo
import pages.experimental as experimental

SECTIONS = {
    "overview":     lambda d: overview.layout(d, df_form_missions, df_km_anomalies),
    "performance":  performance.layout,
    "chauffeurs":   chauffeurs.layout,
    "acteurs":      acteurs.layout,
    "marchandises": marchandises.layout,
    "co2":          co2.layout,
    "economie":     lambda d: economie.layout(d, df_carburant),
    "geo":          geo.layout,
    "experimental": experimental.layout,
}


# ── Callback 1 : boutons nav → store page active ──────────
@app.callback(
    Output("active-page", "data"),
    [Input(f"nav-{key}", "n_clicks") for key, _ in NAV_ITEMS],
    prevent_initial_call=True,
)
def update_active_page(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "overview"
    key = ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-", "")
    return key if key in SECTIONS else "overview"


# ── Callback 2 : store → classes CSS des onglets ─────────
@app.callback(
    [Output(f"nav-{key}", "className") for key, _ in NAV_ITEMS],
    Input("active-page", "data"),
)
def update_nav_classes(active_key):
    return [
        "top-nav-btn active" if key == active_key else "top-nav-btn"
        for key, _ in NAV_ITEMS
    ]


# ── Callback 3 : store + filtres → contenu de la page ────
@app.callback(
    Output("page-content", "children"),
    Input("active-page", "data"),
    Input("filter-day-range", "value"),
    Input("filter-month", "value"),
    prevent_initial_call=True,
)
def render_page(active_key, day_range, selected_month):
    filtered = df.copy()

    if selected_month and selected_month != "tout":
        filtered = filtered[filtered["mois"] == selected_month]

    if day_range and len(day_range) == 2:
        d_min, d_max = day_range
        filtered = filtered[
            (filtered["mission_debut"].dt.day >= d_min) &
            (filtered["mission_debut"].dt.day <= d_max)
        ]

    if not active_key or active_key not in SECTIONS:
        active_key = "overview"

    return SECTIONS[active_key](filtered)
