import re
import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class CasaMaisFacil(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        try:
            soup = cls.get_soup(url)
            scripts = soup.find_all("script")
            for script in scripts:
                if "var skuJson_0" in script.text:
                    match = re.search(r"var skuJson_0\s*=\s*(\{.*\});", script.text, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                        prod_obj["valor_produto"] = General.price_treatment(data["skus"][0]["fullSellingPrice"])
        except (RequestException, AttributeError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        d_para_items = {
            "2020004": "2306",
            "2020005": "2302",
            "2020010": "3536",
            "01020055": "3925",
            "01020042": "2030"
        }

        try:
            product_id = cls.get_product_id(sku, d_para_items)

            payload = {"items": [{"id": product_id, "quantity": 1, "seller": 1}], "postalCode": int(cep.replace("-", "")), "country": "BRA"}

            response_frete = cls.post("https://www.casamaisfacil.com.br/api/checkout/pub/orderForms/simulation", headers=headers, data=json.dumps(payload))
            data = json.loads(response_frete.content)
            for value in data["logisticsInfo"][0]["slas"]:
                if "Retira" not in value["id"]:
                    prod_obj["valor_frete"] = float(f"{value['price']/100:.2f}")
        except (RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
