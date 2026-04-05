# ── Section 04 — Expéditeurs & Destinataires ─────────────

import plotly.express as px
import pandas as pd
from dash import dcc, html

from config import COLORS, PLOTLY_THEME


def layout(df):
    # Top remettants
    top_rmt = (
        df.groupby("remettant")
        .agg(missions=("mission_id", "count"), att_moy=("attente_chargement_min", "median"))
        .reset_index()
        .sort_values("missions", ascending=False)
        .head(12)
    )
    fig_rmt = px.bar(
        top_rmt.sort_values("missions"), x="missions", y="remettant",
        orientation="h", title="Top remettants — volume missions",
        color="att_moy",
        color_continuous_scale=[[0, COLORS["accent3"]], [1, COLORS["accent"]]],
        labels={"missions": "Nb missions", "remettant": "", "att_moy": "Attente moy (min)"},
        text="missions",
    )
    fig_rmt.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_rmt.update_layout(**PLOTLY_THEME, coloraxis_showscale=True,
                          xaxis=dict(gridcolor=COLORS["border"]))

    # Top destinataires
    top_dst = (
        df.groupby("destinataire")
        .agg(missions=("mission_id", "count"), att_moy=("attente_dechargement_min", "median"))
        .reset_index()
        .sort_values("missions", ascending=False)
        .head(12)
    )
    fig_dst = px.bar(
        top_dst.sort_values("missions"), x="missions", y="destinataire",
        orientation="h", title="Top destinataires — volume missions",
        color="att_moy",
        color_continuous_scale=[[0, COLORS["accent3"]], [1, COLORS["accent"]]],
        labels={"missions": "Nb missions", "destinataire": "", "att_moy": "Attente moy (min)"},
        text="missions",
    )
    fig_dst.update_traces(textposition="outside", textfont_color=COLORS["text"])
    fig_dst.update_layout(**PLOTLY_THEME, coloraxis_showscale=True,
                          xaxis=dict(gridcolor=COLORS["border"]))

    # Comparaison temps d'attente
    rmt_att = df.groupby("remettant")["attente_chargement_min"].median().reset_index()
    rmt_att.columns = ["acteur", "attente_min"]
    rmt_att["role"] = "Remettant"

    dst_att = df.groupby("destinataire")["attente_dechargement_min"].median().reset_index()
    dst_att.columns = ["acteur", "attente_min"]
    dst_att["role"] = "Destinataire"

    att_df = pd.concat([rmt_att, dst_att])
    att_df = att_df[att_df["attente_min"].between(0, 240)]

    fig_att = px.box(
        att_df, x="role", y="attente_min", color="role",
        title="Distribution temps d'attente : remettants vs destinataires",
        color_discrete_map={"Remettant": COLORS["accent"], "Destinataire": COLORS["accent3"]},
        labels={"attente_min": "Attente médiane (min)", "role": ""},
    )
    fig_att.update_layout(**PLOTLY_THEME, showlegend=False,
                          yaxis=dict(gridcolor=COLORS["border"]))

    return html.Div([
        html.H2("EXPÉDITEURS & DESTINATAIRES", style={
            "color": COLORS["accent"], "fontFamily": "'Courier New', monospace",
            "letterSpacing": "3px", "marginBottom": "20px", "fontSize": "14px",
        }),
        html.Div([
            html.Div(dcc.Graph(figure=fig_rmt, config={"displayModeBar": False}), style={"flex": "1"}),
            html.Div(dcc.Graph(figure=fig_dst, config={"displayModeBar": False}), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        dcc.Graph(figure=fig_att, config={"displayModeBar": False}),
    ])
