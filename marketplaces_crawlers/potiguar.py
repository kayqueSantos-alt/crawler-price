import json
import logging
from bs4 import BeautifulSoup
from modules.base_crawler import BaseCrawler
from modules.general import General
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class Potiguar(BaseCrawler):

    D_PARA_PRODUTO = {
        "2020005": "89425",
        "2020011": "99813",
        "02020010": "99778",
        "02020009": "89423",
        "2020004": "74257",
        "2020033": "89424",
        "2020008": "76407",
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.D_PARA_PRODUTO)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup, index=0)

            if ld_json:
                valor_produto = float(ld_json["offers"][0]["price"])
        except RequestException as e:
            logger.error(f"[Potiguar] Erro de rede ao acessar {url}: {e}")
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[Potiguar] Erro ao extrair preco de {url}: {e}")

        # --- Frete ---
        payload = {
            "parametroCompraProduto": {
                "ProdutoId": product_id,
                "StrOpcional": "Selecione",
                "IsAssinatura": False,
                "DadosProduto": [
                    {
                        "ProdutoComboId": "0",
                        "ProdutoVarianteId": "274917",
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

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-length": "349",
            "content-type": "application/json; charset=UTF-8",
            "cookie": '"__utmc=124266330; __utmz=124266330.1755622978.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _gcl_au=1.1.539621109.1755622979; __bid=d58a5dfc-2182-456a-86db-10e783d9b81d; _fbp=fb.2.1755622978743.23749493401259822; key_egoi_client=1772115; smeventsclear_535d1c39bd2a4ab8b388b99bd744732c=true; _hjSessionUser_1946489=eyJpZCI6ImYwNDA4MGQzLTA3NGYtNWQ2Mi1hMTA3LWMzYTUyMDUwOWEwZiIsImNyZWF0ZWQiOjE3NTU2MjI5Nzg1NzYsImV4aXN0aW5nIjp0cnVlfQ==; acceptedCookies=true; _hjSession_1946489=eyJpZCI6ImUwNjkyYTFiLTkyYjUtNDA2OS1hODk0LTE5MjY0MzAzOTU4YyIsImMiOjE3NTY0MTAwMjQzMzMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; __utma=124266330.593749997.1755622978.1755622978.1756410024.2; _gid=GA1.3.2142500073.1756410024; _pk_ses.1772115.2cad=*; parceiroSelecionado=demais-regioes; __utmt_fbits=1; cep-cotado=29177-306; smeventssent_535d1c39bd2a4ab8b388b99bd744732c=true; historicoProduto=99813,89423,76407,89425,99778,74257,89424; Fbits.Parceiro={"parceiroAtivo":"","utmSource":"","utmCampaign":"","utmMedium":"","utmTerm":"","utmContent":"","parceiroUltimaData":false,"directUltimaData":"2025-08-28T20:07:32.000Z","urlTrackeada":false}; __utmb=124266330.10.10.1756410024; _ga_2GDJXZQVRW=GS2.1.s1756410024$o2$g1$t1756411654$j58$l0$h0; _ga=GA1.3.593749997.1755622978; _pk_id.1772115.2cad=3f77393fbd71915f.1755622979.2.1756411655.1756410025."',
            "origin": "https://www.apotiguar.com.br",
            "priority": "u=1, i",
            "referer": "https://www.apotiguar.com.br/produto/tanque-de-agua-polietileno-5-000l-fortlev-76407",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

        try:
            response = cls.post_json(
                "https://www.apotiguar.com.br/Produto/CalcularFreteProdutoCarrinhoNovo",
                data=json.dumps(payload),
                headers=headers,
            )

            if len(response) > 1:
                soup_frete = BeautifulSoup(response[1]["opcoesFrete"], "html.parser")
                valor_frete = General.price_treatment(
                    soup_frete.find_all("tr")[1].find("span", {"class", "valor"}).text
                )
                prazo_frete = soup_frete.find_all("tr")[1].find("span", {"class", "prazo"}).text
        except RequestException as e:
            logger.error(f"[Potiguar] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"[Potiguar] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
