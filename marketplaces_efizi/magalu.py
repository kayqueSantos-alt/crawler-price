class Magalu:
    def crawler(url, cep, sku, loja, data_product):
        import json
        import requests
        import cloudscraper
        from bs4 import BeautifulSoup
        from datetime import datetime, timedelta
        from modules.efizitools import Efizi

        # data e hora atual
        hoje = datetime.now()
        # trigésimo próximo dia
        dia_30 = hoje+timedelta(days=30)
        # converter para timestamp em milissegundos
        timestamp_30d_ms = int(dia_30.timestamp() * 1000)
        timestamp_hj_ms = int(hoje.timestamp() * 1000)

        channel = "Magalu"

        prod_obj = {}

        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.52 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.171 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.76 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.35 Safari/537.36",
        ]

        for user_agent in user_agent_list:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
                "cookie": f'pdp_desk_b2c_mixer=1; __ssds=3; _vwo_uuid_v2=DD23F670A2C2419F6384DE05659A0B68D|ce882fa81df6d30e2f09fb2ef91128bd; _tt_enable_cookie=1; _ttp=01JQ6HPVCQQGCK63Y88M5D0DN5_.tt.2; _vwo_uuid=DD23F670A2C2419F6384DE05659A0B68D; __ssuzjsr3=a9be0cd8e; __uzmaj3=3bf8f5b5-d0ae-4aa6-a4df-f30e12eda696; ml_tid=f55d545f-8e7e-4cf6-87dc-27f319114d20; stwu=temp_42eb5719-7786-4377-83bd-c498f089a3be; stwt=1; __bid=630b4c44-e34f-4905-9765-ecc95f435d78; _fbp=fb.2.1742902883837.93047746842950995; _ga=GA1.1.727136666.1742902884; _pin_unauth=dWlkPVkyRmpaak00T1RZdE1tTmpOQzAwWWpZM0xUZzFPR010T0RRM1pXVTBNelZtTldWbA; _hjSessionUser_4936838=eyJpZCI6ImJhNmQxMDM5LWEzMTctNTI0YS05NjI4LWIwOTliMmU5ZGE5MCIsImNyZWF0ZWQiOjE3NDI5MDI4ODQwMTcsImV4aXN0aW5nIjp0cnVlfQ==; __spdt=29826508698a46f58c0f7ce4d877cbee; __uzma=4c922683-75da-49a4-a043-1e494c23b79f; __uzmb=1754671543; __uzme=9363; _gcl_gs=2.1.k1$i1754671542$u134098578; _gcl_au=1.1.1763702385.1754671545; _gcl_aw=GCL.1754671546.CjwKCAjwwNbEBhBpEiwAFYLtGNs0V68acQEXDmNUX0WRX_Wm91YjrbprWGogYpAhVtjuUUZsrtr4cBoCzyUQAvD_BwE; _gcl_dc=GCL.1754671546.CjwKCAjwwNbEBhBpEiwAFYLtGNs0V68acQEXDmNUX0WRX_Wm91YjrbprWGogYpAhVtjuUUZsrtr4cBoCzyUQAvD_BwE; _ga_C98RVP2QRJ=GS2.1.s1754671547$o5$g1$t1754671599$j8$l0$h0; noe_freight=AUTO; noe_hub_shipping_enabled=1; toggle_wishlist=false; show_seller_score_above=5; FCCDCF=1; ml2_redirect_8020=0; FCNEC=1; mixer_shipping=AUTO; mixer_hub_shipping=true; toggle_pdp_seller_score=true; toggle_vwo=true; toggle_agatha=true; toggle_ads=true; toggle_new_service_page=true; toggle_quick_click=false; enable_fallback_banner=0; MLPARCEIRO=0; _vwo_ds=3%241757679756%3A52.90989698%3A%3A; _vis_opt_s=5%7C; _vis_opt_test_cookie=1; _clck=l8pmkt%5E2%5Efz9%5E0%5E1910; _azfp_sc=757320def85c21bd5a46fb682336ad62bce39cb2adb238f5fe0099e068937ecd; toggle_offer_timer=true; toggle_enable_product_review=true; page_before_login=produto; __gtm_referrer=https%3A%2F%2Fvalidate.perfdrive.com%2F; _hjSession_4936838=eyJpZCI6IjQ3ZDFhYmM0LWQ0MGMtNDdjZC05ZDhiLWVlMThiZjZiMTNkYyIsImMiOjE3NTc2ODUwODQ1NDEsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; storedSessionIdLCJ5VBTH8V=s1757685085%24o7%24g0%24t1757685085%24j60%24l0%24h0; GTMUtmTimestamp={timestamp_hj_ms}; GTMUtmSource=validate.perfdrive.com; GTMUtmMedium=referral; GTMIsTrueDirect=1; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22WYMu5HVrrhAvCUNabdWY%22%2C%22expiryDate%22%3A%222026-09-12T14%3A22%3A14.495Z%22%7D; __uzmbj3={timestamp_30d_ms}; __uzmcj3=6598420821278; __uzmdj3={timestamp_30d_ms}; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222026-09-12T14%3A22%3A15.469Z%22%7D; _ga_LCJ5VBTH8V=GS2.1.s1757685085$o7$g1$t{timestamp_30d_ms}$j60$l0$h0; _vwo_sn=5328%3A60; cto_bundle=aa8Gnl9TN2pMd1NTcEdoUDVKVFpacnZaJTJCJTJCYjcxUGRqUkN3dDlhMlU5UnM2R1hWT2cyU1AwbHVoVmhESEVWUGNvdFBlUVp2JTJCSERLQlJ6WEVxRUxQY0NicHlQUzFZbVlLa3RGZThRbU1GQVJOVmpvQjJEZ2FBTFVOR0d1b1hQZW4lMkZrdWFNOEZnUnlMajF5Qjg1Qnd6T2M0QUptTjZFQ0FQdW9zakMwaEdmbjY4TjNyJTJGM0xnTzM5NnV4czNYYnNBeW9RN0MzZWtubzczbXg2aUlWT3U2clQ5YWZRdUhtUW0lMkJxR3podVRUSUh2QmhEUWh4SGdpUWh5ZWM3TlpnWiUyRlJvakhmZnRrNFZha0I0Z0k2OEl4ZUVndjZvQjRnJTNEJTNE; _uetsid=2b19e1808fd311f0ba773fb07f28b984; _uetvid=14291160096e11f0863967f54fc036e3; ttcsid={timestamp_30d_ms}::fLXTddgtzmAe657P0ifT.5.{timestamp_30d_ms}; __uzmc=4419831910120; __uzmd=1757686936; ttcsid_C1I87V1T0U322RQPSRKG=1757685084573::WoONPABJ7q49B7H1Cry6.5.{timestamp_30d_ms}; _clsk=fthtq4%5E1757686936423%5E45%5E0%5El.clarity.ms%2Fcollect; _dd_s=rum=0&expire={timestamp_30d_ms}',
                "if-none-match": "io1awqybq3vz1k",
                "priority": "u=0, i",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": user_agent
            }

            try:
                response = requests.get(url, headers=headers, timeout=10).content
                soup = BeautifulSoup(response,"html.parser")
                prod = soup.find("script", {"id":"__NEXT_DATA__", "type":"application/json"})
                break
            except:
                continue
        data = json.loads(prod.string)

        prod_obj["valor_produto"] = float(data["props"]["pageProps"]["data"]["item"]["offers"][0]["price"])

        frete = Efizi.frete_mkt(int(cep.replace("-","")), sku, "rbcguutgb", data_product ,channel, prod_obj["valor_produto"])
        prod_obj["valor_frete_fr"] = frete[0]
        prod_obj["prazo_frete_fr"] = frete[1]
        
        dims = data["props"]["pageProps"]["data"]["item"].get("dimensions", {})
        height = dims.get("height")
        length = dims.get("depth")
        weight =  dims.get("weight")
        width = dims.get("width")

        payload = {
            "operationName":"shippingQuery",
            "variables":{
                "shippingRequest":{
                    "metadata":{
                        "categoryId":"CJ",
                        "clientId":"",
                        "organizationId":"magazine_luiza",
                        "pageName":"",
                        "partnerId":"0",
                        "salesChannelId":"45",
                        "sellerId":"efiziazu",
                        "sellerName":"Efizi Azu",
                        "subcategoryId":"CXDA"
                    },
                    "product":{
                        "dimensions":{
                            "height":height,
                            "length":length,
                            "weight":weight,
                            "width":width
                        },
                        "id":f"0{sku}",
                        "price":prod_obj["valor_produto"],
                        "quantity":1,
                        "type":"product"
                    },
                    "zipcode":str(cep).replace("-","")
                    }
                },
            "query":"fragment estimateError on EstimateErrorResponse {\n  error\n  status\n  message\n  uuid\n  __typename\n}\n\nfragment shippings on ShippingResponse {\n  status\n  shippings {\n    id\n    packages {\n      deliveryTypes {\n        id\n        description\n        type\n        time\n        price\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment estimate on EstimateResponse {\n  disclaimers {\n    sequence\n    message\n    __typename\n  }\n  deliveries {\n    closenessGroup {\n      id\n      __typename\n    }\n    id\n    status {\n      code\n      __typename\n    }\n    modalities {\n      id\n      type\n      name\n      shippingTime {\n        unit\n        value {\n          min\n          max\n          __typename\n        }\n        description\n        disclaimers {\n          sequence\n          message\n          __typename\n        }\n        __typename\n      }\n      cost {\n        customer\n        __typename\n      }\n      prices {\n        customer\n        operation\n        currency\n        exchangeRate\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  closenessGroups {\n    customerCost\n    disclaimer\n    id\n    items {\n      seller {\n        id\n        sku\n        __typename\n      }\n      __typename\n    }\n    name\n    operationCost\n    slug\n    shortPolicy\n    target\n    targetRemaining\n    __typename\n  }\n  status\n  __typename\n}\n\nquery shippingQuery($shippingRequest: ShippingRequest!) {\n  shipping(shippingRequest: $shippingRequest) {\n    status\n    ...shippings\n    ...estimate\n    ...estimateError\n    __typename\n  }\n}"
        }
        response = requests.post("https://federation.magazineluiza.com.br/graphql", json=payload, headers=headers).json()
        try:
            prod_obj["valor_frete"] = float(response["data"]["shipping"]["deliveries"][0]["modalities"][0]["cost"]["customer"])
            prod_obj["prazo_frete"] = str(response["data"]["shipping"]["deliveries"][0]["modalities"][0]["shippingTime"]["value"]["max"])
        except:
            if "Frete indispon" in response["errors"][0]["message"]:
                prod_obj["disponibilidade"] = "CEP INDISPONIVEL"


        print(prod_obj)
        return prod_obj