import sys 
from pathlib import Path
import traceback
import os
path = os.getenv('REPOSITORY_PRICE')
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

import time
import json
from modules.logging_config import setup_logging
setup_logging()

from modules.general import General
from modules.efizitools import Efizi
from marketplaces_crawlers.ferpam import Ferpam
from marketplaces_crawlers.jl_meurer import Jl_meurer
from marketplaces_efizi.mercado_livre import MercadoLivre
from marketplaces_efizi.via_varejo import ViaVarejo
from marketplaces_efizi.magalu import Magalu
from marketplaces_efizi.quero_quero import QueroQuero
from marketplaces_efizi.carrefour import Carrefour
from marketplaces_efizi.madeiramadeira import MadeiraMadeira
from marketplaces_crawlers.leroy_merlin import Leroy

# Credenciais
credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")

states_list = ["TO"]
region_products = Efizi.get_bigquery(f'select * from bi.produtos_sites where estado in ({str(states_list)[1:-1]})', "efizi-analises", credentials)
data_product = Efizi.get_bigquery("select sku, altura, categoria, largura, comprimento, peso from bi.categoria_fr", "efizi-analises", credentials)

crawlers_dict = {
    "CARREFOUR": Carrefour,
    "EFIZI VIA VAREJO": ViaVarejo,
    "LEROY MERLIN": Leroy,
    "EFIZI MADEIRA MADEIRA": MadeiraMadeira,
    "EFIZI MAGALU": Magalu,
    "EFIZI MERCADO LIVRE": MercadoLivre,
    # "EFIZI QUERO QUERO": QueroQuero,
    "FERPAM": Ferpam,
    "JL MEURER": Jl_meurer
}

for state in states_list:
    try:
        # Busca produtos do Estado
        competitors_state = region_products[(region_products["ESTADO"] == state)]
        list_prices = []

        for index, row in competitors_state.iterrows():
            try:
                prod_obj = {}

                if "LEROY MERLIN" in row["LOJA"]:
                    prod_obj = crawlers_dict["LEROY MERLIN"].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"])
                if "CARREFOUR" in row["LOJA"]:
                    prod_obj = crawlers_dict["CARREFOUR"].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "MERCADO LIVRE" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "MAGALU" in row["LOJA"]:
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
        General.send_to_database(list_prices)
    except Exception as e:
        General.send_email_error(state, str(e))