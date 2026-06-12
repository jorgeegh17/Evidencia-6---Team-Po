"""
CNH México – Aftermarket Intelligence Dashboard
Actividad 3 – Insights Actionables
Dash + Plotly | Multi-page | Dark/Light Theme Toggle
Paleta: #1C1A21 / #EDECEC / #900C0E / #9797A0 / #827970 / #C0A1A2
"""

import base64
import io
import json


import dash
from dash import dcc, html, Input, Output, callback, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import subprocess, sys, os, threading, webbrowser, time, importlib.util



from cnh_pipeline import (load_data, load_processed_data_from_buffers, REQUIRED_FILES,
                          build_contacto_optimo_data, build_conversion_data,
                          build_retencion_600_data)

# ─────────────────────────────────────────────
# PALETA CNH — DARK & LIGHT
# ─────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg":        "#1C1A21",
        "sidebar":   "#15131A",
        "card":      "#221F28",
        "card2":     "#2A2730",
        "border":    "#3A3640",

        # BRAND CORE
        "accent":    "#900C0E",   # rojo CNH profundo
        "accent2":   "#C1121F",   # rojo brillante
        "accent3":   "#EDECEC",   # blanco industrial

        # ANALYTICS CORE
        "analytic":  "#3A86FF",   # azul eléctrico
        "analytic2": "#00B4D8",   # cyan industrial
        "analytic3": "#90CAF9",   # azul claro

        # HIGH CONTRAST DATAVIZ
        "viz1":      "#C1121F",   # rojo intenso
        "viz2":      "#3A86FF",   # azul eléctrico
        "viz3":      "#00B4D8",   # cyan
        "viz4":      "#FFB703",   # ámbar industrial
        "viz5":      "#8ECAE6",   # hielo
        "viz6":      "#8338EC",   # púrpura técnico
        "viz7":      "#FB5607",   # naranja fuerte
        "viz8":      "#06D6A0",   # verde aqua

        # SECUENCIAL / HEATMAPS
        "heat_low":  "#3A3640",
        "heat_mid":  "#3A86FF",
        "heat_high": "#C1121F",

        # ESTADOS
        "success":   "#06D6A0",
        "warning":   "#FFB703",
        "danger":    "#C1121F",

        # TEXTO
        "warn":      "#C0A1A2",
        "text":      "#EDECEC",
        "muted":     "#9797A0",

        # MARCAS
        "caseih":    "#900C0E",
        "newholland":"#3A86FF",

        "name":      "dark",
    },

    "light": {
        "bg":        "#EDECEC",
        "sidebar":   "#FFFFFF",
        "card":      "#FFFFFF",
        "card2":     "#F5F4F4",
        "border":    "#C0A1A2",

        # BRAND CORE
        "accent":    "#900C0E",
        "accent2":   "#C1121F",
        "accent3":   "#1C1A21",

        # ANALYTICS CORE
        "analytic":  "#00509D",
        "analytic2": "#3A86FF",
        "analytic3": "#90CAF9",

        # HIGH CONTRAST DATAVIZ
        "viz1":      "#C1121F",
        "viz2":      "#00509D",
        "viz3":      "#0096C7",
        "viz4":      "#FFB703",
        "viz5":      "#8ECAE6",
        "viz6":      "#8338EC",
        "viz7":      "#FB5607",
        "viz8":      "#06D6A0",

        # HEATMAPS
        "heat_low":  "#C0A1A2",
        "heat_mid":  "#3A86FF",
        "heat_high": "#C1121F",

        # ESTADOS
        "success":   "#06D6A0",
        "warning":   "#FFB703",
        "danger":    "#C1121F",

        # TEXTO
        "warn":      "#827970",
        "text":      "#1C1A21",
        "muted":     "#827970",

        # MARCAS
        "caseih":    "#900C0E",
        "newholland":"#00509D",

        "name":      "light",
    },
}

FONT = "'IBM Plex Sans', 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', monospace"

# ─────────────────────────────────────────────
# DATOS SINTÉTICOS
# ─────────────────────────────────────────────
funnel_data = dict(
    stage=["Flota activa", "Generan alarma servicio", "Atienden servicio 300h",
           "Atienden servicio 600h", "Retornan a 900h tras incumplir 600h"],
    value=[4167, 2800, 1950, 1100, 54],
    pct=[100, 67, 47, 26, 4.9]
)

meses = ["Ene'24","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic'24",
         "Ene'25","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic'25"]
abandono_mensual = [72.1, 71.8, 73.0, 51.1, 58.3, 62.4, 64.8, 67.2, 65.1, 71.3, 76.8, 80.3,
                    71.9, 70.5, 72.8, 52.3, 57.9, 61.7, 63.5, 66.8, 64.9, 73.1, 77.2, 80.3]

zonas = ["Noreste", "Centro", "Sur-Sureste", "Centro Occidente", "Noroeste"]
meses_hm = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
heatmap_values = np.array([
    [88, 87, 85, 70, 78, 82, 84, 86, 83, 89, 91, 95],
    [76, 74, 75, 55, 62, 67, 70, 71, 68, 74, 79, 83],
    [74, 72, 74, 53, 57, 65, 68, 70, 67, 73, 77, 81],
    [73, 71, 72, 51, 58, 64, 67, 69, 66, 72, 76, 80],
    [68, 66, 67, 56, 54, 42, 59, 63, 62, 68, 71, 75],
])

cumplimiento_zona = {
    "Noreste": 17.0, "Centro": 31.3, "Sur-Sureste": 31.4,
    "Centro Occidente": 32.8, "Noroeste": 36.8
}
registros_zona = {
    "Noreste": 487, "Centro": 1172, "Sur-Sureste": 551,
    "Centro Occidente": 1438, "Noroeste": 519
}

distribuidores = ["AGTRAC","TEPSA","MADISA","ATN","FERTIMEX","AGROMEX","SERVIAG","CAMSA","ARBSA","ENAGRI"]
alarmas_proyectadas = [96, 83, 69, 66, 41, 38, 35, 32, 28, 22]
umbral_capacidad = 46.4

retraso_labels = ["Puntual (≤7 días)", "Moderado (8–30 días)", "Grave (>30 días)"]
tasa_abandono_retraso = [95.1, 66.7, 74.3]

mes_optimo = {
    "Noroeste": ("Junio", 0.69),
    "Sur-Sureste": ("Abril", 0.61),
    "Centro Occidente": ("Abril", 0.60),
    "Centro": ("Abril", 0.55),
    "Noreste": ("Abril", 0.34),
}

np.random.seed(42)
n_units = 120
unit_lats = np.concatenate([
    np.random.normal(27.5, 1.5, 20), np.random.normal(27.0, 1.5, 20),
    np.random.normal(20.5, 1.2, 35), np.random.normal(19.5, 1.0, 25),
    np.random.normal(17.0, 1.5, 20)
])
unit_lons = np.concatenate([
    np.random.normal(-109.5, 1.5, 20), np.random.normal(-104.5, 1.5, 20),
    np.random.normal(-103.0, 1.2, 35), np.random.normal(-99.5, 1.0, 25),
    np.random.normal(-94.0, 1.5, 20)
])
unit_brands = np.random.choice(["Case IH", "New Holland AG", "Case CE", "New Holland CE"],
                                n_units, p=[0.35, 0.30, 0.20, 0.15])
unit_status = np.random.choice(["Activa", "Alarma servicio", "En taller", "Sin telemetría"],
                                n_units, p=[0.55, 0.25, 0.10, 0.10])
unit_hours = np.random.randint(50, 1200, n_units)
units_df = pd.DataFrame({
    "lat": unit_lats, "lon": unit_lons,
    "brand": unit_brands, "status": unit_status, "hours": unit_hours,
    "id": [f"CNH-{1000+i}" for i in range(n_units)]
})

intervalos = ["150h", "300h", "600h", "900h", "1200h"]
cumplimiento_intervalo = [78.2, 63.4, 24.1, 4.9, 2.3]
incumplimiento_intervalo = [100-x for x in cumplimiento_intervalo]
# ── Datos: Cluster de riesgo (INS-01 & INS-02) ────────────────────────
np.random.seed(42)

# Cluster A — Bajo riesgo: c_fuera = 0, cumplimiento histórico alto
_n1 = 180
_c1 = dict(
    c_fuera  = np.random.uniform(0, 0.4, _n1),
    pct_cumple = np.random.normal(72, 10, _n1).clip(40, 100),
    score    = np.random.uniform(0.04, 0.22, _n1),
    cluster  = ["Bajo riesgo (c_fuera = 0)"] * _n1,
)

# Cluster B — Riesgo medio: 1er servicio externo → ventana crítica INS-02
_n2 = 120
_c2 = dict(
    c_fuera  = np.random.uniform(0.6, 1.4, _n2),
    pct_cumple = np.random.normal(44, 11, _n2).clip(18, 70),
    score    = np.random.uniform(0.32, 0.62, _n2),
    cluster  = ["Riesgo medio (c_fuera = 1)"] * _n2,
)

# Cluster C — Alto riesgo: 2+ externos → retorno 12.1% (DX4)
_n3 = 80
_c3 = dict(
    c_fuera  = np.random.uniform(1.6, 4.2, _n3),
    pct_cumple = np.random.normal(19, 7, _n3).clip(4, 38),
    score    = np.random.uniform(0.66, 0.97, _n3),
    cluster  = ["Alto riesgo (≥2 externos)"] * _n3,
)

cluster_df = pd.DataFrame({
    k: np.concatenate([_c1[k], _c2[k], _c3[k]])
    for k in ["c_fuera", "pct_cumple", "score", "cluster"]
})

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_plot_layout(C):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=C["text"], size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor=C["border"], zerolinecolor=C["border"]),
        yaxis=dict(gridcolor=C["border"], zerolinecolor=C["border"]),
    )

def apply_layout(fig, C, **kwargs):
    base = get_plot_layout(C)
    for k in ["xaxis", "yaxis", "margin"]:
        if k in kwargs:
            base[k] = {**base.get(k, {}), **kwargs.pop(k)}
    base.update(kwargs)
    fig.update_layout(**base)
    return fig

def kpi_card(title, value, subtitle="", color="#900C0E", icon="◈", C=None):
    if C is None:
        C = THEMES["light"]
    return html.Div([
        html.Div(icon, style={"fontSize":"20px","color":color,"marginBottom":"6px"}),
        html.Div(value, style={
            "fontSize":"28px","fontWeight":"800","color":color,
            "fontFamily":FONT_MONO,"letterSpacing":"-1px"
        }),
        html.Div(title, style={
            "fontSize":"11px","color":C["text"],"fontWeight":"700",
            "textTransform":"uppercase","letterSpacing":"1px","marginTop":"4px"
        }),
        html.Div(subtitle, style={"fontSize":"10px","color":C["muted"],"marginTop":"4px"}),
    ], style={
        "background": C["card"],
        "border": f"1px solid {C['border']}",
        "borderTop": f"3px solid {color}",
        "borderRadius": "12px",
        "padding": "16px",
        "minWidth": "140px",
        "boxShadow": f"0 2px 12px rgba(0,0,0,0.15)",
        "transition": "all 0.2s",
    })

def section_title(text, sub="", C=None):
    if C is None:
        C = THEMES["light"]
    return html.Div([
        html.Span("▸ ", style={"color": C["accent"]}),
        html.Span(text, style={"color": C["text"], "fontWeight": "700", "fontSize": "13px",
                               "textTransform": "uppercase", "letterSpacing": "1.5px"}),
        html.Div(sub, style={"color": C["muted"], "fontSize": "11px", "marginTop": "2px",
                             "paddingLeft": "12px"}) if sub else None
    ], style={"marginBottom": "12px", "paddingBottom": "8px",
              "borderBottom": f"1px solid {C['border']}"})

def chart_card(children, title="", C=None):
    if C is None:
        C = THEMES["light"]
    return html.Div([
        html.Div(title, style={
            "fontSize":"11px","color":C["muted"],"textTransform":"uppercase",
            "letterSpacing":"1.5px","marginBottom":"12px","fontWeight":"700"
        }) if title else None,
        children
    ], style={
        "background": C["card"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "12px",
        "padding": "18px",
        "boxShadow": f"0 2px 14px rgba(0,0,0,0.12)",
        "transition": "background 0.3s, border-color 0.3s",
    })

# ─────────────────────────────────────────────
# FIGURAS (theme-aware)
# ─────────────────────────────────────────────
def fig_funnel(C):
    fig = go.Figure(go.Funnel(
        y=funnel_data["stage"],
        x=funnel_data["value"],
        textinfo="value+percent initial",
        textfont=dict(family=FONT_MONO, size=11, color=C["text"]),
        marker=dict(
            color=[C["accent3"], "#4A4550", "#6B6370", C["warn"], C["accent2"]],
            line=dict(width=1, color=C["bg"])
        ),
        connector=dict(line=dict(color=C["border"], width=1)),
    ))
    apply_layout(fig, C, height=280, margin=dict(l=160, r=30, t=10, b=10))
    return fig

def fig_serie_abandono(C):
    meses_ext = meses + ["Ene'26", "Feb'26"]
    historico = abandono_mensual + [None, None]
    forecast = [None]*22 + [80.3, 79.8, 71.5, 70.2]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses_ext, y=historico, mode="lines+markers",
        line=dict(color=C["accent"], width=2),
        marker=dict(size=5, color=C["accent"]),
        name="Histórico", fill="tozeroy",
        fillcolor=f"rgba(144,12,14,0.10)"
    ))
    fig.add_trace(go.Scatter(
        x=meses_ext, y=forecast, mode="lines+markers",
        line=dict(color=C["accent3"], width=2, dash="dash"),
        marker=dict(size=5, color=C["accent3"]),
        name="Forecast SARIMA"
    ))
    fig.add_hrect(y0=75, y1=100, fillcolor="rgba(144,12,14,0.07)", line_width=0,
                  annotation_text="Zona crítica", annotation_font_size=9,
                  annotation_font_color=C["accent2"])
    fig.add_hrect(y0=0, y1=60, fillcolor="rgba(130,121,112,0.07)", line_width=0,
                  annotation_text="Zona favorable", annotation_font_size=9,
                  annotation_font_color=C["muted"])
    apply_layout(fig, C, height=240,
                 yaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[0, 100]),
                 xaxis=dict(gridcolor=C["border"], tickfont=dict(size=9)),
                 legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
                 margin=dict(l=10, r=10, t=10, b=40))
    return fig

def fig_heatmap_zonas(C):
    text_vals = [[f"{v}%" for v in row] for row in heatmap_values]
    fig = go.Figure(go.Heatmap(
        z=heatmap_values, x=meses_hm, y=zonas,
        text=text_vals, texttemplate="%{text}",
        textfont=dict(size=9, family=FONT_MONO),
        colorscale=[
            [0,   "#827970"],
            [0.4, C["accent3"]],
            [0.7, C["accent"]],
            [1,   C["accent2"]],
        ],
        zmin=40, zmax=100, showscale=True,
        colorbar=dict(ticksuffix="%", tickfont=dict(size=9, color=C["text"]),
                      thickness=10, len=0.8)
    ))
    apply_layout(fig, C, height=220, margin=dict(l=110, r=60, t=10, b=40))
    return fig
