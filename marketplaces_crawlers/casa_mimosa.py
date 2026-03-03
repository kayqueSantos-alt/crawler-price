import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.crawler_settings import Crawler

logger = logging.getLogger("crawlers")


class CasaMimosa(BaseCrawler):

    d_para_item = {
        "2020032": "4748",
        "2020049": "2812",
        "2020047": "17644",
        "2020009": "8394",
        "1020080": "17430",
        "2020008": "8402",
        "2020004": "2385",
        "2020054": "8397",
        "1020081": "17429",
        "2020005": "2371",
        "1020042": "1887",
        "2020010": "8396",
        "2020017": "8437",
        "2020048": "2816",
        "1020055": "8",
        "02020011": "210108"
    }

    url_freight = "https://www.casamimosa.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=806a4164-3c9e-4680-aa5d-f0159f680875&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%227ce5ad49f177bdecfef578def58ba597a57ae64295229da99c804bfe933d4b42%22%2C%22sender%22%3A%22vtex.store-components%403.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%3D%22%7D"

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            data_price = Crawler.request_pattern_price(url)
            prod_obj["valor_produto"] = float(data_price["offers"]["highPrice"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[CasaMimosa] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            item_id = cls.get_product_id(sku, cls.d_para_item)
            data_freight = Crawler.requests_pattern_freight(
                cep, item_id, cls.url_freight, "Transportadora Própria"
            )
            prod_obj["valor_frete"] = float(data_freight["price"] / 100)
            prod_obj["prazo_frete"] = str(data_freight["shippingEstimate"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[CasaMimosa] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
