import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.crawler_settings import Crawler
from modules.efizitools import Efizi

logger = logging.getLogger("crawlers")


class Chatuba(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            data = Efizi.d_para()
            item_id = data["ECOMMERCE"]["CHATUBA"][sku]
        except (KeyError, TypeError) as e:
            logger.error(f"[Chatuba] Erro ao buscar item_id no d_para: {e}")
            return cls.validate_result(
                cls.build_result(valor_produto=None, valor_frete=None, prazo_frete=None)
            )

        try:
            data_price = Crawler.request_pattern_price(url)
            prod_obj["valor_produto"] = data_price["offers"]["offers"][0]["price"]
        except (RequestException, KeyError, IndexError, TypeError) as e:
            logger.error(f"[Chatuba] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        url_freight = "https://www.chatuba.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ea653273-ac5e-448e-9cde-0a75024c9ab9&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%220530e1390216727ca495b0a14f6e19b6fefde6c02d6bd7691bd9a25593c223da%22%2C%22sender%22%3A%22chatuba.apps-custom%401.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%22%7D"

        try:
            data_frete = Crawler.requests_pattern_freight(cep, item_id, url_freight, "Econômica")
            prod_obj["valor_frete"] = float(data_frete["price"] / 100)
            prod_obj["prazo_frete"] = str(data_frete["shippingEstimate"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[Chatuba] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
