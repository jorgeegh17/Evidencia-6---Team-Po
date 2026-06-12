import io
import pandas as pd

REQUIRED_FILES = {
    "mantenimientos": "Mantenimientos", "unidades": "Unidades",
    "horas_2025": "Horas", "population": "Population",
}

# ← DICCIONARIO EXACTO DEL NOTEBOOK (solo nombres con acento, igual que celda 10)
ZONA_SADER = {
    'Baja California':'Noroeste','Baja California Sur':'Noroeste','Sonora':'Noroeste',
    'Sinaloa':'Noroeste','Nayarit':'Noroeste',
    'Chihuahua':'Noreste','Coahuila':'Noreste','Durango':'Noreste',
    'Nuevo León':'Noreste','Tamaulipas':'Noreste','Zacatecas':'Noreste',
    'San Luis Potosí':'Noreste',
    'Jalisco':'Centro Occidente','Michoacán':'Centro Occidente',
    'Colima':'Centro Occidente','Aguascalientes':'Centro Occidente',
    'Guanajuato':'Centro Occidente','Querétaro':'Centro Occidente',
    'Ciudad de México':'Centro','Estado de México':'Centro',
    'Hidalgo':'Centro','Morelos':'Centro','Puebla':'Centro','Tlaxcala':'Centro',
    'Veracruz':'Sur-Sureste','Oaxaca':'Sur-Sureste','Chiapas':'Sur-Sureste',
    'Tabasco':'Sur-Sureste','Campeche':'Sur-Sureste','Yucatán':'Sur-Sureste',
    'Quintana Roo':'Sur-Sureste','Guerrero':'Sur-Sureste',
}

NOMBRES_MES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
               7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

MARCAS_AG = ['NEW HOLLAND AG', 'CASE IH']

def _read_excel_buffer(b): return pd.read_excel(io.BytesIO(b))

def load_data(buffers):
    mant  = _read_excel_buffer(buffers["Mantenimientos 2024-2025.xlsx"])
    uda   = _read_excel_buffer(buffers["Reporte_unidades_dia_anterior.xlsx"])
    horas = _read_excel_buffer(buffers["Horas 2024-2025.xlsx"])
    return mant, uda, horas

def prepare_data(mant, uda):
    mant = mant.copy()
    uda  = uda.copy()

    # ← FILTRO DE MARCA AG (igual que notebook celda 10) en AMBOS dataframes
    if "marca" in mant.columns:
        mant = mant[mant["marca"].isin(MARCAS_AG)].copy()
    if "marca" in uda.columns:
        uda = uda[uda["marca"].isin(MARCAS_AG)].copy()

    if "fecha" in mant.columns:
        mant["fecha"] = pd.to_datetime(mant["fecha"], errors="coerce")
    if "horometro" in mant.columns:
        mant["horometro"] = pd.to_numeric(mant["horometro"], errors="coerce")
    if "actual" in mant.columns:
        mant["actual"] = pd.to_numeric(mant["actual"], errors="coerce")

    mant["cumplimiento"] = mant["estatus"].isin(["Cerrada","PorVencer","EnProceso"]).astype(int)
    mant["abandono"] = 1 - mant["cumplimiento"]
    mant["mes_num"]  = mant["fecha"].dt.month
    mant["mes"]      = mant["mes_num"].map(NOMBRES_MES)

    # ← diff_hrs con VALOR ABSOLUTO (igual que notebook), no clip
    if "actual" in mant.columns and "horometro" in mant.columns:
        mant["diff_hrs"] = (mant["actual"] - mant["horometro"]).abs()

    if "estado" in uda.columns:
        uda["zona"] = uda["estado"].map(ZONA_SADER)

    zona_alias = uda[["alias","zona"]].dropna().drop_duplicates()
    mant = mant.merge(zona_alias, on="alias", how="left")

    return mant, uda
