# pyrefly: ignore [missing-import]
from pandas.core.arrays import floating
from dashboard_codigo.secciones import retencion
from dash import dcc, html
#Importaciones de librerias internas
from ..componentes_secciones.componentes import make_topbar, kpi_card, chart_card, apply_layout, empty_figure
import plotly.graph_objects as go
from theme import NB_GREEN, NB_WHITE, FONT_MONO, NB_RED_BAR, NB_FONT
from plotly.subplots import make_subplots as _msp
intervalos_ag = ["150h", "300h", "600h", "900h", "1200h"]

cumplimiento_intervalo = [78.2, 63.4, 24.1, 4.9, 2.3]
incumplimiento_intervalo = [100-x for x in cumplimiento_intervalo]


meses = ["Ene'24","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic'24",
         "Ene'25","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic'25"]
abandono_mensual = [72.1, 71.8, 73.0, 51.1, 58.3, 62.4, 64.8, 67.2, 65.1, 71.3, 76.8, 80.3,
                    71.9, 70.5, 72.8, 52.3, 57.9, 61.7, 63.5, 66.8, 64.9, 73.1, 77.2, 80.3]
# En retencion.py (visualización) — AGREGAR esta función nueva
def fig_tasa_cumplimiento(retencion_data, C):
    try:

        df_tasa = retencion_data['df_tasa']

        C_TEAL = '#2A9D8F'
        C_CRIMSON = '#A20503'
        C_WHITE = '#FFFFFF'
        C_NAVY = '#1B2A4A'
        FONT = 'Arial, sans-serif'

        fig = go.Figure()

        # ────────────────────────────────────────────
        # Barra verde (cumplimiento)
        # ────────────────────────────────────────────
        fig.add_trace(go.Bar(
            y=df_tasa['intervalo'],
            x=[1.0] * len(df_tasa),
            orientation='h',
            marker=dict(
                color=C_TEAL,
                line=dict(color=C_WHITE, width=1)
            ),
            text=[
                f"{v:.1%} cumple"
                for v in df_tasa['tasa_cumple']
            ],
            textposition='outside',
            textfont=dict(
                size=12,
                family=FONT,
                color=C_TEAL
            ),
            customdata=df_tasa[
                ['n_cumplieron', 'tasa_cumple', 'n']
            ].values,
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Tasa de cumplimiento: <b>%{customdata[1]:.1%}</b><br>'
                'Unidades con dato registrado: <b>%{customdata[2]:,}</b><br>'
                '🟢 Unidades que cumplieron: <b>%{customdata[0]:,}</b>'
                '<extra></extra>'
            ),
            showlegend=False,
            name='Cumplimiento'
        ))

        # ────────────────────────────────────────────
        # Barra roja (incumplimiento)
        # ────────────────────────────────────────────
        fig.add_trace(go.Bar(
            y=df_tasa['intervalo'],
            x=df_tasa['tasa_incumple'],
            orientation='h',
            marker=dict(
                color=C_CRIMSON,
                line=dict(color=C_WHITE, width=1)
            ),
            text=[
                f"<b>{v:.1%}</b> incumple"
                for v in df_tasa['tasa_incumple']
            ],
            textposition='inside',
            insidetextanchor='end',
            textfont=dict(
                size=13,
                family=FONT,
                color=C_WHITE
            ),
            customdata=df_tasa[
                ['n', 'tasa_incumple', 'n_incumplieron']
            ].values,
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Tasa de incumplimiento: <b>%{customdata[1]:.1%}</b><br>'
                'Unidades con dato registrado: <b>%{customdata[0]:,}</b><br>'
                '🔴 Unidades que incumplieron: <b>%{customdata[2]:,}</b>'
                '<extra></extra>'
            ),
            showlegend=False,
            name='Incumplimiento'
        ))

        fig.update_layout(
            barmode='overlay',
            template='plotly_white',
            autosize=True,
            height=520,
            margin=dict(
                t=120,
                b=20,
                l=35,
                r=35
            ),
            bargap=0.15,
            title=dict(
                text="<b>TASA DE INCUMPLIMIENTO / CUMPLIMIENTO POR INTERVALO DE SERVICIO",
                x=0.02,
                xanchor="left",
                font=dict(
                    size=22,
                    color="#80838A"
                )
            ),
            xaxis=dict(
                range=[0, 1.20],
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                autorange='reversed',
                showgrid=False
            )
        )

        return fig

    except Exception as e:
        print(f"[RETENCION] {e}")
        return empty_figure()
