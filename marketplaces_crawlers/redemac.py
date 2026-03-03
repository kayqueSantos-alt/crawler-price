import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Redemac(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020008": "112_014560"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco e Frete (buy-box API) ---
        try:
            headers = {
                "x-store-token": "ab68c950-50c2-48fe-9b3b-b8100caa5a75"
            }

            api_url = (
                f"https://api.lojavirtual.ninja/ecommerce/products/{product_id}"
                f"/buy-box?postalcode={cep.replace('-', '')}"
            )
            response_product = cls.get_json(api_url, headers=headers)

            valor_produto = response_product["data"][0]["value"]
            valor_frete = response_product["data"][0]["freight"]
            prazo_frete = response_product["data"][0]["freight"]
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Redemac] Erro ao extrair dados (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Redemac] Erro de rede ao acessar API (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
