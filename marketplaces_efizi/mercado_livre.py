class MercadoLivre:
    def crawler(url, cep, sku, loja, dados_produtos):
        import os
        from pathlib import Path
        import sys
        import requests
        import re

        path = os.getenv('REPOSITORY_PRICE')
        # Seta o caminho da pasta que contém os modules
        sys.path.append(path)

        from modules.meli import Meli
        from modules.efizitools import Efizi

        channel = "Mercado_Livre"
        data = Efizi.d_para()
        product_id = data["MARKETPLACES"]["MERCADO_LIVRE"][sku]["product_id"]
        item_id = data["MARKETPLACES"]["MERCADO_LIVRE"][sku]["mlb"]
        

        google_sheets_id = "1eKOcnESAnVz-WuF3QbLyKQX0SjG-NFzZlcSFGXwUJLs"
        enviroment_path = os.getenv('REPOSITORY_PRODUCTION')
        credentials_google_sheets = Path(enviroment_path) / "credentials" / "service_account_google_sheets.json"

        prod_obj = {}

        token = Efizi.read_sheet(google_sheets_id, "access", credentials_google_sheets, range_data="A2")
        token = token.columns.to_list()[0]

        result = Meli.getProductData(token, product_id)
        prod_obj["valor_produto"] = float(result["results"][0]["price"])


        cookie_obj = {
            "_d2id": "67b9e3ab-fda7-41a9-b00a-1c2167e733d5",
            "_cq_duid": "1.1754060180.6EWn97zW7WSkGXUa",
            "ftid": "S2Ylqhsif8KW0MccB5D59E55INkgfzik-1754491247136",
            "ssid": "ghy-091710-bL7TfYvkoOsxdTmMPBFX9iS62Az5pu-__-214998910-__-1852815363422--RRR_0-RRR_0",
            "orguseridp": "2100411988",
            "orgnickp": "GP20241115155221",
            "sc-menu-hide-new-item_catalog_suggestions": "catalog_suggestions",
            "QSI_SI_d4ikElJeWDP7fzo_intercept": "true",
            "orguserid": "0Z0Td0dT00477",
            "c_home": "2.25.0",
            "cp":f"{cep.replace("-","")}",
            "c_ui-navigation": "6.6.152",
            "c_meliplus-plan-picker": "4.135.0-rc-3",
            "_csrf": "KeiyMuY6fwgzO0UGlR9hRDuo",
            "backend_dejavu_info": "j%3A%7B%7D",
            "_cq_suid": "1.1760538299.zMGfU5tN9nryo6gi",
            "_mldataSessionId": "5e15397b-b7ea-4955-94dd-36c1ec26bf46",
            "nsa_rotok": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjMiLCJ0eXAiOiJKV1QifQ.eyJpZGVudGlmaWVyIjoiOTAxN2E3OTItYjNkNi00ZjQ4LWIzMDItYTFiZmU4N2U1Zjk0Iiwicm90YXRpb25faWQiOiI1NDY1MDc5OS1lZTkxLTQ1OTEtOTBlYS0yMGFhMmFmOGY0OGEiLCJwbGF0Zm9ybSI6Ik1MIiwicm90YXRpb25fZGF0ZSI6MTc2MDYzNTk4NCwiZXhwIjoxNzYzMjI3Mzg0LCJqdGkiOiIxMjY3YmJjMy1mM2RhLTQwOGUtYjZiMi0wMmEzMDU2ZWQzNGIiLCJpYXQiOjE3NjA2MzUzODQsInN1YiI6IjkwMTdhNzkyLWIzZDYtNGY0OC1iMzAyLWExYmZlODdlNWY5NCJ9.h0Rh_yMeVtKX0k7dfYd0nfOv5_cBzrHgJoWGsyYA8oR70eQXmspee8mHOO_g-8MRab7iRgT8I5LpgdCJDg0_AF9uHdb3M3JIPiVuIF4BwnMDpa4k0Zzu74-QvO6e6GyxPWW5aHaaUolfxfmv8YJbDrKY-lyCz_v2D8exs5-NxV4cksOw9MEdWADaUQ-crnSwIu-Ix1CVXBHacPedrs8nDfUTfPory7n2-1qy7DDD1Mt_pPOR8pzU5hMJGfzcCrBl63hHNLmkidRFYbGMEIuTzLCYjUVp2rLIchRI7xYfYgIzKgy0apX3SDo5PEYsZlXXiaHQW5a2uEtAYcqyX3Ds1g",
            "device_force_view": "mobile",
            "c_vpp": "1.164.0",
            "__rtbh.uid": "%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%222100411988%22%2C%22expiryDate%22%3A%222026-10-16T17%3A23%3A45.593Z%22%7D",
            "__rtbh.lid": "%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22cIFGMCegIiYAfOARC1fc%22%2C%22expiryDate%22%3A%222026-10-16T17%3A23%3A45.593Z%22%7D",
            "cto_bundle": "PEaa-F9NamFPMTc1cFBjUDNhMEJ1UW1IN0VURk56REhvaElqTlklMkZkU1pLT0JCY2dLVVBvSjVTUk14cU0zMlhoNkY2VVglMkZObUhBanBQT3FqUnhkM0phcFFRYzJiRE8yVVdKQjdIcnNvTWduYzZaUWhvcFZhb2hTJTJCQzZGY0l4TmZWSlFDeHp6NFB0JTJGb3lLTFNKSFAyakE2SWpUN3F2dW5pdlB6OCUyRlB4YVdKOEJrckpNY1B4a2pDVElDMVVSZWxuNGNiMCUyRnk0b2c5WktjTmNQJTJGWlRZN2tQWDhxcGF5MTBCYnpVR1IwNXFQVWxyWGc0aXg0QklsYjlwUlJ4MXZxZDc0WDFEUyUyQjBZdzdFRFFYZ1NWU3VhNzJubThZcXclM0QlM0Q",
            "ttcsid_CFVSC2JC77U0ARCJTCJ0": "1760635413284::figlkJZRrkyjTYbFoSFB.52.1760635426341.0"
        }


        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

        response = requests.get(f"https://www.mercadolivre.com.br/gz/shipping-calculator?noIndex=true&item_id={item_id}&new_version=true&modal=true&informative=true&page_context=vpp&location=true&quantity=1&can_go_cart_checkout=true&modal=true", headers=headers,cookies=cookie_obj)
        try:
            match = re.search(r'"cost":\s*([\d.]+)', response.text)
            if match:
                prod_obj["valor_frete"] = float(match.group(1))

            match = re.search(r'"min_days":\s*([\d.]+)', response.text)
            if match:
                prod_obj["prazo_frete"] = str(match.group(1))
        except:
            prod_obj["disponibilidade"] = "CEP INDISPONIVEL"

        frete = Efizi.frete_mkt(int(cep.replace("-","")), sku, "tA3LZuqPH", dados_produtos, channel, prod_obj["valor_produto"])

        prod_obj["valor_frete_fr"] = float(frete[0]) if frete[0] != None else None
        prod_obj["prazo_frete_fr"] = frete[1] 

        return prod_obj


# https://www.mercadolivre.com.br/navigation/api/addresses-hub?modal=true&flow=true&go=https:%2F%2Fwww.mercadolivre.com.br%2Fgz%2Fshipping-calculator%3FnoIndex%3Dtrue%26item_id%3DMLB3520252854%26new_version%3Dtrue%26modal%3Dtrue%26informative%3Dtrue%26page_context%3Dvpp%26location%3Dtrue%26quantity%3D1%26can_go_cart_checkout%3Dtrue%26backFromPickerMobile%3Dtrue
#CEP INVALIDO







