import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Normatel(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}

        d_para_item = {
            "1020042": "274873"
        }

        try:
            soup = cls.get_soup(url)
            prod_data_obj = soup.find("script", {"type": "application/ld+json"}).text
            prod_obj["valor_produto"] = float(json.loads(prod_data_obj)["offers"]["price"])
        except (RequestException, AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            product_id = cls.get_product_id(sku, d_para_item)

            payload = {
                "operationName": "shippingQuotes",
                "variables": {
                    "cep": cep,
                    "productVariantId": int(product_id),
                    "quantity": 1
                },
                "query": """
                query shippingQuotes($cep: CEP, $productVariantId: Long, $quantity: Int) {
                shippingQuotes(cep: $cep, productVariantId: $productVariantId, quantity: $quantity) {
                    name
                    shippingQuoteId
                    deadline
                    type
                    value
                }
                }
                """
            }

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "tcs-access-token": "tcs_norma_b560a74eb4fe44dfab40ebe312306382",
                "content-type": "application/json",
            }

            response = cls.post("https://storefront-api.fbits.net/graphql", data=json.dumps(payload), headers=headers)
            data = json.loads(response.content)

            for i in data["data"]["shippingQuotes"]:
                if "Entrega" in i["name"]:
                    prod_obj["prazo_frete"] = str(i["deadline"])
                    prod_obj["valor_frete"] = float(i["value"])
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
