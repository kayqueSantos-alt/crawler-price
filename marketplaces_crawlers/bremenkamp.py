import json
import re
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Bremenkamp(BaseCrawler):

    d_para_items = {
        "2020004": "228195800",
        "2020005": "228188613",
        "2020008": "215180438",
        "2020009": "228876368",
        "2020010": "228876370",
        "2020011": "228876371",
        "2020047": "228743254",
        "1020080": "316106918",
        "1020055": "228176480",
        "1020042": "228170952"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            response = cls.get(url)
            match = re.search(r'full_price:\s*([\d\.]+)', response.text)
            if match:
                prod_obj["valor_produto"] = float(match.group(1))
            else:
                prod_obj["valor_produto"] = None
        except (RequestException, ValueError) as e:
            logger.error(f"[Bremenkamp] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            item_id = cls.get_product_id(sku, cls.d_para_items)

            response_freight = cls.get(
                f"https://www.bremenkampconstrucao.com.br/carrinho/frete?cep={cep}&produto_id={item_id}&quantidade=1"
            )
            data = json.loads(response_freight.content)

            for value in data:
                if "Retirar pessoalmente" not in value["name"]:
                    prod_obj["prazo_frete"] = str(value["deliveryTime"])
                    prod_obj["valor_frete"] = float(value["price"])
                    break
        except (RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[Bremenkamp] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
