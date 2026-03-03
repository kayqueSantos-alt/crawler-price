import json
import re
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Engecopi(BaseCrawler):

    @classmethod
    def _extract_sku_json(cls, soup):
        """
        Extrai dados do produto buscando pelo padrao 'var skuJson_0'
        em vez de usar indice fixo.
        """
        for script in soup.find_all("script"):
            text = script.string or script.text or ""
            if "var skuJson_0" in text:
                cleaned = text.replace("var skuJson_0 = ", "")
                cleaned = re.split(r';\s*CATALOG_SDK', cleaned)[0]
                cleaned = cleaned.strip().rstrip(";")
                return json.loads(cleaned)

        logger.warning("[Engecopi] Padrao 'var skuJson_0' nao encontrado no HTML")
        return None

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            sku_data = cls._extract_sku_json(soup)

            if sku_data:
                valor = sku_data["skus"][0]["fullSellingPrice"]
                valor_produto = None if len(str(valor)) >= 13 else valor
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[Engecopi] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Engecopi] Erro de rede ao acessar {url}: {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
        )
        return cls.validate_result(result)
