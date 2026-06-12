from openpyxl.chart import updown_bars
import numpy as np
import pandas as pd

# ============================================================
# CONSTANTES — INS-01 Retención 600h
# ============================================================

COL_MANT_300 = "mant_300"
COL_MANT_600 = "mant_600"
VALOR_CUMPLIDO = "Cerrada"


# ============================================================
# HELPERS
# ============================================================

def _codificar(v) -> float:
    """0 = cumplió (Cerrada), 1 = incumplió, NaN = sin dato."""
    if pd.isna(v):
        return np.nan
    return 0.0 if v == VALOR_CUMPLIDO else 1.0

def _calcular_retencion_externa(uda: pd.DataFrame):

    cols_intervalos = [
        'mant_50','mant_300','mant_600','mant_900',
        'mant_1200','mant_1500','mant_1800',
        'mant_2100','mant_2400'
    ]

    cols_disp = [c for c in cols_intervalos if c in uda.columns]

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
            "retorno_posterior": retorno
        })

    df = pd.DataFrame(registros)

    if df.empty:

        return {
            "tasas": {},
            "n": {},
            "control": 0,
            "or": None,
            "p": None,
            "ic": [None, None]
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
        .agg(["mean","size"])
        .reindex(orden)
    )

    tasas = (res["mean"] * 100).round(2).to_dict()

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
        "control": control
    }
# ============================================================
# BUILD
# ============================================================

def build_retencion_data(uda: pd.DataFrame, uda_crudo: pd.DataFrame = None) -> dict:
    """
    INS-01: Retención al umbral de 600 horas.

    Analiza si las unidades que llegaron a mant_600 habían
    cumplido o no su mantenimiento de mant_300 previo,
    y calcula las tasas cruzadas de cumplimiento en 600h.

    Parámetros
    ----------
    uda : DataFrame con columnas mant_300 y mant_600.

    Retorna
    -------
    dict con:
        n_cumplio, n_incumplio, total_600,
        pct_cumplio, pct_incumplio,
        tasa_cumplio_en_600, tasa_incumplio_en_600
    """
    
    uda = (uda_crudo if uda_crudo is not None else uda).copy()
    cols_mant = [
        'mant_50', 'mant_300', 'mant_600', 'mant_900',
        'mant_1200', 'mant_1500', 'mant_1800',
        'mant_2100', 'mant_2400'
    ]
    

    bin_cols = []

    for c in cols_mant:
        col_bin = f"{c}_bin"
        uda[col_bin] = uda[c].map(_codificar)
        bin_cols.append(col_bin)

    uda["mant_300_bin"] = uda[COL_MANT_300].map(_codificar)
    uda["mant_600_bin"] = uda[COL_MANT_600].map(_codificar)

    

    # ── Filtrar unidades que llegaron al intervalo 600
    llegaron_600 = uda[uda['mant_600_bin'].notna()].copy()

    # ── Grupos según cumplimiento en mant_300
    cumplio_300   = llegaron_600[llegaron_600['mant_300_bin'] == 0]
    incumplio_300 = llegaron_600[llegaron_600['mant_300_bin'] == 1]

    # ── Conteos gráfica 1
    n_cumplio   = len(cumplio_300)
    n_incumplio = len(incumplio_300)
    total       = n_cumplio + n_incumplio
    pct_cumplio   = n_cumplio   / total
    pct_incumplio = n_incumplio / total

    # ── Tasas de cumplimiento en mant_600 por grupo (gráfica 2)
    # (mant_600_bin == 0 significa que cumplió ese servicio)
    tasa_cumplio_en_600   = (cumplio_300['mant_600_bin']   == 0).mean()
    tasa_incumplio_en_600 = (incumplio_300['mant_600_bin'] == 0).mean()





    tasa_incumplimiento = []
    for col_bin, nombre in zip(bin_cols, cols_mant):

        n = uda[col_bin].notna().sum()

        tasa_incumple = uda[col_bin].mean()

        tasa_cumple = 1 - tasa_incumple

        n_incumplieron = int((uda[col_bin] == 1).sum())

        n_cumplieron = int((uda[col_bin] == 0).sum())

        tasa_incumplimiento.append({
            "intervalo": nombre,
            "n": n,
            "tasa_incumple": tasa_incumple,
            "tasa_cumple": tasa_cumple,
            "n_incumplieron": n_incumplieron,
            "n_cumplieron": n_cumplieron
        })

    df_tasa = pd.DataFrame(tasa_incumplimiento)

    pares = []

    for i in range(len(bin_cols) - 1):

        col_i   = bin_cols[i]
        col_ip1 = bin_cols[i + 1]

        sub = uda[[col_i, col_ip1]].dropna()

        incumplieron = sub[sub[col_i] == 1]

        tasa_retorno = (
            (incumplieron[col_ip1] == 0).mean()
            if len(incumplieron) > 0
            else np.nan
        )

        pares.append({
            "intervalo": cols_mant[i],
            "n_incumplieron": len(incumplieron),
            "tasa_retorno": tasa_retorno
        })

    df_pares = pd.DataFrame(pares)
    # Tasa de CUMPLIMIENTO (inverso de incumplimiento)
    tasa_cumple = 1 - df_tasa['tasa_incumple']
    tasa_abandona = df_tasa['tasa_incumple']
    
    # Etiquetas combinadas: "X% / Y% abandona"
    textos = [
        f"{c:.2%} / {a:.0%} abandona"
        for c, a in zip(tasa_cumple, tasa_abandona)
    ]
    retencion_externa = _calcular_retencion_externa(uda_crudo if uda_crudo is not None else uda)

    return {
        "n_cumplio": n_cumplio,
        "n_incumplio": n_incumplio,
        "pct_cumplio": pct_cumplio,
        "pct_incumplio": pct_incumplio,
        "tasa_cumplio_en_600": tasa_cumplio_en_600,
        "tasa_incumplio_en_600": tasa_incumplio_en_600,
        # 
        "df_tasa": df_tasa,
        "df_pares": df_pares,
        "tasa_cumple": tasa_cumple.tolist(),
        "tasa_abandona": tasa_abandona.tolist(),
        "textos": textos,
        "retencion_externa": retencion_externa,
    }