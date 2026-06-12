import base64
import pandas as pd
import numpy as np
from datetime import datetime

import dash
from dash import Input, Output, State, no_update, html

from theme import THEMES, FONT, FONT_MONO


def register_callbacks(app, _dashboard_shell, load_processed_data_from_buffers,
                       page_upload, THEMES, FONT, FONT_MONO):

    #from pages.agricultura import zonas   # datos globales de parcoords

    @app.callback(
        Output("upload-store","data"),
        Input("upload-pop","contents"), Input("upload-hrs","contents"),
        Input("upload-mnt","contents"), Input("upload-rep","contents"),
        Input("btn-detach-pop","n_clicks"), Input("btn-detach-hrs","n_clicks"),
        Input("btn-detach-mnt","n_clicks"), Input("btn-detach-rep","n_clicks"),
        State("upload-pop","filename"),  State("upload-hrs","filename"),
        State("upload-mnt","filename"),  State("upload-rep","filename"),
        State("upload-store","data"),
        prevent_initial_call=True,
    )
    def accumulate_uploads(pop_c,hrs_c,mnt_c,rep_c,pop_d,hrs_d,mnt_d,rep_d,
                           pop_n,hrs_n,mnt_n,rep_n,current_store):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_store or {}
        store = dict(current_store or {})
        tid = ctx.triggered[0]["prop_id"].split(".")[0]
        if   tid=="upload-pop" and pop_c: store["PopulationView_2026.xlsx"]           = {"filename":pop_n,"content":pop_c}
        elif tid=="upload-hrs" and hrs_c: store["Horas 2024-2025.xlsx"]               = {"filename":hrs_n,"content":hrs_c}
        elif tid=="upload-mnt" and mnt_c: store["Mantenimientos 2024-2025.xlsx"]      = {"filename":mnt_n,"content":mnt_c}
        elif tid=="upload-rep" and rep_c: store["Reporte_unidades_dia_anterior.xlsx"] = {"filename":rep_n,"content":rep_c}
        elif tid=="btn-detach-pop": store.pop("PopulationView_2026.xlsx",           None)
        elif tid=="btn-detach-hrs": store.pop("Horas 2024-2025.xlsx",               None)
        elif tid=="btn-detach-mnt": store.pop("Mantenimientos 2024-2025.xlsx",      None)
        elif tid=="btn-detach-rep": store.pop("Reporte_unidades_dia_anterior.xlsx", None)
        return store

    @app.callback(
        Output("process-trigger","data"),
        Input("upload-store","data"),
        State("process-trigger","data"),
        prevent_initial_call=True,
    )
    def update_process_trigger(upload_store, current_trigger):
        return (current_trigger or 0)+1

    @app.callback(
        Output("app-shell","children"),
        Output("pipeline-ready","data"),
        Input("process-trigger","data"),
        Input("url","pathname"),
        State("upload-store","data"),
        State("pipeline-ready","data"),
        State("pipeline-data","data"),
        State("theme-store","data"),
        prevent_initial_call=False,
    )
    def render_app_shell(trigger,pathname,upload_store,pipeline_ready,pipeline_data_stored,theme):
        if pipeline_ready and pipeline_data_stored:
            def _reconstruct(raw_dict, df_keys):
                if not raw_dict: return raw_dict or {}
                out = dict(raw_dict)
                for k in df_keys:
                    if k in out and isinstance(out[k],list):
                        out[k] = pd.DataFrame(out[k])
                return out
            contacto_data = _reconstruct(pipeline_data_stored.get("contacto_data",{}),
                                         ["pivot","hm","df_estrategia","df_tasa"])
            if contacto_data and "pivot" in contacto_data and isinstance(contacto_data["pivot"],pd.DataFrame):
                pv = contacto_data["pivot"]
                if len(pv.columns)>1 and "zona" in pv.columns:
                    contacto_data["pivot"] = pv.set_index("zona")
            conversion_data    = _reconstruct(pipeline_data_stored.get("conversion_data",{}),["top3","bottom3","dist_dual"])
            retencion_data = _reconstruct(pipeline_data_stored.get("retencion_data",{}), ["df_tasa", "df_pares"])
            pipeline_data = {"contacto_data":contacto_data,"conversion_data":conversion_data,"retencion_data":retencion_data}
            return _dashboard_shell(pathname,theme,pipeline_data), True
        if pipeline_ready:
            return _dashboard_shell(pathname,theme,{}), True
        return page_upload(upload_store,theme), False

    @app.callback(
        Output("pipeline-ready","data",        allow_duplicate=True),
        Output("app-shell","children",         allow_duplicate=True),
        Output("upload-processing-output","children", allow_duplicate=True),
        Output("btn-process-files","disabled", allow_duplicate=True),
        Output("pipeline-data","data",         allow_duplicate=True),
        Input("btn-process-files","n_clicks"),
        State("upload-store","data"),
        State("url","pathname"),
        State("theme-store","data"),
        prevent_initial_call=True,
    )
    def process_and_launch(n_clicks,upload_store,pathname,theme):
        if not n_clicks or not upload_store:
            return no_update,no_update,no_update,no_update,no_update
        C = THEMES.get(theme,THEMES["light"])
        try:
            buffers = {}
            for cname,fi in upload_store.items():
                if fi and "content" in fi:
                    _,b64 = fi["content"].split(",",1)
                    buffers[cname] = base64.b64decode(b64)
            result = load_processed_data_from_buffers(buffers)
            contacto_raw   = result.get("contacto_data",{})
            conversion_raw = result.get("conversion_data",{})
            retencion_raw  = result.get("retencion_data",{})

            def _df_to_dict(obj):
                """
                Convierte cualquier estructura compleja a un formato
                serializable por JSON/Dash.
                """

                if obj is None:
                    return None

                # DataFrame
                if isinstance(obj, pd.DataFrame):
                    return obj.to_dict("records")

                # Series
                if isinstance(obj, pd.Series):
                    return obj.to_dict()

                # NumPy scalars
                if isinstance(obj, np.integer):
                    return int(obj)

                if isinstance(obj, np.floating):
                    return float(obj)

                if isinstance(obj, np.bool_):
                    return bool(obj)

                # Arrays NumPy
                if isinstance(obj, np.ndarray):
                    return obj.tolist()

                # Diccionarios (recursivo)
                if isinstance(obj, dict):
                    return {
                        k: _df_to_dict(v)
                        for k, v in obj.items()
                    }

                # Listas / tuplas (recursivo)
                if isinstance(obj, (list, tuple)):
                    return [
                        _df_to_dict(v)
                        for v in obj
                    ]

                # Timestamp pandas
                if isinstance(obj, pd.Timestamp):
                    return obj.isoformat()

                # NaN
                if pd.isna(obj):
                    return None

                # Cualquier otro tipo nativo
                return obj

            stored_data = {"contacto_data":_df_to_dict(contacto_raw),
                           "conversion_data":_df_to_dict(conversion_raw),
                           "retencion_data":_df_to_dict(retencion_raw)}
            pipeline_data = {"contacto_data":contacto_raw,"conversion_data":conversion_raw,"retencion_data":retencion_raw}
            return True, _dashboard_shell(pathname,theme,pipeline_data), "", True, stored_data
        except Exception as exc:
            err_msg = html.Div(f"⚠ Error al procesar: {exc}",style={
                "color":C["danger"],"fontSize":"12px","marginTop":"12px","fontFamily":FONT_MONO,
                "padding":"10px 14px","background":"rgba(193,18,31,0.08)",
                "borderRadius":"8px","border":f"1px solid {C['danger']}",
            })
            return False, html.Div([page_upload(upload_store,theme),err_msg]),"",False,no_update

    @app.callback(Output("clock","children"),Input("interval-clock","n_intervals"))
    def update_clock(n):
        return datetime.now().strftime("%d %b %Y  %H:%M:%S")