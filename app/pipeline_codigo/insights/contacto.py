import numpy as np
import pandas as pd

# ============================================================
# CONSTANTES — INS-03 Contacto óptimo
# ============================================================

ORDEN_ZONAS = [
    "Noroeste",
    "Centro Occidente",
    "Centro",
    "Sur-Sureste",
    "Noreste",
]

ORDEN_MESES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

COLS_MANT_INTERVALOS = [
    "mant_50",   "mant_300",  "mant_600",  "mant_900",
    "mant_1200", "mant_1500", "mant_1800", "mant_2100", "mant_2400",
]

VALOR_CUMPLIDO = "Cerrada"
TOP_N_MESES    = 2      # cuántos meses óptimos calcular por zona

INTERVALOS_COMPORTAMIENTO = [
    ("mant_50",   50,   "#2A9D8F", False),
    ("mant_300",  300,  "#E9C46A", False),
    ("mant_600",  600,  "#F4A261", True),
    ("mant_900",  900,  "#C1121F", False),
    ("mant_1200", 1200, "#7B1E1E", False),
]


# ============================================================
# HELPERS
# ============================================================

def _codificar(v) -> float:
    """0 = cumplió, 1 = incumplió, NaN = sin dato."""
    if pd.isna(v):
        return np.nan
    return 0.0 if v == VALOR_CUMPLIDO else 1.0


def _build_pivot(mant: pd.DataFrame) -> pd.DataFrame:
    hm = (
        mant[mant["zona"] != "Otras"]          # ← filtro igual al notebook
        .groupby(["zona", "mes"])["cumplimiento"]
        .mean()
        .mul(100)
        .round(1)                               # ← redondear antes de pivotar
        .reset_index()
    )
    return (
        hm.pivot(index="zona", columns="mes", values="cumplimiento")
        .reindex(index=ORDEN_ZONAS)
        .reindex(columns=ORDEN_MESES)
    )


def _build_estrategia(pivot: pd.DataFrame) -> tuple[dict, list]:
    mes_top    = {}
    estrategia = []

    for zona in pivot.index:
        serie = pivot.loc[zona].dropna()
        if len(serie) == 0:
            continue

        top = serie.sort_values(ascending=False).head(TOP_N_MESES)
        mejor_mes  = top.index[0]
        mejor_pct  = top.iloc[0]
        segundo_mes = top.index[1]  if len(top) > 1 else mejor_mes
        segundo_pct = top.iloc[1]   if len(top) > 1 else mejor_pct

        mes_top[zona] = (
            mejor_mes, round(mejor_pct, 1),
            segundo_mes, round(segundo_pct, 1),
        )
        estrategia.append({
            "zona":    zona,
            "mes_opt": mejor_mes,
            "pct_opt": mejor_pct,
            "mes_2do": segundo_mes,
            "pct_2do": segundo_pct,
        })

    return mes_top, estrategia


def _build_tasas(uda: pd.DataFrame) -> pd.DataFrame:

    filas = []

    for col, horas, color, es_quiebre in INTERVALOS_COMPORTAMIENTO:

        if col not in uda.columns:
            continue

        tmp = uda[col].map(_codificar)

        tasa_incumple = float(tmp.mean())
        tasa_cumple   = 1 - tasa_incumple

        filas.append({
            "intervalo": col,
            "horas": horas,
            "n": int(tmp.notna().sum()),
            "tasa_incumple": tasa_incumple,
            "tasa_cumple": tasa_cumple,
            "color": color,
            "es_quiebre": es_quiebre
        })

    return pd.DataFrame(filas)


# ============================================================
# BUILD
# ============================================================

MARCAS_HEATMAP = ['NEW HOLLAND AG', 'CASE IH']
def build_contacto_optimo_data(mant: pd.DataFrame, uda: pd.DataFrame) -> dict:
    """
    INS-03: Ventana de contacto óptimo por zona y mes.

    Construye el heatmap de cumplimiento (zona × mes),
    la estrategia de los 2 mejores meses por zona,
    y la tasa de incumplimiento por intervalo de mantenimiento.

    Parámetros
    ----------
    mant : DataFrame de mantenimientos limpio (necesita 'zona', 'mes', 'cumplimiento').
    uda  : DataFrame de unidades (para tasas por intervalo mant_*).

    Retorna
    -------
    dict con pivot, hm, mes_top, df_estrategia, df_tasa,
    orden_zonas, orden_meses.
    """
    if "marca" in mant.columns:
        mant = mant[mant["marca"].isin(MARCAS_HEATMAP)].copy()
    pivot              = _build_pivot(mant)
    mes_top, estrategia = _build_estrategia(pivot)
    tasas              = _build_tasas(uda)

    hm = (
        mant.groupby(["zona", "mes"])["cumplimiento"]
        .mean()
        .mul(100)
        .reset_index()
    )

    return {
        "pivot":        pivot,
        "hm":           hm,
        "mes_top":      mes_top,
        "df_estrategia": pd.DataFrame(estrategia),
        "df_tasa":      tasas,
        "orden_zonas":  ORDEN_ZONAS,
        "orden_meses":  ORDEN_MESES,
    }