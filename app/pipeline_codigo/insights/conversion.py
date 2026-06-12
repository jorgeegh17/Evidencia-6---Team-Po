import numpy as np
import pandas as pd

# ============================================================
# CONSTANTES — INS-02 Conversión
# ============================================================

ESTATUS_EN_RED   = ["Cerrada", "EnProceso", "PorVencer", "Abierta"]
ESTATUS_FUERA    = "Fuera"          # substring para búsqueda
MIN_ALARMAS_DIST = 20               # mínimo de registros por distribuidor
TOP_N_DIST       = 3                # top/bottom de distribuidores
TOP_N_SC         = 10               # top distribuidores por sobrecarga

CANDIDATOS_DIST_COL = ["distribuidor", "dealer", "dealer_name"]

# Monetización fija (ajustar cuando haya datos reales)
MONETIZACION_DEFAULT = {
    "labels":    ["INS-03", "INS-NEW"],
    "servicios": [200, 150],
    "ingresos":  [3_000_000, 2_250_000],
    "ticket":    15_000,
    "total_svc": 350,
    "total_ing": 5_250_000,
}

# Fallback cuando no hay columna de distribuidor en mant
FALLBACK_TOP3 = {
    "distribuidor":  ["ARBSA", "ATC", "MTM"],
    "tasa_conv_pct": [55.0, 50.0, 42.0],
    "moda_retraso":  [0, 0, 5],
}
FALLBACK_BOTTOM3 = {
    "distribuidor":  ["ENAGRI", "TAPSA", "AGTRAC"],
    "tasa_conv_pct": [7.0, 9.5, 10.0],
    "moda_retraso":  [149, 78, 86],
}
FALLBACK_DIST_DUAL = {
    "distribuidor":  ["ARBSA", "ATC", "MTM", "AGTRAC", "TAPSA", "ENAGRI"],
    "tasa_conv_pct": [55.0, 50.0, 42.0, 10.0, 9.5, 7.0],
    "moda_retraso":  [0, 0, 5, 86, 78, 149],
}
FALLBACK_SC = {
    "distribuidores": [
        "AGTRAC","TEPSA","MADISA","ATN",
        "FERTIMEX","AGROMEX","SERVIAG",
        "CAMSA","ARBSA","ENAGRI"
    ],
    "alarmas_proy": [
        96,83,69,66,41,
        38,35,32,28,22
    ],
    "sobrecarga_pct": [
        41,20,15,12,
        0,0,0,0,0,0
    ]
}
FALLBACK_UMBRAL = 46.4


# ============================================================
# HELPERS
# ============================================================
def _calcular_retencion_externa(uda):

    cols_intervalos = [
        'mant_50',
        'mant_300',
        'mant_600',
        'mant_900',
        'mant_1200',
        'mant_1500',
        'mant_1800',
        'mant_2100',
        'mant_2400'
    ]

    cols_disp = [
        c for c in cols_intervalos
        if c in uda.columns
    ]

    registros = []

    for _, row in uda.iterrows():

        servicios = [
            (c, row[c])
            for c in cols_disp
            if pd.notna(row[c])
        ]

        if not servicios:
            continue

        fuera = 0
        corte = None

        for i, (_, estatus) in enumerate(servicios):

            if estatus == "CerradaFuera":

                fuera += 1

                if fuera == 2:
                    corte = i
                    break

        if corte is not None:

            posteriores = servicios[corte + 1:]

            retorno = int(
                any(e == "Cerrada"
                    for _, e in posteriores)
            )

            grupo = 1

        else:

            retorno = int(
                any(e == "Cerrada"
                    for _, e in servicios)
            )

            grupo = 0

            fuera = sum(
                1
                for _, e in servicios
                if e == "CerradaFuera"
            )

        registros.append({
            "tuvo_2_fuera_previo": grupo,
            "n_fuera_previo": fuera,
            "n_servicios_total": len(servicios),
            "horometro_corte": row.get("horometro", np.nan),
            "retorno_posterior": retorno
        })

    df = pd.DataFrame(registros)

    if df.empty:
        return {
            "tasas": {},
            "n": {},
            "control": 0,
            "df_dx4": pd.DataFrame()
        }

    df["grupo_3"] = df["n_fuera_previo"].apply(
        lambda x:
            "0 externos"
            if x == 0
            else (
                "1 externo"
                if x == 1
                else "≥2 externos"
            )
    )

    orden = [
        "0 externos",
        "1 externo",
        "≥2 externos"
    ]

    res = (
        df.groupby("grupo_3")
        ["retorno_posterior"]
        .agg(["mean", "size"])
        .reindex(orden)
    )

    tasas = (
        res["mean"] * 100
    ).round(2).to_dict()

    n_grupo = (
        res["size"]
        .fillna(0)
        .astype(int)
        .to_dict()
    )

    control = round(
        df.loc[
            df["tuvo_2_fuera_previo"] == 0,
            "retorno_posterior"
        ].mean() * 100,
        2
    )

    return {
        "tasas": tasas,
        "n": n_grupo,
        "control": control,
        "df_dx4": df
    }

