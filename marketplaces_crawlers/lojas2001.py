# DEPRECATED: Este crawler esta desativado e nao e usado em producao.
# class Lojas2001:
#     # def crawler(url, cep, loja, sku, produto_nome, estado, regiao):
#         import json
#         import requests
#         import cloudscraper
#         from bs4 import BeautifulSoup
#         from modules.general import General

#         prod_obj = {}

#         response = requests.get(url).content
#         soup = BeautifulSoup(response, "html.parser")

# #         from modules.general import General
# #         prod_obj = {}
# #         response = requests.get(url).content
# #         soup = BeautifulSoup(response, "html.parser")

# #         try:
# #             produto = str(soup.find("script", {"type": "application/ld+json"})).replace('<script type="application/ld+json">', '').replace('</script>', '')
# #             price = json.loads(produto)
# #             prod_obj["valor_produto"] = float(price["offers"]["sale_price"])
# #         except:
# #             prod_obj["valor_produto"] = None

#         cookies = {
#             "PHPSESSID": "9n7sjacbvidi2hnsftcj76j7ht",
#             "__trf.src": "encoded_eyJmaXJzdF9zZXNzaW9uIjp7InZhbHVlIjoiKG5vbmUpIiwiZXh0cmFfcGFyYW1zIjp7fX0sImN1cnJlbnRfc2Vzc2lvbiI6eyJ2YWx1ZSI6Iihub25lKSIsImV4dHJhX3BhcmFtcyI6e319LCJjcmVhdGVkX2F0IjoxNzU2MTUxNzA3NTM5fQ==",
#             "_gcl_au": "1.1.1498872887.1756151708",
#             "_ga_MMC35LCCPL": "GS2.1.s1756151707$o1$g0$t1756151707$j60$l0$h2021650745",
#             "_fbp": "fb.1.1756151707919.424615790533066424",
#             "_ga": "GA1.2.1770697850.1756151708",
#             "_gid": "GA1.2.734432403.1756151708",
#             "_clck": "1c374v4%5E2%5Efyr%5E0%5E2063",
#             "_clsk": "1hbjffw%5E1756151708932%5E1%5E1%5El.clarity.ms%2Fcollect",
#             "AdoptConsent": "N4Ig7gpgRgzglgFwgSQCIgFwgGwEYAmAxtgJwCsEAtAOzYAcAhpQCwBmh1lDATIU7oTpliDZtzrMSIADQgAbnHgIA9gCdk+TCGrcADAGYodQlTa66LXLlaU6UXfhpR8YhiQaNWumSGUAHBGQAOwAVBgBzGEwAbQBdWX8EAHkAVwQwyJj4kEJlIJgIIMDNLAAhADkAfXgAZR8IOUL0gE8/CC0wOzgACQAvCHKfXPymgDUIVXg8zDpZFL98BiR8AEEELT1uMkpzSi2Q3BIMMjIMXH0AOgNsAC0QAF8gA==",
#             "AdoptVisitorId": "OwJgDAzARgHAxgUwLQBYBmYaoIzbUmKMAEyWCmJRAEMBOamajIA=",
#             "_ad_token": "wvlrgjl237j8cmugvmfre",
#             "rdtrk": "%7B%22id%22%3A%2273fb1ff5-2a64-416b-923d-f58f2d16162c%22%7D",
#             "_ga_8RDK425VFH": "GS2.1.s1756151707$o1$g1$t1756151745$j22$l0$h0"
#         }

