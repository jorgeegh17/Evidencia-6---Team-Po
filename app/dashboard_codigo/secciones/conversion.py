
#Importaciones de librerias externas
from dash import dcc, html
import plotly.graph_objects as go

from plotly.subplots import make_subplots as _msp

#Importaciones de librerias internas
from ..componentes_secciones.componentes import make_topbar, kpi_card, empty_figure
from theme import NB_NAVY, NB_WHITE, NB_TEAL, NB_CRIMSON, NB_FONT, NB_GRAY, NB_GOLD, NB_LGRAY
import pandas as _pd


def fig_conv_funnel(conversion_data):
    """Funnel de estado de la flota por unidad."""
    try:
        f = conversion_data['funnel']

        fig = go.Figure(go.Funnel(
            y=f['etapas'],
            x=f['pcts'],
            textposition='inside',
            textinfo='text',                          # oculta el decimal crudo de Plotly
            text=[
                f"<b>{p:.1f}%</b>  ({v:,})"
                for p, v in zip(f['pcts'], f['vals'])
            ],
            marker=dict(
                color=f['colors'],
                line=dict(color='white', width=2)
            ),
            connector=dict(line=dict(color='#e5e7eb', width=1.5, dash='dot')),
            hovertemplate='<b>%{y}</b><br>%{x:.1f}% de la flota<br><extra></extra>'
        ))

        n   = f['n_unidades']
        enr = f['en_red']

        fig.update_layout(
            title=dict(
                text="<b>Estado actual de la flota por unidad</b>",
                subtitle=dict(
                    text=f"{n:,} unidades New Holland AG + Case IH · corte al día anterior",
                    font=dict(size=12, family=NB_FONT, color=NB_GRAY)
                ),
                font=dict(size=20, family=NB_FONT, color=NB_NAVY),
                x=0.03, y=0.97
            ),
            paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
            height=500,
            margin=dict(t=100, b=100, l=210, r=60),
            font_family=NB_FONT,
        )
        return fig

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[FIG_CONV_FUNNEL] {e}")
        return empty_figure()

def fig_conv_top_bottom(conversion_data):
    try:
        """Top 3 vs Bottom 3 distribuidores por conversión."""
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
        fig.update_yaxes(tickfont=dict(size=11, family=NB_FONT), showgrid=False, autorange="reversed")
        return fig
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[FIG_CONV_TOP_BOTTOM] {e}")
        return empty_figure()
def fig_conv_dual(conversion_data):
    """
    Visualización 14: Conversión vs retraso modal por distribuidor.
    Barras de conversión (eje izq.) + línea punteada de retraso modal (eje der.).
    """
    try:
        from plotly.subplots import make_subplots

        dd = conversion_data["dist_dual"]

        if dd.empty:
            return empty_figure()

        # Color de barra condicional — idéntico al notebook
        def color_barra(t):
            if t < 10:  return '#9B1B30'   # C_CRIMSON
            if t < 20:  return '#F4A261'   # C_CORAL
            if t < 35:  return '#E9C46A'   # C_GOLD
            return '#2A9D8F'               # C_TEAL

        colores = [color_barra(t) for t in dd["tasa_conv_pct"]]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # ── Barras: tasa de conversión (eje izquierdo) ────────────────
        fig.add_trace(go.Bar(
            name="Tasa de conversión",
            x=dd["distribuidor"],
            y=dd["tasa_conv_pct"],
            marker=dict(
                color=colores,
                line=dict(color="white", width=1.5)
            ),
            text=[f"{v:.1f}%" for v in dd["tasa_conv_pct"]],
            textposition="outside",
            textfont=dict(size=8, family=NB_FONT, color=NB_NAVY),
            hovertemplate="<b>%{x}</b><br>Conversión: %{y:.1f}%<extra></extra>",
            opacity=0.9,
        ), secondary_y=False)

        # ── Línea: retraso modal (eje derecho) ────────────────────────
        fig.add_trace(go.Scatter(
            name="Retraso modal (días)",
            x=dd["distribuidor"],
            y=dd["moda_retraso"],
            mode="lines+markers",
            line=dict(color=NB_NAVY, width=2.5, dash="dot"),
            marker=dict(size=9, color=NB_NAVY,
                        line=dict(color="white", width=2)),
            text=[f"{v:.0f}d" for v in dd["moda_retraso"]],
            textposition="top center",
            textfont=dict(size=8, family=NB_FONT, color=NB_NAVY),
            hovertemplate="<b>%{x}</b><br>Retraso modal: %{y:.0f} días<extra></extra>",
        ), secondary_y=True)
        prom_conv = conversion_data['prom_conv']
        fig.add_hline(
            y=prom_conv,
            line_color="#2A9D8F",
            line_width=1.5,
            line_dash="dash",
            secondary_y=False,
            annotation=dict(
                text=f"Prom. red {prom_conv:}%",
                font=dict(size=10, color="#2A9D8F", family=NB_FONT),
                showarrow=False,
                x=0.75,
                xref="paper",
                xanchor="left",
                yanchor="bottom",
            )
        )

        # ── Layout ────────────────────────────────────────────────────
        fig.update_layout(
            title=dict(
                text="<b>Conversión vs retraso modal por distribuidor</b>",
                subtitle=dict(
                    text="Barras = % de alarmas convertidas en red (eje izq.)  |  Línea punteada = días de retraso modal (eje der.)",
                    font=dict(size=12, family=NB_FONT, color=NB_GRAY),
                ),
                font=dict(size=20, family=NB_FONT, color=NB_NAVY),
                x=0.03, y=0.97,
            ),
            paper_bgcolor=NB_WHITE, plot_bgcolor=NB_WHITE,
            height=460,
            margin=dict(t=100, b=90, l=60, r=80),
            font_family=NB_FONT,
            xaxis=dict(
                tickfont=dict(size=10, family=NB_FONT),
                tickangle=-35,
                showgrid=False,
            ),
            legend=dict(
                orientation="h", y=-0.24, x=0,
                font=dict(size=11, family=NB_FONT),
            ),
            bargap=0.3,
        )

        # ── Ejes Y ────────────────────────────────────────────────────
        fig.update_yaxes(
            title_text="% de conversión",
            ticksuffix="%",
            range=[0, 70],
            showgrid=True, gridcolor=NB_LGRAY,
            zeroline=False,
            tickfont=dict(size=11, family=NB_FONT),
            secondary_y=False,
        )
        fig.update_yaxes(
            title_text="Retraso modal (días)",
            range=[0, dd["moda_retraso"].max() * 1.3],
            showgrid=False, zeroline=False,
            tickfont=dict(size=11, family=NB_FONT),
            secondary_y=True,
        )

        return fig

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[FIG_CONV_DUAL] {e}")
        return empty_figure()

