# ── Layout principal ──────────────────────────────────────

from dash import html, dcc
from dash_app import app
from config import COLORS, NAV_ITEMS
from data import df


def _nav_button(key, label):
    return html.Div(
        html.Button(
            label,
            id=f"nav-{key}",
            n_clicks=0,
            style={
                "display": "block", "width": "100%", "textAlign": "left",
                "background": "none", "border": "none",
                "borderLeft": f"2px solid {COLORS['border']}",
                "padding": "10px 16px",
                "color": COLORS["muted"],
                "fontFamily": "'Courier New', monospace",
                "fontSize": "11px", "letterSpacing": "1px",
                "cursor": "pointer",
            },
        )
    )


app.layout = html.Div([
    # ── En-tête ──────────────────────────────────────────
    html.Div([
        html.Div([
            html.Img(src="/assets/Logo-Leila.webp", style={"height": "32px", "verticalAlign": "middle"}),
            html.Span(" · TEST de mise en condition", style={
                "color": COLORS["muted"], "fontSize": "13px",
                "fontFamily": "'Courier New', monospace", "letterSpacing": "3px",
                "verticalAlign": "middle", "marginLeft": "8px",
            }),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div("Plateau des Guyanes · Jan–Mars 2026", style={
            "color": COLORS["muted"], "fontSize": "11px",
            "fontFamily": "'Courier New', monospace",
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "padding": "14px 28px",
        "borderBottom": f"1px solid {COLORS['border']}",
        "background": COLORS["card"],
        "position": "sticky", "top": "0", "zIndex": "100",
    }),

    # ── Corps principal ───────────────────────────────────
    html.Div([
        # Navigation latérale
        html.Div(
            [_nav_button(key, label) for key, label in NAV_ITEMS] + [
                html.Div(style={"height": "1px", "background": COLORS["border"], "margin": "16px 0"}),
                html.Div([
                    html.Div("SOURCE", style={
                        "color": COLORS["muted"], "fontSize": "9px",
                        "fontFamily": "'Courier New', monospace",
                        "letterSpacing": "2px", "marginBottom": "6px",
                    }),
                    html.Div(f"{len(df)} missions validées", style={
                        "color": COLORS["text"], "fontSize": "11px",
                        "fontFamily": "'Courier New', monospace",
                    }),
                    html.Div("MariaDB · snfAnonymise", style={
                        "color": COLORS["muted"], "fontSize": "10px",
                        "fontFamily": "'Courier New', monospace",
                    }),
                    html.Div("Vue : v_missions", style={
                        "color": COLORS["muted"], "fontSize": "10px",
                        "fontFamily": "'Courier New', monospace",
                    }),
                ], style={"padding": "0 16px"}),
            ],
            style={
                "width": "180px", "minWidth": "180px",
                "padding": "24px 0",
                "borderRight": f"1px solid {COLORS['border']}",
                "position": "sticky", "top": "53px",
                "height": "calc(100vh - 53px)",
                "overflowY": "auto",
            },
        ),

        # Contenu dynamique
        html.Div(id="page-content", style={"flex": "1", "padding": "28px", "overflowY": "auto"}),
    ], style={"display": "flex", "minHeight": "calc(100vh - 53px)"}),

], style={"background": COLORS["bg"], "minHeight": "100vh", "color": COLORS["text"]})
