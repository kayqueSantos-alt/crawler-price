def add_product(obj):
    from modules.efizitools import Efizi
    from pandas import DataFrame

    produto = obj.get("PRODUTO")
    sku = obj.get("SKU")
    link = obj.get("LINK")
    loja = obj.get("LOJA")
    cep = obj.get("CEP")
    estado = obj.get("ESTADO")

    if None in [produto, sku, link, loja, cep, estado]:
        return {"msg": "O produto não pode ter dados nulos.", "code": 400}

    credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")
    data = DataFrame([obj])

    Efizi.send_bigquery(data, "efizi-analises", "bi.produtos_sites", "append", credentials)

    return {"msg": "Produto cadastrado com sucesso!", "code": 200}