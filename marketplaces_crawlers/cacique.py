import json
import re
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Cacique(BaseCrawler):

    D_PARA_ITEMS = {
        "2020008": "268",
    }

    @classmethod
    def _extract_sku_json(cls, soup):
        """
        Extrai dados do produto buscando pelo padrao 'var skuJson_0'
        em vez de usar indice fixo [35] que quebra facilmente.
        """
        for script in soup.find_all("script"):
            text = script.string or script.text or ""
            if "var skuJson_0" in text:
                # Remove o wrapper JS para extrair o JSON
                cleaned = text.replace("var skuJson_0 = ", "")
                # Remove tudo apos o primeiro ';' que fecha o JSON
                cleaned = re.split(r';\s*CATALOG_SDK', cleaned)[0]
                cleaned = cleaned.strip().rstrip(";")
                return json.loads(cleaned)

        logger.warning("[Cacique] Padrao 'var skuJson_0' nao encontrado no HTML")
        return None

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEMS)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            sku_data = cls._extract_sku_json(soup)

            if sku_data:
                best_price = sku_data["skus"][0]["bestPrice"]
                # bestPrice vem em centavos (ex: 12990 = R$ 129,90)
                valor_produto = float(str(best_price)[:-2] + "." + str(best_price)[-2:])
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"[Cacique] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[Cacique] Erro de rede ao acessar {url}: {e}")

        # --- Frete ---
        freight_url = (
            f"https://www.caciquehomecenter.com.br/frete/calcula/{product_id}"
            f"?shippinCep={cep}&quantity=1"
        )
        try:
            soup_freight = cls.get_soup(freight_url)
            tbody = soup_freight.find("tbody")

            if tbody:
                rows = tbody.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 2:
                        continue

                    valor_text = cols[0].get_text(strip=True)
                    descricao = cols[1].get_text(strip=True)

                    if "Retira na Loja" in descricao or "Retira na loja" in descricao:
                        continue

                    if "Frete Grátis" in valor_text:
                        valor_frete = 0.0
                    else:
                        valor_frete = cls.parse_price(valor_text)

                    # Tenta extrair prazo se houver mais colunas
                    if len(cols) >= 3:
                        prazo_frete = cls.parse_deadline(cols[2].get_text(strip=True))

                    break
            else:
                logger.warning(f"[Cacique] Tabela de frete nao encontrada (CEP: {cep})")
        except RequestException as e:
            logger.warning(f"[Cacique] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (AttributeError, IndexError, TypeError) as e:
            logger.warning(f"[Cacique] Erro ao parsear frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
