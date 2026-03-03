import json

from pathlib import Path
import sys
import os
path = os.getenv('REPOSITORY_PRICE')
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

from modules.general import General
from modules.efizitools import Efizi
from marketplaces_crawlers.carajas import Carajas
from marketplaces_crawlers.casamaisfacil import CasaMaisFacil
from marketplaces_crawlers.paraibaHomeCenter import ParaibaHomeCenter
from marketplaces_crawlers.ferreira_costa import FerreiraCosta
from marketplaces_crawlers.potiguar import Potiguar
from marketplaces_crawlers.pisolar import Pisolar
from marketplaces_crawlers.acal_home_center import AcalHomeCenter
from marketplaces_crawlers.engecopi import Engecopi
from marketplaces_crawlers.veneza import Veneza
# from marketplaces_crawlers.lojas2001 import Lojas2001
from marketplaces_crawlers.afp import AFP
from marketplaces_crawlers.normatel import Normatel
from marketplaces_crawlers.leroy_merlin import Leroy
from marketplaces_efizi.mercado_livre import MercadoLivre
from marketplaces_efizi.via_varejo import ViaVarejo
from marketplaces_efizi.magalu import Magalu
from marketplaces_efizi.quero_quero import QueroQuero
from marketplaces_efizi.carrefour import Carrefour
from marketplaces_efizi.madeiramadeira import MadeiraMadeira

# Credenciais
credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")
states_list= ["PI", "PE", "AL"]
region_products = Efizi.get_bigquery(f'select * from bi.produtos_sites where estado in ({str(states_list)[1:-1]})', "efizi-analises", credentials)
data_product = Efizi.get_bigquery("select sku, altura, categoria, largura, comprimento, peso from bi.categoria_fr", "efizi-analises", credentials)

crawlers_dict = {
    "ACAL HOME CENTER": AcalHomeCenter,
    "AFP CONSTRUCAO": AFP,
    "CARAJÁS": Carajas,
    "CARREFOUR": Carrefour,
    "CASA FACIL CONSTRUÇÃO": CasaMaisFacil,
    "EFIZI MADEIRA MADEIRA": MadeiraMadeira,
    "EFIZI MAGALU": Magalu,
    "EFIZI MERCADO LIVRE": MercadoLivre,
    # "EFIZI QUERO QUERO": QueroQuero,
    # "EFIZI VIA VAREJO": ViaVarejo, 
    "ENGECOPI": Engecopi,
    "FERREIRA COSTA": FerreiraCosta,
    "LEROY MERLIN": Leroy,
    # "LOJAS 2001":
    "NORMATEL": Normatel,
    "PARAIBA HOME CENTER": ParaibaHomeCenter,
    "PISOLAR": Pisolar,
    "POTIGUAR": Potiguar,
    "VENEZA": Veneza
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
                elif "CARREFOUR" in row["LOJA"]:
                    prod_obj = crawlers_dict["CARREFOUR"].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "MERCADO LIVRE" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "MAGALU" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], row["CEP"], row["SKU"], row["LOJA"], data_product)
                elif "FERREIRA COSTA" in row["LOJA"]:
                    prod_obj = crawlers_dict["FERREIRA COSTA"].crawler(row["LINK"], row["CEP"], row["SKU"], row["ESTADO"])
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
                continue
        General.send_to_database(list_prices)
    except Exception as e:
        General.send_email_error(state, str(e))
        continue