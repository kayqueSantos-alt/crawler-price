import json
import re
import logging
from modules.base_crawler import BaseCrawler
from modules.general import General
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class LojasPedrao(BaseCrawler):

    D_PARA_ITEM = {
        "1020081": "46434",
        "2020048": "46432",
        "2020047": "46431",
        "2020010": "46429",
        "2020009": "46427",
        "2020008": "46425",
        "2020017": "33531",
        "2020076": "",
        "1020080": "",
        "1020042": "",
        "1020055": "",
    }

    @classmethod
    def _extract_sku_json(cls, soup):
        """
        Extrai dados do produto buscando pelo padrao 'var skuJson_0'
        em vez de usar indice fixo.
        """
        for script in soup.find_all("script"):
            text = script.string or script.text or ""
            if "var skuJson_0" in text:
                cleaned = text.replace("var skuJson_0 = ", "")
                cleaned = re.split(r';\s*CATALOG_SDK', cleaned)[0]
                cleaned = cleaned.strip().rstrip(";")
                return json.loads(cleaned)

        logger.warning("[LojasPedrao] Padrao 'var skuJson_0' nao encontrado no HTML")
        return None

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEM)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            sku_data = cls._extract_sku_json(soup)

            if sku_data:
                raw_price = float(f"{sku_data['skus'][0]['spotPrice'] / 100}")
                if float(f"{raw_price:.2f}") > 100000:
                    valor_produto = None
                else:
                    valor_produto = float(f"{raw_price:.2f}")
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[LojasPedrao] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[LojasPedrao] Erro de rede ao acessar {url}: {e}")

        # --- Frete ---
        freight_url = (
            f"https://www.lojadopedrao.com.br/frete/calcula/{product_id}"
            f"?shippinCep={cep.replace('-', '')}&quantity=1"
        )
        try:
            soup_freight = cls.get_soup(freight_url)
            linhas = soup_freight.find_all("tr")

            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 2:
                    tipo_frete = colunas[0].get_text(strip=True)
                    descricao = colunas[1].get_text(strip=True)

                    if "Retirada" not in descricao:
                        valor_frete = float(0 if "Frete Grátis" in tipo_frete else General.price_treatment(tipo_frete))
                        match = re.search(r"(\d+)\s*dias?\s*úteis?", descricao)
                        prazo_frete = match.group(1) if match else None
                        break
        except RequestException as e:
            logger.warning(f"[LojasPedrao] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (AttributeError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[LojasPedrao] Erro ao parsear frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
