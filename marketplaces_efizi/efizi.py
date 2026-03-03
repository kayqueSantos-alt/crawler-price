class EfiziEcommerce:
    def crawler(url, loja, sku, nome_produto):
        import json
        import time
        import requests
        from bs4 import BeautifulSoup
        from selenium import webdriver

        prod_list = []

        d_para_region = {
            "Acre": "Norte",
            "Alagoas": "Nordeste",
            "Amapá": "Norte",
            "Amazonas": "Norte",
            "Bahia": "Nordeste",
            "Ceará": "Nordeste",
            "Distrito Federal": "Centro-Oeste",
            "Espírito Santo": "Sudeste",
            "Goiás": "Centro-Oeste",
            "Maranhão": "Nordeste",
            "Mato Grosso": "Centro-Oeste",
            "Mato Grosso do Sul": "Centro-Oeste",
            "Minas Gerais": "Sudeste",
            "Pará": "Norte",
            "Paraíba": "Nordeste",
            "Paraná": "Sul",
            "Pernambuco": "Nordeste",
            "Piauí": "Nordeste",
            "Rio de Janeiro": "Sudeste",
            "Rio Grande do Norte": "Nordeste",
            "Rio Grande do Sul": "Sul",
            "Rondônia": "Norte",
            "Roraima": "Norte",
            "Santa Catarina": "Sul",
            "São Paulo - Grande SP": "Sudeste",
            "São Paulo - Interior": "Sudeste",
            "Sergipe": "Nordeste",
            "Tocantins": "Norte"
        }


        d_para_cep = {
            "Acre": "69921-695",
            "Alagoas": "57010-003",
            "Amapá": "68906-535",
            "Amazonas": "69082-440",
            "Bahia": "45600-485",
            "Ceará": "60060-090",
            "Distrito Federal": "70050-000",
            "Espírito Santo": "29010-004",
            "Goiás": "74805-145",
            "Maranhão": "65042-686",
            "Mato Grosso": "78005-050",
            "Mato Grosso do Sul": "79002-002",
            "Minas Gerais": "30110-008",
            "Pará": "68447-000",
            "Paraíba": "58013-370",
            "Paraná": "85805-540",
            "Pernambuco": "51130-020",
            "Piauí": "64014-055",
            "Rio de Janeiro": "22793-100",
            "Rio Grande do Norte": "59063-400",
            "Rio Grande do Sul": "90040-320",
            "Rondônia": "76800-000",
            "Roraima": "69312-660",
            "Santa Catarina": "88010-002",
            "São Paulo - Grande SP": "01310-930",  
            "São Paulo - Interior": "12020-365",
            "Sergipe": "49072-000",
            "Tocantins": "77015-000"
        }

        d_para_sigla = {
            "Acre": "AC",
            "Alagoas": "AL",
            "Amapá": "AP",
            "Amazonas": "AM",
            "Bahia": "BA",
            "Ceará": "CE",
            "Distrito Federal": "DF",
            "Espírito Santo": "ES",
            "Goiás": "GO",
            "Maranhão": "MA",
            "Mato Grosso": "MT",
            "Mato Grosso do Sul": "MS",
            "Minas Gerais": "MG",
            "Pará": "PA",
            "Paraíba": "PB",
            "Paraná": "PR",
            "Pernambuco": "PE",
            "Piauí": "PI",
            "Rio de Janeiro": "RJ",
            "Rio Grande do Norte": "RN",
            "Rio Grande do Sul": "RS",
            "Rondônia": "RO",
            "Roraima": "RR",
            "Santa Catarina": "SC",
            "São Paulo - Grande SP": "SP_CAPITAL",
            "São Paulo - Interior": "SP_INTERIOR",
            "Sergipe": "SE",
            "Tocantins": "TO"
        }


        prod_obj = {}

        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        produto = soup.find("input", {"id": "current-prices-by-regions"})

        value_str = produto.get("value")
        precos = json.loads(value_str)

        driver.quit()

        for i in precos:
            if i["price"] == None:
                continue
            i["price"]= float(f'{i["price"]/100:.2f}'.replace(",", "X").replace(".", ",").replace("X", ".").replace(",", "."))

            prod_obj["produto"] = nome_produto
            prod_obj["estado"] = d_para_sigla[i["regionName"]]
            prod_obj["regiao"] = d_para_region[i["regionName"]]
            prod_obj["loja"] = loja
            prod_obj["link"] = url
            prod_obj["sku"] = sku
            prod_obj["valor_produto"] = i["price"]

            headers_freight = {
                "Cookie": "localization=BR; _shopify_y=c499467e-3557-477e-ba2e-635aaad4ce5e; _tracking_consent=3.AMPS_BRES_f_f_9pceJvuvSBycRj7vtjs1TA; _orig_referrer=; _clck=1jhplq0%5E2%5Efyo%5E0%5E2060; _fbp=fb.2.1755880625228.644758958273997457; _gcl_au=1.1.1213023615.1755880625; xe_config=MTI0RUJPVTA5MCw2MzgxRTA1RS0xRUE5LUE1QkMtRERBRS00NDg2REQ5ODUxQTAsZWZpemkuY29tLmJy; rdtrk=%7B%22id%22%3A%2254c228e9-95e3-467b-af08-c2d94098f388%22%7D; xe_visitor=eyJpZCI6IjhiNzgyNjM0LTVkOTQtNDkxOC05ODI1LWU5OTgzMTQzYmI3MCIsImVtYWlsIjoiIn0=; rdtrk=%7B%22id%22%3A%2254c228e9-95e3-467b-af08-c2d94098f388%22%7D; _shopify_s=5941a9ca-27b9-4efd-aa5e-4d6db4b8e1b4; _ga_2H7S3WF0TS=GS2.1.s1755880625$o1$g1$t1755880874$j60$l0$h2019953909; __trf.src=encoded_eyJmaXJzdF9zZXNzaW9uIjp7InZhbHVlIjoiKG5vbmUpIiwiZXh0cmFfcGFyYW1zIjp7fX0sImN1cnJlbnRfc2Vzc2lvbiI6eyJ2YWx1ZSI6Iihub25lKSIsImV4dHJhX3BhcmFtcyI6e319LCJjcmVhdGVkX2F0IjoxNzU1ODgwODc0NTI5fQ==; _clsk=14lywo2%5E1755880874775%5E8%5E1%5El.clarity.ms%2Fcollect; cart_currency=BRL; keep_alive=eyJ2IjoyLCJ0cyI6MTc1NTg4MDg5MzgwOSwiZW52Ijp7IndkIjowLCJ1YSI6MSwiY3YiOjEsImJyIjoxfSwiYmh2Ijp7Im1hIjoyMCwiY2EiOjEsImthIjoyLCJzYSI6Miwia2JhIjowLCJ0YSI6MCwidCI6MjAsIm5tIjoxLCJtcyI6MC42MywibWoiOjAuNDgsIm1zcCI6MC40NywidmMiOjAsImNwIjowLCJyYyI6MCwia2oiOjAsImtpIjowLCJzcyI6MCwic2oiOjAsInNzbSI6MCwic3AiOjAsInRzIjowLCJ0aiI6MCwidHAiOjAsInRzbSI6MH0sInNlcyI6eyJwIjo0LCJzIjoxNzU1ODgwNjI0NDgwLCJkIjoyNjZ9fQ%3D%3D; cart=hWN26HRXnsbxMJ5ldKxz3VJK%3Fkey%3D6ef5b829e7488fdacdefbf109a44979e; _shopify_essential=:AZjSpBInAAEA0rYieEj_ulhCA0oBlVfn7Si4QrS4jeVaNytx_HaG-JnPRQcu_sV6mcWKc2bXbzGHngCycgjCByK39CWyebV2K1WVlusKZXoe9omnRLVn6EpK2nr-CfzqgWs:"
            }

            if d_para_cep[i["regionName"]] != "":

                region_to_search = i["regionName"]
                if region_to_search in ("São Paulo - Grande SP", "São Paulo - Interior"):
                    region_to_search = "São Paulo"

                try:
                    response = requests.get(f'https://efizi.com.br/cart/shipping_rates.json?shipping_address%5Bcountry%5D=Brazil&shipping_address%5Bprovince%5D={region_to_search.replace(" ", "+")}&shipping_address%5Bzip%5D={d_para_cep[i["regionName"]]}', headers=headers_freight)
                    prod_obj["valor_frete"] = float(response.json()["shipping_rates"][0]["price"])
                    prod_obj["prazo_frete"] = str(response.json()["shipping_rates"][0]["delivery_days"][0])
                except:
                    if response.json()["shipping_rates"] == []:
                        prod_obj["disponibilidade"] = "CEP INDISPONIVEL"
                    
                prod_obj["cep"] = d_para_cep[i["regionName"]]
                    
            prod_list.append(prod_obj.copy())

        return prod_list
