import json
import logging
from modules.base_crawler import BaseCrawler
from modules.efizitools import Efizi
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Obramax(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku, datadome):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        data_id = Efizi.d_para()
        product_id = data_id["ECOMMERCE"]["OBRAMAX"][sku]

        url_trat = url.replace("https://www.obramax.com.br/", "").replace("/p", "")
        api_obramax = "https://www.obramax.com.br/_v/public/graphql/v1"
        cookie = {"datadome": datadome}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Origin": "www.obramax.com.br",
            "referer": url,
            "x-requested-with": "XMLHttpRequest"
        }

        # --- Region ID ---
        try:
            region_response = cls.get_json(
                f"https://www.obramax.com.br/api/checkout/pub/regions?country=BRA&postalCode={cep}&sc=1"
            )
            region_id = region_response[0]["id"]
        except RequestException as e:
            logger.error(f"[Obramax] Erro de rede ao buscar regiao para CEP {cep}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete)
            return cls.validate_result(result)
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Obramax] Erro ao extrair region_id para CEP {cep}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete)
            return cls.validate_result(result)

        # --- Preco (GraphQL) ---
        payload_price = {
            "query": "query getPriceProductByRegionId($slug:String, $regionId:String) {\r\n  product(\r\n    slug:$slug,\r\n  \tregionId: $regionId\r\n  )@context(provider: \"vtex.search-graphql\"){\r\n   productName\r\n    priceRange{\r\n      sellingPrice{\r\n        highPrice\r\n        lowPrice\r\n      }\r\n    }\r\n  }\r\n  }",
            "variables": {
                "regionId": region_id,
                "slug": url_trat
            }
        }

        try:
            response = cls.post(api_obramax, data=json.dumps(payload_price), headers=headers, cookies=cookie)
            value_product = json.loads(response.content)
            valor_produto = float(value_product["data"]["product"]["priceRange"]["sellingPrice"]["lowPrice"])
        except RequestException as e:
            logger.error(f"[Obramax] Erro de rede ao buscar preco: {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Obramax] Erro ao extrair preco: {e}")

        # --- Frete (GraphQL) ---
        payload_frete = {
            "query": """
                query simulateShipping(
                $country: String!,
                $postalCode: String!,
                $items: [ShippingItem!]!
                ) {
                shipping(
                    country: $country,
                    postalCode: $postalCode,
                    items: $items
                ) @context(provider: "vtex.store-graphql") {
                    logisticsInfo {
                    slas {
                        id
                        name
                        deliveryChannel
                        price
                        shippingEstimate
                        friendlyName
                    }
                    }
                }
                }
            """,
            "variables": {
                "country": "BRA",
                "postalCode": cep.replace("-", ""),
                "items": [
                    {
                        "id": product_id,
                        "seller": "1",
                        "quantity": 1
                    }
                ]
            }
        }

        try:
            response_frete = cls.post(api_obramax, headers=headers, data=json.dumps(payload_frete), cookies=cookie)
            data = json.loads(response_frete.content)

            for sla in data["data"]["shipping"]["logisticsInfo"][0]["slas"]:
                if "Retira" not in sla["friendlyName"]:
                    prazo_frete = str(sla["shippingEstimate"])
                    valor_frete = round(sla["price"] / 100, 2)
        except RequestException as e:
            logger.error(f"[Obramax] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Obramax] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
