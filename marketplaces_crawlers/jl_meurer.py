import json
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class Jl_meurer(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):

        d_para_produtos = {
            "2020005": "4149"
        }

        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produto = str(soup.find("script", {"type": "application/ld+json"})).replace('<script type="application/ld+json">', "").replace("</script>", "")
            price = json.loads(produto)
            prod_obj["valor_produto"] = float(price["offers"]["price"])
        except (RequestException, AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            product_id = cls.get_product_id(sku, d_para_produtos)

            response_freight = cls.get(f'https://www.jlmeurer.com.br/mvc/store/product/shipping/?nocache=68b17331ee594&loja=1013190&simular=ok&cep1={cep.split("-")[0]}&cep2={cep.split("-")[1]}&quantidade=1&id_produto={product_id}')
            soup = BeautifulSoup(response_freight.content, "html.parser")
            prod_obj["valor_frete"] = General.price_treatment(soup.find_all("td", {"width": "100px", "align": "center"})[1].find("strong").text)
            prod_obj["prazo_frete"] = None
        except (RequestException, AttributeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[{cls.__name__}] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
