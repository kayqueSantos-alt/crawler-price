import re
import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Constrular_facil(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
            "x-requested-with": "XMLHttpRequest"
        }

        try:
            soup = cls.get_soup(url, headers=headers)

            raw_json = soup.find("script", {"type": "application/ld+json"}).string.replace('style="', "style='")
            raw_json = re.sub(r"[\n\r\t]", "", raw_json).strip()
            data = json.loads(raw_json)

            if len(data["@graph"]) > 0:
                price = data["@graph"][0]["offers"]["price"]
                prod_obj["valor_produto"] = float(price)
        except (RequestException, AttributeError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        d_para_item = {
            "2020009": "95",
            "2020010": "62935167",
            "2020011": "409",
            "2020004": ""
        }

        try:
            product_id = cls.get_product_id(sku, d_para_item)

            payload = {
                "postcode": cep.replace("-", ""),
                "product_id": product_id,
                "quantidade": "1",
                "ibge": "5219308"
            }

            response = cls.post("https://constrularfacil.com.br/index.php?route=extension/total/shipping/quote", headers=headers, data=payload)

            if len(response.content) > 0:
                data = json.loads(response.content)
                for value in data["shipping_method"]:
                    if "Retira" not in value["quote"][0]["title"]:
                        prod_obj["valor_frete"] = float(value["quote"][0]["cost"])
                        prod_obj["prazo_frete"] = str(value["quote"][0]["days"])
                        break
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
