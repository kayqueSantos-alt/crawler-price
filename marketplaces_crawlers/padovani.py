import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Padovani(BaseCrawler):

    D_PARA_HASH_PROD = {
        "2020009": "28e5b25be0874fbcbeb12d17eac476ea",
        "2020008": "28e5b25be0874fbcbeb12d17eac476ea",
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        order_form_hash = cls.get_product_id(sku, cls.D_PARA_HASH_PROD)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup, index=0)

            if ld_json:
                valor_produto = ld_json["offers"]["highPrice"]
        except RequestException as e:
            logger.error(f"[Padovani] Erro de rede ao acessar {url}: {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"[Padovani] Erro ao extrair preco de {url}: {e}")

        # --- Frete (VTEX orderForm attachment) ---
        body = {
            "logisticsInfo": [
                {
                    "addressId": None,
                    "itemIndex": 0,
                    "selectedDeliveryChannel": None,
                    "selectedSla": None
                }
            ],
            "clearAddressIfPostalCodeNotFound": False,
            "selectedAddresses": [
                {
                    "addressType": "residential",
                    "country": "BRA",
                    "postalCode": cep
                }
            ],
            "expectedOrderFormSections": [
                "items", "totalizers", "clientProfileData", "shippingData",
                "paymentData", "sellers", "messages", "marketingData",
                "clientPreferencesData", "storePreferencesData",
                "giftRegistryData", "ratesAndBenefitsData", "openTextField",
                "commercialConditionData", "customData"
            ]
        }

        url_freight = f'https://www.padovani.com.br/api/checkout/pub/orderForm/{order_form_hash}/attachments/shippingData'

        try:
            response_freight = cls.post_json(url_freight, json=body)

            for value in response_freight["totalizers"]:
                if value["id"] == "Shipping":
                    valor_frete = float(str(value["value"])[:-2] + "." + str(value["value"])[-2:])

            prazo_frete = response_freight["shippingData"]["logisticsInfo"][0]["slas"][0]["shippingEstimate"]
        except RequestException as e:
            logger.error(f"[Padovani] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Padovani] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
