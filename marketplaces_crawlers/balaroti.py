import json
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from modules.base_crawler import BaseCrawler

logger = logging.getLogger("crawlers")


class Balaroti(BaseCrawler):

    d_para_item = {
        "2020008": "337540",
        "1020080": ""
    }

    @classmethod
    def crawler(cls, url, cep, sku):
        prod_obj = {}

        try:
            soup = cls.get_soup(url)
            produtos = soup.find("script", {"type": "application/ld+json"}).string
            data = json.loads(produtos)
            prod_obj["valor_produto"] = float(data["offers"]["price"])
        except (RequestException, json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError) as e:
            logger.error(f"[Balaroti] Erro ao buscar preco: {e}")
            prod_obj["valor_produto"] = None

        payload = {
            "fileName": "page_cart_snippet.html",
            "queryName": "SnippetQueries/page_cart_with_shipping.graphql",
            "variables": {
                "checkoutId": "a81278d3-73cb-4349-b270-ff452b9258ec",
                "checkoutIdShipping": "a81278d3-73cb-4349-b270-ff452b9258ec",
                "hasCheckout": True,
                "cep": cep,
                "useSelectedAddress": False
            }
        }

        headers = {
            "cookie": 'VtexRCMacIdv7=d74b2304-3d67-4c4c-96ce-7556cbeba83b; _fbp=fb.2.1749754016950.25542291492433162; beon-customer-id=anon_d946651a-0233-4460-b476-64cdebe1f2d5; __kdtv=t%3D1749754017154%3Bi%3D017bdba41805df5b2385c275c1ae1bf41d4853fe; _kdt=%7B%22t%22%3A1749754017154%2C%22i%22%3A%22017bdba41805df5b2385c275c1ae1bf41d4853fe%22%7D; _pin_unauth=dWlkPVkyRmpaak00T1RZdE1tTmpOQzAwWWpZM0xUZzFPR010T0RRM1pXVTBNelZtTldWbA; AdoptVisitorId=KwNgnGAcIEyQtJAxgQwCbwCxMxlBmEBSGTABhhhDTCTGCA==; vtex-search-anonymous=a87be75322e14594bd09e215a8990613; vtex_binding_address=balaroti.myvtex.com/; nav_id=3be01c9b-d26f-494b-ab73-5d3deec1606b; legacy_p=3be01c9b-d26f-494b-ab73-5d3deec1606b; chaordic_browserId=3be01c9b-d26f-494b-ab73-5d3deec1606b; legacy_c=3be01c9b-d26f-494b-ab73-5d3deec1606b; legacy_s=3be01c9b-d26f-494b-ab73-5d3deec1606b; zipcode_info={"postalCode":"04011060","country":"BRA"}; checkout.vtex.com=__ofid=d4870d4ad48741fcbc2590ff4959e87d; CheckoutOrderFormOwnership=DaV6GWI+rx6z+zshEkbMKPejTiswmz/MpQnMLINDJ3mpwTNe6FVPz+51NYuHWjn2; _ga=GA1.1.1097990398.1749754018; _ad_token=xioyyvaash54bldwee0ug; __bid=cc6fdb95-9ef8-4477-86ff-a28875d57f31; smeventsclear_5e2480e7c62e45df9d10cad5150774ab=true; carrinho-id=a81278d3-73cb-4349-b270-ff452b9258ec; sf_storefront_access_token=tcs_balar_4e61440fe3d84744be0d8e52b74689b3; data-layer-visitor-id=VISIT-71f883ee-eb64-45b0-8b5f-c05c4eabac84; _gcl_au=1.1.280181920.1759341910; AdoptConsent=N4Ig7gpgRgzglgFwgSQCIgFwgBwBYAMEAbPgKwCGAtAOym2W4AmRUl2+AnBJY7kyRACMAY1IAzKCAA0IAG5x4CAPYAnZI0whSRDh2xEATNjbDyjBsKaVyAZiLHsBggYNFGHYR1LSQSgA4IyAB2ACrkAOYwmADaIEF+AJ4AUgCqNpQAMgCOANY+RACaAB4IMAAWAFY5fgASPgCiZTVKgsh+wjkpPgBeAGoIRFk2KQD6ADYAGj7hBjUJAEIVCADi2AU+jNRklqSsYtikHAykgrhsEPgGlMIQm/ingoxigpIyZaQArgBaBVkqYsIAIo+Dj4AByAHkOEFUAUwOEfBlZEEipQVKgylA/D5ioDZGUYABhGpJMo+F42UyEKgGchibh8QSkShQUi4K74ahQajYYRkajCKAGHx4mpjJLCMDdKAAdRAAF0ZP4EBCPggwpEYoqQMIlEEYBAgoENFhPmDqOQkj4ILJDeqEn4IJoEAAlADSgOojA9Pl1+rtvQgKngeswghkHz8jHISEYAEEEJoDJdmYJ8JROSFBAYMGmMJcAHTUQTYL4gAC+QA===; _clck=eq8iip%5E2%5Efzy%5E1%5E1989; _pk_ses.1614534.2010=*; wake_use_relative_graphql_url=true; sf_regional_cep=01050-050; sf_partner_access_token=sf_UxurOQY0RoeoX0AqLXZy2v0DB6U/BweLqf/8iREt8ZtW2KngI6J1w5Xr5MChOMce4/tqtOZ7hVeQsZ7xpQmdTausu+STDoqKYP981OAdyswQtXZPmHMKEneTRjtP7IYuiGaN0hHlU+WiiPx+lEVQpQ==; _ga_FN25LC0Q02=GS2.1.s1759839002$o12$g1$t1759839605$j60$l0$h0; _clsk=mp0olk%5E1759839606438%5E4%5E1%5El.clarity.ms%2Fcollect; _pk_id.1614534.2010=85c10f60beb9232d.1749754018.10.1759839608.1759839004.'
        }

        try:
            response = cls.post("https://www.balaroti.com.br/snippet", json=payload, headers=headers)
            soup_frete = BeautifulSoup(response.content, "html.parser")
            prod_obj["valor_frete"] = float(
                soup_frete.find("option", {"id": "37f0cc75-5c83-4caf-8852-d7285acb18f8"})["value"]
            )
        except (RequestException, TypeError, KeyError, ValueError, AttributeError) as e:
            logger.error(f"[Balaroti] Erro ao buscar frete: {e}")
            prod_obj.setdefault("valor_frete", None)

        result = cls.build_result(
            valor_produto=prod_obj.get("valor_produto"),
            valor_frete=prod_obj.get("valor_frete"),
            prazo_frete=prod_obj.get("prazo_frete")
        )
        return cls.validate_result(result)
