"""Módulo para download e extração de dados da NASA Exoplanet Archive."""

import logging
import os
import time
from io import StringIO
from pathlib import Path
import pandas as pd
import requests

logger = logging.getLogger(__name__)

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

QUERY = """
select
    kepoi_name,
    koi_disposition,
    koi_period,
    koi_duration,
    koi_depth,
    koi_prad,
    koi_insol,
    koi_teq,
    koi_impact,
    koi_model_snr,
    koi_steff,
    koi_slogg,
    koi_srad,
    koi_kepmag
from cumulative
"""


def download_dataset(
    output_path: str | Path = "data/cumulative_koi.csv",
    max_retries: int = 3,
    timeout: int = 60,
    force_download: bool = False,
) -> pd.DataFrame:
    """Baixa o dataset de Kepler da NASA.

    Se o arquivo já existir localmente e `force_download=False`, carrega do disco.
    Em caso de falha de conexão (ex.: ambiente offline ou API instável), recorre ao arquivo local.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force_download:
        logger.info("Dataset já encontrado em %s. Carregando localmente.", output_path)
        return pd.read_csv(output_path)

    logger.info("Iniciando extração da NASA Exoplanet Archive (TAP)...")
    session = requests.Session()

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Tentativa %d de %d...", attempt, max_retries)
            response = session.get(
                NASA_TAP_URL,
                params={"query": QUERY, "format": "csv"},
                timeout=timeout,
            )
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.content.decode("utf-8")))
            df.to_csv(output_path, index=False)
            logger.info("Dataset salvo com sucesso em %s (shape: %s).", output_path, df.shape)
            return df

        except Exception as exc:
            logger.warning("Erro na tentativa %d: %s", attempt, exc)
            if attempt < max_retries:
                time.sleep(2)

    # Fallback caso falhe e o arquivo já exista
    if output_path.exists():
        logger.warning("Falha no download online. Utilizando arquivo local existente: %s", output_path)
        return pd.read_csv(output_path)

    raise ConnectionError(
        f"Não foi possível baixar os dados da NASA após {max_retries} tentativas e nenhum arquivo local existe em {output_path}."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_dataset()

