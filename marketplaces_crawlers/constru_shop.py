import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class ConstruShop(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            prod_obj["valor_produto"] = General.price_treatment(
                soup.find("span", {"class": "woocommerce-Price-amount amount"}).text
            )
        except (RequestException, AttributeError, TypeError, ValueError) as e:
            logger.error(f"[ConstruShop] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=None,
            prazo_frete=None
        )
        return cls.validate_result(result)