def fig_conv_sobrecarga(conversion_data):
    try:
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
                font=dict(size=15, family=NB_FONT, color=NB_NAVY),
                x=0.5,
                y=0.97,
                xanchor='center'
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
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[FIG_CONV_ALARMAS_PROY] {e}")
        return empty_figure()

def card_monetizacion_conversion_html(conversion_data):
    try:
        """Tarjeta de potencial de monetización campaña 70/30 para sección Conversión."""
        mon = conversion_data['monetizacion']
        rec_ins03  = mon['servicios'][0]
        ingreso_03 = mon['ingresos'][0]
        return html.Div([
            html.Div("Ingreso Potencial (MXN)", style={
                "fontSize": "14px", "fontWeight": "800",
                "color": NB_NAVY, "marginBottom": "4px"
            }),
            html.Div([
                #{ingreso_03/1e6:.2f}
                html.Span("$3.58M", style={
                    "fontSize": "32px", "fontWeight": "900",
                    "color": NB_TEAL, "fontFamily": "monospace"
                }),
                html.Span(" MXN", style={"fontSize": "13px", "color": NB_GRAY, "marginLeft": "4px"}),
            ]),
            html.Div("239 servicios adicionales estimados",
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
            html.Div("Mejora +15% relativo sobre tasa actual de conversión en meses óptimos.",
                    style={"fontSize": "10px", "color": NB_GRAY, "marginTop": "8px"}),
        ], style={
            "background": NB_WHITE, "border": f"1px solid {NB_CRIMSON}55",
            "borderTop": f"3px solid {NB_CRIMSON}",
            "borderRadius": "12px", "padding": "16px",
            "boxShadow": "0 2px 12px rgba(155,27,48,0.10)",
            "marginTop": "12px",
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()

        print(f"[CARD_MEJORA_INCREMENTAL] {e}")

        return html.Div()

def card_sobrecarga_proyectada(conversion_data):
    try:
        dists = conversion_data["distribuidores_sc"][:4]
        alarm = conversion_data["alarmas_proy"][:4]
        pcts  = conversion_data["sobrecarga_pct"][:4]

        filas = []

        for d, a, p in zip(dists, alarm, pcts):

            filas.append(
                html.Div([
                    html.Span(
                        d,
                        style={
                            "fontWeight": "900",
                            "fontSize": "18px",
                            "color": NB_CRIMSON,
                        }
                    ),

                    html.Span(
                        f" : {a} alarmas (+{p:.1f}% vs mes anterior)",
                        style={
                            "fontSize": "18px",
                            "color": NB_CRIMSON,
                        }
                    )
                ], style={"marginBottom": "18px"})
            )

        return html.Div([

            html.Div(
                "DISTRIBUIDORES CON SOBRECARGA PROYECTADA",
                style={
                    "fontSize": "16px",
                    "fontWeight": "900",
                    "color": "#7A7A7A",
                    "marginBottom": "24px"
                }
            ),

            *filas

        ], style={
            "background": "#F3F4F6",
            "padding": "20px",
            "borderRadius": "12px",
            "border": "1px solid #E5E7EB"
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()

        print(f"[CARD_SOBRECARGA_PROYECTADA] {e}")

        return empty_figure()

def card_retencion_historial_externo(conversion_data):
    try:
        ret = conversion_data["retencion_externa"]

        pct_0 = ret["tasas"].get("0 externos", 0)
        pct_1 = ret["tasas"].get("1 externo", 0)
        pct_2 = ret["tasas"].get("≥2 externos", 0)

        n_0 = ret["n"].get("0 externos", 0)
        n_1 = ret["n"].get("1 externo", 0)
        n_2 = ret["n"].get("≥2 externos", 0)

        control = ret.get("control", 0)

        or_val = ret.get("or")
        p_val = ret.get("p")
        ic_lo = ret.get("ic_lo")
        ic_hi = ret.get("ic_hi")

        footer = []

        if (
            or_val is not None
            and p_val is not None
            and ic_lo is not None
            and ic_hi is not None
        ):
            footer.append(
                html.Div(
                    f"OR={or_val:.4f} | p={p_val:.2e} | IC95% [{ic_lo:.2f}, {ic_hi:.2f}]",
                    style={
                        "marginTop": "10px",
                        "fontSize": "11px",
                        "color": "#6B7280",
                        "textAlign": "center"
                    }
                )
            )

        return html.Div(

            [

                html.H4(
                    "Retención según historial externo",
                    style={
                        "color": "#1B2A4A",
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "marginBottom": "4px"
                    }
                ),

                html.P(
                    "El comportamiento del cliente indica el retorno",
                    style={
                        "color": "#C1121F",
                        "fontSize": "14px",
                        "fontWeight": "700",
                        "marginBottom": "22px"
                    }
                ),

                # ===========================
                # 0 EXTERNOS
                # ===========================
                html.Div([
                    html.Span(
                        "0 servicios externos",
                        style={
                            "width": "140px",
                            "fontWeight": "600",
                            "color": "#1B2A4A"
                        }
                    ),

                    html.Div([
                        html.Div(
                            style={
                                "width": f"{pct_0:.1f}%",
                                "height": "100%",
                                "background": "#2A9D8F",
                                "borderRadius": "5px"
                            }
                        )
                    ],
                    style={
                        "flex": "1",
                        "height": "26px",
                        "background": "#E5E7EB",
                        "borderRadius": "5px"
                    }),

                    html.Span(
                        f"{pct_0:.1f}%",
                        style={
                            "width": "55px",
                            "fontWeight": "700",
                            "color": "#2A9D8F",
                            "textAlign": "right"
                        }
                    )

                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginBottom": "18px"
                }),

                # ===========================
                # 1 EXTERNO
                # ===========================
                html.Div([

                    html.Span(
                        "1 servicio externo",
                        style={
                            "width": "140px",
                            "fontWeight": "600",
                            "color": "#1B2A4A"
                        }
                    ),

                    html.Div([
                        html.Div(
                            style={
                                "width": f"{pct_1:.1f}%",
                                "height": "100%",
                                "background": "#C9A227",
                                "borderRadius": "5px"
                            }
                        )
                    ],
                    style={
                        "flex": "1",
                        "height": "26px",
                        "background": "#E5E7EB",
                        "borderRadius": "5px"
                    }),
                    html.Span(
                        f"{pct_1:.1f}%",
                        style={
                            "width": "55px",
                            "fontWeight": "700",
                            "color": "#B8860B",
                            "textAlign": "right"
                        }
                    )

                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginBottom": "4px"
                }),

                html.Div(
                    "Punto de no retorno",
                    style={
                        "fontSize": "11px",
                        "fontWeight": "700",
                        "color": "#C0392B",
                        "marginBottom": "10px"
                    }
                ),

                # ===========================
                # VENTANA
                # ===========================
                html.Div([

                    html.Div([

                        html.Div(
                            "Ventana de intervención — cliente aún recuperable",
                            style={
                                "fontWeight": "700",
                                "fontSize": "13px",
                                "color": "#9A6F00",
                                "marginBottom": "6px"
                            }
                        ),

                        html.Div(
                            "15 días tras el primer servicio externo",
                            style={
                                "fontSize": "12px",
                                "color": "#9A6F00"
                            }
                        )

                    ])

                ],
                style={
                    "marginBottom": "18px",
                    "background": "#FEF9C3",
                    "border": "1.5px solid #C9A227",
                    "borderRadius": "8px",
                    "padding": "12px"
                }),

                # ===========================
                # 2+ EXTERNOS
                # ===========================
                html.Div([

                    html.Span(
                        "≥2 servicios externos",
                        style={
                            "width": "140px",
                            "fontWeight": "600",
                            "color": "#9B1B30"
                        }
                    ),

                    html.Div([
                        html.Div(
                            style={
                                "width": f"{pct_2:.1f}%",
                                "height": "100%",
                                "background": "#9B1B30",
                                "borderRadius": "5px"
                            }
                        )
                    ],
                    style={
                        "flex": "1",
                        "height": "26px",
                        "background": "#E5E7EB",
                        "borderRadius": "5px"
                    }),
                    html.Span(
                        f"{pct_2:.1f}%",
                        style={
                            "width": "55px",
                            "fontWeight": "700",
                            "color": "#9B1B30",
                            "textAlign": "right"
                        }
                    )

                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginBottom": "12px"
                }),
                html.Div(
                    "punto de no retorno",
                    style={
                        "marginLeft": "150px",
                        "fontSize": "10px",
                        "fontWeight": "700",
                        "color": "#C1121F",
                        "marginTop": "-6px",
                        "marginBottom": "14px"
                    }
                ),

                *footer

            ],

            style={
                "background": NB_WHITE,
                "border": "1px solid #E5E7EB",
                "borderRadius": "12px",
                "padding": "16px"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CARD_MEJORA_INCREMENTAL] {e}")

        return empty_figure()


def page_conversion(C, conversion_data=None):
    """Sección Conversión."""
    if conversion_data is None:
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
                'labels': ['INS-03\nIngreso Potencial (MXN)','INS-NEW\nDistribuidores'],
                'servicios': [200, 150],
                'ingresos': [3000000, 2250000],
                'ticket': 15000,
                'total_svc': 350,
                'total_ing': 5250000,
            },
        }
    f = conversion_data["funnel"]

    total_alarmas = f["vals"][0]
    sin_atender   = f["vals"][1]
    fuera_red     = f["vals"][2]
    sin_servicio  = f["vals"][3]
    servicio_red  = f["vals"][4]

    print(f"Total alarmas: {total_alarmas}")
    print(f"Servicio en red CNH: {servicio_red}")
    print(f"Fuera de la red: {fuera_red}")
    print(f"Sin servicio: {sin_servicio}")
    pct_serv_red = servicio_red / total_alarmas * 100
    print(f"Porcentaje servicio en red: {pct_serv_red}")
    

    pct_conversion = (
        servicio_red / total_alarmas * 100
        if total_alarmas else 0
    )

    pct_no_red = (
        (fuera_red + sin_atender) / total_alarmas * 100
        if total_alarmas else 0
    )
    return html.Div([
        make_topbar("Conversión · Distribuidores & Monetización", C),
        html.Div([
            # ── Columna izquierda ──────────────────────────────────────
            html.Div([
                #KPIs
                html.Div([
                    kpi_card(
                        "de unidades que no terminan en servicio en la red CNH",
                        f"{pct_no_red:.1f}%",
                        f"{sin_atender + fuera_red:,} alarmas",
                        C["heat_low"],
                        C=C
                    ),

                    kpi_card(
                        "tasa de conversión promedio",
                        f"{pct_serv_red:.1f}%",
                        f"{servicio_red:,} servicios",
                        C["success"],
                        C=C
                    ),
                    kpi_card("ARBSA responde el mismo dia",       "0 vs 149 dias",    "Enagri tarda 149 dias",        C["warning"], C=C),
                    kpi_card("distribuidores con sobrecarga proyectada el proximo mes",   "4 en crisis", " ", C["heat_low"],    C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),
                # Funnel
                html.Div([
                    dcc.Graph(figure=fig_conv_funnel(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Top vs Bottom
                html.Div([
                    dcc.Graph(figure=fig_conv_top_bottom(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Conversión vs retraso modal
                html.Div([
                    dcc.Graph(figure=fig_conv_dual(conversion_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            # ── Columna derecha ────────────────────────────────────────
            html.Div([
                card_retencion_historial_externo(conversion_data),
                card_sobrecarga_proyectada(conversion_data),
                #fig_conv_sobrecarga(conversion_data),
                # Monetización
                card_monetizacion_conversion_html(conversion_data),

            ], style={"width":"360px","minWidth":"360px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),

        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])

