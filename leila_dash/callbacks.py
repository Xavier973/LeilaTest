# ── Callbacks de navigation ───────────────────────────────

import dash
from dash import Input, Output

from dash_app import app
from config import NAV_ITEMS
from data import df, df_carburant

import pages.overview     as overview
import pages.performance  as performance
import pages.chauffeurs   as chauffeurs
import pages.acteurs      as acteurs
import pages.marchandises as marchandises
import pages.co2          as co2
import pages.economie     as economie
import pages.geo          as geo

SECTIONS = {
    "overview":     overview.layout,
    "performance":  performance.layout,
    "chauffeurs":   chauffeurs.layout,
    "acteurs":      acteurs.layout,
    "marchandises": marchandises.layout,
    "co2":          co2.layout,
    "economie":     lambda df: economie.layout(df, df_carburant),
    "geo":          geo.layout,
}


@app.callback(
    Output("page-content", "children"),
    [Input(f"nav-{key}", "n_clicks") for key, _ in NAV_ITEMS],
    prevent_initial_call=False,
)
def render_page(*args):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == 0:
        return SECTIONS["overview"](df)

    key = ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-", "")
    return SECTIONS.get(key, SECTIONS["overview"])(df)
