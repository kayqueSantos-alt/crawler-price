import requests
from datetime import datetime
from pathlib import Path
import os
import sys
import json
path = os.getenv('REPOSITORY_PRICE')
sys.path.append(path)
from modules.efizitools import Efizi
import pandas as pd

credentials_bi = Efizi.get_credentials("CREDENTIALS_BI")
credentials_bi = json.loads(credentials_bi)

try:
    google_sheets_id = "1eKOcnESAnVz-WuF3QbLyKQX0SjG-NFzZlcSFGXwUJLs"
    enviroment_path = os.getenv('REPOSITORY_PRODUCTION')
    credentials_google_sheets = Path(enviroment_path) / "credentials" / "service_account_google_sheets.json"

    CLIENT_ID = "4853712245807904"
    CLIENT_SECRET = "hkoHwVD7qkbpMbJzPpNfekps3TUoSA8i"

    df_code = Efizi.read_sheet(google_sheets_id, "code", credentials_google_sheets, range_data="C2")
    acess_token_old = df_code.columns.to_list()[0]

    Efizi.write_sheet(google_sheets_id, "code", credentials_google_sheets, df = pd.DataFrame([["Efizi", acess_token_old]], columns=["conta", "refresh_antigo"]))

    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": acess_token_old
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    resposta = requests.post(url, data=payload, headers=headers)
    retorno = resposta.text
    json_resposta = resposta.json()

    access_token = json_resposta["access_token"]
    refresh_token = json_resposta["refresh_token"]


    Efizi.write_sheet(google_sheets_id, "access", credentials_google_sheets, df=pd.DataFrame([[access_token]], columns=["acess"]))

    data = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")

    df_update_code = pd.DataFrame(
    [["Efizi", "", refresh_token, data, hora, retorno]],
    columns=["conta", "refresh_antigo", "refresh_novo", "data", "hora", "bruto"]
    )

    Efizi.write_sheet(google_sheets_id, "code", credentials_google_sheets, df=df_update_code)
except:
    Efizi.send_email(credentials_bi["email"], credentials_bi["password"], "ti@efizi.com.br", f"[ERRO] REFRESH TOKEN", "plain")