def edit_product(original, new):
    from modules.efizitools import Efizi

    original_produto = original.get("PRODUTO")
    original_sku = original.get("SKU")
    original_link = original.get("LINK")
    original_loja = original.get("LOJA")
    original_cep = original.get("CEP")
    original_estado = original.get("ESTADO")

    new_produto = new.get("PRODUTO")
    new_sku = new.get("SKU")
    new_link = new.get("LINK")
    new_loja = new.get("LOJA")
    new_cep = new.get("CEP")
    new_estado = new.get("ESTADO")

    if None in [original_produto, original_sku, original_link, original_loja, original_cep, original_estado]:
        return {"msg": "O produto não pode ter dados nulos.", "code": 400}

    if None in [new_produto, new_sku, new_link, new_loja, new_cep, new_estado]:
        return {"msg": "O produto não pode ter dados nulos.", "code": 400}

    credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")

    Efizi.get_bigquery(
        f"""
            update
                bi.produtos_sites
            set
                PRODUTO = '{new_produto}',
                SKU = '{new_sku}',
                LINK = '{new_link}',
                LOJA = '{new_loja}',
                CEP = '{new_cep}',
                ESTADO = '{new_estado}'
            where
                SKU = '{original_sku}'
                and LOJA = '{original_loja}'
                and CEP = '{original_cep}'
                and ESTADO = '{original_estado}'
        """,
        "efizi-analises",
        credentials
    )
    return {"msg": "Produto editado com sucesso!", "code": 200}