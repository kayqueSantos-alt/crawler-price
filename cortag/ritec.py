class Ritec:
  def crawlyn(url, cep, sku):
        import requests
        import httpx
        from bs4 import BeautifulSoup

        prod_obj = {}

        response = requests.get(url).content
        soup = BeautifulSoup(response, "html.parser")
        div_price = soup.find("div", {"class":"data-itemscope"})
        data_price = div_price.get_text(strip=True)
        prod_obj["valor_produto"] = float(str(data_price).replace("R$",""))

        dimension = soup.find("div",{"class":"product-dimension offset-top-34"})
        texto = dimension.find_all("div")[0].get_text(separator="|", strip=True)

        dados = {}

        for item in texto.split("|"):
            chave, valor = item.split(":")
            dados[chave.strip().lower()] = valor.strip()

        peso = dados.get("peso").replace("kg","").replace(".","").replace(",",".")
        altura = dados.get("altura").replace("cm","").replace(".","").replace(",",".")
        largura = dados.get("largura").replace("cm","").replace(".","").replace(",",".")
        comprimento = dados.get("comprimento").replace("cm","").replace(".","").replace(",",".")

        params = {
            "postcode": "29161-716",
            "product_id": 3129,
            "model": 1085263,
            "weight":peso,
            "width": largura,
            "height": altura,
            "length": comprimento,
            "days_stock": 0,
            "price": prod_obj["valor_produto"],
            "price_without_currency": valor,
            "product_special_price": "",
            "price_special_type": "",
            "special_percent": "",
            "special_payment_method": "",
            "quantity_product": 1,
            "product_option_value_id_size": 0,
            "form[option[3134]]": 3544,
            "form[product_id]": 3129
        }  
        
        response_frete = requests.post("https://www.ritec.com.br/index.php?route=module/shipping/simulate",data=params).json()

        for frete, data_fright in response_frete["shipping_method"].items():
            if "RETIRE EM NOSSO DEPOSITO" in frete:
                continue
            data_fright = data_fright
            quote = next(iter(data_fright["quote"].values()))
            prod_obj["valor_frete"] = quote["cost"]
            prod_obj["prazo_frete"] = quote["days_delivery_time"]
            break

        return prod_obj
