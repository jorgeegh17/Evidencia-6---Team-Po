from dash import dcc, html
from theme import THEMES, FONT, FONT_MONO

FILE_META = {
    "PopulationView_2026.xlsx":           ("◈", "Population View",  "Control Room – inventario de unidades activas"),
    "Horas 2024-2025.xlsx":               ("⬡", "Horas 2024–2025",  "Horómetros mensuales por unidad (hojas 2024 / 2025)"),
    "Mantenimientos 2024-2025.xlsx":      ("◎", "Mantenimientos",   "Órdenes de trabajo y estatus de servicios"),
    "Reporte_unidades_dia_anterior.xlsx": ("⊞", "Unidades Día Ant.","Reporte diario de unidades con horómetro y alertas"),
}

ID_MAP = {
    "PopulationView_2026.xlsx":           "pop",
    "Horas 2024-2025.xlsx":               "hrs",
    "Mantenimientos 2024-2025.xlsx":       "mnt",
    "Reporte_unidades_dia_anterior.xlsx":  "rep",
}


def page_upload(upload_store=None, theme="dark"):
    C = THEMES.get(theme, THEMES["dark"])
    if upload_store is None:
        upload_store = {}

    def _file_cell(canonical_name, icon, label, desc):
        file_info   = upload_store.get(canonical_name)
        uploaded    = file_info is not None
        key         = ID_MAP[canonical_name]
        actual_name = file_info.get("filename", "") if uploaded else ""

        loaded_row = html.Div([
            html.Div([
                html.Span(icon, style={"fontSize":"20px","color":C["success"],"marginRight":"14px"}),
                html.Div([
                    html.Div(label,       style={"fontSize":"13px","fontWeight":"700","color":C["text"],"letterSpacing":"0.3px"}),
                    html.Div(actual_name, style={"fontSize":"10px","color":C["muted"],"fontFamily":FONT_MONO,"marginTop":"2px","wordBreak":"break-all"}),
                    html.Div(desc,        style={"fontSize":"10px","color":C["muted"],"marginTop":"1px"}),
                ], style={"flex":"1","minWidth":"0"}),
            ], style={"display":"flex","alignItems":"center","flex":"1","minWidth":"0"}),
            html.Div([
                html.Span("✓ Cargado", style={"fontSize":"10px","color":C["success"],"fontFamily":FONT_MONO,"fontWeight":"700","marginRight":"12px"}),
                html.Button("✕ Desacoplar", id=f"btn-detach-{key}", n_clicks=0, style={
                    "background":"transparent","color":C["danger"],"border":f"1px solid {C['danger']}",
                    "borderRadius":"6px","padding":"4px 10px","fontSize":"10px","fontWeight":"600",
                    "cursor":"pointer","transition":"all 0.2s",
                }),
            ], style={"display":"flex","alignItems":"center","whiteSpace":"nowrap","marginLeft":"12px"}),
        ], style={
            "display":"flex" if uploaded else "none",
            "alignItems":"center","justifyContent":"space-between",
            "padding":"14px 18px","background":"rgba(6,214,160,0.06)",
            "border":"1px solid rgba(6,214,160,0.25)","borderRadius":"10px","transition":"all 0.3s",
        })

        upload_zone = dcc.Upload(
            id=f"upload-{key}",
            children=html.Div([
                html.Span(icon, style={"fontSize":"20px","color":C["accent"],"marginRight":"14px"}),
                html.Div([
                    html.Div(label, style={"fontSize":"13px","fontWeight":"700","color":C["text"]}),
                    html.Div("Arrastra aquí tu archivo Excel o haz clic para seleccionarlo",
                             style={"fontSize":"11px","color":C["muted"],"marginTop":"2px"}),
                    html.Div(desc, style={"fontSize":"10px","color":C["muted"],"marginTop":"1px"}),
                ], style={"textAlign":"left","flex":"1"}),
            ], style={"display":"flex","alignItems":"center"}),
            style={
                "border":f"1px dashed {C['border']}","borderRadius":"10px","padding":"14px 18px",
                "background":"rgba(144,12,14,0.02)","cursor":"pointer","transition":"all 0.2s",
                "display":"none" if uploaded else "block",
            },
            multiple=False,
        )
        return html.Div([upload_zone, loaded_row], style={"marginBottom":"10px"})

    file_cells = [_file_cell(fname, *meta) for fname, meta in FILE_META.items()]
    all_loaded  = all(f in upload_store for f in FILE_META)

    return html.Div([
        html.Div(style={"position":"fixed","inset":"0",
                        "background":f"radial-gradient(ellipse at 20% 50%, rgba(144,12,14,0.08) 0%, transparent 60%), {C['bg']}",
                        "zIndex":"-1"}),
        html.Div([
            html.Div([
                html.Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/CNH_Industrial.svg/500px-CNH_Industrial.svg.png",
                         style={"height":"32px","filter":"brightness(0) invert(1)" if theme=="dark" else "brightness(0)",
                                "opacity":"0.9","marginBottom":"12px"}),
                html.Div("AFTERMARKET INTELLIGENCE", style={"fontSize":"9px","letterSpacing":"4px","color":C["muted"],"marginBottom":"4px"}),
                html.H2("Cargar archivos de datos", style={"color":C["text"],"fontWeight":"800","fontSize":"24px","margin":"0 0 6px 0","letterSpacing":"-0.5px"}),
                html.Div("Sube cada uno de los cuatro archivos Excel en su celda correspondiente para inicializar el pipeline.",
                         style={"color":C["muted"],"fontSize":"12px","maxWidth":"460px","lineHeight":"1.6"}),
            ], style={"marginBottom":"32px","textAlign":"center"}),

            html.Div(file_cells, id="upload-file-cells"),
            html.Div(id="upload-error-msg", style={"color":C["danger"],"fontSize":"12px","marginTop":"12px","fontFamily":FONT_MONO,"minHeight":"18px"}),

            html.Div([
                dcc.Loading(
                    id="loading-process",
                    children=[
                        html.Button(
                            [html.Span("⬡", style={"marginRight":"8px"}), "Procesar y lanzar dashboard"],
                            id="btn-process-files",
                            disabled=not all_loaded,
                            style={
                                "background":C["accent"] if all_loaded else C["card2"],
                                "color":"#FFFFFF" if all_loaded else C["muted"],
                                "border":"none","borderRadius":"10px","padding":"13px 32px",
                                "fontSize":"13px","fontWeight":"700","fontFamily":FONT,
                                "cursor":"pointer" if all_loaded else "not-allowed","letterSpacing":"0.5px",
                                "boxShadow":"0 4px 20px rgba(144,12,14,0.35)" if all_loaded else "none","transition":"all 0.2s",
                            }
                        ),
                        html.Div(id="upload-processing-output", style={"display":"none"}),
                    ],
                    type="circle", color=C["accent"], style={"marginTop":"20px"},
                ),
            ], style={"textAlign":"center","minHeight":"60px"}),

        ], style={"maxWidth":"560px","width":"100%","margin":"0 auto","padding":"60px 24px 40px","fontFamily":FONT}),
    ], style={"height":"100vh","background":C["bg"],"display":"flex","alignItems":"center",
              "justifyContent":"center","color":C["text"],"fontFamily":FONT,"overflowY":"auto"})