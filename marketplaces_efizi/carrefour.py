class Carrefour:  
    def crawler(url, cep, sku, loja, data_product):
        import json
        import requests
        from bs4 import BeautifulSoup
        from modules.efizitools import Efizi
        
        channel = "Carrefour"
        
        seller = "2697"
        if loja == "COPAFER CARREFOUR":
            seller = "31777"
            
        prod_obj = {}

        response_product = requests.get(url).content

        soup = BeautifulSoup(response_product, "html.parser")
        product_data = soup.find("script", {"type": "application/ld+json"}).text
        product_data = json.loads(product_data)

        prod_obj["valor_produto"] = float(product_data["offers"]["price"])

        body_json = {"items":[{"id":f"0{sku}","quantity":1,"seller":seller}], "postalcode":cep}
        resp_frieght = requests.post("https://api3.carrefour.com.br/cci/publico/cci-digitalcomm-marketplace-in/pvt/orderForms/simulation", json=body_json).json()
        try:
            prod_obj["valor_frete"] = float(resp_frieght["logisticsInfo"][0]["slas"][0]["price"]/100)
            prod_obj["prazo_frete"] = str(resp_frieght["logisticsInfo"][0]["slas"][0]["shippingEstimate"])
        except:
            if resp_frieght["logisticsInfo"][0]["slas"]== []:
                prod_obj["disponibilidade"] = "CEP INDISPONIVEL"
                
        if "EFIZI" in loja:
            frete = Efizi.frete_mkt(int(cep.replace("-","")), sku, "YtUnKrhPs", data_product,channel ,prod_obj["valor_produto"])
            prod_obj["valor_frete_fr"] = frete[0]
            prod_obj["prazo_frete_fr"] = f"{frete[1]} days" 
    
        print(prod_obj)
        return prod_obj            

