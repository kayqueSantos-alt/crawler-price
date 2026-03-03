import os 
from dotenv import load_dotenv
import json
from pathlib import Path
import sys
sys.path.append(str(Path(Path.cwd())))

class Efizi():

    global enviroment_path

    enviroment_path = os.getenv('REPOSITORY_PRICE')

    def deprecated(func):
        """Função que impede a utilização de funções inativas"""
        def wrapper(*args, **kwargs):
            raise NotImplementedError(f"A função {func.__name__} está inativa.")
        return wrapper

    def remove_special_character(string):
        import re
        import unicodedata

        text_nfkd = unicodedata.normalize('NFKD', string.upper())
        string = re.sub(r'[\u0300-\u036f.?]', '', text_nfkd)
        string = re.sub(r'[\s+-/]', '_', string)
        return string


    def get_credentials(credential_name):
        """
            Função que realiza a busca de credenciais

            Parâmetros:
                `credential_name*`: Nome da credencial a ser buscada
        """
        load_dotenv(dotenv_path=Path(enviroment_path)/"credentials/credentials.env")
        credential = os.getenv(credential_name)
        return credential


    def load_json_credentials(credentials):
        with open(Path(enviroment_path)/"credentials"/credentials) as past:
            credentials_ = json.load(past)
            return credentials_


    def write_log(filename, content):
        """
            Função que realiza a escrita de arquivo log na pasta `/logs`
            Esta função por padrão realiza o append das informações caso o arquivo de log já exista, caso não, ela cria um novo arquivo e insere os dados

            Parâmetros:
                `filename*`: Nome do arquivo (com extensão .json) para ser escrito
                `content*`: Conteúdo a ser escrito no arquivo.
        """
 
        if ".json" not in filename:
            raise Exception("O arquivo de Log deve ser um .json")

        # Caso o arquivo não exista, cria o arquivo e adiciona o conteúdo
        if filename not in os.listdir(Path(enviroment_path)/"logs"):
            with open(Path(enviroment_path)/"logs/"+filename, "w") as log_file:
                log_file.write(json.dumps({"data": [content]}, indent=4))
                log_file.close()
        else:
            # Lê o arquivo e busca os dados dentro de "data" e insere o novo conteúdo
            with open(Path(enviroment_path)/"logs/"+filename, "r") as log_file:
                content_file = json.loads(log_file.read())
                content_file["data"].append(content)
                log_file.close()

            # Escreve o novo conteúdo no arquivo
            with open(Path(enviroment_path)/"logs/"+filename, "w") as log_file:
                log_file.write(json.dumps(content_file, indent=4))
                log_file.close()


    def send_email(origin, password, destiny, title, message, type_email, filepath=None):
        """
            Função que realiza envio de email

            Parâmetros:
                `origin*`: email que realizará o envio
                `password*`: senha do email que realizará o envio
                `destiny*`: email de destino
                `title*`: título do email
                `message*`: mensagem que será enviada por email
                `type_email*`: tipo de email: html ou plain(texto simples)
                `filepath`: caminho do arquivo para anexo
        """
        import smtplib

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        from email.mime.base import MIMEBase
        from email import encoders

        if title == None or message == None:
            raise Exception("O título ou a mensagem não devem ser Nulos")

        if filepath != None:
            # Lê arquivo
            attachment_file = open(filepath, "rb")

            # Prepara arquivo para anexar
            to_attach_file = MIMEBase('application', 'octet-stream')
            to_attach_file.set_payload(attachment_file.read())
            encoders.encode_base64(to_attach_file)

            # Adicionar header para anexar
            to_attach_file.add_header('Content-Disposition', f'attachment; filename= {filepath.split("/")[-1]}')

            # Fecha arquivo
            attachment_file.close()


        # Start Server SMTP
        host = "smtp.gmail.com"
        port = "587"
        login = origin
        senha = password

        #  Inicia o server SMTP
        server = smtplib.SMTP(host, port)

        # Inicia mecanismos de segurança para envio de email
        server.ehlo()
        server.starttls()
        # Login no email
        server.login(login, senha)

        # Construção de email
        corpo = message

        email_final = MIMEMultipart()
        email_final["From"] = login
        email_final["To"] = destiny
        email_final["Subject"] = title

        email_final.attach(MIMEText(corpo, type_email))

        # Anexa arquivo no email
        if filepath != None:
            email_final.attach(to_attach_file)

        server.sendmail(email_final["From"], email_final["To"], email_final.as_string())

        server.quit()

        return {"result": "OK", "msg": "Email enviado"}



   
    def send_bigquery(dataframe, project_id, table, send_method, credentials, schema=None):
        """
            Função que realiza envio de dados ao BigQuery.

            Parâmetros:
                `dataframe` Dados que serão enviados ao BigQuery
                `project_id` ID do projeto da Google Cloud
                `table`: Tabela que vai receber os dados
                `send_method`: Método de envio (replace ou append)
                `credentials`: credenciais do projeto GCP
                `schema`: Definição dos datatypes das colunas (opcional)
        """

        from google.oauth2 import service_account
        import pandas_gbq

        # seta as credenciais
        pandas_gbq.context.credentials = service_account.Credentials.from_service_account_info(credentials)

        # seta o projeto no google cloud    
        pandas_gbq.context.project = project_id

        # Verifica se o schema foi enviado
        if schema == None:
            # envia devoluções para o BigQuery
            pandas_gbq.to_gbq(dataframe, table, project_id=project_id, if_exists=send_method, table_schema=None)
        else:
            # envia devoluções para o BigQuery
            pandas_gbq.to_gbq(dataframe, table, project_id=project_id, if_exists=send_method, table_schema=schema)


    def read_sheet(sheet_id, tab_name, credentials_path, range_data=None):
        """
            Função que realiza leitura de planilha Google Sheets.

            Parâmetros
                `sheet_id*`: ID da planilha Google Sheets.
                `tab_name*`: Nome da aba onde estão os dados.
                `credentials_path*`: caminho das credenciais.
                `range_data`: definição de qual o intervalo dos dados a serem lidos.
        """

        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        import pandas as pd

        # Caminho para o arquivo de credenciais da conta de serviço
        SERVICE_ACCOUNT_FILE = credentials_path
        # SERVICE_ACCOUNT_FILE = f'C:\\Users\\PedroOliveira\\OneDrive - Efizi\\Área de Trabalho\\efizi-scripts\\credentials\\service_account_google_sheets.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # Autenticação
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        # Cria o serviço da API do Google Sheets
        service = build('sheets', 'v4', credentials=credentials)

        # Adiciona o "!" caso exista um range específico a ser buscado
        if range_data == None:
            range_data = ""
        else:
            range_data = "!"+range_data

        # ID da planilha e aba a ser lida
        SPREADSHEET_ID = sheet_id
        RANGE_NAME = f'{tab_name}{str(range_data)}'

        # Chama a API para ler os dados
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        # Retorna os dados lidos
        if not values:
            return pd.DataFrame()
        else:
            values = pd.DataFrame(columns=values[0], data=values[1:])
            return values



    def write_sheet(sheet_id, tab_name, credentials_path, df):
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        # import pandas as pd

        """
        Função que escreve dados em uma planilha do Google Sheets.

        Parâmetros:
            sheet_id (str): ID da planilha.
            tab_name (str): Nome da aba onde os dados serão escritos.
            credentials_path (str): Caminho das credenciais.
            df (pd.DataFrame): DataFrame com os dados a serem escritos...

        Retorno:
            response: Resposta da API Google sheets.
        """
        try:
            # Verifica se o DataFrame está vazio
            if df.empty:
                raise ValueError("O DataFrame está vazio")

            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            # Carrega as credenciais
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES)
            
            # Cria o serviço da API
            service = build('sheets', 'v4', credentials=credentials)

            # Converte o DataFrame para uma lista de listas
            values = [df.columns.tolist()] + df.values.tolist()
            body = {'values': values}

            # Define o range onde os dados serão escritos
            RANGE_NAME = f'{tab_name}!A1'

            # Executa a atualização
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=RANGE_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()

            print("Dados escritos com sucesso!")
            return result

        except FileNotFoundError:
            print(f"Erro: Arquivo de credenciais não encontrado em {credentials_path}")
        except Exception as e:
            print(f"Erro ao escrever na planilha: {str(e)}")
            return None
        
    def d_para():
        import json
        from pathlib import Path
        caminho_json = Path(enviroment_path)/"source"/"produtos.json"
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados


    def get_bigquery(query, project_id, credentials):
        """
            Função que busca dados ao BigQuery.

            Parâmetros:
                `query`: Consulta de dados no BigQuery
                `project_id`: ID do projeto da Google Cloud
                `credentials`: credenciais do projeto GCP
        """

        from google.oauth2 import service_account
        import pandas_gbq

        # seta as credenciais
        pandas_gbq.context.credentials = service_account.Credentials.from_service_account_info(credentials)

        # seta o projeto no google cloud    
        pandas_gbq.context.project = project_id

        # envia devoluções para o BigQuery
        return pandas_gbq.read_gbq(query, project_id=project_id)
    

    def frete_mkt(cep, sku, mkt, dados_produtos, channel, value=None):
            import sys
            from pathlib import Path
            import time
            sys.path.append(str(Path(Path.cwd())))

            from modules.efizitools import Efizi
            from modules.frete_rapido import FreteRapido

            token = Efizi.get_credentials("FRETE_RAPIDO")
            FreteRapido.set_token(token)

            cnpj = "34229157000105"
            plataforma = mkt
            cep_expedidor = 29168067
            tipo_pessoa = 0
            tipo_simulacao = 0
            
            for _,produto in dados_produtos.iterrows():
                if produto["sku"] == sku:
                    array_prods = [{
                        "amount": 1,
                        "category": produto["categoria"],
                        "height": float(produto["altura"].replace(",",".")),
                        "sku": f"0{produto["sku"]}",
                        "width": float(produto["largura"].replace(",",".")),
                        "length": float(produto["comprimento"].replace(",",".")),
                        "unitary_price":value,
                        "unitary_weight": float(produto["peso"].replace(",","."))
                    }]
            resp = FreteRapido.freight_simulation(cnpj, plataforma, tipo_pessoa, cep, cnpj, cep_expedidor, array_prods, tipo_simulacao, channel)
            prazo = None
            preco = None
            if resp and "dispatchers" in resp and resp["dispatchers"]:
                ofertas = resp["dispatchers"][0].get("offers", [])
                if ofertas:
                    melhor_oferta = min(ofertas, key=lambda x: x["final_price"])
                    try:
                        preco = melhor_oferta["final_price"]
                        prazo = str(melhor_oferta["delivery_time"]["days"])
                    except:
                        None

            time.sleep(0.8)

            return preco, prazo

    def get_datadome_playwright(url, proxy_url=None):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser_args = {}
            if proxy_url:
                browser_args["proxy"] = {"server": proxy_url}

            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            cookies = context.cookies()

            datadome = None
            for c in cookies:
                if c["name"] == "datadome":
                    datadome = c["value"]
                    break

            browser.close()

            if not datadome:
                raise Exception("datadome não foi gerado")

            return datadome
