import requests

url = "https://www.babamateriais.com.br/08700-caixa-dagua-600-litros-tanque-tampa-rosca-slim-fortlev/p"
# Extrai o slug da URL
slug = url.split("/")[-2]
domain = "https://www.babamateriais.com.br"

api_url = f"{domain}/api/catalog_system/pub/products/search/{slug}/p"
response = requests.get(api_url)
data = response.json()

if data:
    product_id = data[0]["productId"]
    print(product_id)