def _detectar_col_dist(mant: pd.DataFrame) -> str | None:
    for col in CANDIDATOS_DIST_COL:
        if col in mant.columns:
            return col
    if "alias" in mant.columns:
        return "alias"
    return None

# ── Constantes que necesita el funnel ─────────────────────────────────────────
MARCAS_FUNNEL = ['NEW HOLLAND AG', 'CASE IH']
COLS_INT = [
    'mant_50', 'mant_300', 'mant_600', 'mant_900',
    'mant_1200', 'mant_1500', 'mant_1800', 'mant_2100', 'mant_2400'
]
COLMAP_FUNNEL = {
    'En red CNH':             '#2A9D8F',
    'Sin atender':            '#F4A261',
    'Atendida fuera de red':  '#9B1B30',
    'Sin servicios vencidos': '#adb5bd',
}


def _calcular_funnel(mant: pd.DataFrame, uda: pd.DataFrame) -> dict:
    """
    Replica exactamente la lógica del notebook (Visualización 12).

    Fuente: uda (Unidades día anterior), filtrada por marca y
    melteada sobre columnas de intervalo. NO usa mant.

    Clasificación por unidad (MECE, prioridad en orden):
      1. CerradaFuera  → 'Atendida fuera de red'
      2. Pendiente     → 'Sin atender'
      3. resto         → 'En red CNH'
      4. sin filas     → 'Sin servicios vencidos'
    """
    # Filtrar marcas y construir base melted (igual que el notebook)
    uda_f = uda[uda['marca'].isin(MARCAS_FUNNEL)].copy()
    N_UNIDADES = len(uda_f)

    cols_disp = [c for c in COLS_INT if c in uda_f.columns]
    base = (
        uda_f.melt(
            id_vars=['alias'],
            value_vars=cols_disp,
            var_name='intervalo',
            value_name='estatus'
        )
        .dropna(subset=['estatus'])
    )

    # Clasificar cada alias con la misma función del notebook
    def clasifica(estados):
        if 'CerradaFuera' in estados:
            return 'Atendida fuera de red'
        if 'Pendiente' in estados:
            return 'Sin atender'
        return 'En red CNH'

    estado_unidad = base.groupby('alias')['estatus'].agg(set).apply(clasifica)
    vc = estado_unidad.value_counts()

    # Cuarta categoría: unidades sin ningún intervalo registrado
    sin_servicio = N_UNIDADES - estado_unidad.index.nunique()

    conteo = {
        'En red CNH':             int(vc.get('En red CNH', 0)),
        'Sin atender':            int(vc.get('Sin atender', 0)),
        'Atendida fuera de red':  int(vc.get('Atendida fuera de red', 0)),
        'Sin servicios vencidos': sin_servicio,
    }

    # Ordenar por volumen descendente (da la forma de funnel correcta)
    items = sorted(conteo.items(), key=lambda kv: kv[1], reverse=True)

    etapas = ['Flota total'] + [k for k, _ in items]
    vals   = [N_UNIDADES]   + [v for _, v in items]
    pcts   = [100.0]        + [round(v / N_UNIDADES * 100, 1) for _, v in items]
    colors = ['#457B9D']    + [COLMAP_FUNNEL[k] for k, _ in items]

    return {
        "etapas":     etapas,
        "vals":       vals,
        "pcts":       pcts,
        "colors":     colors,
        "n_unidades": N_UNIDADES,
        "en_red":     conteo['En red CNH'],
    }

