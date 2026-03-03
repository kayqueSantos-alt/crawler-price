import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Taqi(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020004": "197377",
        "1020080": "197371",
        "1020081": "197370",
        "1020042": "197368",
        "1020055": "100069013",
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco ---
        try:
            response_product = cls.get_json(
                f'https://www.taqi.com.br/ccstoreui/v1/products?productIds={product_id}&includeChildren=false'
            )
            price = response_product["items"][0]["listPrices"]["real"]
            valor_produto = price
        except RequestException as e:
            logger.error(f"[Taqi] Erro de rede ao buscar preco do produto {product_id}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete)
            return cls.validate_result(result)
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Taqi] Erro ao extrair preco do produto {product_id}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete)
            return cls.validate_result(result)

        # --- Preparacao de dimensoes para frete ---
        try:
            width = int(response_product["items"][0]["width"])
            height = int(response_product["items"][0]["height"])
            length = int(response_product["items"][0]["length"])
            weight = int(response_product["items"][0]["weight"])
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Taqi] Erro ao extrair dimensoes do produto {product_id}: {e}")
            result = cls.build_result(valor_produto=valor_produto, valor_frete=valor_frete, prazo_frete=prazo_frete)
            return cls.validate_result(result)

        # --- Frete ---
        url_frete = "https://www.taqi.com.br/ccstorex/custom/v1/hervalApiCalls/getData"

        payload = json.dumps({
            "url": "/fretes/api/CotacaoFrete",
            "data": {
                "shippingGroupIdsToPrice": [
                    "fakeGroupID"
                ],
                "request": {
                    "address": {
                        "country": "BR",
                        "postalCode": cep.replace("-", "")
                    },
                    "items": [
                        {
                            "amount": 0,
                            "product": {
                                "length": length,
                                "width": width,
                                "weight": weight,
                                "shippingSurcharge": None,
                                "id": product_id,
                                "taxCode": None,
                                "height": height
                            },
                            "quantity": 1,
                            "rawTotalPrice": 0,
                            "discount": 0,
                            "catalogRefId": product_id
                        }
                    ]
                },
                "order": {
                    "shoppingCart": {
                        "numberOfItems": 1,
                        "items": [
                            {
                                "unitPrice": price,
                                "quantity": 1,
                                "productId": product_id,
                                "length": length,
                                "width": width,
                                "weight": weight,
                                "height": height,
                                "dynamicProperties": [
                                    {
                                        "id": "x_cepOrigem",
                                        "label": "CEP de Origem",
                                        "value": cep.replace("-", "")
                                    }
                                ]
                            }
                        ]
                    },
                    "shippingGroups": [
                        {
                            "shippingGroupId": "fakeGroupID",
                            "items": [
                                {
                                    "unitPrice": price,
                                    "quantity": 1,
                                    "productId": product_id,
                                    "length": length,
                                    "width": width,
                                    "weight": weight,
                                    "height": height,
                                    "dynamicProperties": [
                                        {
                                            "id": "x_cepOrigem",
                                            "label": "CEP de Origem",
                                            "value": cep.replace("-", "")
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "siteId": "siteUS"
                }
            },
            "method": "POST"
        })

        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'ak_bmsc=6B0D63DFB4ACEB2FDF30B5C10480CE8C~000000000000000000000000000000~YAAQlIwQAiT1quOYAQAA9pny9hyPkFOsbaniN5FzGMF5b5GVlOebiSI6PUWR+/PEAj0H0GGf0mRdTK8rqKUinSjp7OA29HKLVqlpb2MqkJ59SVCH0xPZ+/XcN+vGLs9K4q9y0S+kBODxxu9nHRdxtFQBiqPwIUPuYQ69osk4nbioisTGdz5bfoRz8RJBFqUtYq+nu96P484QGPxc0iPt1Ou0PKePxgPalHjQSlRJBz5ZbMrjOngr1ZSE7jc97w7xOs0IGV4fn5sWJHxfhWHgDHWjOOPd0dthAPaxQWLHYNgEJJpFQCLJl5ZVLwYOLUQpexRaRYo+RzfNsMy0iREwAoNYmp+8rvk8Fkjqmrmw; GEO_CITY=SERRA; GEO_COUNTRY_CODE=BR; GEO_REGION_CODE=ES'
        }

        try:
            response = cls.post_json(url_frete, headers=headers, data=payload)
            valor_frete = response["shippingMethods"][0]["shippingCost"]
            prazo_frete = str(response["shippingMethods"][0]["deliveryDays"])
        except RequestException as e:
            logger.error(f"[Taqi] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"[Taqi] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
