# ── Composants HTML réutilisables ─────────────────────────

from dash import html
from config import COLORS


def card(children, style=None):
    s = {
        "background":    COLORS["card"],
        "border":        f"1px solid {COLORS['border']}",
        "borderRadius":  "8px",
        "padding":       "20px",
        "marginBottom":  "16px",
    }
    if style:
        s.update(style)
    return html.Div(children, style=s)


def kpi_card(label, value, sub="", color=None):
    if color is None:
        color = COLORS["accent"]
    return html.Div([
        html.Div(label, style={
            "color": COLORS["muted"], "fontSize": "11px",
            "fontFamily": "'Courier New', monospace",
            "letterSpacing": "2px", "textTransform": "uppercase",
        }),
        html.Div(value, style={
            "color": color, "fontSize": "32px",
            "fontWeight": "700", "fontFamily": "'Courier New', monospace",
            "lineHeight": "1.1", "marginTop": "6px",
        }),
        html.Div(sub, style={
            "color": COLORS["muted"], "fontSize": "11px", "marginTop": "4px",
        }),
    ], style={
        "background":   COLORS["card"],
        "border":       f"1px solid {color}33",
        "borderLeft":   f"3px solid {color}",
        "borderRadius": "6px",
        "padding":      "16px 20px",
        "flex":         "1",
        "minWidth":     "140px",
    })
