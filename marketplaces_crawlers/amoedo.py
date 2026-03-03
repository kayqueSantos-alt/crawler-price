import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Amoedo(BaseCrawler):

    d_para_item = {
        "2020008": "1430943",
        "2020010": "2215846",
        "2020011": "2037646",
        "2020047": "2732749",
        "2020048": "2732756"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            for data in soup.find_all("script", {"type": "application/ld+json"}):
                if "highPrice" in data.text and "offers" in data.text:
                    data_price = json.loads(data.text)
                    prod_obj["valor_produto"] = float(data_price["offers"]["offers"][0]["price"])
        except (RequestException, json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.error(f"[Amoedo] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            item_id = cls.get_product_id(sku, cls.d_para_item)

            payload = {
                "items": [{"id": item_id, "quantity": 1, "seller": "1"}],
                "country": "BRA",
                "postalCode": cep
            }

            response = cls.post(
                "https://www.amoedo.com.br/api/checkout/pub/orderForms/simulation",
                data=json.dumps(payload)
            )
            data = response.json()

            for values in data["logisticsInfo"][0]["slas"]:
                if "Retira" not in values["id"]:
                    prod_obj["prazo_frete"] = str(values["shippingEstimate"])
                    prod_obj["valor_frete"] = float(f"{values['price']/100:.2f}")
                    break
        except (RequestException, KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"[Amoedo] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        prod_obj["link"] = url

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete"),
            link=url
        )
        return cls.validate_result(result)
