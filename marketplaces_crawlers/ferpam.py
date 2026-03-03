import json
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Ferpam(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produto = str(soup.find("div", {"class": "no-display price product-price"})).replace('<div class="no-display price product-price">', "").replace("</div>", "")
            prod_obj["valor_produto"] = float(produto)
        except (RequestException, AttributeError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        d_para_items = {
            "2020033": "29642",
            "2020008": "21153",
            "2020009": "21132",
            "2020011": "21124",
            "1020042": "30052",
            "2020010": "",
            "1020055": "147494"
        }

        try:
            product_id = cls.get_product_id(sku, d_para_items)

            response = cls.get(f"https://www.ferpam.com.br/rest/V1/shippingquoteproductpage/?product={product_id}&selected_configurable_option=&related_product=&item={product_id}&form_key=2O7GAU4CkNPTfyBQ&qty=1&cep={cep}&tipobusca=1&_=1755815916803")
            response_text = response.content.decode("utf-8")
            try:
                data = json.loads(json.loads(response_text))
            except (TypeError, ValueError, json.JSONDecodeError):
                data = json.loads(response_text)

            if "message" not in data:
                if data[-1]["carrier"] != "FERPAM RETIRE AQUI":
                    prod_obj["prazo_frete"] = str(data[-1]["title"])
                    prod_obj["valor_frete"] = float(data[-1]["price"].replace("R$", "").replace(".", "").replace(",", "."))
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
