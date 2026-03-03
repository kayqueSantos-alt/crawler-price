class Meli:

    def getProductData(authData, productId):
        import requests
        import json

        url = "https://api.mercadolibre.com/products/" +productId+"/items"

        headers = {"Authorization":f"Bearer {authData}"}

        response = requests.get(url, headers=headers).json()

        return response
    
    def getShippingProduct(authData, productId, cep):
        import requests
        import json

        url = f"https://api.mercadolibre.com/items/"+productId+"/shipping_options?zip_code="+ cep

        headers = {"Authorization":f"Bearer {authData}"}

        response = requests.get(url, headers=headers).json()

        return response
    