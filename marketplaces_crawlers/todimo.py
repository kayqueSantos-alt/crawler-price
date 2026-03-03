import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Todimo(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020004": "11609",
        "2020008": "5449",
        "2020010": "25129",
        "2020011": "25327"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco e Frete (VTEX simulation API) ---
        try:
            headers = {
                "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
            }

            payload = {
                "items": [
                    {
                        "id": product_id,
                        "quantity": 1,
                        "seller": "1"
                    }
                ],
                "country": "BRA",
                "postalCode": cep
            }

            response = cls.post_json(
                "https://www.todimo.com.br/api/checkout/pub/orderForms/simulation",
                headers=headers,
                json=payload,
            )

            # Preco vem em centavos (ex: 12990 = R$ 129,90)
            if response["items"][0]["price"] is not None:
                price_raw = response["items"][0]["price"]
                valor_produto = float(str(price_raw)[:-2] + "." + str(price_raw)[-2:])

            # Frete
            if len(response["logisticsInfo"][0]["slas"]) > 0:
                freight_raw = response["logisticsInfo"][0]["slas"][1]["price"]
                valor_frete = float(str(freight_raw)[:-2] + "." + str(freight_raw)[-2:])
                prazo_frete = response["logisticsInfo"][0]["slas"][1]["transitTime"]
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Todimo] Erro ao extrair dados (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Todimo] Erro de rede (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