#         headers = {
#             "accept": "*/*",
#             "cookies": "PHPSESSID=9n7sjacbvidi2hnsftcj76j7ht; __trf.src=encoded_eyJmaXJzdF9zZXNzaW9uIjp7InZhbHVlIjoiKG5vbmUpIiwiZXh0cmFfcGFyYW1zIjp7fX0sImN1cnJlbnRfc2Vzc2lvbiI6eyJ2YWx1ZSI6Iihub25lKSIsImV4dHJhX3BhcmFtcyI6e319LCJjcmVhdGVkX2F0IjoxNzU2MTUxNzA3NTM5fQ==; _gcl_au=1.1.1498872887.1756151708; _ga_MMC35LCCPL=GS2.1.s1756151707$o1$g0$t1756151707$j60$l0$h2021650745; _fbp=fb.1.1756151707919.424615790533066424; _ga=GA1.2.1770697850.1756151708; _gid=GA1.2.734432403.1756151708; _clck=1c374v4%5E2%5Efyr%5E0%5E2063; _clsk=1hbjffw%5E1756151708932%5E1%5E1%5El.clarity.ms%2Fcollect; AdoptConsent=N4Ig7gpgRgzglgFwgSQCIgFwgGwEYAmAxtgJwCsEAtAOzYAcAhpQCwBmh1lDATIU7oTpliDZtzrMSIADQgAbnHgIA9gCdk+TCGrcADAGYodQlTa66LXLlaU6UXfhpR8YhiQaNWumSGUAHBGQAOwAVBgBzGEwAbQBdWX8EAHkAVwQwyJj4kEJlIJgIIMDNLAAhADkAfXgAZR8IOUL0gE8/CC0wOzgACQAvCHKfXPymgDUIVXg8zDpZFL98BiR8AEEELT1uMkpzSi2Q3BIMMjIMXH0AOgNsAC0QAF8gA==; AdoptVisitorId=OwJgDAzARgHAxgUwLQBYBmYaoIzbUmKMAEyWCmJRAEMBOamajIA=; _ad_token=wvlrgjl237j8cmugvmfre; rdtrk=%7B%22id%22%3A%2273fb1ff5-2a64-416b-923d-f58f2d16162c%22%7D; _ga_8RDK425VFH=GS2.1.s1756151707$o1$g1$t1756151745$j22$l0$h0",
#             "accept-encoding": "gzip, deflate, br, zstd",
#             "accept-language": "pt-PT,pt;q=0.9",
#             "priority": "u=1, i",
#             "referer": url,
#             "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
#             "sec-ch-ua-mobile": "?0",
#             "sec-ch-ua-platform": "Windows",
#             "sec-fetch-dest": "empty",
#             "sec-fetch-mode": "cors",
#             "sec-fetch-site": "same-origin",
#             "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
#             "x-requested-with": "XMLHttpRequest"
#         }

#         scrapper = cloudscraper.create_scraper()

#         session = requests.Session()
#         response_freight = session.get("https://lojas2001.com/components/product-freight.php", headers=headers, cookies=cookies)
#         # response_freight = requests.get(, headers=headers, cookies=cookies)

#         print("")
#         print(response_freight.content)


# #         prod_obj["cep"] = cep
# #         prod_obj["estado"] = estado
# # 
# #         prod_obj["loja"] = loja
# #         prod_obj["link"] = url
# #         prod_obj["sku"] = sku
# #         prod_obj["produto"] = produto_nome
# #         print(prod_obj)
# #         return prod_obj
        
#         response = requests.get("https://lojas2001.com/caixa-d-agua-polietileno-5000l--2020010--fortlev-521787-1").content
#         print(response)


import requests
import json

session = requests.session()
url = "https://lojas2001.com/caixa-dagua-polietileno-15000l--2020036--fortlev-656449-1"

payload = {
    "cep":"51.130-020",
    "id_produto":"656449",
    "acao":"consultarEntregaProduto"
}

headers = {
    "x-requested-with": "XMLHttpRequest",
    "origin":"https://lojas2001.com",
    "priority":"u=1, i",
    "referer":url,
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
}

session.get(url)

response = session.post("https://lojas2001.com/controllers/order-controller.php", headers=headers, data=payload).content
params = json.loads(response)

response = session.get("https://lojas2001.com/components/product-freight.php", headers=headers, params=params).content
print(response)

