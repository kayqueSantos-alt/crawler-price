import re
import json
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Construbel(BaseCrawler):

    d_para_produto = {
        "2020011": "167636861",
        "2020010": "167636859",
        "2020033": "167636849",
        "2020010": "167636853",
        "2020076": "167636857",
        "2020011": "167636855",
        "2020005": "167636847",
        "2020032": "167636851",
        "1020080": "167634417",
        "1020080": "167638875",
        "1020081": "167638877",
        "1020055": "167638875",
        "2020053": "167636859",
        "2020054": "167636861"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produto = str(
                soup.find("script", {"type": "application/ld+json"})
            ).replace('<script type="application/ld+json">', "").replace("</script>", "").strip()
            produto = produto.replace("\n", "").replace(" ", "").replace("&bull", "").replace(";", "")
            clean_str = re.sub(r'[\x00-\x1f\x7f]', "PEDRAO", produto)

            # GAMBIARRA SINISTRA
            clean_str = clean_str.replace(
                ":", "KK"
            ).replace(
                '"KK', '":'
            ).replace(
                ",", "QQ"
            ).replace(
                '"QQ', '",'
            ).replace(
                '}QQ', '},'
            ).replace(
                '""', ''
            ).replace(
                '"PEDRAO', ''
            )

            price = json.loads(clean_str)

            try:
                prod_obj["valor_produto"] = float(price["offers"]["sale_price"])
            except (KeyError, TypeError, ValueError):
                try:
                    prod_obj["valor_produto"] = float(price["offers"]["price"])
                except (KeyError, TypeError, ValueError):
                    prod_obj["valor_produto"] = None
        except (RequestException, json.JSONDecodeError, AttributeError, TypeError) as e:
            logger.error(f"[Construbel] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        try:
            prod_id = cls.get_product_id(sku, cls.d_para_produto)
            cep_parts = cep.split("-")

            response_freight = cls.get(
                f"https://www.construbel.com.br/mvc/store/product/shipping/?nocache=68aed823435c8&loja=1076270&simular=ok&cep1={cep_parts[0]}&cep2={cep_parts[1]}&quantidade=1&variacao=0&id_produto={prod_id}"
            )
            soup_freight = BeautifulSoup(response_freight.content, "html.parser")
            table_freight = soup_freight.find_all("table")

            try:
                element_value_freight = table_freight[1].find_all("tr")[1].find_all("td")
                prod_obj["prazo_frete"] = element_value_freight[3].text.split("dia(s)")[0][-3:].strip()
                value_freight = element_value_freight[2].find("strong").text
                if value_freight in ("FRETE GRÁTIS", "FRETE GR\u00a1TIS"):
                    prod_obj["valor_frete"] = 0
                else:
                    prod_obj["valor_frete"] = value_freight
            except (IndexError, AttributeError, TypeError):
                span = soup_freight.find("span", class_="color")

                if span:
                    span_text = span.get_text(strip=True)
                    if "-" in span_text:
                        prod_obj["disponibilidade"] = "CEP indisponivel"
                    else:
                        prod_obj["disponibilidade"] = span_text
                else:
                    prod_obj["disponibilidade"] = "CEP indisponivel"
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[Construbel] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete"),
            disponibilidade=prod_obj.get("disponibilidade")
        )
        return cls.validate_result(result)