def fig_parallel_coordinates(C, month_range=None, visible_zones=None):
    if month_range is None:
        month_range = [0, 11]
    
    # Si no se define el estado de visibilidad, por defecto todas están visibles
    if visible_zones is None:
        visible_zones = zonas.copy()
        
    start_idx, end_idx = month_range
    if start_idx == end_idx:
        if end_idx < 11:
            end_idx += 1
        else:
            start_idx -= 1
            
    selected_months = meses_hm[start_idx : end_idx + 1]

    # Construir dataframe original
    df = pd.DataFrame(heatmap_values, columns=meses_hm)
    df["Zona"] = zonas
    df["zona_idx"] = range(len(zonas))

    # Definir colores fijos mapeados a cada índice de zona (Paleta especial para Claro)
    if C["name"] == "light":
        zona_colors = ["#00509D", "#007A87", "#A0522D", "#C1121F", "#6F2DA8"]
    else:
        zona_colors = [C["viz2"], C["viz3"], C["viz4"], C["viz7"], C["viz1"]]
    
    # Filtrar solo las zonas visibles del dataframe
    # ESTO es lo equivalente a ocultar una traza en go.Scatter:
    # eliminamos los datos de las zonas no visibles para que simplemente no existan.
    df_visible = df[df["Zona"].isin(visible_zones)].copy().reset_index(drop=True)

    # Reindexar zona_idx para la escala de colores con solo las zonas visibles
    visible_zona_colors = [
        color for zona, color in zip(zonas, zona_colors)
        if zona in visible_zones
    ]

    # Construir escala de colores con step-transitions solo para las zonas visibles
    n_vis = max(len(df_visible), 1)
    if len(df_visible) == 0:
        # Ninguna zona visible: gráfico vacío
        custom_colorscale = [[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]]
    elif len(df_visible) == 1:
        c = visible_zona_colors[0]
        custom_colorscale = [[0, c], [1, c]]
    else:
        custom_colorscale = []
        for i, color in enumerate(visible_zona_colors):
            pos_start = i / n_vis
            pos_end = (i + 1) / n_vis
            custom_colorscale.append([pos_start, color])
            # Punto de corte abrupto antes de que empiece la siguiente zona
            if i < n_vis - 1:
                custom_colorscale.append([pos_end - 1e-6, color])
                custom_colorscale.append([pos_end, visible_zona_colors[i + 1]])
            else:
                custom_colorscale.append([pos_end, color])

    dimensions = []
    for mes in selected_months:
        dimensions.append(dict(
            label=mes,
            values=df_visible[mes] if len(df_visible) > 0 else [],
            range=[40, 100],
            tickvals=[40, 55, 70, 85, 100],
            ticktext=["40%","55%","70%","85%","100%"],
        ))

    fig = go.Figure()

    # Agregar la traza de Coordenadas Paralelas con solo las zonas visibles
    fig.add_trace(go.Parcoords(
        line=dict(
            color=df_visible["zona_idx"] if len(df_visible) > 0 else [],
            colorscale=custom_colorscale,
            showscale=False,
            cmin=0,
            cmax=len(zonas)
        ),
        unselected=dict(
            line=dict(opacity=0)
        ),
        dimensions=dimensions,
        labelangle=0,
        labelside="bottom",
        labelfont=dict(size=10, color=C["text"], family=FONT),
        tickfont=dict(size=8, color=C["muted"], family=FONT_MONO),
        rangefont=dict(size=8, color=C["muted"], family=FONT_MONO),
    ))

    # Añadir trazas falsas (Scatter) que actúan como la LEYENDA INTERACTIVA
    for i, (zona, color) in enumerate(zip(zonas, zona_colors)):
        is_visible = zona in visible_zones
        legend_group_color = color if is_visible else C["muted"]
        
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=legend_group_color, symbol="square"),
            name=zona,
            showlegend=True,
            customdata=[zona],
            visible=True if is_visible else "legendonly"
        ))

    apply_layout(fig, C,
        height=320,
        margin=dict(l=60, r=60, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(
            font=dict(size=9, color=C["text"]),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center",
            itemclick="toggle",
            itemdoubleclick="toggle"
        )
    )

    return fig


def make_parcoords_container(C):
    return chart_card(
        html.Div([
            # Componente de memoria para guardar qué zonas están activas/visibles
            dcc.Store(id="parcoords-visible-zones-store", data=zonas),
            
            dcc.Graph(id="parcoords-graph", figure=fig_parallel_coordinates(C), config={"displayModeBar": False}),
            html.Div("Seleccione el rango de meses:", style={
                "fontSize": "10px", 
                "color": C["muted"], 
                "fontWeight": "700", 
                "textTransform": "uppercase", 
                "letterSpacing": "1px",
                "marginTop": "10px",
                "marginBottom": "6px",
                "textAlign": "center"
            }),
            dcc.Graph(
                id="parcoords-slider-chart",
                figure=fig_parcoords_slider_chart(C),
                config={"displayModeBar": False}
            )
        ]),
        title="Coordenadas Paralelas: Abandono por Zona × Mes",
        C=C
    )


def fig_parcoords_slider_chart(C, month_range=None):
    if month_range is None:
        month_range = [0, 11]
        
    fig = go.Figure()
    
    # Colores sincronizados para modo Claro/Oscuro
    if C["name"] == "light":
        zona_colors = ["#00509D", "#007A87", "#A0522D", "#C1121F", "#6F2DA8"]
    else:
        zona_colors = [C["viz2"], C["viz3"], C["viz4"], C["viz7"], C["viz1"]]
    
    for i, (zona, color) in enumerate(zip(zonas, zona_colors)):
        fig.add_trace(go.Scatter(
            x=meses_hm,
            y=heatmap_values[i],
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=6),
            name=zona,
            customdata=[zona]*len(meses_hm),
            hovertemplate=(
                "<b>Zona:</b> %{customdata}<br>"
                "<b>Mes:</b> %{x}<br>"
                "<b>Abandono:</b> %{y:.1f}%<br>"
                "<extra></extra>"
            ),
            showlegend=False
        ))
        
    apply_layout(fig, C,
        height=130,
        margin=dict(l=60, r=60, t=10, b=10),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=C["card"],
            bordercolor=C["border"],
            font=dict(family=FONT, size=11, color=C["text"])
        ),
        xaxis=dict(
            gridcolor=C["border"],
            rangeslider=dict(
                visible=True,
                thickness=0.35,
                bgcolor="rgba(0,0,0,0)",
                bordercolor=C["border"]
            ),
            tickfont=dict(size=8, color=C["muted"], family=FONT_MONO)
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        )
    )
    return fig

def fig_cumplimiento_zona(C):
    zonas_ord = sorted(cumplimiento_zona, key=cumplimiento_zona.get)
    vals = [cumplimiento_zona[z] for z in zonas_ord]
    colors = C["viz2"], C["viz3"], C["viz4"], C["viz7"], C["viz1"]  # escala de colores para barras
    fig = go.Figure(go.Bar(
        x=vals, y=zonas_ord, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v}% ({registros_zona[z]} reg.)" for v, z in zip(vals, zonas_ord)],
        textposition="outside",
        textfont=dict(size=10, family=FONT_MONO, color=C["text"]),
    ))
    apply_layout(fig, C, height=200,
                 xaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[0, 55]),
                 yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                 margin=dict(l=110, r=90, t=10, b=30))
    return fig

from plotly.colors import sample_colorscale

def fig_distribuidores(C):

    # Escala de colores personalizada
    colorscale = [
        [0.0, C["analytic"]],
        [0.5, C["analytic2"]],
        [1.0, C["analytic3"]]
    ]

    # Genera posiciones uniformes para cada barra
    n = len(distribuidores)

    positions = [
        i / (n - 1) if n > 1 else 0.5
        for i in range(n)
    ]

    # Un color distinto por barra
    colors = sample_colorscale(colorscale, positions)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=distribuidores,
        y=alarmas_proyectadas,

        marker=dict(
            color=colors,
            line=dict(width=0)
        ),

        text=alarmas_proyectadas,
        textposition="outside",

        textfont=dict(
            size=10,
            family=FONT_MONO,
            color=C["text"]
        ),
    ))

    fig.add_hline(
        y=umbral_capacidad,
        line=dict(
            color=C["accent3"],
            width=2,
            dash="dash"
        ),

        annotation_text=f"Umbral 150% = {umbral_capacidad}",

        annotation_font=dict(
            size=10,
            color=C["accent3"]
        ),

        annotation_position="top left"
    )

    apply_layout(
        fig,
        C,
        height=240,

        yaxis=dict(
            gridcolor=C["border"],
            title="Alarmas proyectadas"
        ),

        xaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10)
        ),

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=40
        )
    )

    return fig

def fig_retrasos(C):
    colors_bar = [C["analytic"], C["analytic2"], C["analytic3"]]
    fig = go.Figure(go.Bar(
        x=retraso_labels, y=tasa_abandono_retraso,
        marker=dict(color=colors_bar, line=dict(width=0)),
        text=[f"{v}%" for v in tasa_abandono_retraso],
        textposition="outside",
        textfont=dict(size=11, family=FONT_MONO, color=C["text"]),
    ))
    fig.add_annotation(
        x="Grave (>30 días)", y=74.3,
        text="OR=0.24 → 76.2%↓<br>riesgo next service",
        showarrow=True, arrowhead=2, arrowcolor=C["accent"],
        font=dict(size=9, color=C["accent"]), bgcolor=C["card2"],
        bordercolor=C["accent"], borderwidth=1, ay=-60
    )
    apply_layout(fig, C, height=230,
                 yaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[0, 115]),
                 xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                 margin=dict(l=10, r=10, t=10, b=10))
    return fig

def fig_mapa_unidades(C):
    color_map = {
        "Case IH": C["caseih"], "New Holland AG": C["newholland"],
        "Case CE": "#827970", "New Holland CE": "#C0A1A2"
    }
    map_style = "carto-darkmatter" if C["name"] == "dark" else "carto-positron"
    fig = go.Figure()
    for brand in units_df["brand"].unique():
        mask = units_df["brand"] == brand
        sub = units_df[mask]
        fig.add_trace(go.Scattermap(
            lat=sub["lat"], lon=sub["lon"], mode="markers",
            marker=dict(
                size=[10 if s == "Alarma servicio" else 7 for s in sub["status"]],
                color=color_map[brand], opacity=0.85,
            ),
            text=sub.apply(lambda r: f"{r['id']}<br>{r['brand']}<br>{r['hours']}h<br>{r['status']}", axis=1),
            hoverinfo="text", name=brand,
        ))
    apply_layout(fig,
        C,
        mapbox=dict(style=map_style, center=dict(lat=23.5, lon=-102.0), zoom=4.2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=300,
        legend=dict(font=dict(size=9, color=C["text"]),
                    bgcolor=f"rgba({int(C['card'][1:3],16)},{int(C['card'][3:5],16)},{int(C['card'][5:7],16)},0.85)",
                    bordercolor=C["border"], borderwidth=1,
                    x=0.01, y=0.99, xanchor="left", yanchor="top"),
        font=dict(family=FONT, color=C["text"]),
    )
    return fig
def fig_cluster_riesgo(C):
    COLOR_MAP = {
        "Bajo riesgo (c_fuera = 0)":  C["analytic"],   # azul
        "Riesgo medio (c_fuera = 1)": C["warning"],    # ámbar
        "Alto riesgo (≥2 externos)":  C["accent2"],    # rojo
    }

    TASA_RETORNO = {
        "Bajo riesgo (c_fuera = 0)":  "Retorno: ~53.8%",
        "Riesgo medio (c_fuera = 1)": "1er svc externo — ventana crítica",
        "Alto riesgo (≥2 externos)":  "Retorno: 12.1%  (OR = 0.091)",
    }

    fig = go.Figure()

    for cluster, color in COLOR_MAP.items():
        sub = cluster_df[cluster_df["cluster"] == cluster]

        # Convertir hex a rgba para el relleno de la elipse
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        # Elipse de agrupamiento como shape
        cx = sub["c_fuera"].mean()
        cy = sub["pct_cumple"].mean()
        rx = sub["c_fuera"].std() * 1.8
        ry = sub["pct_cumple"].std() * 1.8

        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=cx - rx, y0=cy - ry,
            x1=cx + rx, y1=cy + ry,
            line=dict(color=color, width=1.5, dash="dot"),
            fillcolor=f"rgba({r},{g},{b},0.07)",
            layer="below",
        )

        # Puntos del scatter
        fig.add_trace(go.Scatter(
            x=sub["c_fuera"],
            y=sub["pct_cumple"],
            mode="markers",
            name=cluster,
            marker=dict(
                size=6,
                color=sub["score"],
                colorscale=[
                    [0.0, C["analytic"]],
                    [0.5, C["warning"]],
                    [1.0, C["accent2"]],
                ],
                cmin=0, cmax=1,
                opacity=0.75,
                line=dict(color=color, width=0.8),
                showscale=False,
            ),
            customdata=sub[["cluster", "score"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "c_fuera: %{x:.1f}<br>"
                "Cumplimiento: %{y:.0f}%<br>"
                "Score riesgo: %{customdata[1]:.2f}"
                "<extra></extra>"
            ),
        ))

        # Anotación centrada en la elipse
        fig.add_annotation(
            x=cx, y=cy,
            text=f"<b>{cluster}</b><br><span style='font-size:9px'>{TASA_RETORNO[cluster]}</span>",
            showarrow=False,
            font=dict(size=9, color=color, family=FONT_MONO),
            bgcolor=C["card"],
            bordercolor=color,
            borderwidth=1,
            borderpad=4,
            opacity=0.92,
        )

    # Línea vertical: umbral punto de no retorno (2 externos)
    fig.add_vline(
        x=1.55,
        line=dict(color=C["accent2"], width=1.5, dash="dot"),
        annotation_text="Punto de<br>no retorno",
        annotation_font=dict(size=9, color=C["accent2"]),
        annotation_position="top right",
    )

    # Colorbar manual como traza fantasma
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(
            colorscale=[
                [0.0, C["analytic"]],
                [0.5, C["warning"]],
                [1.0, C["accent2"]],
            ],
            cmin=0, cmax=1,
            showscale=True,
            colorbar=dict(
                title=dict(text="Score riesgo", font=dict(size=9, color=C["muted"])),
                thickness=10, len=0.7,
                tickvals=[0, 0.5, 1],
                ticktext=["Bajo", "Medio", "Alto"],
                tickfont=dict(size=8, color=C["muted"]),
                x=1.01,
            ),
        ),
        showlegend=False,
    ))

    apply_layout(fig, C,
        height=310,
        xaxis=dict(
            title=dict(text="Servicios realizados fuera de la red CNH (c_fuera)", font=dict(size=10, color=C["muted"])),
            gridcolor=C["border"], range=[-0.3, 4.8],
        ),
        yaxis=dict(
            title=dict(text="Cumplimiento histórico (%)", font=dict(size=10, color=C["muted"])),
            gridcolor=C["border"], range=[-5, 108],
        ),
        legend=dict(
            font=dict(size=9),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.18, x=0.5, xanchor="center",
        ),
        margin=dict(l=50, r=60, t=20, b=60),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=C["card"],
            bordercolor=C["border"],
            font=dict(family=FONT, size=10, color=C["text"]),
        ),
    )

    return fig

