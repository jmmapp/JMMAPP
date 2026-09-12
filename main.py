import requests

url = "https://api.mercadolibre.com/sites/MLB/search?q=perfume"

response = requests.get(url)

print("Status:", response.status_code)
print("Tamanho da resposta:", len(response.text))
print(response.json())