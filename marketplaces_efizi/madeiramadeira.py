class MadeiraMadeira:
    def crawler(url, cep, sku):
        import cloudscraper
        from datetime import datetime
        from modules.efizitools import Efizi

        data = Efizi.d_para()
        produto_id = data["MARKETPLACES"]["MADEIRA_MADEIRA"][sku]

        scrapper = cloudscraper.create_scraper()

        prod_obj = {}
        
        response_freight = scrapper.get(f'https://www.madeiramadeira.com.br/api/freight/{produto_id}?zipCode={cep.replace("-", "")}&seller=8284&quantity=1').json()
        for data_prices in response_freight["buyBox"]:
            saller_name = data_prices["seller"]["name"].strip().lower()
            if "efizi" in saller_name:
                prod_obj["valor_produto"] = float(data_prices["price"]["total"])
                try:
                    prod_obj["valor_frete"] = data_prices["shipping"][0]["shipping"]["price"]
            
                    data_dia = datetime.strptime(data_prices["shipping"][0]["estimatedDelivery"]["max"], '%Y-%m-%d')
                    prod_obj["prazo_frete"] = str((data_dia - datetime.now()).days)
                except:
                    if "Desculpe, não entregamos para esta região." == data_prices["shipping"][0]["comment"]:
                        prod_obj["disponibilidade"] = "CEP INDISPONIVEL"
        print(prod_obj)
        return prod_obj