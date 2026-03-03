import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.efizitools import Efizi

logger = logging.getLogger("crawlers")


class FerreiraCosta(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku, uf):

        prod_obj = {}

        try:
            data_json = Efizi.d_para()
            region = data_json["ECOMMERCE"]["FERREIRA_COSTA"]["PRICE_REGION"][uf]
            item_id = data_json["ECOMMERCE"]["FERREIRA_COSTA"]["ITEM_ID"][sku]

            response_price = cls.get_json(f"https://fcxlabs-ecommerce-api.ferreiracosta.com/catalog/v1/products/id/{item_id}?branchId={region}")
            prod_obj["valor_produto"] = float(response_price["prices"][0]["salePrice"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            data_json = Efizi.d_para()
            item_id = data_json["ECOMMERCE"]["FERREIRA_COSTA"]["ITEM_ID"][sku]

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
            }

            response_freight = cls.get(f"https://fcxlabs-ecommerce-api.ferreiracosta.com/shipping/v1/options?ProductId={item_id}&Quantity=1&Package=0&ZipCode={cep}&BranchId=8", headers=headers)

            if len(response_freight.content) > 0:
                data = json.loads(response_freight.content)
                if "errors" not in data:
                    prod_obj["prazo_frete"] = str(data[0]["arrivesTextShort"])
                    prod_obj["valor_frete"] = float(data[0]["value"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
