import json
import logging
from modules.base_crawler import BaseCrawler
from requests.exceptions import RequestException

logger = logging.getLogger("crawlers")


class AcalHomeCenter(BaseCrawler):

    DE_PARA_ITEMS = {
        "2020009": 13925,
        "2020008": 20096,
        "2020005": 7998,
        "2020004": 2997,
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        valor_produto = None
        valor_frete = None
        prazo_frete = None

        product_id = cls.get_product_id(sku, cls.DE_PARA_ITEMS)

        # --- Preco ---
        try:
            soup = cls.get_soup(url)
            ld_json = cls.extract_ld_json(soup, index=0)

            if ld_json:
                valor_produto = ld_json["offers"]["highPrice"]
        except RequestException as e:
            logger.error(f"[AcalHomeCenter] Erro de rede ao acessar {url}: {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"[AcalHomeCenter] Erro ao extrair preco de {url}: {e}")

        # --- Frete (VTEX simulation) ---
        payload = {
            "country": "BRA",
            "postalCode": cep,
            "items": [
                {
                    "quantity": "1",
                    "id": product_id,
                    "seller": "1"
                }
            ]
        }

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "cookie": 'xe_visitor=eyJpZCI6ImY4NzQ2ZTU5LWRkZGMtNDI2OS04ZWE1LTZkMzI3ZWJlODljNiIsImVtYWlsIjoicGVkcm9ib2x6YW4xN0BnbWFpbC5jb20ifQ==; checkout.vtex.com=__ofid=1e896445b76b41fba745d2ac8ec8a374; VtexWorkspace=master%3A-; _fbp=fb.2.1759931130727.177383405569717829.Bg; vtex-search-session=afbe1b339bd84723b024c68acab605ae; vtex-search-anonymous=7096d259bc174d7599ad36134b5297cc; VtexRCSessionIdv7=31543698-64a6-43a9-80cb-8c7d62c4f42b; VtexRCMacIdv7=042db4d4-1c24-4cdc-858d-c7ceb3428dcf; _gcl_au=1.1.2103991719.1759931131; vtex_binding_address=lojaacal.myvtex.com/; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjAxZDQ4YWJkLWYzOWMtNDUxYi04NmQ0LTIzMDAzZGJhNDA5YyIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiI4MjRhOTc1Mi1hMWU1LTRmYmItYWU1ZS1hOGQwYmQ0MDVkNGQiLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3NjA2MjIzMzIsImlhdCI6MTc1OTkzMTEzMiwianRpIjoiMTkwZDUyNDEtMTBiMS00ZDZhLTg2NjgtYWI0YTU1Yjk0NmJiIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9.mNMR1mWX05eRtODOEbWzJHXJLPW6oVLcW09jsoE4mH9y67Cvoy56GvnuXqRkd6Ipi2oPSjyEyStp8iaEKa2JzQ; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkJSTCIsImN1cnJlbmN5U3ltYm9sIjoiUiQiLCJjb3VudHJ5Q29kZSI6IkJSQSIsImN1bHR1cmVJbmZvIjoicHQtQlIiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyJ9; xe_config=MUtSNTM3VjA5MCw2Q0E4NjBBQi1FQjU4LTk0RkYtRDczMC1FNzM0OTNBRDg4MjcsYWNhbGhvbWVjZW50ZXIuY29tLmJy; _gid=GA1.3.1181635280.1759931132; _clck=1oix5dy%5E2%5Efzz%5E0%5E2107; _tt_enable_cookie=1; _ttp=01K7213TG7AFZY22NYN9QM88G4_.tt.2; _pin_unauth=dWlkPVkyRmpaak00T1RZdE1tTmpOQzAwWWpZM0xUZzFPR010T0RRM1pXVTBNelZtTldWbA; cartstack.com-bwrid=MTIxNzA0Njg0; cookieconsent_status_RECOMMENDATION=ALLOW; cookieconsent_status_PERSONALIZATION=ALLOW; cookieconsent_status_TRACKING=ALLOW; cookieconsent_status_MARKETING=ALLOW; cookieconsent_status_EMAIL_MARKETING=ALLOW; cookieconsent_status_ESSENTIAL=ALLOW; cookieconsent_status_ANALYTICS=ALLOW; cookieconsent_status_UNCATEGORIZED=ALLOW; xe_cookieConsent-6CA860AB-EB58-94FF-D730-E73493AD8827=UkVDT01NRU5EQVRJT058UEVSU09OQUxJWkFUSU9OfFRSQUNLSU5HfE1BUktFVElOR3xFTUFJTF9NQVJLRVRJTkd8RVNTRU5USUFMfEFOQUxZVElDU3xVTkNBVEVHT1JJWkVE; _gat_UA-124280991-3=1; i18next=pt-BR; _clsk=1wxjt0f%5E1759932704322%5E5%5E1%5El.clarity.ms%2Fcollect; ttcsid=1759931132433::BKI3vhJYJSK8Gnhp7U_K.1.1759932704358.0; ttcsid_C83077OJVRJLR9PJHIK0=1759931132431::vH_fQvV0C0NHzwxYBQRZ.1.1759932704358.0; _ga=GA1.3.1398876731.1759931132; _ga_Z2HQXJ3SPJ=GS2.1.s1759931132$o1$g1$t1759932707$j53$l0$h0; cartstack.com-cart=MQ==; cartstack.com-cartid=NjA5Mjc3MTQz; CheckoutOrderFormOwnership=gS6UMG6QATweQ%2BX9XMhVK6r73XRiSSddNDQrcXhWny%2B2tjczaG9YNsgyF3TMg%2Bikd2XHW7Fk8Au%2Fjz5xUUsgmt75ckCB9bY288xkBmnIsvA%3D',
            "priority": "u=1, i",
            "referer": "https://www.acalhomecenter.com.br/checkout/",
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

        try:
            response = cls.post(
                "https://www.acalhomecenter.com.br/api/checkout/pub/orderForms/simulation",
                headers=headers,
                json=payload,
            )
            data = json.loads(response.content)

            for value in data["logisticsInfo"][0]["slas"]:
                if "Transportadora" in value["id"]:
                    prazo_frete = str(value["shippingEstimate"])
                    valor_frete = float(f"{value['price'] / 100.0:.2f}")
        except RequestException as e:
            logger.error(f"[AcalHomeCenter] Erro de rede ao buscar frete (CEP: {cep}): {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"[AcalHomeCenter] Erro ao extrair frete (CEP: {cep}): {e}")

        result = cls.build_result(
            valor_produto=valor_produto,
            valor_frete=valor_frete,
            prazo_frete=prazo_frete,
        )
        return cls.validate_result(result)
