import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Copafer(BaseCrawler):

    d_para_items = {
        "2020010": "20077",
        "2020009": "19969",
        "2020008": "19964",
        "2020017": "780",
        "2020054": ""
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produto = soup.find("script", {"type": "application/ld+json"}).string
            price = json.loads(produto)
            prod_obj["valor_produto"] = float(price["offers"]["offers"][0]["price"])
        except (RequestException, json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError) as e:
            logger.error(f"[Copafer] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        if prod_obj["valor_produto"] is None:
            return cls.validate_result(
                cls.build_result(valor_produto=None, valor_frete=None, prazo_frete=None)
            )

        try:
            item_id = cls.get_product_id(sku, cls.d_para_items)

            payload = {
                "items": [{"id": item_id, "quantity": 1, "seller": "1"}],
                "country": "BRA",
                "postalCode": cep
            }

            response = cls.post(
                "https://www.copafer.com.br/api/checkout/pub/orderForms/simulation?RnbBehavior=1",
                data=json.dumps(payload)
            )
            data = response.json()

            if "error" not in data:
                for values in data["logisticsInfo"][0]["slas"]:
                    if "Retirada em CD" not in values["id"]:
                        prod_obj["prazo_frete"] = str(values["shippingEstimate"])
                        prod_obj["valor_frete"] = float(f"{values['price']/100:.2f}")
                        break
        except (RequestException, KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"[Copafer] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
