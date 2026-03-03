import json
import logging
from datetime import datetime
from modules.base_crawler import BaseCrawler
from modules.general import General
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Sodimac(BaseCrawler):

    USE_CLOUDSCRAPER = True

    D_PARA_MES = {
        "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4,
        "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8,
        "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12,
    }

    D_PARA_PRODUTOS = {
        "2020004": "628095",
        "2020008": "112555",
        "2020047": "1004895",
        "2020017": "750313",
        "2020049": "1004894",
        "2020052": "1004886",
        "2020048": "1004896",
        "2020054": "1003455",
        "2020053": "1003454",
        "2020032": "750309",
        "2020005": "750310",
        "2020010": "628100",
        "2020009": "112556",
    }

    @classmethod
    def _parse_delivery_date(cls, json_prazo_frete):
        """Calcula prazo em dias a partir da resposta de frete da Sodimac."""
        mes_str = json_prazo_frete["slotDate"]["month"]
        dia = json_prazo_frete["slotDate"]["date"]

        mes = cls.D_PARA_MES.get(mes_str)
        if mes is None:
            logger.warning(f"[Sodimac] Mes desconhecido no frete: '{mes_str}'")
            return None

        now = datetime.now()
        ano = now.year + 1 if now.month > mes else now.year

        try:
            data_entrega = datetime.strptime(f"{ano}-{mes}-{dia}", "%Y-%m-%d")
            dias = (data_entrega - now).days
            return str(max(dias, 0))
        except ValueError as e:
            logger.warning(f"[Sodimac] Erro ao calcular data de entrega: {e}")
            return None

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            script_tag = soup.find("script", {"data-rh": "true"})
            if script_tag and script_tag.string:
                price_data = json.loads(script_tag.string)
                valor_produto = float(price_data["offers"][0]["price"])
            else:
                logger.warning(f"[Sodimac] Tag script data-rh nao encontrada em {url}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Sodimac] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Sodimac] Erro de rede ao acessar {url}: {e}")

        # --- Frete (tentativa 1: API economic) ---
        headers = {
            "x-channel-id": "WEB",
            "x-ecomm-name": "sodimac-br",
        }
        freight_url = (
            f"https://www.sodimac.com.br/s/checkout/v1/shipments/delivery-estimates/products"
            f"?priceGroup=1072&postCode={cep}&deliveryMethod=homeDeliveryEconomic"
            f"&skuId={product_id}&quantity=1"
        )

        try:
            json_freight = cls.get_json(freight_url, headers=headers)
            slot = json_freight["data"]["homeDeliveryEconomic"]["deliverySlots"][0]
            cost_str = slot["customTimeSlots"][0]["cost"]
            valor_frete = General.price_treatment(cost_str)
            prazo_frete = cls._parse_delivery_date(slot)
        except RequestException as e:
            logger.warning(f"[Sodimac] Erro de rede no frete economic (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Sodimac] Erro ao parsear frete economic (CEP: {cep}): {e}")

        # --- Frete (tentativa 2: API delivery-estimates POST) ---
        if valor_frete is None:
            try:
                headers_v2 = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "x-channel-id": "WEB",
                    "x-ecomm-name": "sodimac-br",
                    "content-type": "application/json",
                }
                payload = {
                    "data": {
                        "cartId": "b51e5d61-ac64-4478-9105-035c46cafc5a",
                        "destination": {
                            "postCode": cep,
                        },
                    },
                    "metadata": {
                        "zoneId": "44585",
                        "priceGroup": "1072",
                    },
                }
                cls.post(
                    "https://www.sodimac.com.br/s/checkout/v1/shipments/delivery-estimates",
                    data=json.dumps(payload),
                    headers=headers_v2,
                )
                logger.info(f"[Sodimac] Fallback de frete executado para CEP {cep}")
            except RequestException as e:
                logger.warning(f"[Sodimac] Fallback de frete tambem falhou (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