def _calcular_dist_stats(mant: pd.DataFrame, dist_col: str) -> pd.DataFrame:
    tmp = mant.copy()

    # Retraso: usar diff_hrs precalculado si existe, igual que el notebook
    if "diff_hrs" in tmp.columns:
        tmp["_retraso"] = tmp["diff_hrs"]
    elif "actual" in tmp.columns and "horometro" in tmp.columns:
        tmp["_retraso"] = (tmp["actual"] - tmp["horometro"]).clip(lower=0)
    else:
        tmp["_retraso"] = 0

    # Filtro de outliers idéntico al notebook
    tmp = tmp[tmp["_retraso"] < 1500]

    stats = (
        tmp.groupby(dist_col)
        .agg(
            # ← usar cumplimiento directamente, igual que el notebook
            tasa_conv_pct=("cumplimiento", lambda s: round(s.mean() * 100, 1)),
            moda_retraso=(
                "_retraso",
                lambda s:
                    round(
                        s.mode().iloc[0]
                        if len(s.mode()) > 0
                        else s.median(),
                        0
                    )
            ),
            n_alarmas=("cumplimiento", "count"),
        )
        .reset_index()
        .rename(columns={dist_col: "distribuidor"})
    )

    # MIN_ALARMAS_DIST debe ser 20 para coincidir con el notebook
    return (
        stats[stats["n_alarmas"] >= MIN_ALARMAS_DIST]
        .copy()
        .sort_values("tasa_conv_pct", ascending=False)
    )
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

def _calcular_sobrecarga_proyectada(mant, dist_col):

    if "fecha" not in mant.columns:
        return pd.DataFrame()

    tmp = mant.copy()

    tmp["fecha"] = pd.to_datetime(
        tmp["fecha"],
        errors="coerce"
    )

    tmp = tmp.dropna(subset=["fecha"])

    tmp["anio_mes"] = (
        tmp["fecha"]
        .dt
        .to_period("M")
    )

    dist_activos = (
        tmp[dist_col]
        .value_counts()
    )

    dist_activos = (
        dist_activos[
            dist_activos >= MIN_ALARMAS_DIST
        ]
        .index
    )

    serie = (
        tmp[tmp[dist_col].isin(dist_activos)]
        .groupby([dist_col, "anio_mes"])
        .size()
        .reset_index(name="n_alarmas")
    )

    if serie.empty:
        return pd.DataFrame()

    todos_meses = pd.period_range(
        serie["anio_mes"].min(),
        serie["anio_mes"].max(),
        freq="M"
    )

    idx = pd.MultiIndex.from_product(
        [dist_activos, todos_meses],
        names=[dist_col, "anio_mes"]
    )

    serie = (
        serie
        .set_index([dist_col, "anio_mes"])
        .reindex(idx, fill_value=0)
        .reset_index()
    )

    proyecciones = []

    for dist in dist_activos:

        sub = (
            serie[
                serie[dist_col] == dist
            ]
            .sort_values("anio_mes")
        )

        vals = sub["n_alarmas"].values

        if len(vals) < 3:
            continue

        try:

            modelo = SimpleExpSmoothing(
                vals,
                initialization_method="estimated"
            ).fit(optimized=True)

            proximo = modelo.forecast(1)[0]
            ultimo = vals[-1]

            proyecciones.append({
                "distribuidor": dist,
                "ultimo_mes": ultimo,
                "proyeccion_proximo": round(proximo, 1),
                "variacion_pct": round(
                    (proximo - ultimo)
                    / (ultimo + 1)
                    * 100,
                    1
                )
            })

        except Exception:
            pass

    return (
        pd.DataFrame(proyecciones)
        .sort_values(
            "proyeccion_proximo",
            ascending=False
        )
    )

# ============================================================
# BUILD
# ============================================================

