import sys
from pathlib import Path
import json
import os
path = os.getenv('REPOSITORY_PRICE')
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

import numpy as np
import json
import os
from modules.general import General
from modules.efizitools import Efizi
from dutra_maquinas import Dutra_maquinas

# # Credenciais
credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")



data_prod = Efizi.read_sheet("1S3Cs-ZrWOGcMzgWjr-ofAyEVciOoK37Rj3C_jAQdl-I", "dados", path+"/credentials/service_account_google_sheets.json")
ceps = Efizi.read_sheet("1S3Cs-ZrWOGcMzgWjr-ofAyEVciOoK37Rj3C_jAQdl-I", "cep", path+"/credentials/service_account_google_sheets.json")

# PRODUTO/LOJA/LINK/SKU/REGIAO_ATUACAO
crawlers_dict ={
    "DUTRA MATERIAL": Dutra_maquinas
}

for _, values_prod in data_prod.iterrows():

    regiao_atuacao = str(values_prod["REGIAO_ATUACAO"]).upper().strip()

    for _, values_cep in ceps.iterrows():

        uf_cep = str(values_cep["UF"]).upper().strip()
        local_cep = str(values_cep["LOCALIDADE"]).upper().strip()

        usar_cep = False
        if "TODAS" in regiao_atuacao:
            usar_cep = True

        else:
            regioes = regiao_atuacao.replace(",", ";").split(";")

            for reg in regioes:
                reg = reg.strip()

                if reg == uf_cep:
                    usar_cep = True
                    break

        if not usar_cep:
            continue
        nome_loja = str(values_prod["LOJA"]).upper().strip()

        if nome_loja not in crawlers_dict:
            continue

        prod_obj = crawlers_dict[nome_loja].crawler(
            values_prod["URL"],
            values_cep["CEP"],
            values_cep["UF"]
        )

        print(prod_obj)
