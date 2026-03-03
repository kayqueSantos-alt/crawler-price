import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Carajas(BaseCrawler):

    D_PARA_ITEM = {
        "2020004": "3540",
        "2020009": "4033",
        "2020008": "4048",
        "2020005": "3510",
        "2020048": "",
    }

    @classmethod
    def _extract_state_price(cls, soup):
        """
        Extrai preco do template __STATE__ da VTEX.
        Busca pelo campo highPrice nos dados parseados.
        """
        template = soup.find("template", {"data-varname": "__STATE__"})
        if not template:
            logger.warning("[Carajas] Template __STATE__ nao encontrado")
            return None

        raw = str(template)
        raw = raw.replace("<script>", "").replace(
            '<template data-type="json" data-varname="__STATE__">', ""
        ).replace("</script>", "").replace("</template>", "")

        price_data = json.loads(raw)
        for _, value in price_data.items():
            if "highPrice" in value:
                return None if value["highPrice"] == 0 else value["highPrice"]

        return None

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEM)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        # --- Preco ---
        try:
            soup = cls.get_soup(url, headers=headers)
            valor_produto = cls._extract_state_price(soup)
        except RequestException as e:
            logger.error(f"[Carajas] Erro de rede ao acessar {url}: {e}")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning(f"[Carajas] Erro ao extrair preco de {url}: {e}")

        # --- Frete (VTEX simulation) ---
        payload = {
            "items": [
                {
                    "id": product_id,
                    "quantity": 1,
                    "seller": "1"
                }
            ],
            "postalCode": int(cep.replace("-", "")),
            "country": "BRA",
            "shippingData": {
                "logisticsInfo": [
                    {
                        "itemIndex": 0,
                        "selectedSLAId": "Envio Padrão",
                        "selectedDeliveryChannel": "delivery"
                    }
                ]
            }
        }

        try:
            response = cls.post(
                "https://www.carajas.com.br/api/checkout/pub/orderForms/simulation",
                headers=headers,
                data=json.dumps(payload),
            )
            data = json.loads(response.content)

            if "error" not in data:
                for value in data["logisticsInfo"][0]["slas"]:
                    if "Retira" not in value["id"]:
                        valor_frete = float(str(value["price"])[:-2] + "." + str(value["price"])[-2:])
                        prazo_frete = value["shippingEstimate"]
        except RequestException as e:
            logger.error(f"[Carajas] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Carajas] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
