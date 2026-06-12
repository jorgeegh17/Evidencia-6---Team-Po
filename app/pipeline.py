import logging
import sys
import traceback

from pipeline_codigo.carga_datos.procesamiento_datos import load_data, prepare_data
from pipeline_codigo.insights.contacto import build_contacto_optimo_data
from pipeline_codigo.insights.conversion import build_conversion_data
from pipeline_codigo.insights.retencion import build_retencion_data
from pipeline_codigo.carga_datos.procesamiento_datos import REQUIRED_FILES

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CNH_PIPELINE")

SEP = "=" * 80


# ============================================================
# ORQUESTADOR PRINCIPAL
# ============================================================

def load_processed_data_from_buffers(buffers: dict) -> dict:
    """
    Punto de entrada del dashboard.

    Ejecuta el pipeline completo en orden:
        1. Carga de Excel desde buffers en memoria.
        2. Limpieza y enriquecimiento.
        3. Cálculo de los tres insights.

    Parámetros
    ----------
    buffers : dict  {nombre_archivo: bytes}
        Proveniente del componente dcc.Upload del dashboard.

    Retorna
    -------
    dict con claves:
        "contacto_data", "conversion_data", "retencion_data"

    Lanza
    -----
    Cualquier excepción interna; el error queda registrado en
    pipeline.log antes de propagarse.
    """
    try:
        logger.info(SEP)
        logger.info("PIPELINE START")
        logger.info(SEP)

        # — Carga —
        logger.info("Cargando archivos Excel...")
        mant, uda, horas = load_data(buffers)
        logger.info(
            "Carga OK | mant=%d filas | uda=%d filas | horas=%d filas",
            len(mant), len(uda), len(horas),
        )

        # — Limpieza —
        logger.info("Preparando datos...")
        uda_crudo = uda.copy()
        mant, uda = prepare_data(mant, uda)
        logger.info("Limpieza OK")

        # — Insights —
        logger.info("Calculando INS-03 (contacto óptimo)...")
        contacto_data = build_contacto_optimo_data(mant, uda)

        logger.info("Calculando INS-02 (conversión)...")
        conversion_data = build_conversion_data(mant, uda, uda_crudo)

        logger.info("Calculando INS-01 (retención 600h)...")
        retencion_data = build_retencion_data(uda, uda_crudo)

        logger.info(SEP)
        logger.info("PIPELINE FINALIZADO OK")
        logger.info(SEP)

        return {
            "contacto_data":      contacto_data,
            "conversion_data":    conversion_data,
            "retencion_data": retencion_data,
        }

    except Exception as e:
        logger.error(SEP)
        logger.error("PIPELINE ERROR: %s", str(e))
        logger.error(traceback.format_exc())
        logger.error(SEP)
        raise