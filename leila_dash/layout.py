# ── Layout principal ──────────────────────────────────────

from datetime import datetime

from dash import html, dcc
from dash_app import app
from config import COLORS, NAV_ITEMS
from data import df, df_form_missions, df_km_anomalies
import pages.overview as overview

_MOIS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
}


def _mois_label(s):
    """Convertit '2026-01' → 'Janvier 2026'."""
    year, month = s.split("-")
    return f"{_MOIS_FR[int(month)]} {year}"


_mois_options = (
    [{"label": "Tout", "value": "tout"}]
    + [
        {"label": _mois_label(m), "value": m}
        for m in sorted(df["mois"].unique())
    ]
)


def _nav_button(key, label):
    cls = "top-nav-btn active" if key == "overview" else "top-nav-btn"
    return html.Button(label, id=f"nav-{key}", n_clicks=0, className=cls)


def _last_refresh_label():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


app.layout = html.Div([
    dcc.Store(id="active-page", data="overview"),

    html.Div([
        html.Div([
            html.Img(
                src="/assets/Logo-Leila.webp",
                className="brand-logo",
                style={"height": "56px", "width": "auto", "display": "block"},
            ),
            html.Div([
                html.Div(
                    "Connaître - Rapports - Usine - Global",
                    className="report-title",
                    style={"color": "#FFFFFF"},
                ),
                html.Div(
                    "Vue de pilotage industriel",
                    className="report-subtitle",
                    style={"color": "#D8D4F1"},
                ),
            ]),
        ], className="brand-block"),
        html.Div([
            html.Div(
                "Derniere actualisation (UTC-3)",
                className="update-label",
                style={"color": "#D8D4F1"},
            ),
            html.Div(_last_refresh_label(), className="update-time", style={"color": "#FFFFFF"}),
        ], className="update-block"),
    ], className="app-header", style={"background": "#120449"}),

    html.Div([_nav_button(key, label) for key, label in NAV_ITEMS], className="tabs-row"),

    html.Div([
        html.Div([
            html.Div([
                html.Div("Entre le", className="filter-title"),
                dcc.RangeSlider(
                    id="filter-day-range",
                    min=1,
                    max=31,
                    value=[1, 31],
                    allowCross=False,
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ], className="filter-card"),
            html.Div([
                html.Div("Mois", className="filter-title"),
                dcc.Dropdown(
                    id="filter-month",
                    options=_mois_options,
                    value="tout",
                    clearable=False,
                    searchable=False,
                ),
            ], className="filter-card"),
            html.Div([
                html.Div("Mode", className="filter-title"),
                html.Div([
                    html.Button("Arret", className="mode-btn"),
                    html.Button("Degrade", className="mode-btn"),
                ], className="mode-btn-row"),
            ], className="filter-card"),
            html.Div([
                html.Div("Source", className="filter-title"),
                html.Div(f"{len(df)} missions validees", className="source-line"),
                html.Div("MariaDB - snfAnonymise", className="source-line muted"),
                html.Div("Vue : v_missions", className="source-line muted"),
            ], className="filter-card"),
        ], className="left-panel"),

        html.Div(
            id="page-content",
            className="content-panel",
            children=overview.layout(df, df_form_missions, df_km_anomalies),
        ),
    ], className="dashboard-shell"),
], className="app-root")