def build_conversion_data(mant: pd.DataFrame, uda: pd.DataFrame, uda_crudo: pd.DataFrame = None) -> dict:
    """
    INS-02: Conversión de alarmas a servicio en red CNH.

    Calcula el funnel de conversión, ranking de distribuidores
    (top/bottom por tasa de conversión), sobrecarga proyectada,
    y estimación de monetización.

    Parámetros
    ----------
    mant : DataFrame de mantenimientos limpio.
    uda  : DataFrame de unidades (no usado directamente, reservado).

    Retorna
    -------
    dict con funnel, top3, bottom3, dist_dual, prom_conv,
    distribuidores_sc, alarmas_proy, umbral_cap, monetizacion.
    """
    funnel    = _calcular_funnel(mant,uda)
    prom_conv = round(mant["cumplimiento"].mean() * 100, 1)
    retencion_externa = _calcular_retencion_externa(uda_crudo if uda_crudo is not None else uda)
    dist_col  = _detectar_col_dist(mant)

    if dist_col is not None:
        dist_stats = _calcular_dist_stats(mant, dist_col)
        n = len(dist_stats)

        if n >= TOP_N_DIST:
            top3    = dist_stats.nlargest(TOP_N_DIST, "tasa_conv_pct").reset_index(drop=True)
            bottom3 = dist_stats.nsmallest(TOP_N_DIST, "tasa_conv_pct").reset_index(drop=True)
        elif n > 0:
            top3    = dist_stats.nlargest(n, "tasa_conv_pct").reset_index(drop=True)
            bottom3 = dist_stats.nsmallest(n, "tasa_conv_pct").reset_index(drop=True)
        else:
            top3    = pd.DataFrame(columns=["distribuidor", "tasa_conv_pct", "moda_retraso"])
            bottom3 = pd.DataFrame(columns=["distribuidor", "tasa_conv_pct", "moda_retraso"])

        dist_dual = (
            dist_stats[["distribuidor", "tasa_conv_pct", "moda_retraso"]]
            .sort_values("tasa_conv_pct", ascending=False)
            .reset_index(drop=True)
            .copy()
        )

        df_proj = _calcular_sobrecarga_proyectada(
            mant,
            dist_col
        )
        if not df_proj.empty:

            dist_sc = (
                df_proj["distribuidor"]
                .head(4)
                .tolist()
            )

            alarm_sc = (
                df_proj["proyeccion_proximo"]
                .round()
                .astype(int)
                .head(4)
                .tolist()
            )

            sobrecarga_pct = (
                df_proj["variacion_pct"]
                .head(4)
                .tolist()
            )

        else:

            dist_sc = FALLBACK_SC["distribuidores"][:4]
            alarm_sc = FALLBACK_SC["alarmas_proy"][:4]
            sobrecarga_pct = FALLBACK_SC["sobrecarga_pct"][:4]

        alarm_sc = (
            df_proj["proyeccion_proximo"]
            .round()
            .astype(int)
            .head(4)
            .tolist()
        )

        sobrecarga_pct = (
            df_proj["variacion_pct"]
            .head(4)
            .tolist()
        )
    else:
        top3      = pd.DataFrame(FALLBACK_TOP3)
        bottom3   = pd.DataFrame(FALLBACK_BOTTOM3)
        dist_dual = pd.DataFrame(FALLBACK_DIST_DUAL)
        dist_sc   = FALLBACK_SC["distribuidores"]
        alarm_sc  = FALLBACK_SC["alarmas_proy"]
        sobrecarga_pct = FALLBACK_SC["sobrecarga_pct"]

    if alarm_sc:
        arr = np.array(alarm_sc, dtype=float)
        umbral_cap = round(float(np.median(arr) + np.std(arr)), 1)
    else:
        umbral_cap = FALLBACK_UMBRAL

    return {
        "funnel": funnel,
        "top3": top3,
        "bottom3": bottom3,
        "dist_dual": dist_dual,
        "prom_conv": prom_conv,
        "retencion_externa": retencion_externa,

        "distribuidores_sc": dist_sc,
        "alarmas_proy": alarm_sc,
        "sobrecarga_pct": sobrecarga_pct,

        "umbral_cap": umbral_cap,
        "monetizacion": MONETIZACION_DEFAULT,
    }