import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Tropeiro(BaseCrawler):

    D_PARA_ITEM = {
        "2020009": "821",
        "2020010": "822",
        "02020011": "823",
        "2020008": "827",
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEM)

        # --- Preco (busca ld+json com campo "mainEntity" em vez de indice fixo [2]) ---
        try:
            soup = cls.get_soup(url)
            data = cls.find_ld_json_with_field(soup, "mainEntity")

            if data:
                valor_produto = float(data["mainEntity"]["itemListElement"][2]["offers"][0]["price"])
        except RequestException as e:
            logger.error(f"[Tropeiro] Erro de rede ao acessar {url}: {e}")
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Tropeiro] Erro ao extrair preco de {url}: {e}")

        # --- Frete ---
        payload = {
            "postcode": cep,
            "product_id": product_id,
            "days_stock": "0",
            "quantity_product": "1"
        }

        try:
            response = cls.post_json(
                "https://www.hidraulicatropeiro.com.br/index.php?route=module/shipping/simulate",
                data=payload,
            )
            valor_frete = float(response["shipping_method"]["shipping_custom"]["quote"]["shipping_custom"]["shipping_actual_cost"])
            prazo_frete = str(response["shipping_method"]["shipping_custom"]["quote"]["shipping_custom"]["delivery_time"])
        except RequestException as e:
            logger.error(f"[Tropeiro] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Tropeiro] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
