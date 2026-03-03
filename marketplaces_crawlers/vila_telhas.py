import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class VilaTelhas(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produto = soup.find("script", {"type": "application/ld+json"}).string.replace(
                '<script type="application/ld+json">', ""
            ).replace("</script>", "")
            price = json.loads(produto)
            prod_obj["valor_produto"] = float(price["@graph"][1]["offers"][0]["price"])
        except (RequestException, json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError, ValueError) as e:
            logger.error(f"[VilaTelhas] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=None,
            prazo_frete=None
        )
        return cls.validate_result(result)
