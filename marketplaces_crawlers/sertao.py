import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Sertao(BaseCrawler):

    D_PARA_ITEM = {
        "2020033": "18902",
        "1020055": "27054",
        "2020010": "18495",
        "2020004": "11257",
        "2020008": "11059",
        "2020009": "11060",
        "2020005": "8480",
        "2020011": "18496",
        "2020048": "9679"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEM)

        # --- Preco (template data-type json) ---
        try:
            soup = cls.get_soup(url)
            dados_produto_json = soup.find_all("template", {"data-type": "json"})[-1].find("script").text
            dados_produto_json = json.loads(dados_produto_json)

            key_to_catch = (
                "$Product:"
                + url.replace("https://www.sertao.com.br/", "").replace("/p", "")
                + ".items.0.sellers.0.commertialOffer"
            )
            valor_produto = dados_produto_json.get(key_to_catch)["Price"]
        except (KeyError, IndexError, TypeError, ValueError, AttributeError, json.JSONDecodeError) as e:
            logger.warning(f"[Sertao] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Sertao] Erro de rede ao acessar {url}: {e}")

        # --- Frete (VTEX simulation) ---
        try:
            payload = {
                "items": [
                    {
                        "id": product_id,
                        "quantity": 1,
                        "seller": "1"
                    }
                ],
                "country": "BRA",
                "postalCode": "79680-000"
            }

            data = cls.post_json(
                "https://www.sertao.com.br/api/checkout/pub/orderForms/simulation?RnbBehavior=0&sc=1",
                data=json.dumps(payload),
            )

            for i in data["logisticsInfo"][0]["slas"]:
                if "Retirar na loja" not in i["id"]:
                    prazo_frete = str(i["shippingEstimate"])
                    valor_frete = float(f"{i['price']/100.0:.2f}")
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"[Sertao] Erro ao extrair frete (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Sertao] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
