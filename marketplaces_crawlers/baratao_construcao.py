import logging
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler
from modules.general import General

logger = logging.getLogger("crawlers")


class Baratao(BaseCrawler):

    d_para_prod = {
        "2020004": "6629756",
        "2020008": "6629764",
        "2020010": "6629771"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            prod_id = cls.get_product_id(sku, cls.d_para_prod)

            response = cls.get_json(
                f"https://www.redebarataodaconstrucao.com.br/sku/price?skuId={prod_id}&zipcode={cep}&city=Rio%20de%20Janeiro&state=RJ&origin=bybox&isDebug=false"
            )

            first_key = list(response.keys())[0]
            stockid = response[first_key]["best"]["stockId"]
            prod_obj["valor_produto"] = response[first_key]["best"]["price"]
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"[Baratao] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None
            stockid = None

        if stockid is not None:
            try:
                response_freight = cls.get_json(
                    f"https://www.redebarataodaconstrucao.com.br/rest/consulta-frete?stockIds={stockid}&zipcode={cep}&quantities=1"
                )

                prod_obj["valor_frete"] = General.price_treatment(
                    response_freight["freights"][0]["allFreights"][0]["amount"]
                )
                prod_obj["prazo_frete"] = (
                    str(response_freight["freights"][0]["allFreights"][0]["deliveryTime"])
                    + " dias uteis"
                )
            except (RequestException, KeyError, IndexError, TypeError, ValueError) as e:
                logger.error(f"[Baratao] Erro ao buscar frete: {e}")
                prod_obj.setdefault("valor_frete", None)
                prod_obj.setdefault("prazo_frete", None)
        else:
            prod_obj.setdefault("valor_frete", None)
            prod_obj.setdefault("prazo_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
