
import sys
from pathlib import Path
import json
path = str(Path(Path.cwd()))
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

import threading, time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from marketplaces_crawlers.constrular_facil import Constrular_facil
from marketplaces_crawlers.todimo import Todimo
from marketplaces_crawlers.serpal import Serpal
from marketplaces_crawlers.campeao_da_construcao import Campeao_da_construcao
from marketplaces_crawlers.castelo_forte import Castelo_forte
from marketplaces_crawlers.wanderson_materiais import WandersonMateriais
from marketplaces_crawlers.sertao import Sertao
from marketplaces_crawlers.leroy_merlin import Leroy
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
from marketplaces_crawlers.leroy_merlin import Leroy
from marketplaces_crawlers.casas_da_agua import Casas_da_agua
from marketplaces_crawlers.quevedo import Quevedo
from marketplaces_crawlers.taqi import Taqi
from marketplaces_crawlers.redemac import Redemac
from marketplaces_crawlers.bigolin import Bigolin
from marketplaces_crawlers.panorama import Panorama
from marketplaces_crawlers.leroy_merlin import Leroy
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
from marketplaces_crawlers.baba_materiais import BabaMateriais
from marketplaces_crawlers.constru_shop import ConstruShop
from marketplaces_crawlers.vila_telhas import VilaTelhas
from marketplaces_crawlers.construbel import Construbel
from marketplaces_crawlers.balaroti import Balaroti
from marketplaces_crawlers.hidraulico_tropeiro import Tropeiro
from marketplaces_crawlers.lojas_pedrao import LojasPedrao
from marketplaces_crawlers.guemat import Guemat
from marketplaces_crawlers.casa_mimosa import CasaMimosa
from marketplaces_crawlers.ferpam import Ferpam
from marketplaces_crawlers.jl_meurer import Jl_meurer
from modules.general import General

shop_chooser = {
    "ACAL_HOME_CENTER": AcalHomeCenter,
    "AFP_CONSTRUCAO": AFP,
    "AMOEDO": Amoedo,
    "BABA_MATERIAIS": BabaMateriais,
    "BALAROTI": Balaroti,
    "BARATAO_DA_CONSTRUCAO": Baratao,
    "BIGOLIN": Bigolin,
    "BREMENKAMP": Bremenkamp,
    "CACIQUE_HOME_CENTER": Cacique,
    "CAMPEAO_DA_CONSTRUCAO": Campeao_da_construcao,
    "CARAJAS": Carajas,
    "CASA_FACIL_CONSTRUCAO": CasaMaisFacil,
    "CASA_MATTOS": CasaMattos,
    "CASA_MIMOSA": CasaMimosa,
    "CASAS_DA_AGUA": Casas_da_agua,
    "CASTELO_FORTE": Castelo_forte,
    "CHATUBA": Chatuba,
    "CONSTRUBEL": Construbel,
    "CONSTRULAR_FACIL": Constrular_facil,
    "CONSTRUSHOP": ConstruShop,
    "ENGECOPI": Engecopi,
    "FERPAM": Ferpam,
    "FERREIRA_COSTA": FerreiraCosta,
    "GUEMAT": Guemat,
    "JL_MEURER": Jl_meurer,
    "LEROY_MERLIN": Leroy,
    "LOJAS_PEDRAO": LojasPedrao,
    "NORMATEL": Normatel,
    "OBRAMAX": Obramax,
    "PADOVANI": Padovani,
    "PANORAMA": Panorama,
    "PARAIBA_HOME_CENTER": ParaibaHomeCenter,
    "PISOLAR": Pisolar,
    "POTIGUAR": Potiguar,
    "QUEVEDO": Quevedo,
    "REDEMAC": Redemac,
    "SERPAL": Serpal,
    "SERTAO": Sertao,
    "SODIMAC": Sodimac,
    "TAQI": Taqi,
    "TODIMO": Todimo,
    "TROPEIRO": Tropeiro,
    "VILA_TELHAS": VilaTelhas,
    "WANDERSON_MATERIAIS": WandersonMateriais
}


d_para_region = {
    "AC": "Norte",
    "AL": "Nordeste",
    "AP": "Norte",
    "AM": "Norte",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "ES": "Sudeste",
    "GO": "Centro-Oeste",
    "MA": "Nordeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MG": "Sudeste",
    "PA": "Norte",
    "PB": "Nordeste",
    "PR": "Sul",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RJ": "Sudeste",
    "RN": "Nordeste",
    "RS": "Sul",
    "RO": "Norte",
    "RR": "Norte",
    "SC": "Sul",
    "SP": "Sudeste",
    "SE": "Nordeste",
    "TO": "Norte"
}

app = Flask(__name__)
CORS(app) 