def fig_intervalos_ag(C):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Cumplen", x=intervalos, y=cumplimiento_intervalo,
        marker_color=C["accent"],
        text=[f"{v}%" for v in cumplimiento_intervalo],
        textposition="inside", textfont=dict(size=10, family=FONT_MONO, color="#FFFFFF"),
    ))
    fig.add_trace(go.Bar(
        name="No cumplen", x=intervalos, y=incumplimiento_intervalo,
        marker_color=C["border"],
        text=[f"{v:.0f}%" for v in incumplimiento_intervalo],
        textposition="inside", textfont=dict(size=10, family=FONT_MONO, color=C["text"]),
    ))
    fig.add_annotation(
        x="600h", y=105, text="⚠ Punto de quiebre<br>Retorno 4.9%",
        showarrow=True, arrowhead=2, arrowcolor=C["accent3"],
        font=dict(size=9, color=C["accent3"]), bgcolor=C["card2"],
        bordercolor=C["accent3"], borderwidth=1, ay=-40
    )
    apply_layout(fig, C, barmode="stack", height=250,
                 yaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[0, 115]),
                 xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                 legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)",
                             orientation="h", y=-0.15),
                 margin=dict(l=10, r=10, t=10, b=40))
    return fig

def fig_mes_optimo(C):
    zonas_list = list(mes_optimo.keys())
    probs = [mes_optimo[z][1]*100 for z in zonas_list]
    meses_list = [mes_optimo[z][0] for z in zonas_list]
    bar_colors = [C["accent"] if p >= 60 else C["warn"] if p >= 40 else C["accent2"] for p in probs]
    fig = go.Figure(go.Bar(
        x=zonas_list, y=probs, marker=dict(color=bar_colors),
        text=[f"{m}<br>{p:.0f}%" for m, p in zip(meses_list, probs)],
        textposition="outside",
        textfont=dict(size=10, family=FONT_MONO, color=C["text"]),
    ))
    apply_layout(fig, C, height=230,
                 yaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[0, 90], title="P(cumplimiento)"),
                 xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
                 margin=dict(l=10, r=10, t=10, b=10))
    return fig

def fig_barchart_facetado(C):
    # Construir dataframe largo
    rows = []
    for i, zona in enumerate(zonas):
        for j, mes in enumerate(meses_hm):
            rows.append({"Zona": zona, "Mes": mes, "Abandono": heatmap_values[i][j]})
    df = pd.DataFrame(rows)

    # Orden de meses correcto
    df["Mes"] = pd.Categorical(df["Mes"], categories=meses_hm, ordered=True)

    # Color por nivel de abandono
    def get_color(v):
        if v >= 80: return C["accent2"]
        elif v >= 65: return C["accent"]
        elif v >= 55: return C["warn"]
        else: return C["muted"]

    fig = go.Figure()

    for i, zona in enumerate(zonas):
        sub = df[df["Zona"] == zona].sort_values("Mes")
        bar_colors = [get_color(v) for v in sub["Abandono"]]
        fig.add_trace(go.Bar(
            x=sub["Mes"],
            y=sub["Abandono"],
            name=zona,
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{v}%" for v in sub["Abandono"]],
            textposition="outside",
            textfont=dict(size=8, family=FONT_MONO, color=C["text"]),
            xaxis=f"x{i+1}",
            yaxis=f"y{i+1}",
        ))

    # Layout con 5 subplots en fila
    layout_kwargs = dict(
        grid=dict(rows=1, columns=5, pattern="independent"),
        height=280,
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=40),
    )

    for i, zona in enumerate(zonas):
        xi = f"xaxis{i+1}" if i > 0 else "xaxis"
        yi = f"yaxis{i+1}" if i > 0 else "yaxis"
        layout_kwargs[xi] = dict(
            title=dict(text=zona, font=dict(size=10, color=C["accent"], family=FONT)),
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(size=7, color=C["muted"]),
            tickangle=45,
        )
        layout_kwargs[yi] = dict(
            range=[0, 105],
            ticksuffix="%",
            gridcolor=C["border"],
            tickfont=dict(size=8, color=C["muted"]),
        )

    apply_layout(fig, C, **layout_kwargs)
    return fig

def fig_radar_zonas(C):
    categories = ["Cumplimiento", "Vol. registros", "Riesgo diciembre",
                  "Predictibilidad ciclo", "Potencial aftermarket"]
    vals_by_zona = {
        "Noroeste":         [36.8, 45, 35, 90, 85],
        "Centro Occidente": [32.8, 80, 60, 70, 75],
        "Centro":           [31.3, 65, 65, 65, 70],
        "Sur-Sureste":      [31.4, 40, 62, 60, 65],
        "Noreste":          [17.0, 30, 75, 40, 45],
    }
    zona_colors = [C["accent"], C["accent3"], C["muted"], C["warn"], C["accent2"]]
    fig = go.Figure()
    for i, (zona, vals) in enumerate(vals_by_zona.items()):
        vals_c = vals + [vals[0]]
        cats_c = categories + [categories[0]]
        rc = zona_colors[i]
        try:
            r_int = int(rc[1:3], 16)
            g_int = int(rc[3:5], 16)
            b_int = int(rc[5:7], 16)
            fill = f"rgba({r_int},{g_int},{b_int},0.08)"
        except:
            fill = "rgba(144,12,14,0.08)"
        fig.add_trace(go.Scatterpolar(
            r=vals_c, theta=cats_c, fill="toself", name=zona,
            line=dict(color=rc, width=1.5), fillcolor=fill
        ))
    apply_layout(fig, C,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=C["border"],
                            tickfont=dict(size=8, color=C["muted"])),
            angularaxis=dict(gridcolor=C["border"], tickfont=dict(size=9, color=C["text"])),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
        margin=dict(l=20, r=20, t=20, b=50),
        height=270,
    )
    return fig
# fig_parallel_coordinates is defined above

def fig_roc_curve(C):
    fpr_xgb = [0.0, 0.05, 0.12, 0.22, 0.35, 1.0]
    tpr_xgb = [0.0, 0.32, 0.58, 0.77, 0.90, 1.0]
    fpr_rf  = [0.0, 0.08, 0.18, 0.30, 0.45, 1.0]
    tpr_rf  = [0.0, 0.28, 0.51, 0.69, 0.84, 1.0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr_xgb, y=tpr_xgb, mode="lines",
                             name="XGBoost (AUC=0.741)", line=dict(color=C["accent"], width=3)))
    fig.add_trace(go.Scatter(x=fpr_rf, y=tpr_rf, mode="lines",
                             name="Random Forest (AUC=0.729)",
                             line=dict(color=C["accent3"], width=3, dash="dash")))
    fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines", name="Random",
                             line=dict(color=C["muted"], dash="dot")))
    apply_layout(fig, C, height=260,
                 xaxis=dict(title="False Positive Rate", range=[0,1], gridcolor=C["border"]),
                 yaxis=dict(title="True Positive Rate",  range=[0,1], gridcolor=C["border"]),
                 margin=dict(l=40, r=20, t=20, b=40),
                 legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
    return fig

def fig_risk_scoring(C):
    categorias = ["Bajo riesgo", "Riesgo medio", "Alto riesgo", "Crítico"]
    clientes   = [420, 310, 190, 82]
    colors_rs  = [C["muted"], C["warn"], C["accent"], C["accent2"]]
    fig = go.Figure(go.Bar(
        x=categorias, y=clientes, marker=dict(color=colors_rs),
        text=clientes, textposition="outside",
        textfont=dict(family=FONT_MONO, size=11, color=C["text"])
    ))
    apply_layout(fig, C, height=250,
                 yaxis=dict(title="Clientes", gridcolor=C["border"]),
                 xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                 margin=dict(l=20, r=20, t=20, b=30))
    return fig

# ─────────────────────────────────────────────
# TOGGLE BUTTON
# ─────────────────────────────────────────────
def make_theme_toggle(current_theme):
    is_dark = current_theme == "dark"
    return html.Button(
        [
            html.Span("☀" if is_dark else "☾",
                      style={"fontSize":"14px","marginRight":"6px"}),
            html.Span("Modo claro" if is_dark else "Modo oscuro",
                      style={"fontSize":"11px","fontWeight":"700","letterSpacing":"0.5px"}),
        ],
        id="theme-toggle",
        n_clicks=0,
        style={
            "position": "fixed",
            "bottom": "20px",
            "right": "20px",
            "zIndex": "999",
            "background": THEMES[current_theme]["accent"],
            "color": "#FFFFFF",
            "border": "none",
            "borderRadius": "24px",
            "padding": "10px 18px",
            "cursor": "pointer",
            "fontFamily": FONT,
            "display": "flex",
            "alignItems": "center",
            "boxShadow": "0 4px 16px rgba(144,12,14,0.4)",
            "transition": "all 0.2s",
        }
    )

# ─────────────────────────────────────────────
# FIGURAS — CONTACTO ÓPTIMO (notebook colors)
# ─────────────────────────────────────────────

# Colores del notebook (se usan tal como están en el notebook)
NB_WHITE   = '#FFFFFF'
NB_NAVY    = '#1B2A4A'
NB_GRAY    = '#6B7280'
NB_LGRAY   = '#F3F4F6'
NB_TEAL    = '#2A9D8F'
NB_GOLD    = '#E9C46A'
NB_CRIMSON = '#9B1B30'
NB_RED_BAR = '#A20503'
NB_GREEN   = '#27ae60'
NB_FONT    = 'Arial, sans-serif'

COLORES_ZONAS_NB = {
    'Noroeste':        '#003087',
    'Centro Occidente':'#2A9D8F',
    'Centro':          '#E9A820',
    'Sur-Sureste':     '#F4A261',
    'Noreste':         '#E63946',
}














def fig_contacto_heatmap(contacto_data):
    """Heatmap de receptividad al servicio — Zona × Mes (colores notebook)."""
    pivot       = contacto_data['pivot']
    orden_zonas = contacto_data['orden_zonas']
    orden_meses = contacto_data['orden_meses']
    mes_top     = contacto_data['mes_top']

    annotations = []
    for i, zona in enumerate(orden_zonas):
        for j, mes in enumerate(orden_meses):
            try:
                val = pivot.loc[zona, mes]
            except KeyError:
                continue
            if pd.isna(val):
                continue
            is_best    = mes_top.get(zona, ('',))[0] == mes
            text_color = 'white' if val > 45 else NB_NAVY
            txt = f"<b>{val:.0f}%</b>" if is_best else f"{val:.0f}%"
            annotations.append(dict(
                x=j, y=i, text=txt, showarrow=False,
                font=dict(size=12 if is_best else 10, family=NB_FONT, color=text_color),
                xref='x', yref='y'
            ))

    colorscale = [[0,'#FFF0F0'],[0.2,'#FECACA'],[0.4,'#FDE68A'],
                  [0.6,'#BBF7D0'],[0.8,'#34D399'],[1.0,'#065F46']]

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=orden_meses, y=orden_zonas,
        colorscale=colorscale, zmin=0, zmax=75,
        showscale=True,
        colorbar=dict(title=dict(text='% cumple', font=dict(size=12, family=NB_FONT)),
                      ticksuffix='%', tickfont=dict(family=NB_FONT, size=11),
                      len=0.8, thickness=14, x=1.02),
        xgap=3, ygap=3,
        hovertemplate='<b>%{y}</b> — <b>%{x}</b><br>Cumplimiento real: %{z:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        title=dict(
            text='<b>Mapa de receptividad al servicio — Zona × Mes</b>',
            font=dict(size=16, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=380, font_family=NB_FONT,
        margin=dict(t=110, b=30, l=150, r=80),
        xaxis=dict(side='top', tickfont=dict(size=12, family=NB_FONT), showgrid=False),
        yaxis=dict(tickfont=dict(size=12, family=NB_FONT), showgrid=False),
        annotations=annotations,
    )
    return fig


def fig_contacto_70_30(contacto_data):
    """Gráfica de distribución 70/30 del esfuerzo comercial (colores notebook)."""
    df_est = contacto_data['df_estrategia']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_est['zona'], x=[70]*len(df_est),
        orientation='h', name='70% — Mes óptimo',
        marker=dict(color=NB_TEAL, line=dict(color='white', width=2)),
        text=[f"<b>{row['mes_opt']}</b> ({row['pct_opt']:.0f}% cumple)"
              for _, row in df_est.iterrows()],
        textposition='inside',
        textfont=dict(size=12, color='white', family=NB_FONT),
        hovertemplate='<b>%{y}</b><br>70% al mes óptimo: %{text}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        y=df_est['zona'], x=[30]*len(df_est),
        orientation='h', name='30% — Segundo mejor mes',
        marker=dict(color=NB_GOLD, line=dict(color='white', width=2)),
        text=[f"{row['mes_2do']} ({row['pct_2do']:.0f}%)"
              for _, row in df_est.iterrows()],
        textposition='inside',
        textfont=dict(size=11, color=NB_NAVY, family=NB_FONT),
        hovertemplate='<b>%{y}</b><br>30% al segundo mejor: %{text}<extra></extra>'
    ))
    fig.add_vline(x=70, line_color='#CBD5E1', line_width=1.5, line_dash='dot')
    fig.update_layout(
        title=dict(
            text='<b>Distribución recomendada del esfuerzo comercial — Regla 70/30</b>',
            font=dict(size=16, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        barmode='stack',
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=400, font_family=NB_FONT,
        margin=dict(t=90, b=120, l=160, r=60),
        xaxis=dict(title='% del esfuerzo de contacto', ticksuffix='%',
                   range=[0, 106], gridcolor=NB_LGRAY,
                   tickfont=dict(size=12, family=NB_FONT)),
        yaxis=dict(tickfont=dict(size=13, family=NB_FONT), showgrid=False),
        legend=dict(orientation='h', y=-0.25, x=0.05,
                    font=dict(size=12, family=NB_FONT)),
    )
    return fig


def fig_contacto_tasa_incumplimiento(contacto_data):
    """Tasa de incumplimiento por intervalo de servicio (colores notebook)."""
    df_tasa = contacto_data['df_tasa']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_tasa['intervalo'],
        y=df_tasa['tasa_incumple'],
        marker_color=NB_RED_BAR,
        marker_line_color='white',
        marker_line_width=1,
        opacity=0.85,
        text=[f'{v:.1%}' for v in df_tasa['tasa_incumple']],
        textposition='outside',
        name='Incumplimiento'
    ))
    fig.update_layout(
        title=dict(text='<b>Tasa de incumplimiento por intervalo de servicio</b>',
                   font=dict(size=16, family=NB_FONT, color=NB_NAVY)),
        xaxis_title='<b>Intervalo de servicio</b>',
        yaxis_title='<b>Tasa de incumplimiento</b>',
        yaxis=dict(tickformat='.0%', range=[0, 1.1]),
        xaxis=dict(tickangle=45),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        template='plotly_white',
        showlegend=False,
        height=420,
        margin=dict(t=70, b=100),
        font_family=NB_FONT,
    )
    return fig


