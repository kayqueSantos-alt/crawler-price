# DEPRECATED: Este crawler esta desativado e nao e usado em producao.
class g_haus:
    def crawnly(url, cep, sku, produto, estado):
        loja = "G-Haus"
        import sys 
        import os
        path = os.getenv('REPOSITORY_PRICE')
        # Seta o caminho da pasta que contém os modules
        sys.path.append(path)
        from modules.crawler_settings import Crawler

        url = "https://www.g-haus.com.br/biodigestor-max-700l-dia-preto-polietileno-fortlev/p"
        # https://www.g-haus.com.br/tanque-de-polietileno-com-tampa-de-rosca-verde-fortlev/p
        url_frieght = "https://www.g-haus.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ed5041cd-630b-4f1c-867a-1537436e4965&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%220b86bf8e1dd01c1b55ece6b383de192d5047eba4faf48f887232c901e57d53a6%22%2C%22sender%22%3A%22ghaus.custom-shipping-simulator%403.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%22%7D"
        
        prod_obj = {}
        cep = "93950-000"
        sku = "01020055"
        d_para_produtos ={
            "01020055":"135674"      
        }

        try:
            data_price = Crawler.request_pattern_price(url)
            prod_obj["valor_produto"] = data_price["offers"]["offers"][0]["price"]
        except:
            prod_obj["valor_produto"] = None
        try:
            data_frieght = Crawler.requests_pattern_freight(cep,d_para_produtos[sku], url_frieght)
            prod_obj["valor_frete"] = data_frieght["price"]
            prod_obj["prazo_frete"] = data_frieght["shippingEstimate"]    
        except:
            prod_obj["valor_frete"] = None
            prod_obj["prazo_frete"] = None


        prod_obj = Crawler.datas(cep=cep, estado=estado, loja=loja, url=url, sku=sku, produto=produto)


        return prod_obj