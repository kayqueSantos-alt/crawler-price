import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Veneza(BaseCrawler):

    USE_CLOUDSCRAPER = True

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None

        # --- Preco (usa cloudscraper via cls.get_soup) ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup, index=0)

            if ld_json is not None:
                valor_produto = float(ld_json["offers"]["price"])
        except RequestException as e:
            logger.error(f"[Veneza] Erro de rede ao acessar {url}: {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"[Veneza] Erro ao extrair preco de {url}: {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
        )
        return cls.validate_result(result)
