class ViaVarejo:
    def crawler(url, cep, sku):
        import time
        import json
        import requests
        from bs4 import BeautifulSoup
        from modules.general import General
        from modules.efizitools import Efizi

        # channel = "Via_Varejo"

        prod_obj = {}

        d_para = Efizi.d_para()
        item_produto = d_para["MARKETPLACES"]["VIA_VAREJO"][sku]

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",

            "cookie": "_vwo_uuid_v2=D6F3B1B443B6F5DBE5B88E9D81612C723|f0c5caf1cdec83fc7828557391442c79; _evga_5c8d={%22uuid%22:%2226a7835211bc7976%22}; _sfid_9016={%22anonymousId%22:%2226a7835211bc7976%22%2C%22consents%22:[{%22consent%22:{%22purpose%22:%22Personalization%22%2C%22provider%22:%22Sitemap%22%2C%22status%22:%22Opt%20In%22}%2C%22lastUpdateTime%22:%222025-06-17T11:32:57.217Z%22%2C%22lastSentTime%22:%222025-06-17T11:32:57.220Z%22}]}; _gcl_au=1.1.1904403477.1750159978; cto_deduplication=other; _ga=GA1.1.1254087808.1750159979; _clck=16d8dwt%7C2%7Cfwu%7C0%7C1994; _tt_enable_cookie=1; _ttp=01JXYTKWEWAZ0ZN16WQAX5PYVR_.tt.2; _fbp=fb.2.1750159978983.856371550674207636; _uetvid=d20c8e104b6e11f08ba973df7c825ebb; _pin_unauth=dWlkPVkyRmpaak00T1RZdE1tTmpOQzAwWWpZM0xUZzFPR010T0RRM1pXVTBNelZtTldWbA; afUserId=399bc332-f1b9-4ec9-be72-65a1cb14edc7-p; __privaci_cookie_consent_uuid=d5fd7f15-a1f4-4f88-abbe-7bc2d0b81590:7; __privaci_cookie_consent_generated=d5fd7f15-a1f4-4f88-abbe-7bc2d0b81590:7; header-search-history=%5B%22biodigestor%22%5D; persistentSearchKeyword=biodigestor; IPI-CasasBahia=UsuarioGUID=f2abd1a2-9d6f-4727-bb97-1bb9e4902d60&cepClienteProvavel=; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222026-06-17T11%3A33%3A27.574Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%229wZpMoGgU59L5NpNpVUy%22%2C%22expiryDate%22%3A%222026-06-17T11%3A33%3A27.574Z%22%7D; ttcsid=1750159978978::YZHZkPbbc9wug0ud_fOa.1.1750160007626; cto_bundle=Yv9-hV9PSyUyRmtVVHczJTJCSWNla0VSUUNFRHFHUkEyb1ZFJTJCeHRQSWJwTklsYnlWUnhaM25sbGh3U0xBUUhhVnR4dGZOYVBTa0RSUHI4ZDFCS0t5b3BacndkSXYlMkJKVUt0SiUyRk9QSVZqempsaFFUTXJkRFI5cW9mSDFrSnZnbkgwd0RtUUM4JTJCUUZEQXJVV3UlMkZYUlFtbmNQJTJCdXZHbGtQSHRKamxmUEE2TkVFMjRqNnI1ZkZnZVNJelNJVXdsMk9XYzNmaHNHcncxMTZFblZtNmclMkJwdktoSGRwQXoySE13JTNEJTNE; ttcsid_C3FHO5PLLTKUJAC5B40G=1750159978975::lg0hbRctOr2-k7Pqerdg.1.1750160007969; _ga_SGTM=GS2.1.s1750159978$o1$g1$t1750160451$j60$l0$h1345677428; _ga_DPL4W0QCQ5=GS2.1.s1750159978$o1$g1$t1750160451$j60$l0$h0; GCB-TRACKING=45.162.22.108; ak_geo=SERRA::-20.12:-40.30:ES; bm_ss=ab8e18ef4e; _abck=EE7C56C8325E89E2AC3E05D0E3EAB10A~0~YAAQyGAXAgOkATaZAQAAR/wJOg535Hzkl961+t+68f2O1zX0d7RoiVaHgMJU3AUGWJ4+qw5rcB1ZEXQg+PYLR4av8ONKAlv5q8WSzcWnTjxkGKYcvuPYRqI0VaqQWfxOB3hw7SUKIk0GVUrqUspYcbVbDyffhuI6cRnZpedkFCPpx9sXLG8PkCw9mqhPB876WM57yKI8iHeC0t1ziH6f9r0Ac5b/wGu0oTlu9ckn7+VHoKkSZORowFyBCBlXgKqr5bgaUgLWZVc/AIEveLM0qUL1Dbe1MJe+0c4gIwrgvCL0NLkN48TPvyV+I9m3CSGUYmHp+t/8JBWlzbtKCHvcGo+wYx3Kwc9uMuzbeck5tRr2ahs02ZBwuiKXHHycn83P79SOtPQfevNeztbxZKPL90aWy62oKChfuLaXg6QmrtmvfdiCAhNcZSdyWyaTyFzuEHbgpOJLoRndeTEpe61wPEjsWB/jLSqEdpTePZCV8ZX95b3s3+jAdThZO6aKYufDYxOS4p3kn69x68LSf3+z8l4lWdT7TKeezUWevcgGBVpNGqpcf5j+fS6S+2rx7PjCfwoyZfruIbnh8IpIUoINnjMbmeIYdUDk9EfTNej7Z0P2zS9NKrdIljQD+T/2GT71qsqdm2cIDg+x5fXiN76XiZA9RFHWpUkE/WlnxheE~-1~-1~1754690111~-1~-1; ak_bmsc=6514B8345AFF1AA13B82222B4BFE4A88~000000000000000000000000000000~YAAQyGAXAgSkATaZAQAAR/wJOh2Tnt2b+cXL9QT3sDigrbgN8+fIGJt9vbFMoUPd3lNF28Nfw3n+jxJdjdG6LI2qdRY2jBc1aeR6cPfgs/37LFY5WW97Af/xWhHoS63wn5pLCTH/bsSRvZIfa4pdQ1UJNBxJLcG9gDuCI7m9ukf4rU8hHll/uy1ZBpspUZ5Y37UOpjrmOMOqB06fbLW8iIvk8depRgrZFCrj7ctMbGXYFrvoGv0zsnoAKBNoyyAqskOmv6gegLTdEICovtbMqyiwR3nI74emQdAWLad40UpZcF42iTRU8fU12aqShlhBE52gEiNe91Pm1mrWVEV4plJU934kFasD7CArQCuuBzVbPfSAuQ30wAyf0oFCfeJf0LX2IqlYhpjc; bm_so=728305FC56343E636D52D507B3B46CB6E06727D085125A35286C06E48EA8AB4C~YAAQyGAXAgekATaZAQAAR/wJOgR4xB13LTGjN6msXNhbh4r/ZjCIsPiAwbGESh7T8a8++tS2ya0n4wH6oYGmD2prgNDsUJfkugz7QJOD824y6zXKw/HBi9P4ASIpUUnc1FD6OdO+Ar7NEU6clAHm36lt2oIAAIgmWn4O+FiTxDQbCaYgjkik0xGyWhwvcxFprbFkb6WtI0qph9Nufo1LAzpKWt+nKjAZ8RkRp9Zogm47x1IEsDzC0XXlduX2in23BUiu3jCLeGXR1s9Unk6nkDhsdFJo5SzEpPGQTMAxTBGgDly23ZH1Ob++zQgfY2/92kOHyKWNcBcw56aavfondq90spP34MoEV3wjSW2m6dFLt2bw36M1xEsaurDv6BGWQnR+qiAU0mDr+3zPU3PI9LIGjbX+dj0l6+cduAzbwHGLA3kI8jcMtuB9FNNW4T2bIGcnaocOinquxBZ6v3L9oEGJiBco; bm_lso=728305FC56343E636D52D507B3B46CB6E06727D085125A35286C06E48EA8AB4C~YAAQyGAXAgekATaZAQAAR/wJOgR4xB13LTGjN6msXNhbh4r/ZjCIsPiAwbGESh7T8a8++tS2ya0n4wH6oYGmD2prgNDsUJfkugz7QJOD824y6zXKw/HBi9P4ASIpUUnc1FD6OdO+Ar7NEU6clAHm36lt2oIAAIgmWn4O+FiTxDQbCaYgjkik0xGyWhwvcxFprbFkb6WtI0qph9Nufo1LAzpKWt+nKjAZ8RkRp9Zogm47x1IEsDzC0XXlduX2in23BUiu3jCLeGXR1s9Unk6nkDhsdFJo5SzEpPGQTMAxTBGgDly23ZH1Ob++zQgfY2/92kOHyKWNcBcw56aavfondq90spP34MoEV3wjSW2m6dFLt2bw36M1xEsaurDv6BGWQnR+qiAU0mDr+3zPU3PI9LIGjbX+dj0l6+cduAzbwHGLA3kI8jcMtuB9FNNW4T2bIGcnaocOinquxBZ6v3L9oEGJiBco^1757615356547; bm_sv=C8A9DAA89C7FBEDF87E9A71AE3EC779A~YAAQyGAXAkulATaZAQAANgIKOh2WiJedgDyAC1JQPI6y5hUWZ0bAnrQp3s5pRHmivejE/pDcOh/jPT9w+fx+YNBl3lHERyK5R7FzWgoEV6VOYEtJop+e/kqIZcQf85okcvMLF+QfhnUODyYQEGedYhsDuQQyh7qOLa7ZquZviqYpMZa7zWYgz7fMynaC0NyTYwUK4L1AxIqXr3wKEgnzTj2fMORn0YIQw+kXtK18mDlQXl0hLWzdjkBFm0GrZf/npx5OPlrfNg==~1; bm_sz=7FB0412C5680B9795BDD3FD9C4DABEA3~YAAQyGAXAkylATaZAQAANgIKOh0HA1ojHomcmZ9K91QAph6Rixh3JIGLiWWxq37XvELlTSlWHGNl9NtkznTlGXlinco0xf4tcZF0UZP9AItJr3DIGweCKY1wtLm14HpEl0/WByOMj5oVJtfXagGapqRKsHWcYGXQtEiVgjQHtKgVnk8aYhvrcND6uNCAPeNop7gafSuKwmQ7onRU+NbY/idVDagEJBY0Gs0z/0Sw7tL7clHxeyPECoBF/MsVLMMAq0fmpPsnv+sI7HbJEX+h1EbN83eKHwxexjoTgwrr2tRiN+Nvi9yzTfXM2cEatlmxhs1Cor9dKWPRJCi+dGOHCFYq3MIN5Bt66GwFBvr1OHLdxVjA7io0b23BslRh2L1ZeEGp/IxHnJe+aBTbGFWuv9O+KlNT69L7MA==~4536130~3356210; akavpau_wwwcasasbahia=1757615659~id=40c7c6e3ed09eec2dfc2dc3fd33d891e; bm_s=YAAQyGAXAtKlATaZAQAAwQYKOgRnpVbKQpMXhWbzWjRdBncUxuUIoguOmXr4WwwSFhj6a66y1EMC/HQACPovEU01cDWVJOdcuuCIm09TOrw875zAsfE3Xv4Sbfm6cFdZ6Z7b5p4X6IW9Cr3pZJRvKVVyXGUCjtl+YBi2IXqa6X7B9fpVdIMRapcvSB1zEuiYlKpnriTNDqM6zboNSTwj1nq41XPeRVN2RDeEJZy203l4I7kfWzqTcIGphBDh0RnRxefCpsdivTaZSjE65rHsvj3mt4GvnxZZrM2mFkdxWzmisggRt9laGMqloCUGFbVeJg9wdC8QAJcLhEYRy1fwu56qOXABbXlzlOijyRFcGJnju8lLMPcBzjt8eEbpC9TEDoFF1rNc9GCNtqNsVSyBdclrKfj/jJoFb4jCRCSXje7GWZKyKcFDFvyYM+dHFpKI9diCCwrIDiYiWiAz/079IYcx8CgoQc6G8EufGUUt2Z8y9LoUz4qbDRLcuy4JtZTroz1mBGFYALHqVOtViLM5RNTcQc3z1FiMaL8ITASYCUT+uN/4Bu+dVkhTo2bQydXrRPcgKxuSJmQBtQuMdw==; bm_sc=2~1~53723222~YAAQyGAXAtOlATaZAQAAwQYKOgWtnFfR5yiCxYisXhqYymQRUDEhkIJvd9gVWi+0jYKVso5u0G+p0gWNmI8w8CjMXNpqXfF/3nxdaxpF1/ycSeGEqMkxa8fzPnSdmF/Rc+myGZw81LkB4Ymbc86nIR6idse8/7s16l1b0qRYHVvtFmJknvTpqClJDlysj/16gum0E8QVyRbhxC32ALa6ubD2WpMH+++QNnwZPlbGM+n57SzPDTqZHZQoXGPfy1LGYMeHzsIXlL78aiMpjmnM5gBpjw0XR09ueperjnmNMAZ8oI4yEQ5cz21l+9rDQTJuyQvI8G0X5KRUXQ82cw3piCLe7jXSPcV9guwhjx84jzVUWMUyLnF6psE73R6VajoCqyE9s/UEOGGCXHFspgw+ZRo769sj2+jLR8zjfa91pwolRaphvI3gAB4Dif2CFgctGOcP2tlfzgeo2JCxyxeLqf606jVaRv6N76SjMsyIu5Cu4nw4Mvpp/d/ChgkJ9UthjCpxPL0nSyzTdoRoxEBOt2ZR1fPbw0fe0SUQSr/qbRl1bRdt7aEVuQ3Vjg==",

            "referer": url,
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

        response_product = requests.get(url, headers=headers).content

        soup = BeautifulSoup(response_product, "html.parser")
        product_data = soup.find("script", {"id": "schemaLdJson", "type": "application/ld+json"}).text
        product_data = json.loads(product_data)

        prod_obj["valor_produto"] = product_data["offers"][0]["price"]

        response_freight = requests.get(f'https://pdp-api.casasbahia.com.br/api/v2/sku/{item_produto}/freight/seller/61597/zipcode/{cep}/source/CB?channel=DESKTOP&orderby=price', headers=headers).json()

        prod_obj["valor_frete"] = response_freight["options"][0]["price"]
        prod_obj["prazo_frete"] = str(response_freight["options"][0]["deadline"])

        print(prod_obj)
        return prod_obj
    