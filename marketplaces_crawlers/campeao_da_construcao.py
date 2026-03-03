import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Campeao_da_construcao(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}
        session = requests.session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://campeaodaconstrucao.com.br",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive"
        }

        try:
            response = cls.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            produto = soup.find("script", {"type": "application/ld+json"}).string
            raw = re.sub(r'"description":".*?",', '', produto, flags=re.DOTALL)
            data = json.loads(raw)
            price = data["@graph"][0]["offers"]["price"]
            prod_obj["valor_produto"] = float(price)
        except (RequestException, AttributeError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        d_para_items = {
            "2020017": "19177"
        }

        try:
            product_id = cls.get_product_id(sku, d_para_items)

            payload = {
                "postcode": cep.replace("-", ""),
                "product_id": product_id,
                "quantidade": "1",
                "page": "product/product",
                "tipo": "",
                "ibge": "5300108"
            }

            session.get(url, headers=headers)
            response = session.post("https://campeaodaconstrucao.com.br/index.php?route=extension/total/shipping/quote", data=payload, headers=headers).content
            data = json.loads(response)

            for value in data["shipping_method"]:
                if "Retirar na loja" not in value["title"]:
                    if "erro" not in value["quote"][0]:
                        prod_obj["valor_frete"] = float(value["quote"][0]["cost"])
                        prod_obj["prazo_frete"] = str(value["quote"][0]["days"])
                        break
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
