import json
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class Bigolin(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        d_para_hash_prod = {
            "2020011": "1efd2808439242369dfc0b8b7af030a8",
            "2020010": "1efd2808439242369dfc0b8b7af030a8",
            "2020009": "1efd2808439242369dfc0b8b7af030a8",
            "2020032": "1efd2808439242369dfc0b8b7af030a8",
            "2020008": "1efd2808439242369dfc0b8b7af030a8",
            "2020004": "1efd2808439242369dfc0b8b7af030a8"
        }

        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            prod_obj["valor_produto"] = General.price_treatment(soup.find(class_="skuBestPrice").text)
        except (RequestException, AttributeError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            hash_prod = cls.get_product_id(sku, d_para_hash_prod)

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
                "expectedOrderFormSections": ["items", "totalizers", "clientProfileData", "shippingData", "paymentData", "sellers", "messages", "marketingData", "clientPreferencesData", "storePreferencesData", "giftRegistryData", "ratesAndBenefitsData", "openTextField", "commercialConditionData", "customData"]
            }

            url_to_get = f'https://www.bigolinmateriais.com.br/api/checkout/pub/orderForm/{hash_prod}/attachments/shippingData'
            response_freight = cls.post(url_to_get, json=body).json()

            for value in response_freight["totalizers"]:
                if value["id"] == "Shipping":
                    prod_obj["valor_frete"] = float(str(value["value"])[:-2] + "." + str(value["value"])[-2:])

            prod_obj["prazo_frete"] = response_freight["shippingData"]["logisticsInfo"][0]["slas"][0]["shippingEstimate"]
        except (RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
