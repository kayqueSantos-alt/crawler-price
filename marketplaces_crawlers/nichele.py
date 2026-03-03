import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.crawler_settings import Crawler

logger = logging.getLogger("crawlers")


class Nichele(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        url_freight = "https://www.nichele.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=67f3ec13-dee4-4882-9403-2242d792510c&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%227ce5ad49f177bdecfef578def58ba597a57ae64295229da99c804bfe933d4b42%22%2C%22sender%22%3A%22vtex.store-components%403.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%3D%22%7D"

        prod_obj = {}

        d_para_produtos = {
            "1020055": "1003303",
            "2020009": "1003299"
        }

        try:
            data_price = Crawler.request_pattern_price(url)
            prod_obj["valor_produto"] = data_price["offers"]["offers"][0]["price"]
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            product_id = cls.get_product_id(sku, d_para_produtos)
            data_freight = Crawler.requests_pattern_freight(cep, product_id, url_freight, "Nichele Entrega")
            prod_obj["valor_frete"] = float(data_freight["price"] / 100)
            prod_obj["prazo_frete"] = str(data_freight["shippingEstimate"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar frete: {e}")
            prod_obj["valor_frete"] = None
            prod_obj["prazo_frete"] = None

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
