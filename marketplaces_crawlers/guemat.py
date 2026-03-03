import json
import html
import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Guemat(BaseCrawler):

    d_para_item = {
        "1020080": "201446794",
        "2020010": "99437690",
        "2020052": "99436710",
        "2020005": "156882188",
        "2020017": "99454853",
        "2020048": "128252059",
        "2020047": "128250531",
        "2020011": "99449970",
        "2020008": "99451938",
        "2020004": "156882197",
        "2020032": "",
        "2020033": "",
        "2020076": ""
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            scripts = soup.find_all("script")

            for script in scripts:
                if "dataLayer" in script.text and "ecommerce" in script.text:
                    produto = (
                        script.text.strip()
                        .replace("dataLayer.push(", "")
                        .replace(");", "")
                        .replace('.replace(",",".")', "")
                        .replace("'", '"')
                    )
                    produto = html.unescape(produto)
                    try:
                        data = json.loads(produto)
                        prod_obj["valor_produto"] = float(
                            data["ecommerce"]["detail"]["products"][0]["price"]
                        )
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
                        logger.error(f"[Guemat] Erro ao parsear dataLayer: {e}")
                        prod_obj["valor_produto"] = None
        except (RequestException, TypeError) as e:
            logger.error(f"[Guemat] Erro ao buscar pagina: {e}")
            prod_obj["valor_produto"] = None

        try:
            item_id = cls.get_product_id(sku, cls.d_para_item)

            response_freight = cls.get(
                f"https://www.guemat.com.br/carrinho/frete?cep={cep}&produto_id={item_id}&quantidade=1"
            )
            data = json.loads(response_freight.content)

            if "error" not in data:
                for item in data:
                    if item["originalName"] == "Guemat":
                        prod_obj["valor_frete"] = float(item["price"])
                        prod_obj["prazo_frete"] = str(item["deliveryTime"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"[Guemat] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