@app.route("/crud", methods=["GET"])
def crud():
    credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")
    items = Efizi.get_bigquery("select * from bi.produtos_sites", "efizi-analises", credentials)
    items["SKU"] = items["SKU"].str.zfill(8)
    items = json.loads(items.to_json(orient="records", indent=2, force_ascii=False))
    return render_template("tabela.html", items=items, lojas=sorted({produto["LOJA"] for produto in items}))


@app.route("/edit_product", methods=["POST"])
def edit_product():
    from controller.edit_product import edit_product
    try:
        data = request.get_json()

        original_produto = data.get("original").get("PRODUTO")
        original_sku = data.get("original").get("SKU")
        original_link = data.get("original").get("LINK")
        original_loja = data.get("original").get("LOJA")
        original_cep = data.get("original").get("CEP")
        original_estado = data.get("original").get("ESTADO")

        new_produto = data.get("new").get("PRODUTO")
        new_sku = data.get("new").get("SKU")
        new_link = data.get("new").get("LINK")
        new_loja = data.get("new").get("LOJA")
        new_cep = data.get("new").get("CEP")
        new_estado = data.get("new").get("ESTADO")

        if None in [original_produto, original_sku, original_link, original_loja, original_cep, original_estado]:
            return jsonify({"msg": "O produto não pode ter dados nulos."}), 400

        if None in [new_produto, new_sku, new_link, new_loja, new_cep, new_estado]:
            return jsonify({"msg": "O produto não pode ter dados nulos."}), 400

        result_response = edit_product(data["original"], data["new"])
        return jsonify({"msg": result_response["msg"]}), result_response["code"]

    except Exception as e:
        return jsonify({"msg": str(e)}), 400


@app.route("/delete_product", methods=["POST"])
def delete_product():
    from controller.delete_product import delete_product
    try:
        data = request.get_json()

        sku = data.get("SKU")
        loja = data.get("LOJA")
        cep = data.get("CEP")
        estado = data.get("ESTADO")

        if None in [sku, loja, cep, estado]:
            return jsonify({"msg": "O produto não pode ter dados nulos."}), 400

        result_response = delete_product(data)
        return jsonify({"msg": result_response["msg"]}), result_response["code"]

    except Exception as e:
        return jsonify({"msg": str(e)}), 400


@app.route("/add_product", methods=["POST"])
def add_product():
    from controller.add_product import add_product
    try:
        # print(request.remote_addr)
        data = request.get_json()

        produto = data.get("PRODUTO")
        sku = data.get("SKU")
        link = data.get("LINK")
        loja = data.get("LOJA")
        cep = data.get("CEP")
        estado = data.get("ESTADO")

        if None in [produto, sku, link, loja, cep, estado]:
            return jsonify({"msg": "O produto não pode ter dados nulos."}), 400

        result_response = add_product(data)
        return jsonify({"msg": result_response["msg"]}), result_response["code"]

    except Exception as e:
        return jsonify({"msg": str(e)}), 400




@app.route("/execute")
def execute():
    loja = request.args.get("loja")
    estado = request.args.get("estado")

    credentials_bi = Efizi.get_credentials("CREDENTIALS_BI")
    credentials_bi = json.loads(credentials_bi)

    if not loja or not estado:
        return jsonify({"erro": "Uma loja e um estado devem ser informados."}), 400
    else:

        try:
            # Le planilha do estado
            competitors_state = Efizi.read_sheet("1LjbYLnyVU_kn8zqwa7lw1Wh_DbFhyaHWBxFbpzF2-kI", estado, path+"/credentials/service_account_google_sheets.json")
            competitors_state = competitors_state[(competitors_state["LOJA"].str.replace(" ", "_").replace("Á", "A").replace("Ã", "A").replace("Ç", "C") == loja)]

            if competitors_state.empty:
                return jsonify({"error": "Não existem registros dessa loja neste estado"}), 400

            list_prices = []

            for index, row in competitors_state.iterrows():
                try:
                    prod_obj = None

                    loja_class = shop_chooser[loja]
                    prod_obj = loja_class.crawler(row["LINK"], row["CEP"], row["SKU"], row["PRODUTO"], estado, d_para_region[estado])

                    if prod_obj != None:
                        list_prices.append(prod_obj.copy())

                except Exception as e:
                    return jsonify({"erro": str(e)}), 400

            General.send_to_database(list_prices)
            return jsonify({"sucess": "Processo finalizado"}), 200


        except Exception as e:
            return jsonify({"erro": str(e)}), 400












if __name__ == "__main__":
    # debug=True → recarrega automaticamente em desenvolvimento
    app.run(host="0.0.0.0", port=5000, debug=True)