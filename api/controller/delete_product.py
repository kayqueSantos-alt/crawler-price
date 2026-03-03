def delete_product(product):
    from modules.efizitools import Efizi

    sku = product.get("SKU")
    loja = product.get("LOJA")
    cep = product.get("CEP")
    estado = product.get("ESTADO")

    if None in [sku, loja, cep, estado]:
        return {"msg": "O produto não pode ter dados nulos.", "code": 400}

    credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")

    Efizi.get_bigquery(
        f"""
            delete
            from
                bi.produtos_sites
            where
                SKU = '{sku}'
                and LOJA = '{loja}'
                and CEP = '{cep}'
                and ESTADO = '{estado}'
        """,
        "efizi-analises",
        credentials
    )
    return {"msg": "Produto deletado com sucesso!", "code": 200}