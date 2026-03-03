import sys 
from pathlib import Path
import os
path = os.getenv('REPOSITORY_PRICE')
from datetime import date
hoje = date.today()
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

import json
from pandas import DataFrame
from modules.logging_config import setup_logging
setup_logging()

from modules.general import General
from modules.efizitools import Efizi
from marketplaces_efizi.carrefour import Carrefour
from marketplaces_efizi.madeiramadeira import MadeiraMadeira
from marketplaces_efizi.magalu import Magalu
from marketplaces_efizi.mercado_livre import MercadoLivre
from marketplaces_efizi.quero_quero import QueroQuero
from marketplaces_efizi.via_varejo import ViaVarejo
from marketplaces_crawlers.leroy_merlin import Leroy
from datetime import datetime

credentials_google = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")
data_product = Efizi.get_bigquery("select sku, altura, categoria, largura, comprimento, peso from bi.categoria_fr", "efizi-analises", credentials_google)

states_list = ["TO"]

crawlers_dict = {
    # "EFIZI VIA VAREJO": ViaVarejo,
    "EFIZI CARREFOUR": Carrefour,
    "EFIZI LEROY MERLIN": Leroy,
    "EFIZI MAGALU": Magalu,
    "EFIZI MERCADO LIVRE": MercadoLivre,
    # "EFIZI QUERO QUERO": QueroQuero,
    "EFIZI MADEIRA MADEIRA": MadeiraMadeira
}

hoje = datetime.now().strftime("%Y-%m-%d")
region_products = Efizi.get_bigquery(f"select LOJA, LINK, SKU, PRODUTO, CEP, ESTADO from bi.produtos_sites where LOJA in ({str(list(crawlers_dict.keys()))[1:-1]}) and LOJA not in ('EFIZI VIA VAREJO', 'EFIZI CARREFOUR')","efizi-analises", credentials_google)

for state in states_list:
    try:
        # Busca produtos do Estado
        competitors_state = region_products[(region_products["ESTADO"] == state)]

        list_prices = []
        for index, row in competitors_state.iterrows():
            try:
                prod_obj = {}

                if row["LOJA"] == "EFIZI LEROY MERLIN":
                    prod_obj = crawlers_dict["EFIZI LEROY MERLIN"].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"])
                elif "CARREFOUR" in row["LOJA"]:
                    prod_obj = crawlers_dict["CARREFOUR"].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "MERCADO LIVRE" in row["LOJA"] or "MAGALU" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif row["LOJA"] in crawlers_dict:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], row["CEP"], row["SKU"])

                prod_obj["cep"] = row["CEP"]
                prod_obj["estado"] = state
                prod_obj["loja"] = row["LOJA"]
                prod_obj["link"] = row["LINK"]
                prod_obj["sku"] = row["SKU"]
                prod_obj["produto"] = row["PRODUTO"]

                list_prices.append(prod_obj.copy())

            except Exception as e:
                General.send_email_error(state, str(e), row["CEP"], row["LOJA"], row["SKU"], row["LINK"])

        lojas = list({obj["loja"] for obj in list_prices})
        data = DataFrame(list_prices)

        Efizi.get_bigquery(
            f"delete from bi.precos_produtos_sites where estado in ({str(list(data["estado"].unique()))[1:-1]}) and dia = '{hoje}' and loja in ({str(lojas)[1:-1]})",
            "efizi-analises",
            credentials_google
        )

        General.send_to_database(list_prices)
    except Exception as e:
        General.send_email_error(state, str(e))

