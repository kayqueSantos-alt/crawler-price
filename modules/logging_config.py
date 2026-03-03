import logging
import sys
from datetime import datetime


def setup_logging(level=logging.INFO):
    """
    Configura logging para o projeto de scraping.
    - Console: mostra INFO+
    - Arquivo: grava WARNING+ em logs/crawlers_YYYY-MM-DD.log
    """
    logger = logging.getLogger("crawlers")

    # Evita duplicar handlers se chamado mais de uma vez
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler
    try:
        log_filename = f"logs/crawlers_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except FileNotFoundError:
        logger.warning("Pasta 'logs/' nao encontrada. Logging apenas no console.")

    return logger
