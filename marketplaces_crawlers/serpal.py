import json
import logging
import cloudscraper
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Serpal(BaseCrawler):

    D_PARA_ITEMS = {
        "2020008": "134611494",
        "2020009": "134611495",
    }

    @classmethod
    def _clean_ld_json_text(cls, raw_text):
        """
        Aplica a cadeia de replaces necessaria para corrigir o ld+json
        malformado do site Serpal.
        """
        text = raw_text
        text = text.replace("<", "").replace(">", "").replace("/", "")
        text = text.replace(",", "UUU").replace("}UUU", "},").replace('"UUU', '",')
        text = text.replace(":", "DDDD").replace('"DDDD', '":')
        text = text.replace('style="', '').replace("'", "")
        text = text.replace('"', 'JJJ')
        text = text.replace('JJJ:', '":').replace(':JJJ', ':"')
        text = text.replace('JJJ,', '",').replace(',JJJ', ',"')
        text = text.replace('{JJJ', '{"').replace('JJJ}', '"}')
        text = text.replace('JJJ@', '"@')
        text = text.replace('JJJgtin', '"gtin')
        text = text.replace('JJJsku', '"sku')
        text = text.replace('JJJoffers', '"offers')
        return text

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_ITEMS)

        headers_page = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        # --- Preco ---
        try:
            soup = cls.get_soup(url, headers=headers_page)
            scripts = soup.find_all("script", {"type": "application/ld+json"})
            if scripts:
                raw_text = scripts[0].text
                cleaned = cls._clean_ld_json_text(raw_text)
                produto = json.loads(cleaned)
                valor_produto = float(produto["@graph"][0]["offers"]["price"])
        except RequestException as e:
            logger.error(f"[Serpal] Erro de rede ao acessar {url}: {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Serpal] Erro ao extrair preco de {url}: {e}")

        # --- Frete (usa cloudscraper session diretamente) ---
        url_frete = "https://eletricaserpal.com.br/index.php?route=extension/total/shipping/quote"

        payload = {
            "postcode": cep.replace("-", ""),
            "product_id": product_id,
            "quantidade": "1",
            "page": "product/product",
            "tipo": "",
            "ibge": "5300108"
        }

        headers_freight = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://eletricaserpal.com.br",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive"
        }

        try:
            session = cloudscraper.create_scraper()
            session.get(url, headers=headers_freight)
            response = session.post(url_frete, data=payload, headers=headers_freight)
            data = json.loads(response.content)

            for value in data["shipping_method"]:
                if "Retirar na loja" not in value["title"]:
                    valor_frete = float(f"{value['quote'][0]['cost']:.2f}")
                    prazo_frete = str(value["quote"][0]["days"])
        except RequestException as e:
            logger.error(f"[Serpal] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Serpal] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
