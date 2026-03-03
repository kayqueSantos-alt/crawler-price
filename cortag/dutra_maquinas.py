class Dutra_maquinas:     
    def crawler(url, cep, uf):    
        import requests
        from bs4 import BeautifulSoup
        import re

        prod_obj = {}

        produtct_id = "168637"
        response = requests.get(url).content
        soup = BeautifulSoup(response, "html.parser")
        div_price = soup.find("div", {"class":"ou-sem-juros"})
        data_price = div_price.get_text(strip=True).replace("R$","").replace(" ", "").replace(",",".")
        prod_obj["valor_produto"]= float(data_price)
        
        resposne_frete = requests.get(
            f"https://www.dutramaquinas.com.br/model/md_calcula_frete.php?id={produtct_id}&cep={cep}&quantidade=1"
        ).content

        soup_frete = BeautifulSoup(resposne_frete, "html.parser")
        linha_barata = soup_frete.select_one("span.valor-menor")

        if linha_barata:
            data_valor = linha_barata.get_text(strip=True)
            prod_obj["valor_frete"] = float(
                data_valor.replace("R$", "").replace(".", "").replace(",", ".")
            )

            data_prazo = linha_barata.find_parent("tr").select("span")[1].get_text(strip=True)
            prod_obj["prazo_frete"] = re.findall(r"\d+", data_prazo)[-1]

        else:
            linha_rapida = soup_frete.select_one("span.valor")

            data_valor = linha_rapida.get_text(strip=True)
            prod_obj["valor_frete"] = float(
                data_valor.replace("R$", "").replace(".", "").replace(",", ".")
            )

            data_prazo = linha_rapida.find_parent("tr").select("span")[1].get_text(strip=True)
            prod_obj["prazo_frete"] = "".join(filter(str.isdigit, data_prazo))


        # resposne_frete = requests.get(f"https://www.dutramaquinas.com.br/model/md_calcula_frete.php?id={produtct_id}&cep={cep}&quantidade=1").content
        # soup_frete = BeautifulSoup(resposne_frete, "html.parser")
        # div_prazo = soup_frete.find("span", {"class":"prazo"})
        # data_prazo = div_prazo.get_text(strip=True)
        # prod_obj["prazo_frete"] = re.findall(r'\d+', data_prazo)[-1]


        # div_frete = soup_frete.find("span", {"class":"valor-menor"})
        # prod_obj["valor_frete"] = float(div_frete.get_text(strip=True).replace("R$","").replace(" ", "").replace(",","."))

        prod_obj["estado"] = uf
        prod_obj["cep"] = cep
        return prod_obj