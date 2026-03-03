class FreteRapido():
    
    global token
    global url_base
    url_base = 'https://freterapido.com/api/external/embarcador/v1'

    def deprecated(func):
        """Função que impede a utilização de funções inativas"""
        def wrapper(*args, **kwargs):
            raise NotImplementedError(f"A função {func.__name__} está inativa.")
        return wrapper

    def set_token(authentication_string):
        """
            Função que seta o token de integração para realizar busca na API 

            Parâmetros:
                `authentication_string`: token gerado na plataforma Frete Rápido para consumo da API
        """
        global token
        token = authentication_string


    def freight_simulation(shipper_cnpj, platform_code, recipient_type, zipcode_recipient, dispatcher_cnpj, dispatcher_zipcode, array_prods, simulation_type, channel,country_recipient="BRA"):
        """
            Função que realiza cotação de frete na FreteRápido

            Parâmetros:
                (string) `shipper_cnpj`: CNPJ da conta registrada na Frete Rápido. String Numérica de 14 caracteres sem formatação.
                (string) `platform_code`: Código da plataforma integrada (Anymarket e etc).
                (int) `recipient_type`: Tipo de destinatário (0 = Pessoa Física, 1 = Pessoa Jurídica).
                (int) `zipcode_recipient`: CEP do destinatário.
                (string) `country_recipient`: País do destinatário. Para operações no Brasil, informar "BRA" (valor padrão: "BRA").
                (string) `dispatcher_cnpj`: CNPJ do expedidor, caso não tenha expedidor informar o mesmo CNPJ utilizado em `shipper_cnpj`. String Numérica de 14 caracteres sem formatação
                (int) `dispatcher_zipcode`: CEP de origem do expedidor.
                (int) `simulation_type`: Tipo de simulação a realizar (`0 = Fracionada, 1 = Lotação`).
                (array json) `array_prods`: Lista de produtos que deseja realizar a cotação.

            O objeto json do produto dentro do array deve ter a seguinte estrutura:

                {
                    "amount": int,
                    "category": string,
                    "sku": string,
                    "height": float,
                    "width": float,
                    "length": float,
                    "unitary_price": float,
                    "unitary_weight": float
                }

            Caso seja necessário descobrir a categoria do produto, entre na FreteRápido e baixe o relatório de produto, nele vai constar o número da categoria e também as demais informações.
        """

        import requests
        global token

        obj_to_send = {
            "shipper": {
                "registered_number": shipper_cnpj,
                "token": token,
                "platform_code": platform_code
            },
            "recipient": {
                "type": recipient_type,
                "country": country_recipient,
                "zipcode": zipcode_recipient
            },
            "dispatchers": [
                {
                    "registered_number": dispatcher_cnpj,
                    "zipcode": dispatcher_zipcode,
                    "volumes": array_prods
                }
            ],
            "channel":channel,
            #   "Mercado_Livre",
            "simulation_type": [simulation_type]
        }

        try:
            response = requests.post("https://sp.freterapido.com/api/v3/quote/simulate", json=obj_to_send).json()
            return response
        except:
            raise Exception("Houve um erro ao cotar o frete")



