import json
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class CasaMattos(BaseCrawler):

    d_para_items = {
        "2020009": "74834",
        "2020010": "76216",
        "2020008": "71504",
        "2020005": "72652",
        "2020004": "71322"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            item_id = cls.get_product_id(sku, cls.d_para_items)
        except KeyError as e:
            logger.error(f"[CasaMattos] SKU nao encontrado: {e}")
            return cls.validate_result(
                cls.build_result(valor_produto=None, valor_frete=None, prazo_frete=None)
            )

        try:
            response_price = cls.post_json(f"https://www.casamattos.com.br/produto/api/{item_id}")
            prod_obj["valor_produto"] = float(response_price["Variantes"][0]["PrecoPor"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[CasaMattos] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        payload = {
            "parametroCompraProduto": {
                "ProdutoId": item_id,
                "StrOpcional": "Selecione",
                "IsAssinatura": False,
                "DadosProduto": [
                    {
                        "ProdutoComboId": "0",
                        "ProdutoVarianteId": "261425",
                        "ComboId": 0,
                        "ProdutoId": 0,
                        "Atributos": [],
                        "Quantidade": "1",
                        "ListaPersonalizacoes": []
                    }
                ],
                "attrNaoSelecionado": False,
                "sellerBuyBoxNaoSelecionado": False
            },
            "CEP": cep,
            "freteAberto": "True"
        }

        try:
            response_frete = cls.post_json(
                "https://www.casamattos.com.br/Produto/CalcularFreteProdutoCarrinhoNovo",
                json=payload
            )

            html = response_frete[1]["opcoesFrete"]
            soup = BeautifulSoup(html, "html.parser")

            for row in soup.find_all("tr"):
                contrato = row.find("span", class_="contrato").get_text(strip=True)
                valor = row.find("span", class_="valor").get_text(strip=True)
                prazo = row.find("span", class_="prazo").get_text(strip=True)

                if "retirada" not in contrato.lower():
                    prod_obj["valor_frete"] = valor

                    if "Frete Grátis" in prod_obj["valor_frete"]:
                        prod_obj["valor_frete"] = 0.0
                        prod_obj["prazo_frete"] = str(prazo)

            prod_obj["disponibilidade"] = None
        except (RequestException, KeyError, IndexError, TypeError, ValueError, AttributeError) as e:
            logger.error(f"[CasaMattos] Erro ao buscar frete: {e}")
            try:
                data_error = response_frete[0]["errosFrete"]
                prod_obj["disponibilidade"] = data_error
            except (KeyError, IndexError, TypeError, NameError):
                prod_obj["disponibilidade"] = "Erro ao consultar frete"

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete"),
            disponibilidade=prod_obj.get("disponibilidade")
        )
        return cls.validate_result(result)