def card_momento_optimo_html(contacto_data):
    """Genera un componente HTML para la tarjeta Momento Óptimo."""
    mes_top = contacto_data.get('mes_top', {})
    # Calcular porcentaje de cierres ponderado
    valores = [v[1] for v in mes_top.values() if len(v) >= 2]
    pct_cierre = round(sum(valores) / max(len(valores), 1), 1) if valores else 62.0
    zona_max = max(mes_top, key=lambda z: mes_top[z][1]) if mes_top else 'Noroeste'
    mes_global = mes_top[zona_max][0] if zona_max in mes_top else 'Junio'

    return html.Div([
        html.Div("⊙  MOMENTO ÓPTIMO", style={
            "fontSize": "9px", "color": NB_TEAL,
            "letterSpacing": "2px", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.Div(mes_global.upper(), style={
            "fontSize": "22px", "fontWeight": "900",
            "color": NB_NAVY, "fontFamily": "monospace", "marginBottom": "4px"
        }),
        html.Div([
            html.Span(f"{pct_cierre:.0f}%", style={
                "fontSize": "36px", "fontWeight": "900",
                "color": NB_TEAL, "fontFamily": "monospace"
            }),
            html.Span(" de cierres", style={
                "fontSize": "13px", "color": NB_GRAY, "marginLeft": "6px"
            }),
        ]),
        html.Div("Mes óptimo de contacto por zona (XGBoost AUC=0.74)",
                 style={"fontSize": "10px", "color": NB_GRAY, "marginTop": "6px"}),
        html.Div([
            *[html.Div([
                html.Span(z, style={"fontSize": "11px", "color": "#333", "flex": "1"}),
                html.Span(f"{mes_top[z][0]}  {mes_top[z][1]:.0f}%",
                          style={"fontSize": "11px", "color": NB_TEAL,
                                 "fontFamily": "monospace", "fontWeight": "700"})
            ], style={"display": "flex", "justifyContent": "space-between",
                      "padding": "4px 0", "borderBottom": "1px solid #eee"})
              for z in list(mes_top.keys())[:5]
            ]
        ], style={"marginTop": "12px"}),
    ], style={
        "background": NB_WHITE, "border": f"2px solid {NB_TEAL}",
        "borderRadius": "12px", "padding": "16px",
        "boxShadow": "0 2px 12px rgba(42,157,143,0.15)",
    })


def card_monetizacion_contacto_html(contacto_data, monetizacion_data=None):
    """Tarjeta de potencial de monetización campaña 70/30."""
    if monetizacion_data is None:
        rec_ins03  = 200
        ingreso_03 = rec_ins03 * 15000
    else:
        rec_ins03  = monetizacion_data['servicios'][0]
        ingreso_03 = monetizacion_data['ingresos'][0]

    return html.Div([
        html.Div("💰  POTENCIAL DE MONETIZACIÓN", style={
            "fontSize": "9px", "color": NB_CRIMSON,
            "letterSpacing": "2px", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.Div("Campaña 70/30", style={
            "fontSize": "14px", "fontWeight": "800",
            "color": NB_NAVY, "marginBottom": "4px"
        }),
        html.Div([
            html.Span(f"${ingreso_03/1e6:.2f}M", style={
                "fontSize": "32px", "fontWeight": "900",
                "color": NB_TEAL, "fontFamily": "monospace"
            }),
            html.Span(" MXN", style={"fontSize": "13px", "color": NB_GRAY, "marginLeft": "4px"}),
        ]),
        html.Div(f"{rec_ins03:,} servicios adicionales estimados",
                 style={"fontSize": "11px", "color": NB_GRAY, "marginTop": "4px"}),
        html.Div([
            html.Span("Ticket promedio = $15,000 mxn", style={
                "fontSize": "11px", "color": NB_CRIMSON,
                "fontWeight": "700", "fontStyle": "italic"
            }),
        ], style={
            "marginTop": "10px", "padding": "8px 10px",
            "background": "rgba(155,27,48,0.06)",
            "border": f"1px solid {NB_CRIMSON}44",
            "borderRadius": "6px",
        }),
        html.Div("Mejora +20% relativo sobre tasa actual de conversión en meses óptimos.",
                 style={"fontSize": "10px", "color": NB_GRAY, "marginTop": "8px"}),
    ], style={
        "background": NB_WHITE, "border": f"1px solid {NB_CRIMSON}55",
        "borderTop": f"3px solid {NB_CRIMSON}",
        "borderRadius": "12px", "padding": "16px",
        "boxShadow": "0 2px 12px rgba(155,27,48,0.10)",
        "marginTop": "12px",
    })


# ─────────────────────────────────────────────
# FIGURAS — CONVERSIÓN (notebook colors)
# ─────────────────────────────────────────────

def fig_conv_funnel(conversion_data):
    """Funnel de destino de alarmas generadas por telemetría."""
    f = conversion_data['funnel']
    colors_f = ['#457B9D', '#2A9D8F', '#F4A261', '#9B1B30']

    fig = go.Figure(go.Funnel(
        y=f['etapas'], x=f['pcts'],
        textposition='inside',
        text=[f"<b>{p:.1f}%</b>  ({v:,})" for p, v in zip(f['pcts'], f['vals'])],
        marker=dict(color=colors_f, line=dict(color='white', width=2)),
        connector=dict(line=dict(color='#e5e7eb', width=1.5, dash='dot')),
        hovertemplate='<b>%{y}</b><br>%{x:.1f}% del total<extra></extra>'
    ))
    en_red = f['vals'][1]; total = f['vals'][0]
    fig.add_annotation(
        x=0, y=-0.18, xref='paper', yref='paper',
        text=f"<b>Solo {en_red/max(total,1)*10:.1f} de cada 10 alarmas terminan en servicio en la red CNH</b>",
        showarrow=False,
        font=dict(size=12, color='#2A9D8F', family=NB_FONT),
        bgcolor='white', bordercolor='#2A9D8F', borderwidth=2, borderpad=8,
        xanchor='left', yanchor='top'
    )
    fig.update_layout(
        title=dict(
            text="<b>Destino de alarmas generadas por telemetría</b>",
            font=dict(size=18, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=460, margin=dict(t=100, b=100, l=180, r=60),
        font_family=NB_FONT,
    )
    return fig


def fig_conv_top_bottom(conversion_data):
    """Top 3 vs Bottom 3 distribuidores por conversión."""
    from plotly.subplots import make_subplots as _msp
    top3    = conversion_data['top3']
    bottom3 = conversion_data['bottom3']

    fig = _msp(rows=1, cols=2,
               subplot_titles=['🟢 Top 3 — mayor conversión',
                                '🔴 Top 3 — menor conversión'],
               column_widths=[0.5, 0.5])

    fig.add_trace(go.Bar(
        y=top3['distribuidor'], x=top3['tasa_conv_pct'],
        orientation='h',
        marker=dict(color=NB_TEAL, line=dict(color='white', width=2)),
        text=[f"<b>{t:.1f}%</b>  retraso: {r:.0f}d"
              for t, r in zip(top3['tasa_conv_pct'], top3['moda_retraso'])],
        textposition='outside',
        textfont=dict(size=10, color=NB_NAVY, family=NB_FONT),
        showlegend=False,
        hovertemplate='<b>%{y}</b><br>Conversión: %{x:.1f}%<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=bottom3['distribuidor'], x=bottom3['tasa_conv_pct'],
        orientation='h',
        marker=dict(color=NB_CRIMSON, line=dict(color='white', width=2)),
        text=[f"<b>{t:.1f}%</b>  retraso: {r:.0f}d"
              for t, r in zip(bottom3['tasa_conv_pct'], bottom3['moda_retraso'])],
        textposition='outside',
        textfont=dict(size=10, color=NB_NAVY, family=NB_FONT),
        showlegend=False,
        hovertemplate='<b>%{y}</b><br>Conversión: %{x:.1f}%<extra></extra>'
    ), row=1, col=2)

    fig.add_annotation(
        x=0.5, y=-0.28, xref='paper', yref='paper',
        text="🚨 <b>Sobrecarga proyectada:</b>  AGTRAC +41% · TEPSA +20% · MADISA +15% · ATN +12%",
        showarrow=False,
        font=dict(size=10, color=NB_CRIMSON, family=NB_FONT),
        bgcolor='rgba(254,226,226,0.9)', bordercolor=NB_CRIMSON,
        borderwidth=1.5, borderpad=6, xanchor='center', yanchor='top'
    )
    fig.update_layout(
        title=dict(
            text="<b>Los mejores vs los peores distribuidores</b>",
            font=dict(size=18, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=380, margin=dict(t=100, b=110, l=30, r=30),
        font_family=NB_FONT,
    )
    fig.update_xaxes(ticksuffix='%', showgrid=True, gridcolor=NB_LGRAY,
                     zeroline=False, tickfont=dict(size=10, family=NB_FONT))
    x_max_top = top3['tasa_conv_pct'].max() * 1.5 if len(top3) > 0 else 80
    x_max_bot = bottom3['tasa_conv_pct'].max() * 2  if len(bottom3) > 0 else 20
    fig.update_xaxes(range=[0, x_max_top], row=1, col=1)
    fig.update_xaxes(range=[0, x_max_bot], row=1, col=2)
    fig.update_yaxes(tickfont=dict(size=11, family=NB_FONT), showgrid=False)
    return fig


def fig_conv_dual(conversion_data):
    """Conversión vs retraso modal (ejes duales)."""
    from plotly.subplots import make_subplots as _msp
    dist_dual = conversion_data['dist_dual']
    prom_conv = conversion_data['prom_conv']

    fig = _msp(specs=[[{"secondary_y": True}]])

    colors_bar = [NB_CRIMSON if t < 10 else '#F4A261' if t < 20 else NB_GOLD if t < 35 else NB_TEAL
                  for t in dist_dual['tasa_conv_pct']]

    fig.add_trace(go.Bar(
        name='Tasa de conversión',
        x=dist_dual['distribuidor'], y=dist_dual['tasa_conv_pct'],
        marker=dict(color=colors_bar, line=dict(color='white', width=1.5)),
        text=[f"{v:.1f}%" for v in dist_dual['tasa_conv_pct']],
        textposition='outside',
        textfont=dict(size=8, family=NB_FONT, color=NB_NAVY),
        hovertemplate='<b>%{x}</b><br>Conversión: %{y:.1f}%<extra></extra>',
        opacity=0.9,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        name='Retraso modal (días)',
        x=dist_dual['distribuidor'], y=dist_dual['moda_retraso'],
        mode='lines+markers',
        line=dict(color=NB_NAVY, width=2.5, dash='dot'),
        marker=dict(size=9, color=NB_NAVY, line=dict(color='white', width=2)),
        hovertemplate='<b>%{x}</b><br>Retraso modal: %{y:.0f} días<extra></extra>',
    ), secondary_y=True)

    fig.add_hline(y=prom_conv, line_color=NB_TEAL, line_width=1.5, line_dash='dash',
                  secondary_y=False,
                  annotation=dict(
                      text=f"Prom. red {prom_conv:.1f}%",
                      font=dict(size=10, color=NB_TEAL, family=NB_FONT),
                      showarrow=False, x=0.75, xref='paper',
                      xanchor='left', yanchor='bottom'
                  ))

    fig.update_layout(
        title=dict(
            text="<b>Conversión vs retraso modal por distribuidor</b>",
            font=dict(size=18, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=440, margin=dict(t=100, b=90, l=60, r=80),
        font_family=NB_FONT,
        xaxis=dict(tickfont=dict(size=10, family=NB_FONT), tickangle=-35, showgrid=False),
        legend=dict(orientation='h', y=-0.28, x=0, font=dict(size=11, family=NB_FONT)),
        bargap=0.3,
    )
    max_retraso = dist_dual['moda_retraso'].max() if len(dist_dual) > 0 else 160
    fig.update_yaxes(title_text="% de conversión", ticksuffix='%',
                     range=[0, 70], showgrid=True, gridcolor=NB_LGRAY,
                     zeroline=False, tickfont=dict(size=11, family=NB_FONT),
                     secondary_y=False)
    fig.update_yaxes(title_text="Retraso modal (días)", range=[0, max_retraso * 1.3],
                     showgrid=False, zeroline=False,
                     tickfont=dict(size=11, family=NB_FONT), secondary_y=True)
    return fig


def fig_conv_sobrecarga(conversion_data):
    """Distribuidores con sobrecarga proyectada (barras horizontales)."""
    distribuidores = conversion_data['distribuidores_sc']
    alarmas_proy   = conversion_data['alarmas_proy']
    umbral         = conversion_data['umbral_cap']

    colores = [NB_CRIMSON if a > umbral else NB_TEAL for a in alarmas_proy]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=distribuidores, x=alarmas_proy,
        orientation='h',
        marker=dict(color=colores, line=dict(color='white', width=1.5)),
        text=[f"<b>{v}</b>" for v in alarmas_proy],
        textposition='outside',
        textfont=dict(size=11, color=NB_NAVY, family=NB_FONT),
        showlegend=False,
        hovertemplate='<b>%{y}</b><br>Alarmas proyectadas: %{x}<extra></extra>',
    ))
    fig.add_vline(x=umbral, line_color=NB_NAVY, line_width=1.5, line_dash='dash',
                  annotation=dict(
                      text=f"Umbral {umbral} alarmas/mes",
                      font=dict(size=10, color=NB_NAVY, family=NB_FONT),
                      showarrow=False, x=umbral, y=1.05, yref='paper',
                      xanchor='center'
                  ))
    fig.update_layout(
        title=dict(
            text='<b>Distribuidores con sobrecarga proyectada</b>',
            font=dict(size=17, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=380, margin=dict(t=80, b=60, l=100, r=80),
        font_family=NB_FONT,
        xaxis=dict(title='Alarmas proyectadas próximo mes',
                   gridcolor=NB_LGRAY, zeroline=False,
                   tickfont=dict(size=11, family=NB_FONT)),
        yaxis=dict(tickfont=dict(size=11, family=NB_FONT), showgrid=False,
                   autorange='reversed'),
    )
    return fig


def fig_conv_monetizacion(conversion_data):
    """Potencial de monetización combinado INS-03 + INS-NEW."""
    from plotly.subplots import make_subplots as _msp
    mon = conversion_data['monetizacion']
    labels_clean = ['INS-03\nCampaña 70/30', 'INS-NEW\nDistribuidores']
    colors_bar   = [NB_TEAL, NB_CRIMSON]

    fig = _msp(rows=1, cols=2,
               column_widths=[0.5, 0.5],
               subplot_titles=["Servicios recuperables", "Ingreso potencial (MXN)"])

    fig.add_trace(go.Bar(
        x=labels_clean, y=mon['servicios'],
        marker=dict(color=colors_bar, line=dict(color='white', width=2)),
        text=[f"<b>{v:,}</b>" for v in mon['servicios']],
        textposition='inside',
        textfont=dict(size=14, family=NB_FONT, color='white'),
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Servicios: %{y:,}<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=labels_clean, y=mon['ingresos'],
        marker=dict(color=colors_bar, line=dict(color='white', width=2), opacity=0.85),
        text=[f"<b>${v/1e6:.2f}M</b>" for v in mon['ingresos']],
        textposition='inside',
        textfont=dict(size=14, family=NB_FONT, color='white'),
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>$%{y:,.0f} MXN<extra></extra>'
    ), row=1, col=2)

    total_svc = mon['total_svc']; total_ing = mon['total_ing']
    fig.update_layout(
        title=dict(
            text=f"<b>Potencial de monetización — Ticket promedio: ${mon['ticket']:,} MXN</b>",
            font=dict(size=16, family=NB_FONT, color=NB_NAVY), x=0.03, y=0.97
        ),
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        height=420, margin=dict(t=100, b=80, l=60, r=60),
        font_family=NB_FONT,
        annotations=[dict(
            x=0.5, y=-0.18, xref='paper', yref='paper',
            text=f"Total estimado: {total_svc:,} servicios = <b>${total_ing:,.0f} MXN</b>",
            showarrow=False, font=dict(size=12, color=NB_GRAY, family=NB_FONT),
            xanchor='center',
        )]
    )
    max_svc = max(mon['servicios']) if mon['servicios'] else 1
    max_ing = max(mon['ingresos'])  if mon['ingresos']  else 1
    fig.update_yaxes(showgrid=True, gridcolor=NB_LGRAY, zeroline=False,
                     range=[0, max_svc * 1.3], row=1, col=1)
    fig.update_yaxes(tickprefix='$', tickformat=',', showgrid=True,
                     gridcolor=NB_LGRAY, zeroline=False,
                     range=[0, max_ing * 1.3], row=1, col=2)
    fig.update_xaxes(tickfont=dict(size=11, family=NB_FONT), showgrid=False)
    return fig


def card_monetizacion_conversion_html(conversion_data):
    """Tarjeta de potencial de monetización campaña 70/30 para sección Conversión."""
    mon = conversion_data['monetizacion']
    rec_ins03  = mon['servicios'][0]
    ingreso_03 = mon['ingresos'][0]
    return html.Div([
        html.Div("💰  POTENCIAL DE MONETIZACIÓN", style={
            "fontSize": "9px", "color": NB_CRIMSON,
            "letterSpacing": "2px", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.Div("Campaña 70/30", style={
            "fontSize": "14px", "fontWeight": "800",
            "color": NB_NAVY, "marginBottom": "4px"
        }),
        html.Div([
            html.Span(f"${ingreso_03/1e6:.2f}M", style={
                "fontSize": "32px", "fontWeight": "900",
                "color": NB_TEAL, "fontFamily": "monospace"
            }),
            html.Span(" MXN", style={"fontSize": "13px", "color": NB_GRAY, "marginLeft": "4px"}),
        ]),
        html.Div(f"{rec_ins03:,} servicios adicionales estimados",
                 style={"fontSize": "11px", "color": NB_GRAY, "marginTop": "4px"}),
        html.Div([
            html.Span("Ticket promedio = $15,000 mxn", style={
                "fontSize": "11px", "color": NB_CRIMSON,
                "fontWeight": "700", "fontStyle": "italic"
            }),
        ], style={
            "marginTop": "10px", "padding": "8px 10px",
            "background": "rgba(155,27,48,0.06)",
            "border": f"1px solid {NB_CRIMSON}44",
            "borderRadius": "6px",
        }),
        html.Div("Mejora +20% relativo sobre tasa actual de conversión en meses óptimos.",
                 style={"fontSize": "10px", "color": NB_GRAY, "marginTop": "8px"}),
    ], style={
        "background": NB_WHITE, "border": f"1px solid {NB_CRIMSON}55",
        "borderTop": f"3px solid {NB_CRIMSON}",
        "borderRadius": "12px", "padding": "16px",
        "boxShadow": "0 2px 12px rgba(155,27,48,0.10)",
        "marginTop": "12px",
    })


# ─────────────────────────────────────────────
# FIGURAS — RETENCIÓN 600h (notebook colors)
# ─────────────────────────────────────────────

def fig_retencion_600h(retencion_600_data):
    """Subplots: unidades que llegaron a 600h y cumplimiento por grupo."""
    from plotly.subplots import make_subplots as _msp
    d = retencion_600_data
    n_cum = d['n_cumplio']; n_inc = d['n_incumplio']
    total  = d['total_600']
    pct_c  = d['pct_cumplio'];  pct_i  = d['pct_incumplio']
    tc600  = d['tasa_cumplio_en_600']; ti600 = d['tasa_incumplio_en_600']

    fig = _msp(rows=1, cols=2,
               subplot_titles=(
                   '<b>Unidades que llegaron a las 600h<br><sup>Comportamiento en mant_300</sup></b>',
                   '<b>De las que llegaron a 600h, ¿cuántas cumplieron ese servicio?<br><sup>Según comportamiento en mant_300</sup></b>'
               ))

    fig.add_trace(go.Bar(
        x=['Cumplió mant_300', 'Incumplió mant_300'],
        y=[n_cum, n_inc],
        marker_color=[NB_GREEN, NB_RED_BAR],
        marker_line_color='white', marker_line_width=1, opacity=0.88,
        text=[f'{n_cum:,}<br>({pct_c:.1%})', f'{n_inc:,}<br>({pct_i:.1%})'],
        textposition='outside',
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=['Cumplió mant_300', 'Incumplió mant_300'],
        y=[tc600, ti600],
        marker_color=[NB_GREEN, NB_RED_BAR],
        marker_line_color='white', marker_line_width=1, opacity=0.88,
        text=[f'{tc600:.1%}', f'{ti600:.1%}'],
        textposition='outside',
        showlegend=False,
    ), row=1, col=2)

    fig.add_hline(y=0.50, line_dash='dot', line_color='#2c3e50', line_width=1.2,
                  annotation_text='50% referencia', annotation_position='top right',
                  row=1, col=2)

    # Legend traces
    fig.add_trace(go.Bar(x=[None], y=[None], marker_color=NB_GREEN,
                         name='<b>Cumplió mant_300</b>', showlegend=True))
    fig.add_trace(go.Bar(x=[None], y=[None], marker_color='#e74c3c',
                         name='<b>Incumplió mant_300</b>', showlegend=True))

    fig.update_layout(
        paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
        template='plotly_white',
        height=440, margin=dict(t=80, b=110),
        font_family=NB_FONT,
        yaxis=dict(range=[0, max(n_cum, n_inc) * 1.25]),
        yaxis2=dict(tickformat='.0%', range=[0, 1.15]),
        legend=dict(orientation='h', yanchor='bottom', y=-0.32,
                    xanchor='center', x=0.5),
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def make_sidebar(C, pathname=None):
    nav_items = [
        ("◈", "Overview",         "overview"),
        ("⬡", "Agricultura",      "agricultura"),
        ("◎", "Distribuidores",   "distribuidores"),
        ("⊞", "Retención",        "retencion"),
        ("⊙", "Contacto Óptimo", "contacto"),
        ("⬢", "Conversión",       "conversion"),
    ]
    
    links = []
    for icon, label, page in nav_items:
        is_active = (pathname == f"/{page}") or (page == "overview" and pathname in ["/", "", None])
        
        bg = "rgba(144, 12, 14, 0.15)" if is_active else "transparent"
        border_left = f"4px solid {C['accent']}" if is_active else "4px solid transparent"
        font_weight = "700" if is_active else "600"
        box_shadow = f"inset -2px 0 8px rgba(144, 12, 14, 0.05), 0 4px 12px rgba(144, 12, 14, 0.08)" if is_active else "none"
        
        links.append(
            dcc.Link(
                html.Div([
                    html.Span(icon, style={"fontSize": "14px", "marginRight": "10px", "color": C["accent2"] if is_active else C["accent"]}),
                    html.Span(label, style={"fontSize": "12px", "fontWeight": font_weight,
                                            "letterSpacing": "0.5px", "color": C["text"]}),
                ], className="nav-item",
                   style={
                       "display": "flex",
                       "alignItems": "center",
                       "padding": "10px 16px",
                       "cursor": "pointer",
                       "borderRadius": "0 6px 6px 0",
                       "margin": "2px 8px 2px 0",
                       "transition": "all 0.15s",
                       "background": bg,
                       "borderLeft": border_left,
                       "boxShadow": box_shadow,
                   }),
                href=f"/{page}", refresh=False
            )
        )

    return html.Div([
        html.Div([
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/CNH_Industrial.svg/500px-CNH_Industrial.svg.png",
                style={
                    "height": "26px",
                    "filter": "brightness(0) invert(1)" if C["name"] == "dark" else "brightness(0)",
                    "opacity": "0.92",
                    "display": "block",
                    "marginBottom": "6px",
                }
            ),
            html.Div("AFTERMARKET INTEL", style={"fontSize":"8px","color":C["muted"],
                                                "letterSpacing":"2px","marginTop":"0px"}),
        ], style={"padding":"20px 16px 16px","borderBottom":f"1px solid {C['border']}"}),

        html.Div(links, style={"padding":"12px 0"}),

        html.Div("v1.0 · Mayo 2026", style={"position":"absolute","bottom":"16px","left":"16px",
                                             "fontSize":"9px","color":C["muted"]}),
    ], style={
        "width":"180px","minWidth":"180px","height":"100vh",
        "background": C["sidebar"],
        "borderRight":f"1px solid {C['border']}",
        "position":"fixed","left":"0","top":"0","zIndex":"100",
        "display":"flex","flexDirection":"column","overflow":"hidden",
        "transition":"background 0.3s",
    })

def make_topbar(page_title, C):
    return html.Div([
        html.Span(page_title, style={"fontSize":"14px","fontWeight":"700","color":C["text"],
                                     "textTransform":"uppercase","letterSpacing":"2px"}),
        html.Div([
            html.Span("● LIVE", style={"color":C["accent"],"fontSize":"10px",
                                       "marginRight":"16px","fontFamily":FONT_MONO}),
            html.Div(id="clock", style={"fontSize":"11px","color":C["muted"],
                                        "fontFamily":FONT_MONO}),
        ], style={"display":"flex","alignItems":"center"}),
    ], style={
        "display":"flex","justifyContent":"space-between","alignItems":"center",
        "padding":"12px 20px","borderBottom":f"2px solid {C['accent']}",
        "background":C["bg"],"marginBottom":"16px",
        "transition":"background 0.3s",
    })








































# ─────────────────────────────────────────────
# PÁGINAS
# ─────────────────────────────────────────────
def page_overview(C):
    status_counts = units_df["status"].value_counts()
    brand_counts  = units_df["brand"].value_counts()
    return html.Div([
        make_topbar("Dashboard Overview", C),
        html.Div([
            # Central column
            html.Div([
                html.Div([
                    kpi_card("Odds Ratio Incumplimiento", "26.4×",    "p < 0.0001",          C["accent2"], C=C),
                    kpi_card("Retorno tras 600h",          "4.9%",    "Punto de quiebre",     C["accent2"], C=C),
                    kpi_card("Abandono Diciembre",         "80.3%",   "vs 51.1% Abril",       C["warn"],    C=C),
                    kpi_card("R² Modelo Log.",             "0.3618",  "Regresión Logística",  C["accent3"], C=C),
                    kpi_card("Reducción retraso>30d",      "76.2%↓",  "OR = 0.238",           C["accent"],  C=C),
                    kpi_card("Punto no retorno",           "2+ ext.", "Retorno 12.1%",        C["accent2"], C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),

                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_funnel(C), config={"displayModeBar":False}),
                                         "Embudo de retención aftermarket", C)],
                             style={"flex":"1","minWidth":"300px"}),
                    html.Div([chart_card(dcc.Graph(figure=fig_serie_abandono(C), config={"displayModeBar":False}),
                                         "Tasa de abandono mensual 2024–2025", C)],
                             style={"flex":"1","minWidth":"300px"}),
                ], style={"display":"flex","gap":"12px","marginBottom":"12px","flexWrap":"wrap"}),

                make_parcoords_container(C),
                html.Div(style={"height":"12px"}),

                # ── VIZ 2: Cluster de riesgo ──────────────────────────────────────
                chart_card(
                    dcc.Graph(
                        figure=fig_cluster_riesgo(C),
                        config={"displayModeBar": False},
                    ),
                    title="Segmentación de Unidades por Riesgo de Abandono · INS-01 & INS-02",
                    C=C,
                ),
                html.Div(style={"height":"12px"}),

                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_cumplimiento_zona(C), config={"displayModeBar":False}),
                                        "Tasa de cumplimiento por zona", C)],
                            style={"flex":"1","minWidth":"280px"}),
                    html.Div([chart_card(dcc.Graph(figure=fig_retrasos(C), config={"displayModeBar":False}),
                                        "Abandono según nivel de retraso del servicio", C)],
                            style={"flex":"1","minWidth":"280px"}),
                ], style={"display":"flex","gap":"12px","flexWrap":"wrap"}),

            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            # Right column
            html.Div([
                chart_card(dcc.Graph(figure=fig_mapa_unidades(C), config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "displaylogo": False,
                }),
                           "Posición geográfica de unidades", C),
                html.Div(style={"height":"12px"}),

                html.Div([
                    section_title("Flota activa", "datos en tiempo real", C),
                    *[html.Div([
                        html.Span(label, style={"fontSize":"11px","color":C["muted"],"flex":"1"}),
                        html.Span(str(val), style={"fontSize":"12px","color":C["text"],
                                                   "fontFamily":FONT_MONO,"fontWeight":"700"}),
                    ], style={"display":"flex","justifyContent":"space-between",
                              "padding":"6px 0","borderBottom":f"1px solid {C['border']}"})
                      for label, val in [
                        ("Unidades totales",     n_units),
                        ("Activas",              int(status_counts.get("Activa", 0))),
                        ("Con alarma servicio",  int(status_counts.get("Alarma servicio", 0))),
                        ("En taller",            int(status_counts.get("En taller", 0))),
                        ("Sin telemetría",       int(status_counts.get("Sin telemetría", 0))),
                        ("── Agrícolas ──",      ""),
                        ("Case IH",              int(brand_counts.get("Case IH", 0))),
                        ("New Holland AG",       int(brand_counts.get("New Holland AG", 0))),
                        ("── Construcción ──",   ""),
                        ("Case CE",              int(brand_counts.get("Case CE", 0))),
                        ("New Holland CE",       int(brand_counts.get("New Holland CE", 0))),
                    ]],
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"10px","padding":"14px","transition":"background 0.3s"}),

                html.Div(style={"height":"12px"}),
                chart_card(dcc.Graph(figure=fig_radar_zonas(C), config={"displayModeBar":False}),
                           "Perfil estratégico por zona", C),

            ], style={"width":"320px","minWidth":"320px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),
        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),

        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])


def page_agricultura(C):
    now = datetime.now()
    pv_end   = datetime(2026, 10, 31)
    oi_start = datetime(2026, 11, 1)
    days_to_oi         = (oi_start - now).days
    days_remaining_pv  = (pv_end - now).days

    return html.Div([
        make_topbar("Agricultura · Ciclos & Mantenimiento", C),
        html.Div([
            html.Div([
                # Ciclos
                html.Div([
                    section_title("Calendario Agrícola 2026", "Ciclos nacionales de referencia", C),
                    html.Div([
                        html.Div([
                            html.Div("PRIMAVERA–VERANO",
                                     style={"fontSize":"9px","color":C["accent"],"letterSpacing":"2px","fontWeight":"700"}),
                            html.Div("15 Abr → 31 Oct 2026",
                                     style={"fontSize":"13px","color":C["text"],"fontWeight":"600",
                                            "margin":"4px 0","fontFamily":FONT_MONO}),
                            html.Div([
                                html.Span("Días restantes: ", style={"color":C["muted"],"fontSize":"11px"}),
                                html.Span(str(max(0, days_remaining_pv)),
                                          style={"color":C["accent"],"fontSize":"18px","fontWeight":"700",
                                                 "fontFamily":FONT_MONO}),
                            ]),
                            html.Div("Periodo óptimo contacto: ABR–JUN",
                                     style={"fontSize":"10px","color":C["accent"],"marginTop":"6px",
                                            "padding":"3px 8px","background":"rgba(144,12,14,0.10)",
                                            "borderRadius":"4px","display":"inline-block"}),
                        ], style={"flex":"1","background":C["card"],"border":f"1px solid {C['accent']}44",
                                  "borderLeft":f"3px solid {C['accent']}","borderRadius":"8px","padding":"14px"}),

                        html.Div([
                            html.Div("OTOÑO–INVIERNO",
                                     style={"fontSize":"9px","color":C["warn"],"letterSpacing":"2px","fontWeight":"700"}),
                            html.Div("01 Nov → 28 Feb 2027",
                                     style={"fontSize":"13px","color":C["text"],"fontWeight":"600",
                                            "margin":"4px 0","fontFamily":FONT_MONO}),
                            html.Div([
                                html.Span("Inicia en: ", style={"color":C["muted"],"fontSize":"11px"}),
                                html.Span(str(max(0, days_to_oi)),
                                          style={"color":C["warn"],"fontSize":"18px","fontWeight":"700",
                                                 "fontFamily":FONT_MONO}),
                                html.Span(" días", style={"color":C["muted"],"fontSize":"11px"}),
                            ]),
                            html.Div("Mayor riesgo abandono: SEP–DIC",
                                     style={"fontSize":"10px","color":C["warn"],"marginTop":"6px",
                                            "padding":"3px 8px","background":"rgba(130,121,112,0.12)",
                                            "borderRadius":"4px","display":"inline-block"}),
                        ], style={"flex":"1","background":C["card"],"border":f"1px solid {C['warn']}44",
                                  "borderLeft":f"3px solid {C['warn']}","borderRadius":"8px","padding":"14px"}),

                        html.Div([
                            html.Div("⚠  ALERTA CRÍTICA",
                                     style={"fontSize":"9px","color":C["accent2"],"letterSpacing":"2px","fontWeight":"700"}),
                            html.Div("Diciembre = 80.3%",
                                     style={"fontSize":"20px","color":C["accent2"],"fontWeight":"900",
                                            "fontFamily":FONT_MONO,"margin":"4px 0"}),
                            html.Div("tasa de abandono", style={"fontSize":"10px","color":C["muted"]}),
                            html.Div("Activar campañas SEP–NOV",
                                     style={"fontSize":"10px","color":C["accent2"],"marginTop":"6px",
                                            "padding":"3px 8px","background":"rgba(107,10,11,0.12)",
                                            "borderRadius":"4px","display":"inline-block"}),
                        ], style={"flex":"1","background":C["card"],"border":f"1px solid {C['accent2']}44",
                                  "borderLeft":f"3px solid {C['accent2']}","borderRadius":"8px","padding":"14px"}),
                    ], style={"display":"flex","gap":"12px","marginBottom":"16px","flexWrap":"wrap"}),
                ], style={"background":C["card2"],"border":f"1px solid {C['border']}",
                          "borderRadius":"10px","padding":"16px","marginBottom":"12px"}),
                
                

                make_parcoords_container(C),
            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            html.Div([
                html.Div([
                    section_title("Comportamiento por Intervalo", C=C),
                    *[html.Div([
                        html.Div([
                            html.Span(iv, style={"fontSize":"13px","color":C["text"],
                                                  "fontFamily":FONT_MONO,"fontWeight":"700"}),
                            html.Span(" cumplimiento", style={"fontSize":"10px","color":C["muted"],"marginLeft":"6px"}),
                        ]),
                        html.Div([
                            html.Div(style={
                                "height":"6px","borderRadius":"3px","margin":"6px 0",
                                "background":f"linear-gradient(90deg, {C['accent']} {p}%, {C['border']} {p}%)",
                            }),
                            html.Div([
                                html.Span(f"{p}%", style={"color":C["accent"],"fontFamily":FONT_MONO,
                                                           "fontSize":"12px","fontWeight":"700"}),
                                html.Span(f" / {100-p:.0f}% abandona",
                                          style={"color":C["accent2"],"fontSize":"10px","marginLeft":"8px"}),
                            ]),
                        ]),
                        html.Div("⚠ Punto de quiebre" if iv == "600h" else
                                 "⚡ Intervalo crítico" if iv == "300h" else "",
                                 style={"fontSize":"9px","color":C["warn"],"marginTop":"2px",
                                        "fontWeight":"600","letterSpacing":"0.5px"}) if iv in ["300h","600h"] else None,
                        html.Div(style={"height":"12px"}),
                    ]) for iv, p in zip(intervalos, cumplimiento_intervalo)],
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"10px","padding":"16px","marginBottom":"12px"}),

                html.Div([
                    section_title("Ventana de contacto", C=C),
                    *[html.Div([
                        html.Div([
                            html.Span(zona, style={"fontSize":"11px","color":C["text"],"fontWeight":"600"}),
                            html.Span(mes_optimo[zona][0],
                                      style={"fontSize":"11px","color":C["accent"],"fontFamily":FONT_MONO,
                                             "fontWeight":"700","marginLeft":"8px"}),
                        ]),
                        html.Div(f"P(cumple) = {mes_optimo[zona][1]*100:.0f}%",
                                 style={"fontSize":"10px","color":C["muted"],"marginTop":"2px"}),
                        html.Div(style={"height":"8px"}),
                    ]) for zona in mes_optimo],
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"10px","padding":"16px","marginBottom":"12px"}),

                chart_card(dcc.Graph(figure=fig_mapa_unidades(C), config={"displayModeBar":False},
                                     style={"height":"220px"}), "Unidades agrícolas activas", C),
            ], style={"width":"280px","minWidth":"280px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),
        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])


def page_distribuidores(C):
    return html.Div([
        make_topbar("Distribuidores · Capacidad & Proyección", C),
        html.Div([
            html.Div([
                html.Div([
                    kpi_card("Umbral capacidad",           "46.4",  "alarmas/mes (150%)", C["warn"],    C=C),
                    kpi_card("Distribuidores en riesgo",   "4",     "AGTRAC, TEPSA...",   C["accent2"], C=C),
                    kpi_card("Mayor proyección",           "96",    "AGTRAC +41%",        C["accent2"], C=C),
                    kpi_card("F ANOVA",                    "3.04",  "p < 0.001",          C["accent3"], C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),

                chart_card(dcc.Graph(figure=fig_distribuidores(C), config={"displayModeBar":False}),
                           "Proyección de alarmas próximo mes por distribuidor (SES)", C),
                html.Div(style={"height":"12px"}),

                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_retrasos(C), config={"displayModeBar":False}),
                                         "Tasa de abandono por nivel de retraso", C)],
                             style={"flex":"1"}),
                    html.Div([chart_card(dcc.Graph(figure=fig_cumplimiento_zona(C), config={"displayModeBar":False}),
                                         "Cumplimiento por zona", C)],
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"12px","flexWrap":"wrap"}),
            ], style={"flex":"1","padding":"0 20px 20px 20px","overflowY":"auto"}),
        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])


def page_retencion(C, retencion_600_data=None):
    if retencion_600_data is None:
        # fallback sintético
        retencion_600_data = {
            'n_cumplio': 271, 'n_incumplio': 320, 'total_600': 591,
            'pct_cumplio': 0.458, 'pct_incumplio': 0.542,
            'tasa_cumplio_en_600': 0.63, 'tasa_incumplio_en_600': 0.06,
        }
    return html.Div([
        make_topbar("Retención · Análisis de Abandono", C),
        html.Div([
            html.Div([
                html.Div([
                    kpi_card("OR incumplimiento",  "26.4×",   "p < 0.0001",          C["accent2"], C=C),
                    kpi_card("Punto quiebre",       "600h",    "Retorno 4.9%",        C["accent2"], C=C),
                    kpi_card("Punto no retorno",   "≥2 ext.", "Retorno caída 12.1%", C["warn"],    C=C),
                    kpi_card("R² Logística",        "0.3618",  "IC 95% estable",      C["accent3"], C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),

                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_funnel(C), config={"displayModeBar":False}),
                                         "Embudo retención – puntos de quiebre", C)],
                             style={"flex":"1"}),
                    html.Div([chart_card(dcc.Graph(figure=fig_intervalos_ag(C), config={"displayModeBar":False}),
                                         "Cumplimiento por intervalo", C)],
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"12px","marginBottom":"12px","flexWrap":"wrap"}),

                chart_card(dcc.Graph(figure=fig_serie_abandono(C), config={"displayModeBar":False}),
                           "Serie temporal abandono mensual 2024–2025 + SARIMA", C),
                html.Div(style={"height":"12px"}),

                # ── NUEVAS: Unidades 600h ──────────────────────────────
                html.Div([
                    html.Div(["▸ ", html.Span("Unidades que llegaron a las 600h de operación",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_retencion_600h(retencion_600_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

            ], style={"flex":"1","padding":"0 20px 20px 20px","overflowY":"auto"}),
        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])

def page_contacto(C, contacto_data=None, conversion_data=None):
    """Sección Contacto Óptimo."""
    # Fallback si no hay datos del pipeline
    if contacto_data is None:
        import pandas as _pd
        contacto_data = {
            'pivot': _pd.DataFrame(),
            'hm': _pd.DataFrame(),
            'mes_top': {'Noroeste':('Jun',64,'Abr',52),'Centro Occidente':('Jun',55,'May',50),
                        'Centro':('Jun',53,'May',47),'Sur-Sureste':('Jun',51,'May',45),
                        'Noreste':('Jun',40,'May',35)},
            'df_estrategia': _pd.DataFrame({
                'zona':['Noroeste','Centro Occidente','Centro','Sur-Sureste','Noreste'],
                'mes_opt':['Jun','Jun','Jun','Jun','Jun'],
                'pct_opt':[64,55,53,51,40],
                'mes_2do':['Abr','May','May','May','May'],
                'pct_2do':[52,50,47,45,35],
            }),
            'df_tasa': _pd.DataFrame({
                'intervalo':['mant_50','mant_300','mant_600','mant_900','mant_1200',
                             'mant_1500','mant_1800','mant_2100','mant_2400'],
                'tasa_incumple':[0.47,0.58,0.68,0.75,0.80,0.85,0.88,0.91,0.93],
                'n':[500]*9,
            }),
            'orden_zonas':['Noroeste','Centro Occidente','Centro','Sur-Sureste','Noreste'],
            'orden_meses':['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        }

    mon_data = conversion_data['monetizacion'] if conversion_data else None

    return html.Div([
        make_topbar("Contacto Óptimo · Ventana de Intervención", C),
        html.Div([
            # ── Columna principal ──────────────────────────────────────
            html.Div([
                html.Div([
                    kpi_card("Mes Óptimo",     "Junio",  "Todas las zonas",         "#2A9D8F",  C=C),
                    kpi_card("AUC XGBoost",    "0.7371", "Prescriptiva 1",          C["accent3"], C=C),
                    kpi_card("Accuracy",       "68.4%",  "Falla 31.6%",             C["warn"],  C=C),
                    kpi_card("ANOVA F",        "13.53",  "p < 0.0001  Eta²=0.013", C["accent2"], C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),

                # Heatmap receptividad
                html.Div([
                    html.Div(["▸ ", html.Span("Receptividad al Servicio",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_contacto_heatmap(contacto_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # 70/30
                html.Div([
                    html.Div(["▸ ", html.Span("Distribución Recomendada del Esfuerzo Comercial",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_contacto_70_30(contacto_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Tasa incumplimiento
                html.Div([
                    html.Div(["▸ ", html.Span("Tasa de Incumplimiento por Intervalo de Servicio",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_contacto_tasa_incumplimiento(contacto_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            # ── Columna derecha ────────────────────────────────────────
            html.Div([
                card_momento_optimo_html(contacto_data),
                card_monetizacion_contacto_html(contacto_data, mon_data),
            ], style={"width":"300px","minWidth":"300px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),

        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])


def page_conversion(C, conversion_data=None):
    """Sección Conversión."""
    if conversion_data is None:
        import pandas as _pd
        conversion_data = {
            'funnel': {
                'etapas': ['Alarmas generadas','Servicio en red CNH','Fuera de la red','Sin servicio'],
                'vals':   [6770, 1614, 1282, 3874],
                'pcts':   [100, 23.8, 18.9, 57.2],
            },
            'top3': _pd.DataFrame({
                'distribuidor': ['ARBSA','ATC','MTM'],
                'tasa_conv_pct': [55.0, 50.0, 42.0],
                'moda_retraso': [0, 0, 5],
            }),
            'bottom3': _pd.DataFrame({
                'distribuidor': ['ENAGRI','TAPSA','AGTRAC'],
                'tasa_conv_pct': [7.0, 9.5, 10.0],
                'moda_retraso': [149, 78, 86],
            }),
            'dist_dual': _pd.DataFrame({
                'distribuidor': ['ARBSA','ATC','MTM','AGTRAC','TAPSA','ENAGRI'],
                'tasa_conv_pct': [55.0, 50.0, 42.0, 10.0, 9.5, 7.0],
                'moda_retraso': [0, 0, 5, 86, 78, 149],
            }),
            'prom_conv': 25.0,
            'distribuidores_sc': ["AGTRAC","TEPSA","MADISA","ATN","FERTIMEX","AGROMEX","SERVIAG","CAMSA","ARBSA","ENAGRI"],
            'alarmas_proy': [96, 83, 69, 66, 41, 38, 35, 32, 28, 22],
            'umbral_cap': 46.4,
            'monetizacion': {
                'labels': ['INS-03\nCampaña 70/30','INS-NEW\nDistribuidores'],
                'servicios': [200, 150],
                'ingresos': [3000000, 2250000],
                'ticket': 15000,
                'total_svc': 350,
                'total_ing': 5250000,
            },
        }

    return html.Div([
        make_topbar("Conversión · Distribuidores & Monetización", C),
        html.Div([
            # ── Columna izquierda ──────────────────────────────────────
            html.Div([
                html.Div([
                    kpi_card("Alarmas en red CNH", f"{conversion_data['funnel']['pcts'][1]}%",
                             "del total generado",  "#2A9D8F", C=C),
                    kpi_card("Fuera de red",  f"{conversion_data['funnel']['pcts'][2]}%",
                             "talleres externos",    C["accent2"], C=C),
                    kpi_card("Sin realizar",  f"{conversion_data['funnel']['pcts'][3]}%",
                             "sin servicio",         C["warn"],    C=C),
                    kpi_card("ANOVA F",       "3.04",  "p < 0.0001", C["accent3"], C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),

                # Funnel
                html.Div([
                    html.Div(["▸ ", html.Span("Destino de Alarmas Generadas por Telemetría",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_conv_funnel(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Top vs Bottom
                html.Div([
                    html.Div(["▸ ", html.Span("Los Mejores vs los Peores Distribuidores",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_conv_top_bottom(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Conversión vs retraso modal
                html.Div([
                    html.Div(["▸ ", html.Span("Conversión vs Retraso Modal",
                               style={"fontWeight":"700","fontSize":"12px","textTransform":"uppercase",
                                      "letterSpacing":"1.5px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_conv_dual(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            # ── Columna derecha ────────────────────────────────────────
            html.Div([
                # Retención historial externo (HTML estático del notebook)
                html.Div([
                    html.Div("RETENCIÓN — HISTORIAL EXTERNO", style={
                        "fontSize":"9px","color":"#1B2A4A","letterSpacing":"2px",
                        "fontWeight":"700","marginBottom":"12px"
                    }),
                    html.Iframe(
                        srcDoc="""
<div style="font-family:Arial,sans-serif;padding:8px 0;">
  <h4 style="color:#1B2A4A;font-size:13px;margin:0 0 4px 0;font-weight:700;">Retención según historial externo</h4>
  <p style="color:#6B7280;font-size:11px;margin:0 0 16px 0;">El comportamiento del cliente indica el retorno</p>
  <div style="margin-bottom:16px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="min-width:160px;font-size:12px;font-weight:600;color:#1B2A4A;text-align:right;">0 servicios externos</span>
      <div style="flex:1;background:#E5E7EB;border-radius:4px;height:20px;">
        <div style="width:53.8%;background:#2A9D8F;border-radius:4px;height:100%;"></div>
      </div>
      <span style="min-width:46px;font-size:13px;font-weight:700;color:#1B7B6E;">53.8%</span>
    </div>
  </div>
  <div style="margin-bottom:6px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="min-width:160px;font-size:12px;font-weight:600;color:#1B2A4A;text-align:right;">1 servicio externo</span>
      <div style="flex:1;background:#E5E7EB;border-radius:4px;height:20px;">
        <div style="width:30.1%;background:#C9A227;border-radius:4px;height:100%;"></div>
      </div>
      <span style="min-width:46px;font-size:13px;font-weight:700;color:#9A6F00;">30.1%</span>
    </div>
    <div style="margin-left:170px;margin-top:2px;"><span style="font-size:10px;color:#C0392B;font-weight:600;">punto de no retorno</span></div>
  </div>
  <div style="margin-left:170px;margin-bottom:14px;margin-top:4px;background:#FEF9C3;border:1.5px solid #C9A227;border-radius:6px;padding:8px 10px;display:flex;align-items:flex-start;gap:8px;">
    <span style="font-size:16px;line-height:1;">⚡</span>
    <div>
      <span style="font-size:11px;font-weight:700;color:#9A6F00;">Ventana de intervención — cliente aún recuperable</span>
      <p style="font-size:10px;color:#9A6F00;margin:3px 0 0 0;">15 días tras el primer servicio externo</p>
    </div>
  </div>
  <div style="margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="min-width:160px;font-size:12px;font-weight:600;color:#9B1B30;text-align:right;">≥2 servicios externos ▲</span>
      <div style="flex:1;background:#E5E7EB;border-radius:4px;height:20px;">
        <div style="width:11.9%;background:#9B1B30;border-radius:4px;height:100%;"></div>
      </div>
      <span style="min-width:46px;font-size:13px;font-weight:700;color:#9B1B30;">11.9%</span>
    </div>
  </div>
  <div style="margin-left:170px;margin-top:10px;border-top:1px solid #E5E7EB;padding-top:8px;font-size:10px;color:#6B7280;line-height:1.6;">
    OR = 0.0912, p &lt; 0.0001 &nbsp;|&nbsp; IC 95%: [−2.58, −2.21] &nbsp;|&nbsp;
    Diferencia: <strong style="color:#9B1B30;">−41.9 pp en ~90 días</strong>
  </div>
</div>""",
                        style={"border":"none","width":"100%","height":"280px"},
                    ),
                ], style={"background":NB_WHITE,"border":"1px solid #E5E7EB",
                          "borderRadius":"12px","padding":"14px","marginBottom":"12px"}),

                # Sobrecarga proyectada
                html.Div([
                    html.Div(["▸ ", html.Span("Distribuidores con Sobrecarga Proyectada",
                               style={"fontWeight":"700","fontSize":"11px","textTransform":"uppercase",
                                      "letterSpacing":"1px","color":C["text"]})],
                             style={"marginBottom":"8px","paddingBottom":"6px",
                                    "borderBottom":f"1px solid {C['border']}"}),
                    dcc.Graph(figure=fig_conv_sobrecarga(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"14px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Monetización
                card_monetizacion_conversion_html(conversion_data),

            ], style={"width":"360px","minWidth":"360px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),

        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="CNH Aftermarket Intel",
)


# ─────────────────────────────────────────────
# PÁGINA DE CARGA DE ARCHIVOS (pre-despliegue)
# ─────────────────────────────────────────────

FILE_META = {
    "PopulationView_2026.xlsx":              ("◈", "Population View", "Control Room – inventario de unidades activas"),
    "Horas 2024-2025.xlsx":                  ("⬡", "Horas 2024–2025", "Horómetros mensuales por unidad (hojas 2024 / 2025)"),
    "Mantenimientos 2024-2025.xlsx":         ("◎", "Mantenimientos",  "Órdenes de trabajo y estatus de servicios"),
    "Reporte_unidades_dia_anterior.xlsx":    ("⊞", "Unidades Día Ant.","Reporte diario de unidades con horómetro y alertas"),
}

def page_upload(upload_store: dict | None = None, theme: str = "dark"):
    """
    Pantalla inicial de carga de archivos Excel antes de lanzar el dashboard.
    `upload_store` es el dict {canonical_name: {"filename": x, "content": y}} en memoria.
    """
    C = THEMES.get(theme, THEMES["dark"])
    if upload_store is None:
        upload_store = {}

    ID_MAP = {
        "PopulationView_2026.xlsx":           "pop",
        "Horas 2024-2025.xlsx":               "hrs",
        "Mantenimientos 2024-2025.xlsx":       "mnt",
        "Reporte_unidades_dia_anterior.xlsx":  "rep",
    }

    def _file_cell(canonical_name, icon, label, desc):
        file_info  = upload_store.get(canonical_name)
        uploaded   = file_info is not None
        key        = ID_MAP[canonical_name]
        actual_name = file_info.get("filename", "") if uploaded else ""

        # ── Fila de "archivo cargado" (visible solo si uploaded) ────
        loaded_row = html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "20px", "color": C["success"], "marginRight": "14px"}),
                html.Div([
                    html.Div(label,       style={"fontSize": "13px", "fontWeight": "700",
                                                  "color": C["text"], "letterSpacing": "0.3px"}),
                    html.Div(actual_name, style={"fontSize": "10px", "color": C["muted"],
                                                  "fontFamily": FONT_MONO, "marginTop": "2px",
                                                  "wordBreak": "break-all"}),
                    html.Div(desc,        style={"fontSize": "10px", "color": C["muted"], "marginTop": "1px"}),
                ], style={"flex": "1", "minWidth": "0"}),
            ], style={"display": "flex", "alignItems": "center", "flex": "1", "minWidth": "0"}),
            html.Div([
                html.Span("✓ Cargado", style={"fontSize": "10px", "color": C["success"],
                                               "fontFamily": FONT_MONO, "fontWeight": "700",
                                               "marginRight": "12px"}),
                html.Button(
                    "✕ Desacoplar",
                    id=f"btn-detach-{key}",
                    n_clicks=0,
                    style={
                        "background": "transparent",
                        "color": C["danger"],
                        "border": f"1px solid {C['danger']}",
                        "borderRadius": "6px",
                        "padding": "4px 10px",
                        "fontSize": "10px",
                        "fontWeight": "600",
                        "cursor": "pointer",
                        "transition": "all 0.2s",
                    }
                ),
            ], style={"display": "flex", "alignItems": "center",
                      "whiteSpace": "nowrap", "marginLeft": "12px"}),
        ], style={
            "display": "flex" if uploaded else "none",
            "alignItems": "center", "justifyContent": "space-between",
            "padding": "14px 18px",
            "background": "rgba(6,214,160,0.06)",
            "border": "1px solid rgba(6,214,160,0.25)",
            "borderRadius": "10px",
            "transition": "all 0.3s",
        })

        # ── Zona de drop individual (visible solo si NO uploaded) ───
        upload_zone = dcc.Upload(
            id=f"upload-{key}",
            children=html.Div([
                html.Span(icon, style={"fontSize": "20px", "color": C["accent"], "marginRight": "14px"}),
                html.Div([
                    html.Div(label, style={"fontSize": "13px", "fontWeight": "700", "color": C["text"]}),
                    html.Div("Arrastra aquí tu archivo Excel o haz clic para seleccionarlo",
                             style={"fontSize": "11px", "color": C["muted"], "marginTop": "2px"}),
                    html.Div(desc, style={"fontSize": "10px", "color": C["muted"], "marginTop": "1px"}),
                ], style={"textAlign": "left", "flex": "1"}),
            ], style={"display": "flex", "alignItems": "center"}),
            style={
                "border": f"1px dashed {C['border']}",
                "borderRadius": "10px",
                "padding": "14px 18px",
                "background": "rgba(144,12,14,0.02)",
                "cursor": "pointer",
                "transition": "all 0.2s",
                "display": "none" if uploaded else "block",
            },
            multiple=False,
        )

        return html.Div([upload_zone, loaded_row], style={"marginBottom": "10px"})

    file_cells = [_file_cell(fname, *meta) for fname, meta in FILE_META.items()]
    pending    = [f for f in FILE_META if f not in upload_store]
    all_loaded = len(pending) == 0

    return html.Div([
        # ── Fondo ──────────────────────────────────────────────────────
        html.Div(style={
            "position": "fixed", "inset": "0",
            "background": f"radial-gradient(ellipse at 20% 50%, rgba(144,12,14,0.08) 0%, transparent 60%), {C['bg']}",
            "zIndex": "-1",
        }),

        # ── Contenido centrado ─────────────────────────────────────────
        html.Div([

            # Logo + título
            html.Div([
                html.Img(
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/CNH_Industrial.svg/500px-CNH_Industrial.svg.png",
                    style={"height": "32px",
                           "filter": "brightness(0) invert(1)" if theme == "dark" else "brightness(0)",
                           "opacity": "0.9", "marginBottom": "12px"}
                ),
                html.Div("AFTERMARKET INTELLIGENCE", style={
                    "fontSize": "9px", "letterSpacing": "4px",
                    "color": C["muted"], "marginBottom": "4px",
                }),
                html.H2("Cargar archivos de datos", style={
                    "color": C["text"], "fontWeight": "800", "fontSize": "24px",
                    "margin": "0 0 6px 0", "letterSpacing": "-0.5px",
                }),
                html.Div("Sube cada uno de los cuatro archivos Excel en su celda correspondiente para inicializar el pipeline.",
                         style={"color": C["muted"], "fontSize": "12px", "maxWidth": "460px",
                                "lineHeight": "1.6"}),
            ], style={"marginBottom": "32px", "textAlign": "center"}),

            # ── Celdas individuales ────────────────────────────────────
            html.Div(file_cells, id="upload-file-cells"),

            # ── Mensaje de error ───────────────────────────────────────
            html.Div(id="upload-error-msg",
                     style={"color": C["danger"], "fontSize": "12px",
                            "marginTop": "12px", "fontFamily": FONT_MONO,
                            "minHeight": "18px"}),

            # ── FIX: dcc.Loading envuelve tanto el botón como el output
            #         para que el spinner reemplace al botón durante el procesamiento ──
            html.Div([
                dcc.Loading(
                    id="loading-process",
                    children=[
                        html.Button(
                            [html.Span("⬡", style={"marginRight": "8px"}),
                             "Procesar y lanzar dashboard"],
                            id="btn-process-files",
                            disabled=not all_loaded,
                            style={
                                "background": C["accent"] if all_loaded else C["card2"],
                                "color": "#FFFFFF" if all_loaded else C["muted"],
                                "border": "none",
                                "borderRadius": "10px",
                                "padding": "13px 32px",
                                "fontSize": "13px",
                                "fontWeight": "700",
                                "fontFamily": FONT,
                                "cursor": "pointer" if all_loaded else "not-allowed",
                                "letterSpacing": "0.5px",
                                "boxShadow": "0 4px 20px rgba(144,12,14,0.35)" if all_loaded else "none",
                                "transition": "all 0.2s",
                            }
                        ),
                        # Output oculto que el callback escribe para activar el spinner
                        html.Div(id="upload-processing-output", style={"display": "none"}),
                    ],
                    type="circle",
                    color=C["accent"],
                    style={"marginTop": "20px"},
                ),
            ], style={"textAlign": "center", "minHeight": "60px"}),

        ], style={
            "maxWidth": "560px",
            "width": "100%",
            "margin": "0 auto",
            "padding": "60px 24px 40px",
            "fontFamily": FONT,
        }),

    ], style={
        "height": "100vh",
        "background": C["bg"],
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "color": C["text"],
        "fontFamily": FONT,
        "overflowY": "auto",
    })


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="theme-store",    data="dark"),   # persiste tema elegido
    dcc.Store(id="upload-store",   data={}),       # almacena {filename: base64} de archivos subidos
    dcc.Store(id="pipeline-ready", data=False),    # True cuando el pipeline se ejecutó correctamente
    dcc.Store(id="pipeline-data",  data={}),       # datos derivados (contacto, conversion, retencion_600)
    dcc.Store(id="process-trigger", data=0),       # incrementa cuando se pulsa "Procesar"
    html.Div(id="app-shell"),                      # renderiza upload-gate o dashboard completo
])

# CSS global
app.index_string = app.index_string.replace(
    "</head>",
    """<style>
        body { margin: 0; padding: 0; overflow: hidden; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #827970; border-radius: 2px; }
        a { text-decoration: none !important; }
        .nav-item:hover { background: rgba(144,12,14,0.12) !important; }
        * { box-sizing: border-box; }
        #theme-toggle:hover { opacity: 0.85; transform: scale(1.04); }
        .rc-slider-rail { background-color: rgba(130, 121, 112, 0.3) !important; height: 6px !important; }
        .rc-slider-track { background-color: #900C0E !important; height: 6px !important; }
        .rc-slider-handle { border: 2px solid #900C0E !important; background-color: #FFFFFF !important; width: 14px !important; height: 14px !important; margin-top: -4px !important; cursor: grab !important; }
        .rc-slider-handle:active { cursor: grabbing !important; }
        .rc-slider-mark-text { font-size: 10px !important; font-family: 'IBM Plex Mono', monospace !important; }
    </style></head>"""
)

# ════════════════════════════════════════════════════════════════
# CALLBACKS — UPLOAD GATE
# ════════════════════════════════════════════════════════════════

@app.callback(
    Output("upload-store", "data"),
    Input("upload-pop", "contents"),
    Input("upload-hrs", "contents"),
    Input("upload-mnt", "contents"),
    Input("upload-rep", "contents"),
    Input("btn-detach-pop", "n_clicks"),
    Input("btn-detach-hrs", "n_clicks"),
    Input("btn-detach-mnt", "n_clicks"),
    Input("btn-detach-rep", "n_clicks"),
    State("upload-pop", "filename"),
    State("upload-hrs", "filename"),
    State("upload-mnt", "filename"),
    State("upload-rep", "filename"),
    State("upload-store", "data"),
    prevent_initial_call=True,
)
def accumulate_uploads(
    pop_content, hrs_content, mnt_content, rep_content,
    pop_detach, hrs_detach, mnt_detach, rep_detach,
    pop_name, hrs_name, mnt_name, rep_name,
    current_store,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_store or {}

    store = dict(current_store or {})
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if   triggered_id == "upload-pop" and pop_content:
        store["PopulationView_2026.xlsx"]           = {"filename": pop_name, "content": pop_content}
    elif triggered_id == "upload-hrs" and hrs_content:
        store["Horas 2024-2025.xlsx"]               = {"filename": hrs_name, "content": hrs_content}
    elif triggered_id == "upload-mnt" and mnt_content:
        store["Mantenimientos 2024-2025.xlsx"]      = {"filename": mnt_name, "content": mnt_content}
    elif triggered_id == "upload-rep" and rep_content:
        store["Reporte_unidades_dia_anterior.xlsx"] = {"filename": rep_name, "content": rep_content}
    elif triggered_id == "btn-detach-pop": store.pop("PopulationView_2026.xlsx",           None)
    elif triggered_id == "btn-detach-hrs": store.pop("Horas 2024-2025.xlsx",               None)
    elif triggered_id == "btn-detach-mnt": store.pop("Mantenimientos 2024-2025.xlsx",      None)
    elif triggered_id == "btn-detach-rep": store.pop("Reporte_unidades_dia_anterior.xlsx", None)

    return store


@app.callback(
    Output("process-trigger", "data"),
    Input("upload-store", "data"),
    State("process-trigger", "data"),
    prevent_initial_call=True,
)
def update_process_trigger(upload_store, current_trigger):
    """Re-renderiza la pantalla de carga cuando cambia el estado de archivos."""
    return (current_trigger or 0) + 1


@app.callback(
    Output("app-shell",      "children"),
    Output("pipeline-ready", "data"),
    Input("process-trigger", "data"),
    Input("url",             "pathname"),
    State("upload-store",    "data"),
    State("pipeline-ready",  "data"),
    State("pipeline-data",   "data"),
    State("theme-store",     "data"),
    prevent_initial_call=False,
)
def render_app_shell(trigger, pathname, upload_store, pipeline_ready, pipeline_data_stored, theme):
    """Muestra la pantalla de carga o el dashboard completo."""
    if pipeline_ready and pipeline_data_stored:
        # Reconstituir DataFrames desde los dicts almacenados
        import pandas as _pd
        def _reconstruct(raw_dict, df_keys):
            """Reconstruye DataFrames dentro de un dict a partir de listas de registros."""
            if not raw_dict:
                return raw_dict or {}
            out = dict(raw_dict)
            for k in df_keys:
                if k in out and isinstance(out[k], list):
                    out[k] = _pd.DataFrame(out[k])
            return out

        contacto_data = _reconstruct(
            pipeline_data_stored.get("contacto_data", {}),
            ["pivot", "hm", "df_estrategia", "df_tasa"]
        )
        # Reconstituir pivot como DataFrame con índice correcto
        if contacto_data and "pivot" in contacto_data and isinstance(contacto_data["pivot"], _pd.DataFrame):
            pivot_df = contacto_data["pivot"]
            if len(pivot_df.columns) > 1 and "zona" in pivot_df.columns:
                pivot_df = pivot_df.set_index("zona")
                contacto_data["pivot"] = pivot_df

        conversion_data = _reconstruct(
            pipeline_data_stored.get("conversion_data", {}),
            ["top3", "bottom3", "dist_dual"]
        )
        retencion_600_data = pipeline_data_stored.get("retencion_600_data", {})

        pipeline_data = {
            "contacto_data":      contacto_data,
            "conversion_data":    conversion_data,
            "retencion_600_data": retencion_600_data,
        }
        return _dashboard_shell(pathname, theme, pipeline_data), True
    if pipeline_ready:
        return _dashboard_shell(pathname, theme, {}), True
    return page_upload(upload_store, theme), False


@app.callback(
    Output("pipeline-ready",           "data",     allow_duplicate=True),
    Output("app-shell",                "children", allow_duplicate=True),
    # Escribir aquí activa el spinner del dcc.Loading que envuelve el botón
    Output("upload-processing-output", "children", allow_duplicate=True),
    # Deshabilitar el botón en cuanto se hace click (antes de que el pipeline termine)
    Output("btn-process-files",        "disabled", allow_duplicate=True),
    Output("pipeline-data",            "data",     allow_duplicate=True),
    Input("btn-process-files",         "n_clicks"),
    State("upload-store",    "data"),
    State("url",             "pathname"),
    State("theme-store",     "data"),
    prevent_initial_call=True,
)
def process_and_launch(n_clicks, upload_store, pathname, theme):
    """
    Se dispara SÓLO cuando el usuario pulsa 'Procesar'.
    - Deshabilita el botón inmediatamente para evitar doble click.
    - El dcc.Loading muestra el spinner mientras el pipeline corre.
    - En éxito lanza el dashboard; en error re-habilita el botón.
    """
    if not n_clicks or not upload_store:
        return no_update, no_update, no_update, no_update, no_update

    C = THEMES.get(theme, THEMES["dark"])
    try:
        buffers = {}
        for canonical_name, file_info in upload_store.items():
            if file_info and "content" in file_info:
                _, b64 = file_info["content"].split(",", 1)
                buffers[canonical_name] = base64.b64decode(b64)

        result = load_processed_data_from_buffers(buffers)

        # Serializar los datos derivados que necesitan las nuevas secciones
        # (guardamos solo los dicts serializables, no los DataFrames completos)
        contacto_raw  = result.get("contacto_data",      {})
        conversion_raw = result.get("conversion_data",   {})
        retencion_raw  = result.get("retencion_600_data",{})

        # Convertir DataFrames a JSON para almacenarlos en dcc.Store
        def _df_to_dict(obj):
            """Convierte DataFrames dentro de un dict a listas de registros."""
            if obj is None:
                return {}
            import pandas as _pd
            out = {}
            for k, v in obj.items():
                if isinstance(v, _pd.DataFrame):
                    out[k] = v.to_dict("records")
                elif isinstance(v, _pd.Series):
                    out[k] = v.to_dict()
                elif isinstance(v, np.integer):
                    out[k] = int(v)
                elif isinstance(v, np.floating):
                    out[k] = float(v)
                elif isinstance(v, np.ndarray):
                    out[k] = v.tolist()
                else:
                    out[k] = v
            return out

        stored_data = {
            "contacto_data":      _df_to_dict(contacto_raw),
            "conversion_data":    _df_to_dict(conversion_raw),
            "retencion_600_data": retencion_raw,  # ya es dict de scalars
        }

        # Reconstituir DataFrames para renderizar el shell inmediatamente
        pipeline_data_for_shell = {
            "contacto_data":      contacto_raw,
            "conversion_data":    conversion_raw,
            "retencion_600_data": retencion_raw,
        }

        # Éxito: el botón desaparece junto con la pantalla de carga
        return True, _dashboard_shell(pathname, theme, pipeline_data_for_shell), "", True, stored_data

    except Exception as exc:
        err_msg = html.Div(
            f"⚠ Error al procesar: {exc}",
            style={
                "color": C["danger"], "fontSize": "12px",
                "marginTop": "12px", "fontFamily": FONT_MONO,
                "padding": "10px 14px",
                "background": "rgba(193,18,31,0.08)",
                "borderRadius": "8px",
                "border": f"1px solid {C['danger']}",
            },
        )
        # Error: re-habilitar el botón para que el usuario pueda reintentar
        return False, html.Div([page_upload(upload_store, theme), err_msg]), "", False, no_update


def _dashboard_shell(pathname, theme, pipeline_data=None):
    """Retorna el layout completo del dashboard (sidebar + contenido + toggle)."""
    C = THEMES.get(theme, THEMES["dark"])

    base_style = {
        "marginLeft": "180px",
        "minHeight": "100vh",
        "background": C["bg"],
        "fontFamily": FONT,
        "color": C["text"],
        "transition": "background 0.3s, color 0.3s",
    }

    sidebar = make_sidebar(C, pathname)
    toggle  = make_theme_toggle(theme)

    # Extraer datos del pipeline si están disponibles
    retencion_600_data = pipeline_data.get("retencion_600_data") if pipeline_data else None
    contacto_data      = pipeline_data.get("contacto_data")      if pipeline_data else None
    conversion_data    = pipeline_data.get("conversion_data")    if pipeline_data else None

    if pathname == "/agricultura":
        page = page_agricultura(C)
    elif pathname == "/distribuidores":
        page = page_distribuidores(C)
    elif pathname == "/retencion":
        page = page_retencion(C, retencion_600_data=retencion_600_data)
    elif pathname == "/contacto":
        page = page_contacto(C, contacto_data=contacto_data, conversion_data=conversion_data)
    elif pathname == "/conversion":
        page = page_conversion(C, conversion_data=conversion_data)
    else:
        page = page_overview(C)

    return html.Div([
        dcc.Location(id="url-inner", refresh=False),
        sidebar,
        html.Div(page, id="page-content", style=base_style),
        toggle,
    ])


# ════════════════════════════════════════════════════════════════
# CALLBACKS — DASHBOARD (sólo activos cuando el shell existe)
# ════════════════════════════════════════════════════════════════

# ── Toggle theme store ──
@app.callback(
    Output("theme-store", "data"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current):
    if n_clicks and n_clicks > 0:
        return "light" if current == "dark" else "dark"
    return current


@app.callback(Output("clock", "children"), Input("interval-clock", "n_intervals"))
def update_clock(n):
    return datetime.now().strftime("%d %b %Y  %H:%M:%S")

# ── Update Parallel Coordinates Graph based on slider chart range ──
# CALLBACK 1: Gestionar el clic en la leyenda y actualizar el dcc.Store
@callback(
    Output("parcoords-visible-zones-store", "data"),
    Input("parcoords-graph", "restyleData"),
    Input("theme-store", "data"), # Utiliza la fuente de verdad del tema actual
    State("parcoords-visible-zones-store", "data"),
    prevent_initial_call=True
)
def update_legend_store(restyle_data, theme, current_visible):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "theme-store" or current_visible is None:
        return zonas # Resetear con todas las zonas si cambia de página/tema
        
    if restyle_data:
        # restyle_data contiene qué traza cambió y qué propiedad mutó.
        changed_property = restyle_data[0]
        if "visible" in changed_property:
            visible_value = changed_property["visible"][0]
            trace_indices = restyle_data[1]
            
            updated_visible = list(current_visible)
            for t_idx in trace_indices:
                if t_idx >= 1:
                    zona_name = zonas[t_idx - 1]
                    
                    if visible_value == "legendonly" and zona_name in updated_visible:
                        updated_visible.remove(zona_name)
                    elif visible_value == True and zona_name not in updated_visible:
                        updated_visible.append(zona_name)
                        
            return updated_visible

    return current_visible


# CALLBACK 2: Escuchar el dcc.Store y actualizar el gráfico final
@callback(
    Output("parcoords-graph", "figure"),
    Input("parcoords-slider-chart", "relayoutData"),
    Input("parcoords-visible-zones-store", "data"),
    Input("theme-store", "data"), # Conectado directamente a la fuente de verdad persistida
    prevent_initial_call=False
)
def update_parallel_coordinates(slider_data, visible_zones, theme):
    C = THEMES.get(theme, THEMES["dark"])
    
    # Obtener el rango de meses del slider inferior
    month_range = [0, 11]
    if slider_data and "xaxis.range" in slider_data:
        # Convertir floats del range a índices de meses enteros
        raw_range = slider_data["xaxis.range"]
        try:
            start_val = int(round(float(raw_range[0])))
            end_val = int(round(float(raw_range[1])))
            month_range = [max(0, start_val), min(11, end_val)]
        except (ValueError, TypeError):
            pass
            
    # Retornamos el gráfico regenerado aplicando el filtro de meses y de visibilidad por Zonas
    return fig_parallel_coordinates(C, month_range=month_range, visible_zones=visible_zones)

if __name__ == "__main__":
    app.run(debug=True)