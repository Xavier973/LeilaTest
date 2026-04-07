# ── Palette, thème Plotly & constantes métier ─────────────

COLORS = {
    "bg":        "#F2F5F8",
    "card":      "#FFFFFF",
    "border":    "#D4DEE9",
    "accent":    "#B14B34",
    "accent2":   "#2E7FA1",
    "accent3":   "#6F9A3A",
    "text":      "#1F2937",
    "muted":     "#66758A",
    "danger":    "#B8403A",
    "success":   "#2F8D4E",
    "engins": {
        "TR-789-XY": "#E84545",
        "HB-316-CS": "#F5A623",
        "PO-456-AB": "#4ECDC4",
        "VH-234-CD": "#A78BFA",
        "GR-256-CQ": "#34D399",
        "CR-426-DD": "#F472B6",
    },
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'Segoe UI', 'Tahoma', sans-serif", color=COLORS["text"], size=12),
    autosize=False,
    height=360,
    margin=dict(l=40, r=20, t=40, b=40),
    transition=dict(duration=0),
    colorway=[
        COLORS["accent"], COLORS["accent2"], COLORS["accent3"],
        "#A78BFA", "#34D399", "#F472B6",
    ],
)

# Facteurs d'émission ADEME (kg CO₂ / km)
CO2_FACTEURS = {
    "Porteur 8x4":  0.900,
    "Tracteur 6x4": 0.750,
    "Tracteur 4x2": 0.650,
}

NAV_ITEMS = [
    ("overview",     "01 — Vue d'ensemble"),
    ("performance",  "02 — Performance"),
    ("chauffeurs",   "03 — Chauffeurs & Engins"),
    ("acteurs",      "04 — Expéditeurs / Dest."),
    ("marchandises", "05 — Marchandises"),
    ("co2",          "06 — Impact CO₂"),
    ("economie",     "07 — Impact économique"),
    ("geo",          "08 — Géographie"),
]
