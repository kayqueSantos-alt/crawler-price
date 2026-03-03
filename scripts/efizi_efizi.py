import sys 
from pathlib import Path
import os
path = os.getenv('REPOSITORY_PRICE')
# Seta o caminho da pasta que contém os modules
sys.path.append(path)

import json
from modules.logging_config import setup_logging
setup_logging()

from modules.general import General
from modules.efizitools import Efizi
from marketplaces_efizi.efizi import EfiziEcommerce

# Credenciais
credentials_bi = Efizi.get_credentials("CREDENTIALS_BI")
credentials_bi = json.loads(credentials_bi)

prices_links_efizi = Efizi.read_sheet("1LjbYLnyVU_kn8zqwa7lw1Wh_DbFhyaHWBxFbpzF2-kI", "EFZ", path+"/credentials/service_account_google_sheets.json")
for index, row in prices_links_efizi.iterrows():
    try:
        if row["LOJA"] == "EFIZI":
            efizi_prices = EfiziEcommerce.crawler(row["LINK"], row["LOJA"], row["SKU"], row["PRODUTO"])
        General.send_to_database(efizi_prices)
    except Exception as e:
        tb = sys.exc_info()[2]
        lineno = tb.tb_lineno
        Efizi.send_email(
            credentials_bi["email"],
            credentials_bi["password"],
            "ti@efizi.com.br",
            "[ERRO] PREÇOS EFIZI",
            f"""
                Houve erro no seguinte passo:
                Loja: {row["LOJA"]}
                Sku: {row["SKU"]}
                Link: {row["LINK"]}
                Erro na linha: {lineno}
                {str(e)}
            """,
            "plain"
        )
