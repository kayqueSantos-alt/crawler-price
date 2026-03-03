import logging
from modules.base_crawler import BaseCrawler
from modules.crawler_settings import Crawler
from modules.efizitools import Efizi
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class BabaMateriais(BaseCrawler):

    FREIGHT_URL = (
        "https://www.babamateriais.com.br/_v/segment/graphql/v1?"
        "workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR"
        "&__bindingId=b54ee69b-f3cd-4b51-a5d4-b7b5da0de97a"
        "&operationName=getShippingEstimates&variables=%7B%7D"
        "&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22"
        "sha256Hash%22%3A%227ce5ad49f177bdecfef578def58ba597a57ae64295229da99c804bfe933d4b42%22%2C%22"
        "sender%22%3A%22vtex.store-components%403.x%22%2C%22"
        "provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22"
        "variables%22%3A%22{base64}%3D%3D%22%7D"
    )

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        # --- Busca ID do produto no mapeamento ---
        d_para_prod = Efizi.d_para()
        id_product = cls.get_product_id(sku, d_para_prod["ECOMMERCE"]["BABA_MATERIAIS"])

        # --- Preco ---
        soup = cls.get_soup(url)
        price_data = cls.extract_ld_json(soup, index=0)

        if price_data is None:
            logger.error(f"[BabaMateriais] Nao foi possivel extrair ld+json de {url}")
        else:
            availability = (
                price_data.get("offers", {})
                .get("offers", [{}])[0]
                .get("availability", "")
            )
            if availability != "http://schema.org/OutOfStock":
                high_price = price_data.get("offers", {}).get("highPrice")
                valor_produto = float(high_price) if high_price is not None else None
            else:
                logger.info(f"[BabaMateriais] Produto fora de estoque: {url}")

        # --- Frete ---
        try:
            data_freight = Crawler.requests_pattern_freight(
                cep, id_product, cls.FREIGHT_URL, "Frota Babá"
            )
            valor_frete = float(data_freight["price"] / 100)
            prazo_frete = data_freight["shippingEstimate"]
        except RequestException as e:
            logger.warning(f"[BabaMateriais] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"[BabaMateriais] Erro ao parsear frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
