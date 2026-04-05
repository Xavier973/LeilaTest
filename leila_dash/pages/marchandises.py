# ── Section 05 — Marchandises ─────────────────────────────

import plotly.express as px
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # Top 15 marchandises (GROUP_CONCAT → explode)
    mch = (
        df["marchandises"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .reset_index()
    )
    mch.columns = ["marchandise", "count"]
    mch = mch.head(15)

    fig_mch = px.bar(
        mch.sort_values("count"), x="count", y="marchandise",
        orientation="h", title="Top 15 marchandises transportées",
        color="count",
        color_continuous_scale=[[0, "rgba(232,69,69,0.27)"], [1, COLORS["accent"]]],
        labels={"count": "Nb occurrences", "marchandise": ""},
        text="count",
    )
    fig_mch.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_mch.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                          xaxis=dict(gridcolor=COLORS["border"]))

    # Évolution mensuelle — top 6 marchandises principales
    df_m = df[df["marchandises"].notna()].copy()
    df_m["marchandise_principale"] = df_m["marchandises"].str.split(",").str[0].str.strip()
    top_mch = df_m["marchandise_principale"].value_counts().head(6).index.tolist()
    df_m2 = df_m[df_m["marchandise_principale"].isin(top_mch)]
    monthly = df_m2.groupby(["mois", "marchandise_principale"]).size().reset_index(name="missions")

    fig_trend = px.line(
        monthly, x="mois", y="missions", color="marchandise_principale",
        title="Évolution mensuelle — top 6 marchandises",
        markers=True,
        labels={
            "mois": "Mois", "missions": "Nb missions",
            "marchandise_principale": "Marchandise",
        },
    )
    fig_trend.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    return html.Div([
        html.H2("ANALYSE MARCHANDISES", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        html.Div([
            html.Div(dcc.Graph(figure=fig_mch,   config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_trend, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])
