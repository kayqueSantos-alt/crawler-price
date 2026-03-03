import json
import base64
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Casas_da_agua(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            ld_json = cls.find_ld_json_with_field(soup, "highPrice")
            if ld_json:
                prod_obj["valor_produto"] = ld_json["offers"]["highPrice"]
            else:
                prod_obj["valor_produto"] = None
        except (RequestException, KeyError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        d_para_items = {
            "2020004": "27599",
            "2020032": "37704",
            "2020008": "18843",
            "2020009": "18844",
            "2020011": "27599",
            "1020042": "44507"
        }

        try:
            product_id = cls.get_product_id(sku, d_para_items)

            payload = {"country": "BRA", "postalCode": cep, "items": [{"quantity": "1", "id": product_id, "seller": "1"}]}
            json_str = str(payload).replace("'", '"')
            criptografia = base64.b64encode(json_str.encode()).decode()
            freight_url = f"https://www.casasdaagua.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=a77077bb-c420-4491-9258-b73924939fb6&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22630684603f2f47c4ebb135d22f887c496f3a497e01e0bd85e1cd846c8b275bc9%22%2C%22sender%22%3A%22cdagua.custom-shipping%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{criptografia}%3D%22%7D"
            response = cls.get(freight_url)
            data = json.loads(response.content)

            if len(data["data"]["shipping"]["logisticsInfo"][0]["slas"]) > 0:
                if "Retirar" not in data["data"]["shipping"]["logisticsInfo"][0]["slas"]:
                    prod_obj["prazo_frete"] = str(data["data"]["shipping"]["logisticsInfo"][0]["slas"][0]["shippingEstimate"])
                    prod_obj["valor_frete"] = float(data["data"]["shipping"]["logisticsInfo"][0]["slas"][0]["price"])
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
