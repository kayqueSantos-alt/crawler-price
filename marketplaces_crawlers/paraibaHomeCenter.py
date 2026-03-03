import json
import logging
from bs4 import BeautifulSoup
from modules.base_crawler import BaseCrawler
from modules.general import General
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class ParaibaHomeCenter(BaseCrawler):

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        # --- Preco (ld+json com campo "offers") ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.find_ld_json_with_field(soup, "offers")
            if ld_json and "offers" in ld_json:
                valor_produto = ld_json["offers"]["price"]
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"[ParaibaHomeCenter] Erro ao extrair preco de {url}: {e}")
        except RequestException as e:
            logger.error(f"[ParaibaHomeCenter] Erro de rede ao acessar {url}: {e}")

        # --- Frete (PUT com cookies) ---
        try:
            payload = {
                "zipcode": cep,
                "_method": "PUT",
                "cheaperQuote": "1",
                "_token": "098FtJQokAHC0Q6mRmZRjGEKhcnGwQkfTZx1img8"
            }

            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "content-length": "92",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "_gid=GA1.3.413518991.1756484945; _ga=GA1.1.1618977255.1756484945; mp_4087a793328d188d3705be7bee640b9f_mixpanel=%7B%22distinct_id%22%3A%20%22198f6a94a00b82-0d97692d3521e6-26011051-144000-198f6a94a019c6%22%2C%22%24device_id%22%3A%20%22198f6a94a00b82-0d97692d3521e6-26011051-144000-198f6a94a019c6%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; _fbp=fb.2.1756484946623.619840929175948881; _clck=1edi8jh%5E2%5Efyv%5E0%5E2067; _gcl_au=1.1.1794290844.1756484947.698028836.1756484981.1756484981; __goc_session__=xdvkmtisylbyzhjhiisxbsaektmnbuxt; paraiba-home-center_cart=eyJpdiI6IkhmaGxDbHdiUlAzUnBoV2d1czduWmc9PSIsInZhbHVlIjoidklZbUt1TFVCTU5xXC9CMVJYWVFxWCtzZTF1dmdJcHY2KzhZdEJhVzZkS3ZwWjE5S0x5TWRIZ2VvMjZ5eWRtYUIiLCJtYWMiOiIzYzE1ZTQwOTEzZjcwNGYyNWY3Y2UzMWRhMDFhMzA4NDkyYzBmMTU3MjA1NGQ5ZTA2OTA2ODFmMWNjZGQ1YWNiIn0%3D; __ana_uid=1-5rcntjz6-mex1t4en; _ga=GA1.4.1618977255.1756484945; _gid=GA1.4.413518991.1756484945; recommendationLoaded=true; _clsk=hxpqcw%5E1756484985259%5E2%5E0%5El.clarity.ms%2Fcollect; XSRF-TOKEN=eyJpdiI6IlNsamdXWkFDT1JBdWZaTWVZbkRCVkE9PSIsInZhbHVlIjoiOVJuQ3dMWXJxUG9oVGJycDk1MXc2N3E1NnR6YVpyb21mUFoycVUzZXBhQTZNYXRieXdjSWF3ekRaRUl6WWJ0SUJmdXlvMmhEMStER3VaUnAzY1NyT3c9PSIsIm1hYyI6IjM4NzQzOGMwOTllNmU4NjY5YWM2NGE2YzM5OGJiNzY3MzNjMWNhNmM0NWI4MDE5NTBlNmE2MjFmNTIzZGY3M2EifQ%3D%3D; bubbstore_checkout=eyJpdiI6Im9hRTl4Y1BkeEY0eHI5MEJScGJoUlE9PSIsInZhbHVlIjoiZ25HUzVyajV3MEdDVzYrNmJtQ0J6eTVEQjBqRUU2RjFjTjZYajFjR3hIUmdrZE1XZitrbU5QbnFFdnFlbEZ0WDRxUndlclYzSjZ6cVN6Q3p5SFRJSUE9PSIsIm1hYyI6IjUzNzQ3Y2QzZWIzOGYxMGFhNTY3Y2E3ZTcwOTJjM2JhY2E1NmQ1OTk1OTA0YWVlN2FiYTRkMjRlZjFmMGI4YTEifQ%3D%3D; _ga_3W1H0TVXYW=GS2.1.s1756484946$o1$g1$t1756485010$j59$l0$h0",
                "origin": "https://seguro.paraibahomecenter.com.br",
                "priority": "u=1, i",
                "referer": "https://seguro.paraibahomecenter.com.br/cart",
                "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest"
            }

            response_freight = cls._request_with_retry(
                "put",
                "https://seguro.paraibahomecenter.com.br/cart/zipcode",
                headers=headers,
                data=payload,
            )
            soup_freight = BeautifulSoup(response_freight.json()["html"], "html.parser")
            valor_frete = General.price_treatment(
                soup_freight.find("div", {"class": "mb10 medium"}).text
            )
            prazo_frete = (
                soup_freight.find("div", {"class": "shipping-delivery-time f13"})
                .find("span")
                .text.replace(" - até ", "")
            )
        except (KeyError, IndexError, TypeError, ValueError, AttributeError, json.JSONDecodeError) as e:
            logger.warning(f"[ParaibaHomeCenter] Erro ao extrair frete (CEP: {cep}): {e}")
        except RequestException as e:
            logger.error(f"[ParaibaHomeCenter] Erro de rede ao buscar frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
