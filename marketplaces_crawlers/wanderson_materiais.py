import re
import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class WandersonMateriais(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020008": "",
        "2020005": "29706155",
        "2020004": "29727033",
        "2020033": "29706193"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        # --- Preco (ld+json com regex cleanup) ---
        try:
            soup = cls.get_soup(url, headers=headers)

            raw = soup.find("script", {"type": "application/ld+json"})

            clean = re.sub(r"<br\s*/?>", " ", raw.string)
            clean = re.sub(r"[\n\r]", " ", clean)
            clean = re.sub(r"\s+", " ", clean).strip()

            pattern = r'"description"\s*:\s*"(.*?)"\s*,\s*"brand"'
            clean = re.sub(
                pattern,
                lambda m: f'"description":"{m.group(1).replace(chr(92), chr(92)*2).replace(chr(34), chr(92)+chr(34))}","brand"',
                clean,
                flags=re.DOTALL
            )

            data = json.loads(clean)

            if len(data["@graph"]) > 0:
                valor_produto = float(data["@graph"][0]["offers"]["price"])
        except (KeyError, IndexError, TypeError, ValueError, AttributeError, json.JSONDecodeError) as e:
            logger.warning(f"[WandersonMateriais] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[WandersonMateriais] Erro de rede ao acessar {url}: {e}")

        # --- Frete (OpenCart shipping/quote) ---
        if valor_produto is not None:
            try:
                data_to_freight = {
                    "postcode": cep.replace("-", ""),
                    "product_id": product_id,
                    "quantidade": "1",
                    "page": "product/product",
                    "tipo": "RCB",
                    "ibge": "5001102"
                }

                response_freight = cls.post_json(
                    "https://wandersonmateriais.com.br/index.php?route=extension/total/shipping/quote",
                    headers=headers,
                    data=data_to_freight,
                )

                if not response_freight["shipping_method"][0]["quote"][0]["erro"]:
                    valor_frete = response_freight["shipping_method"][0]["quote"][0]["cost"]
                    prazo_frete = str(response_freight["shipping_method"][0]["quote"][0]["days"]) + " dias íteis"
            except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
                logger.warning(f"[WandersonMateriais] Erro ao extrair frete (CEP: {cep}): {e}")
            except RequestException as e:
                logger.error(f"[WandersonMateriais] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
