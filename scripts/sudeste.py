import sys
from pathlib import Path
import json
import os
import traceback
import time
import pandas as pd

path = os.getenv('REPOSITORY_PRICE')
sys.path.append(path)

from modules.logging_config import setup_logging
setup_logging()

from modules.general import General
# ... (seus imports dos crawlers permanecem iguais)
from marketplaces_crawlers.sodimac import Sodimac
from marketplaces_crawlers.baba_materiais import BabaMateriais
from marketplaces_crawlers.obramax import Obramax
from marketplaces_crawlers.padovani import Padovani
from marketplaces_crawlers.leroy_merlin import Leroy
from marketplaces_crawlers.casa_mattos import CasaMattos
from marketplaces_crawlers.cacique import Cacique
from marketplaces_crawlers.amoedo import Amoedo
from marketplaces_crawlers.chatuba import Chatuba
from marketplaces_crawlers.baratao_construcao import Baratao
from marketplaces_crawlers.bremenkamp import Bremenkamp
from modules.efizitools import Efizi
from marketplaces_crawlers.constru_shop import ConstruShop
from marketplaces_crawlers.vila_telhas import VilaTelhas
from marketplaces_crawlers.construbel import Construbel
from marketplaces_crawlers.balaroti import Balaroti
from marketplaces_crawlers.hidraulico_tropeiro import Tropeiro
from marketplaces_crawlers.lojas_pedrao import LojasPedrao
from marketplaces_crawlers.guemat import Guemat
from marketplaces_crawlers.casa_mimosa import CasaMimosa
from marketplaces_crawlers.carajas import Carajas
from marketplaces_efizi.mercado_livre import MercadoLivre
from marketplaces_efizi.via_varejo import ViaVarejo
from marketplaces_efizi.magalu import Magalu
from marketplaces_efizi.quero_quero import QueroQuero
from marketplaces_efizi.carrefour import Carrefour
from marketplaces_efizi.madeiramadeira import MadeiraMadeira
from marketplaces_crawlers.copafer import Copafer

# Credenciais
credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")

states_list = ["SP", "MG", "RJ", "ES"]

# 1. Carrega os produtos
region_products = Efizi.get_bigquery(f'select * from bi.produtos_sites where estado in ({str(states_list)[1:-1]})', "efizi-analises", credentials)

# 2. Carrega a tabela de CEPs
ceps_df = Efizi.get_bigquery("select UF, LOCALIDADE, CEP from bi.ceps", "efizi-analises", credentials)

data_product = Efizi.get_bigquery("select sku, altura, categoria, largura, comprimento, peso from bi.categoria_fr", "efizi-analises", credentials)

crawlers_dict = {
    "AMOEDO": Amoedo,
    "BABA MATERIAIS": BabaMateriais,
    "BALAROTI": Balaroti,
    "BARATÃO DA CONSTRUÇÃO": Baratao,
    "BREMENKAMP": Bremenkamp,
    "CACIQUE HOME CENTER": Cacique,
    "CARREFOUR": Carrefour,
    "CASA MATTOS": CasaMattos,
    "CASA MIMOSA": CasaMimosa,
    "CHATUBA": Chatuba,
    "CONSTRUBEL": Construbel,
    # "CONSTRUSHOP": ConstruShop,
    "COPAFER": Copafer,
    "EFIZI MADEIRA MADEIRA": MadeiraMadeira,
    "EFIZI MAGALU": Magalu,
    "EFIZI MERCADO LIVRE": MercadoLivre,
    # "EFIZI QUERO QUERO": QueroQuero,
    # "EFIZI VIA VAREJO": ViaVarejo,
    "GUEMAT": Guemat,
    "LEROY MERLIN": Leroy,
    "LOJAS PEDRAO": LojasPedrao,
    "OBRAMAX": Obramax,
    "PADOVANI": Padovani,
    "SODIMAC": Sodimac,
    "TROPEIRO": Tropeiro,
    "VILA TELHAS": VilaTelhas,
}

for state in states_list:
    try: # <--- DESCOMENTADO: Protege o loop dos estados
        
        # --- LÓGICA DO CEP ---
        ceps_do_estado = ceps_df[ceps_df["UF"] == state]
        
        if ceps_do_estado.empty:
            print(f"Nenhum CEP encontrado na tabela bi.ceps para o estado {state}")
            continue 

        cep_para_consulta = str(ceps_do_estado.iloc[0]['CEP']).replace("-", "").strip()
        # ---------------------

        competitors_state = region_products[(region_products["ESTADO"] == state)]
        list_prices = []
        
        print(f"\n====== INICIANDO ESTADO {state} (CEP: {cep_para_consulta}) ======")

        for index, row in competitors_state.iterrows():
            try: # <--- DESCOMENTADO: Essencial para não parar o loop de produtos
                prod_obj = {}
                
                if "LEROY MERLIN" in row["LOJA"]:
                    prod_obj = crawlers_dict["LEROY MERLIN"].crawler(row["LINK"], cep_para_consulta, row["SKU"], row["LOJA"])
                elif "CARREFOUR" in row["LOJA"]:
                    prod_obj = crawlers_dict["CARREFOUR"].crawler(row["LINK"], cep_para_consulta, row["SKU"], row["LOJA"], data_product)
                elif "MERCADO LIVRE" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], cep_para_consulta, row["SKU"], row["LOJA"], data_product)
                elif "MAGALU" in row["LOJA"]:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], cep_para_consulta, row["SKU"], row["LOJA"], data_product)
                elif row["LOJA"] in crawlers_dict:
                    prod_obj = crawlers_dict[row["LOJA"]].crawler(row["LINK"], cep_para_consulta, row["SKU"])

                prod_obj["cep"] = cep_para_consulta 
                prod_obj["estado"] = state
                prod_obj["loja"] = row["LOJA"]
                prod_obj["link"] = row["LINK"]
                prod_obj["sku"] = row["SKU"]
                prod_obj["produto"] = row["PRODUTO"]

                # PRINT DE SUCESSO (VERDE)
                print(f"\n--- SUCESSO: {row['LOJA']} ---")
                print(json.dumps(prod_obj, indent=4, ensure_ascii=False))
                print("-" * 30)

                list_prices.append(prod_obj.copy())

            except Exception as e:
                # --- AQUI ESTA A MAGICA PARA NÃO QUEBRAR E MOSTRAR O ERRO ---
                
                error_msg = str(e)
                # Pega o nome do erro (ex: AttributeError)
                error_type = type(e).__name__ 

                error_obj = {
                    "STATUS": "ERRO FATAL NO ITEM",
                    "LOJA": row["LOJA"],
                    "SKU": row["SKU"],
                    "TIPO_ERRO": error_type,
                    "MENSAGEM": error_msg,
                    "CEP_USADO": cep_para_consulta,
                    "LINK": row["LINK"]
                }
                
                # PRINT DE ERRO (VERMELHO/ALERTA)
                print(f"\n>>> ERRO AO PROCESSAR: {row['LOJA']} <<<")
                print(json.dumps(error_obj, indent=4, ensure_ascii=False))
                print(">>> CONTINUANDO PROXIMO ITEM... <<<")
                print("-" * 30)

                # Mantém o envio de email se desejar
                General.send_email_error(state, str(e), cep_para_consulta, row["LOJA"], row["SKU"], row["LINK"])
        
        # Envia para o banco o que conseguiu coletar nesse estado
        if list_prices:
            General.send_to_database(list_prices)
            print(f"Dados salvos no banco para {state}.")

    except Exception as e:
        print(f"ERRO CRÍTICO NO ESTADO {state}: {str(e)}")
        General.send_email_error(state, str(e))