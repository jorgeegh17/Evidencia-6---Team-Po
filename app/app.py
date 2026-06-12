#Librerias de dash
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

#Librerias propias de la aplicación
from theme import THEMES, FONT, FONT_MONO
from dashboard_codigo.componentes_secciones.componentes import make_sidebar, apply_layout
from dashboard_codigo.secciones.subir_archivos      import page_upload
#from dashboard_codigo.secciones.overview            import page_overview
#from dashboard_codigo.secciones.agricultura       import page_agricultura
#from dashboard_codigo.secciones.distribuidores      import page_distribuidores
from dashboard_codigo.secciones.retencion         import page_retencion
from dashboard_codigo.secciones.contacto          import page_contacto
from dashboard_codigo.secciones.conversion        import page_conversion
from pipeline import load_processed_data_from_buffers

#----------------------------------------
# CÓDIGO PRINCIPAL DE LA APLICACIÓN
#----------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="CNH Aftermarket Intel",
)

app.layout = html.Div([
    dcc.Location(id="url",            refresh=False),
    dcc.Store(id="theme-store",       data="light"),
    dcc.Store(id="upload-store",      data={}),
    dcc.Store(id="pipeline-ready",    data=False),
    dcc.Store(id="pipeline-data",     data={}),
    dcc.Store(id="process-trigger",   data=0),
    html.Div(id="app-shell"),
])

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
        .rc-slider-rail { background-color: rgba(130,121,112,0.3) !important; height: 6px !important; }
        .rc-slider-track { background-color: #900C0E !important; height: 6px !important; }
        .rc-slider-handle { border: 2px solid #900C0E !important; background-color: #FFFFFF !important;
                            width: 14px !important; height: 14px !important; margin-top: -4px !important; cursor: grab !important; }
        .rc-slider-handle:active { cursor: grabbing !important; }
        .rc-slider-mark-text { font-size: 10px !important; font-family: 'IBM Plex Mono', monospace !important; }
    </style></head>"""
)


def _dashboard_shell(pathname, theme, pipeline_data=None):
    C       = THEMES.get(theme, THEMES["light"])
    sidebar = make_sidebar(C, pathname)
    #toggle  = make_theme_toggle(theme)
    base_style = {"marginLeft":"180px","minHeight":"100vh","background":C["bg"],
                  "fontFamily":FONT,"color":C["text"],"transition":"background 0.3s, color 0.3s"}

    retencion_data = pipeline_data.get("retencion_data") if pipeline_data else None
    tasa_intervalo     = pipeline_data.get("tasa_intervalo")     if pipeline_data else None
    contacto_data      = pipeline_data.get("contacto_data")      if pipeline_data else None
    conversion_data    = pipeline_data.get("conversion_data")    if pipeline_data else None

    #if   pathname == "/agricultura":   page = page_agricultura(C)
    #elif pathname == "/distribuidores":page = page_distribuidores(C)
    #if pathname == "/retencion":     page = page_retencion(C, retencion_data=retencion_data)
    if pathname == "/contacto":      page = page_contacto(C, contacto_data=contacto_data, conversion_data=conversion_data)
    elif pathname == "/conversion":    page = page_conversion(C, conversion_data=conversion_data)
    else:                              page = page_retencion(C, retencion_data=retencion_data)

    return html.Div([
        dcc.Location(id="url-inner", refresh=False),
        sidebar,
        html.Div(page, id="page-content", style=base_style),
    ])


# ── Callbacks (importados desde callbacks.py) ─────────────────────────────────
from callbacks import register_callbacks   # noqa: E402
register_callbacks(app, _dashboard_shell, load_processed_data_from_buffers,
                   page_upload, THEMES, FONT, FONT_MONO)

if __name__ == "__main__":
    app.run(debug=True)