def fig_retorno_servicio(retencion_data, C):
    FONT      = 'Arial, sans-serif'
    try:
        df_pares = retencion_data['df_pares']
        colores_ret = ['#2A9D8F' if v >= 0.05 else '#A20503' for v in df_pares['tasa_retorno']]

        fig = go.Figure()

        # Barras con color individual por valor
        fig.add_trace(
            go.Bar(
                x=df_pares['intervalo'],
                y=df_pares['tasa_retorno'],
                marker_color=colores_ret,
                marker_line_color='white',
                marker_line_width=1,
                opacity=0.85,
                text=[f'{v:.1%}' for v in df_pares['tasa_retorno']],
                textposition='outside',
                showlegend=False
            )
        )

        # Línea umbral 5%
        fig.add_hline(
            y=0.05,
            line_dash='dash',
            line_color='#2c3e50',
            line_width=1.5,
            annotation_text='Umbral 5% — criterio operativo de negocio',
            annotation_position='top right'
        )
        fig.add_annotation(
            x=0.5,
            y=-0.35,
            xref='paper',
            yref='paper',
            showarrow=False,
            align='center',
            text=(
                '<i>El umbral del 5% fue definido como criterio operativo de negocio, '
                'representa el nivel por debajo del cual<br>'
                'la tasa de retorno indica una pérdida estructural del cliente '
                'que no es recuperable fácilmente</i>'
            ),
            font=dict(
                size=10,
                color='#6B7280'
            )
        )

        fig.add_annotation(
            x=0.5,
            y=-0.48,
            xref='paper',
            yref='paper',
            showarrow=False,
            align='center',
            text=(
                '<b>El punto de quiebre no ocurre cuando el cliente abandona, '
                'ocurre 300 horas antes.</b>'
            ),
            font=dict(
                size=14,
                color='#6B7280'
            )
        )

        # Trazas fantasma para la leyenda
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color='#2A9D8F',
                            name='Retorno ≥ 5%', showlegend=True))
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color='#A20503',
                            name='Retorno < 5%', showlegend=True))

        fig.update_layout(
            title=dict(
                text='<b>TASA DE RETORNO AL SIGUIENTE SERVICIO, TRAS INCUMPLIR EL INTERVALO</b>',
                x=0,
                xanchor='left',
                font=dict(
                    size=18,
                    color='#80838A',
                    family=FONT
                )
            ),
            height=530,
            yaxis_title='<b>Tasa de retorno al siguiente servicio<b>',
            yaxis=dict(tickformat='.0%', range=[0, 0.22]),
            xaxis=dict(tickangle=45),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x= 1
            ),
            template='plotly_white',
            #height=450,
            autosize= True,
            margin=dict(
                l=40,
                r=20,
                t=60,
                b=180
            ),
        )
        return fig
    except Exception as e:
        print(f"[RETENCION] {e}")
        return empty_figure()
