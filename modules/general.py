class General:

    def price_treatment(price):
        import re
        price_to_convert = price.replace("R$", "").replace(".", "").replace(",", ".").replace(" ", "")
        price_to_convert = re.sub(r'[a-zA-Z]', '', price_to_convert)
        try:
            return float(price_to_convert)
        except:
            return None


    def send_to_database(data):
            from datetime import datetime
            from modules.efizitools import Efizi
            from pandas import DataFrame
            import re

            credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")
            data = DataFrame(data)
            data["dia"] = str(datetime.now().date())
            data["sku"] = data["sku"].str.zfill(8)

            data.loc[data["cep"].isin([
                "13310-161",    # Itu
                "13308-096",    # Itu
                "14050-050",    # Ribeirão Preto
                "14095-180",    # Ribeirão Preto
                "13400-050",    # Piracicaba
                "18190-000"     # Araçoiaba da Serra
            ]), "estado"] = "SP_INTERIOR"


            data.loc[data["cep"].isin([
                "01050-050",    # Centro
                "01420-001"     # Jardim Paulista
            ]), "estado"] = "SP_CAPITAL"


            data.loc[data["estado"].isin(["SC", "RS", "PR"]), "regiao"] = "Sul"
            data.loc[data["estado"].isin(["SP_CAPITAL", "SP_INTERIOR", "MG", "RJ", "ES"]), "regiao"] = "Sudeste"
            data.loc[data["estado"].isin(["GO", "MT", "MS", "DF"]), "regiao"] = "Centro-Oeste"
            data.loc[data["estado"].isin(["AC", "AP", "AM", "PA", "RO", "RR", "TO"]), "regiao"] = "Norte"
            data.loc[data["estado"].isin(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]), "regiao"] = "Nordeste"

            # Tratamentos prazo de frete e dia útil
            data["dia_util"] = "0"

            for index, row in data.iterrows():
                try:
                    if any(p in row["prazo_frete"] for p in ["bd", "úteis", "útil"]):
                        data.loc[index, "dia_util"] = "1"
                        data.loc[index, "prazo_frete"] = re.sub(r"\D", "", row["prazo_frete"])
                except:
                    data.loc[index, "dia_util"] = "0"

            data["prazo_frete"] = data["prazo_frete"].astype(str)

            Efizi.send_bigquery(data, "efizi-analises", "bi.precos_produtos_sites", "append", credentials)
    
    def send_email_error(state, msg, cep=None, loja=None, sku=None, link=None):

        from modules.efizitools import Efizi
        import json

        credentials_bi = Efizi.get_credentials("CREDENTIALS_BI")
        credentials_bi = json.loads(credentials_bi)

        Efizi.send_email(
            credentials_bi["email"],
            credentials_bi["password"],
            "ti@efizi.com.br",
            f"[ERRO] PREÇOS CONCORRENTES - {state}",
            f"""
                Houve erro no seguinte item:
                Estado: {state}
                CEP: {cep}
                Loja: {loja}
                Sku: {sku}
                Link: {link}
                Msg: {msg}
            """,
            "plain"
        )