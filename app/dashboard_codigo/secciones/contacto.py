
#Importaciones de librerias externas
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

#Importaciones de librerias internas
from ..componentes_secciones.componentes import make_topbar, kpi_card, chart_card, apply_layout, empty_figure
from theme import NB_NAVY, NB_WHITE, NB_TEAL, NB_CRIMSON, NB_FONT, NB_GRAY, NB_RED_BAR, NB_GOLD, NB_LGRAY

# Graficas
def fig_contacto_heatmap(contacto_data):

    pivot       = contacto_data["pivot"]
    orden_zonas = contacto_data["orden_zonas"]
    orden_meses = contacto_data["orden_meses"]
    mes_top     = contacto_data["mes_top"]

    colorscale = [
        [0.00, "#FFF0F0"],
        [0.20, "#FECACA"],
        [0.40, "#FDE68A"],
        [0.60, "#BBF7D0"],
        [0.80, "#34D399"],
        [1.00, "#065F46"]
    ]
    
    text = [
        [f"{v:.0f}%" if pd.notna(v) else ""
         for v in row]
        for row in pivot.values
    ]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=orden_meses,
            y=orden_zonas,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=11),

            colorscale=colorscale,
            zmin=0,
            zmax=75,

            xgap=3,
            ygap=3,

            showscale=True,

            colorbar=dict(
                title=dict(
                    text="% cumple",
                    font=dict(
                        size=12,
                        family=NB_FONT
                    )
                ),
                ticksuffix="%",
                tickfont=dict(
                    size=11,
                    family=NB_FONT
                ),
                len=0.8,
                thickness=14,
                x=1.02
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br><b>%{x}</b>"
                "<br>Cumplimiento: %{z:.1f}%"
                "<extra></extra>"
            )
        )
    )

    # =====================================================
    # ETIQUETAS DENTRO DE LAS CELDAS
    # =====================================================

    fig.update_layout(

        title=dict(
            text="<b>Mapa de receptividad al servicio — Zona × Mes</b>",
            font=dict(
                size=16,
                family=NB_FONT,
                color=NB_NAVY
            ),
            x=0.03,
            y=0.97
        ),

        paper_bgcolor=NB_WHITE,
        plot_bgcolor=NB_WHITE,

        height=380,

        margin=dict(
            t=110,
            b=30,
            l=150,
            r=80
        ),

        font_family=NB_FONT,

        xaxis=dict(
            side="top",
            tickfont=dict(
                size=12,
                family=NB_FONT
            ),
            showgrid=False
        ),

        yaxis=dict(
            tickfont=dict(
                size=12,
                family=NB_FONT
            ),
            showgrid=False
        )
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
    
def fig_comportamiento_intervalo(contacto_data):

    try:

        df = contacto_data["df_tasa"].copy()

        if df.empty:
            return empty_figure()

        # =====================================================
        # DATOS
        # =====================================================

        y_labels = [
            f"{int(h):,} horas ▲"
            if q else
            f"{int(h):,} horas"
            for h, q in zip(df["horas"], df["es_quiebre"])
        ]

        x_vals = (df["tasa_cumple"] * 100).tolist()

        colores = df["color"].tolist()

        textos = [
            f"<b>{v:.1f}% cumple</b>"
            for v in x_vals
        ]

        # =====================================================
        # FIGURA
        # =====================================================

        fig = go.Figure()

        # Fondo gris (100%)
        fig.add_trace(
            go.Bar(
                y=y_labels,
                x=[100] * len(df),
                orientation="h",
                marker=dict(color="#E5E7EB"),
                hoverinfo="skip",
                showlegend=False
            )
        )

        # Barras reales
        fig.add_trace(
            go.Bar(
                y=y_labels,
                x=x_vals,
                orientation="h",

                marker=dict(
                    color=colores,
                    line=dict(
                        color="white",
                        width=1.5
                    )
                ),

                text=textos,
                textposition="outside",

                textfont=dict(
                    size=13,
                    family=NB_FONT
                ),

                showlegend=False,

                hovertemplate=
                "<b>%{y}</b><br>"
                "Cumplimiento: %{x:.1f}%"
                "<extra></extra>"
            )
        )

        # =====================================================
        # QUIEBRE (600h)
        # =====================================================

        quiebre = df[df["es_quiebre"]]

        if len(quiebre):

            valor_quiebre = float(
                quiebre["tasa_cumple"].iloc[0] * 100
            )

            horas_quiebre = int(
                quiebre["horas"].iloc[0]
            )

            fig.add_vline(
                x=valor_quiebre,

                line=dict(
                    color=NB_NAVY,
                    width=1.5,
                    dash="dot"
                ),

                annotation=dict(
                    text=f"<b>Quiebre<br>{horas_quiebre}h</b>",
                    showarrow=False,
                    y=1.03,
                    yref="paper",
                    font=dict(
                        size=11,
                        color=NB_NAVY,
                        family=NB_FONT
                    )
                )
            )

        # =====================================================
        # LAYOUT
        # =====================================================

        fig.update_layout(

            title=dict(
                text="<b>Comportamiento por intervalo</b>",
                font=dict(
                    size=18,
                    family=NB_FONT,
                    color=NB_NAVY
                ),
                x=0.03,
                y=0.97
            ),

            barmode="overlay",

            paper_bgcolor=NB_WHITE,
            plot_bgcolor=NB_WHITE,

            height=360,

            margin=dict(
                t=90,
                b=40,
                l=130,
                r=130
            ),

            font_family=NB_FONT,

            xaxis=dict(
                range=[0, 120],
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),

            yaxis=dict(
                tickfont=dict(
                    size=13,
                    family=NB_FONT,
                    color=NB_NAVY
                ),
                showgrid=False,
                autorange="reversed"
            )
        )

        return fig

    except Exception as e:

        print(f"[COMPORTAMIENTO_INTERVALO] {e}")

        return empty_figure()
#-------------------------------------------------------------
#Pagina de contacto
#--------------------------------------------------------------

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
                #KPIs
                html.Div([
                    kpi_card("Peor mes de contacto - 70% a 80%≈",       "Diciembre",    " ",        C["accent2"], C=C),
                    kpi_card("Optima combinación de contacto y zona",   "Noroeste-Junio", " ", C["success"],    C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),
                # Heatmap receptividad
                html.Div([
                    dcc.Graph(figure=fig_contacto_heatmap(contacto_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # 70/30
                html.Div([
                    dcc.Graph(figure=fig_contacto_70_30(contacto_data),
                              config={"displayModeBar":False}),
                ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

                # Comportamiento por intervalo
                html.Div([
                    dcc.Graph(figure=fig_comportamiento_intervalo(contacto_data),
                              config={"displayModeBar":False},
                              style={"height": "360px"})
                ],style={"background":C["card"],"border":f"1px solid {C['border']}",
                          "borderRadius":"12px","padding":"18px","marginBottom":"12px",
                          "boxShadow":"0 2px 14px rgba(0,0,0,0.12)"}),

            ], style={"flex":"1","minWidth":"0","padding":"0 16px 20px 20px","overflowY":"auto"}),

            # ── Columna derecha ────────────────────────────────────────
            html.Div([
                card_momento_optimo_html(contacto_data),
            ], style={"width":"300px","minWidth":"300px","padding":"0 20px 20px 0",
                      "overflowY":"auto","flexShrink":"0"}),

        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])
