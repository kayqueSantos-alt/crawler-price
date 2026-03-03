import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Quevedo(BaseCrawler):

    D_PARA_PRODUTOS = {
        "2020008": "10655"
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTOS)

        # --- Preco (HTML input#prod-valor) ---
        try:
            soup = cls.get_soup(url)
            valor_produto = float(soup.find("input", {"id": "prod-valor"})["value"])
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"[Quevedo] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Quevedo] Erro de rede ao acessar {url}: {e}")

        # --- Frete (API) ---
        try:
            freight_url = (
                f"https://www.comercialquevedo.com.br/checkout/cart"
                f"?operation=calculaFreteProduto&codigo={product_id}"
                f"&cep={cep}&preco={valor_produto}&deposito=1&quantidade=1"
            )
            response_freight = cls.get_json(freight_url)
            valor_frete = response_freight["agencias"][0]["servico"][0]["valor"]
            prazo_frete = str(response_freight["agencias"][0]["servico"][0]["prazoFinal"])
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Quevedo] Erro ao extrair frete (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[Quevedo] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
