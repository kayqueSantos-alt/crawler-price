import json
import base64
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Panorama(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020011": "18351",
        "2020004": "18921",
        "2020009": "10339",
        "2020005": "18918",
        "2020010": "18167",
        "2020008": "10338"
    }

    FREIGHT_URL_TEMPLATE = (
        "https://www.panorama.com.br/_v/segment/graphql/v1"
        "?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR"
        "&__bindingId=1d910526-a920-4916-bf0f-b86e26ceb932"
        "&operationName=getShippingEstimates&variables=%7B%7D"
        "&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1"
        "%2C%22sha256Hash%22%3A%227ce5ad49f177bdecfef578def58ba597a57ae64295229da99c804bfe933d4b42%22"
        "%2C%22sender%22%3A%22vtex.store-components%403.x%22"
        "%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D"
        "%2C%22variables%22%3A%22{base64}%3D%22%7D"
    )

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup)
            if ld_json:
                valor_produto = float(ld_json["offers"]["offers"][0]["price"])
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Panorama] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Panorama] Erro de rede ao acessar {url}: {e}")

        # --- Frete (VTEX graphql com base64) ---
        try:
            payload = json.dumps({
                "country": "BRA",
                "postalCode": cep,
                "items": [{"quantity": "1", "id": product_id, "seller": "1"}]
            })
            criptografia = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
            freight_url = cls.FREIGHT_URL_TEMPLATE.replace("{base64}", criptografia)

            data = cls.get_json(freight_url)

            for frete in data["data"]["shipping"]["logisticsInfo"][0]["slas"]:
                if "Frota Própria" in frete["id"]:
                    valor_frete = float(frete["price"] / 100)
                    prazo_frete = frete["shippingEstimate"]
                    break
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Panorama] Erro ao extrair frete (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Panorama] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
