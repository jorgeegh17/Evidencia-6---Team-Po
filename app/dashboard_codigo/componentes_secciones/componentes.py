from dash import dcc, html
from theme import THEMES, FONT, FONT_MONO
import plotly.graph_objects as go
#----------------------------------------
# FUNCIONES PARA HACER LOS PLOTS
#----------------------------------------
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
        "boxShadow": "0 2px 12px rgba(0,0,0,0.15)",
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
        "boxShadow": "0 2px 14px rgba(0,0,0,0.12)",
        "transition": "background 0.3s, border-color 0.3s",
    })


def make_sidebar(C, pathname=None):
    nav_items = [
        ("⊞", "Retención",       "retencion"),
        ("⬢", "Conversión por Distribuidor",      "conversion"),
        ("⊙", "Contacto Óptimo Agricultura","contacto"),
    ]
    links = []
    for icon, label, page in nav_items:
        is_active = (pathname == f"/{page}") or (page == "retencion" and pathname in ["/", "", None])
        bg           = "rgba(144, 12, 14, 0.15)" if is_active else "transparent"
        border_left  = f"4px solid {C['accent']}" if is_active else "4px solid transparent"
        font_weight  = "700" if is_active else "600"
        box_shadow   = "inset -2px 0 8px rgba(144,12,14,0.05), 0 4px 12px rgba(144,12,14,0.08)" if is_active else "none"
        links.append(
            dcc.Link(
                html.Div([
                    html.Span(icon, style={"fontSize":"14px","marginRight":"10px",
                                          "color": C["accent2"] if is_active else C["accent"]}),
                    html.Span(label, style={"fontSize":"12px","fontWeight":font_weight,
                                           "letterSpacing":"0.5px","color":C["text"]}),
                ], className="nav-item", style={
                    "display":"flex","alignItems":"center","padding":"10px 16px",
                    "cursor":"pointer","borderRadius":"0 6px 6px 0",
                    "margin":"2px 8px 2px 0","transition":"all 0.15s",
                    "background":bg,"borderLeft":border_left,"boxShadow":box_shadow,
                }),
                href=f"/{page}", refresh=False
            )
        )
    return html.Div([
        html.Div([
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/CNH_Industrial.svg/500px-CNH_Industrial.svg.png",
                style={"height":"26px",
                       "filter":"brightness(0) invert(1)" if C["name"]=="dark" else "brightness(0)",
                       "opacity":"0.92","display":"block","marginBottom":"6px"}
            ),
            html.Div("AFTERMARKET INTEL", style={"fontSize":"8px","color":C["muted"],
                                                "letterSpacing":"2px","marginTop":"0px"}),
        ], style={"padding":"20px 16px 16px","borderBottom":f"1px solid {C['border']}"}),
        html.Div(links, style={"padding":"12px 0"}),
        html.Div("v1.0 · Mayo 2026", style={"position":"absolute","bottom":"16px","left":"16px",
                                             "fontSize":"9px","color":C["muted"]}),
    ], style={
        "width":"180px","minWidth":"180px","height":"100vh",
        "background":C["sidebar"],"borderRight":f"1px solid {C['border']}",
        "position":"fixed","left":"0","top":"0","zIndex":"100",
        "display":"flex","flexDirection":"column","overflow":"hidden","transition":"background 0.3s",
    })


def make_topbar(page_title, C):
    return html.Div([
        html.Span(page_title, style={"fontSize":"14px","fontWeight":"700","color":C["text"],
                                     "textTransform":"uppercase","letterSpacing":"2px"}),
        html.Div([
            html.Span("● LIVE", style={"color":C["accent"],"fontSize":"10px",
                                       "marginRight":"16px","fontFamily":FONT_MONO}),
            html.Div(id="clock", style={"fontSize":"11px","color":C["muted"],"fontFamily":FONT_MONO}),
        ], style={"display":"flex","alignItems":"center"}),
    ], style={
        "display":"flex","justifyContent":"space-between","alignItems":"center",
        "padding":"12px 20px","borderBottom":f"2px solid {C['accent']}",
        "background":C["bg"],"marginBottom":"16px","transition":"background 0.3s",
    })

def empty_figure():
    fig = go.Figure()

    fig.update_layout(
        template="plotly_white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text="",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper"
            )
        ]
    )

    return fig
