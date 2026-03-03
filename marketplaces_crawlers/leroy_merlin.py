import re
import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Leroy(BaseCrawler):

    USE_CLOUDSCRAPER = True

    @classmethod
    def crawler(cls, url, cep, sku, loja):
        valor_produto = None
        valor_frete = None
        prazo_frete = None
        disponibilidade = None

        sku_mktplace = url[-10:]
        sku_mktplace = re.sub(r'[^0-9]', '', sku_mktplace)

        # --- Regiao (usa cloudscraper via cls.get) ---
        try:
            region_obj = cls.get_json(
                f'https://www.leroymerlin.com.br/api/boitata/v1/zipcode/{cep}'
            )
        except RequestException as e:
            logger.error(f"[Leroy] Erro de rede ao buscar regiao para CEP {cep}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete, disponibilidade=disponibilidade, loja=loja)
            return cls.validate_result(result)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "x-region": region_obj["region"]
        }

        # ---- PEGAR PRECO ----
        url_price = f"https://www.leroymerlin.com.br/api/v3/products/{sku_mktplace}/sellers"
        try:
            response_price = cls.get_json(url_price, headers=headers)

            for item in response_price["data"]:
                id_seller = item.get("id")

                if id_seller == "" and loja == "LEROY MERLIN":
                    valor_produto = item["pricing"]["price"]["from"] or item["pricing"]["price"]["regionPrice"]

                elif id_seller != "" and loja == "EFIZI LEROY MERLIN":
                    valor_produto = item["pricing"]["price"]["to"] or item["pricing"]["installment"]["totalValue"]

        except RequestException as e:
            logger.error(f"[Leroy] Erro de rede ao buscar preco de {url_price}: {e}")
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Leroy] Erro ao extrair preco de {url_price}: {e}")

        # ---- PEGAR FRETE ----
        url_freight = f"https://www.leroymerlin.com.br/api/v3/products/{sku_mktplace}/shipments?zipCode={cep}&newFormat=1"
        try:
            response_freight = cls.get_json(url_freight, headers=headers)

            if not response_freight.get("data", []):
                disponibilidade = "CEP INDISPONIVEL"
            else:
                for item in response_freight["data"]:
                    costs = [frieght["cost"] for frieght in item["modalities"] if "cost" in frieght]
                    deadlines = [frieght["deadline"] for frieght in item["modalities"] if "cost" in frieght]

                    if loja == "LEROY MERLIN" and item["skuId"] is None:
                        valor_frete = costs[0] if costs else None
                        prazo_frete = deadlines[0] if deadlines else None

                    elif loja == "EFIZI LEROY MERLIN" and item["skuId"] is not None:
                        valor_frete = costs[0] if costs else None
                        prazo_frete = deadlines[0] if deadlines else None

        except RequestException as e:
            logger.error(f"[Leroy] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Leroy] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
            disponibilidade=disponibilidade,
            loja=loja,
        )
        return cls.validate_result(result)