def fig_probabilidad_retorno(retencion_data, C):
    try:

        # ── PALETA ─────────────────────────────────────
        C_CRIMSON = '#9B1B30'
        C_RED     = '#A20503'
        C_GOLD    = '#E9C46A'
        C_TEAL    = '#2A9D8F'
        C_GREEN   = '#27AE60'
        C_NAVY    = '#1B2A4A'
        C_GRAY    = '#6B7280'
        C_LGRAY   = '#E5E7EB'
        C_WHITE   = '#FFFFFF'
        FONT      = 'Arial, sans-serif'

        # ── DATOS ──────────────────────────────────────
        ret = retencion_data['retencion_externa']

        pct_0 = ret["tasas"].get("0 externos", 0)
        pct_1 = ret["tasas"].get("1 externo", 0)
        pct_2 = ret["tasas"].get("≥2 externos", 0)

        n_0 = ret["n"].get("0 externos", 0)
        n_1 = ret["n"].get("1 externo", 0)
        n_2 = ret["n"].get("≥2 externos", 0)

        control = ret.get("control", 0)

        caida_pp = round(pct_1, 1) - round(pct_2, 1)

        etiquetas_y = [
            "Sin servicios externos",
            "1 servicio externo<br><sup style='color:#E9A820'>↑ Ventana de intervención</sup>",
            "≥2 servicios externos<br><sup style='color:#E63946'>▲ Punto de no retorno</sup>"
        ]

        tasas = [
            pct_0,
            pct_1,
            pct_2
        ]

        colores = [
            C_TEAL,
            C_GREEN,
            C_RED
        ]

        fig = go.Figure()

        # ──────────────────────────────────────────────
        # Fondo gris (100%)
        # ──────────────────────────────────────────────
        fig.add_trace(go.Bar(
            y=etiquetas_y,
            x=[100, 100, 100],
            orientation='h',
            marker=dict(color=C_LGRAY),
            hoverinfo='skip',
            showlegend=False
        ))

        # ──────────────────────────────────────────────
        # Barras principales
        # ──────────────────────────────────────────────
        fig.add_trace(go.Bar(
            y=etiquetas_y,
            x=tasas,
            orientation='h',
            marker=dict(
                color=colores,
                line=dict(color=C_WHITE, width=2)
            ),
            text=[f'<b>{v:.1f}%</b>' for v in tasas],
            textposition='outside',
            textfont=dict(
                size=16,
                family=FONT,
                color=C_NAVY
            ),
            cliponaxis=False,
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Probabilidad de retorno: %{x:.1f}%<extra></extra>',
            showlegend=False
        ))

        # ──────────────────────────────────────────────
        # Línea grupo control
        # ──────────────────────────────────────────────
        fig.add_vline(
            x=control,
            line=dict(
                color=C_NAVY,
                width=1.5,
                dash='dot'
            )
        )

        # ──────────────────────────────────────────────
        # Línea punto de no retorno
        # ──────────────────────────────────────────────
        fig.add_vline(
            x=pct_2,
            line=dict(
                color=C_RED,
                width=1.5,
                dash='dash'
            )
        )

        # ──────────────────────────────────────────────
        # Flecha recuperación
        # ──────────────────────────────────────────────
        fig.add_annotation(
            x=pct_1,
            y=1,
            ax=pct_2,
            ay=1,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            text='',
            showarrow=True,
            arrowhead=3,
            arrowsize=1.3,
            arrowwidth=3,
            arrowcolor=C_CRIMSON
        )

        # ──────────────────────────────────────────────
        # Caja descriptiva
        # ──────────────────────────────────────────────
        fig.add_annotation(
            x=(pct_1 + pct_2) / 2,
            y=1.9,
            text=(
                '<b>Ventana de recuperación:</b><br>'
                'aquí el cliente todavía es recuperable.<br>'
                f'Caída de <b>{caida_pp:.1f}pp</b> al cruzar al 2do externo.'
            ),
            showarrow=False,
            align='left',
            bgcolor='rgba(255,245,245,0.95)',
            bordercolor=C_CRIMSON,
            borderwidth=1,
            borderpad=8,
            font=dict(
                size=11,
                color=C_CRIMSON,
                family=FONT
            )
        )

        # ──────────────────────────────────────────────
        # Layout
        # ──────────────────────────────────────────────
        fig.update_layout(
            title=dict(
                text='<b>PROBABILIDAD DE RETORNO CON SERVICIOS EXTERNOS</b>',
                x=0,
                xanchor='left',
                font=dict(
                    size=18,
                    color='#80838A',
                    family=FONT
                )
            ),

            annotations=[
                *fig.layout.annotations,
                dict(
                    text='El comportamiento del cliente indica el retorno — El 2do servicio externo cierra la ventana',
                    x=0,
                    y=1.08,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(
                        size=12,
                        color=C_GRAY
                    ),
                    xanchor='left'
                )
            ],

            barmode='overlay',

            xaxis=dict(
                title='<b>Probabilidad de retorno a red CNH (%)</b>',
                ticksuffix='%',
                range=[0, 100],
                gridcolor='#ECECEC',
                zeroline=False
            ),

            yaxis=dict(
                autorange='reversed',
                showgrid=False,
                tickfont=dict(
                    size=13,
                    family=FONT
                )
            ),

            paper_bgcolor=C_WHITE,
            plot_bgcolor=C_WHITE,

            height=450,

            margin=dict(
                t=110,
                b=70,
                l=220,
                r=80
            ),

            font_family=FONT
        )

        return fig

    except Exception as e:
        print(f"[RETENCION] {e}")
        return empty_figure()
def page_retencion(C, retencion_data=None):
    if retencion_data is None:
        # fallback sintético
        retencion_data = {
            'n_cumplio': 271, 'n_incumplio': 320, 'total_600': 591,
            'pct_cumplio': 0.458, 'pct_incumplio': 0.542,
            'tasa_cumplio_en_600': 0.63, 'tasa_incumplio_en_600': 0.06,
        }
    return html.Div([
        make_topbar("Retención · Análisis de Abandono", C),
        html.Div([
            #Columna izquierda
            html.Div([
                html.Div([
                    kpi_card("Punto quiebre",       "600h",    "Retorno 4.9%",        C["accent2"], C=C),
                    kpi_card("Punto no retorno",   "≥2 servicios externos.", "Probabilidad retorno 12.1%", C["warn"],    C=C),
                ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),
                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_retorno_servicio(retencion_data,C), config={"displayModeBar":False}),
                                         None , C)],
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"12px","marginBottom":"12px","flexWrap":"wrap"}),

                html.Div(style={"height":"12px"}),

                # ── NUEVAS: Unidades 600h ──────────────────────────────

                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_probabilidad_retorno(retencion_data,C), config={"displayModeBar":False}),
                                         None, C)],
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"12px","marginBottom":"12px","flexWrap":"wrap"}),
                html.Div([
                    html.Div([chart_card(dcc.Graph(figure=fig_tasa_cumplimiento(retencion_data,C), config={"displayModeBar":False}),
                                         None, C)],
                             style={"flex":"1"}),
                ], style={"display":"flex","gap":"12px","marginBottom":"12px","flexWrap":"wrap"}),

            ], style={"flex":"1","padding":"0 20px 20px 20px","overflowY":"auto"}),

            #Columna derecha
            
        ], style={"display":"flex","height":"calc(100vh - 60px)","overflow":"hidden"}),
        dcc.Interval(id="interval-clock", interval=1000, n_intervals=0),
    ])
