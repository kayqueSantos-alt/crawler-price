import json
import base64
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Pisolar(BaseCrawler):

    D_PARA_ITEM = {
        "2020004": "3916",
        "2020008": "3922",
        "2020005": "9845",
        "2020009": ""
    }

    FREIGHT_URL_TEMPLATE = (
        "https://www.pisolar.com.br/_v/segment/graphql/v1"
        "?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR"
        "&__bindingId=70da700a-96d9-4b3d-92cf-e58620e7f06d"
        "&operationName=getShippingEstimates&variables=%7B%7D"
        "&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1"
        "%2C%22sha256Hash%22%3A%221cec8e9be6c8427c387bb1e127dc5ab8e7a07bd83d8b1a10edecf0a1cd241013%22"
        "%2C%22sender%22%3A%22vtex.store-components%403.x%22"
        "%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D"
        "%2C%22variables%22%3A%22{criptografia}%3D%3D%22%7D"
    )

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEM)

        # --- Preco (ld+json) ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup)
            if ld_json:
                valor_produto = ld_json["offers"]["offers"][0]["price"]
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"[Pisolar] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Pisolar] Erro de rede ao acessar {url}: {e}")

        # --- Frete (VTEX graphql com base64) ---
        try:
            payload = json.dumps({
                "country": "BRA",
                "postalCode": cep.replace("-", ""),
                "items": [{"quantity": "1", "id": product_id, "seller": "1"}]
            })
            criptografia = base64.b64encode(payload.encode()).decode()
            freight_url = cls.FREIGHT_URL_TEMPLATE.replace("{criptografia}", criptografia)

            data = cls.get_json(freight_url)

            if "errors" not in data:
                if len(data["data"]["shipping"]["logisticsInfo"][0]["slas"]) > 0:
                    for i in data["data"]["shipping"]["logisticsInfo"][0]["slas"]:
                        if "Retirar na loja" not in i["id"]:
                            prazo_frete = str(i["shippingEstimate"])
                            valor_frete = float(f"{i['price']/100.0:.2f}")
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"[Pisolar] Erro ao extrair frete (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Pisolar] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
