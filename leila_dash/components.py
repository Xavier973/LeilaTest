# ── Composants HTML réutilisables ─────────────────────────

from dash import html
from config import COLORS


def card(children, style=None):
    s = {
        "background":    COLORS["card"],
        "border":        f"1px solid {COLORS['border']}",
        "borderRadius":  "12px",
        "padding":       "18px",
        "marginBottom":  "16px",
        "boxShadow":     "0 10px 24px rgba(22, 34, 51, 0.06)",
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
            "fontWeight": "600",
            "letterSpacing": "0.5px", "textTransform": "uppercase",
        }),
        html.Div(value, style={
            "color": color, "fontSize": "32px",
            "fontWeight": "700",
            "lineHeight": "1.1", "marginTop": "6px",
        }),
        html.Div(sub, style={
            "color": COLORS["muted"], "fontSize": "11px", "marginTop": "4px",
        }),
    ], style={
        "background":   COLORS["card"],
        "border":       f"1px solid {COLORS['border']}",
        "borderTop":    f"4px solid {color}",
        "borderRadius": "12px",
        "padding":      "16px 18px",
        "boxShadow":    "0 8px 20px rgba(22, 34, 51, 0.05)",
        "flex":         "1",
        "minWidth":     "140px",
    })
