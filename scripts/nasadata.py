import requests
from PIL import Image
from io import BytesIO

# Use sua chave da API ou a demo_key
API_KEY = "fgJ83KUui1fLrPUmHCexxSgME9sPWVnZtXdzhepW"
URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

# Requisição à API
response = requests.get(URL)

if response.status_code == 200:
    data = response.json()
    print("Título:", data["title"])
    print("Data:", data["date"])
    print("Descrição:", data["explanation"])
    print("URL da imagem:", data["url"])

    # Baixar e mostrar a imagem
    img_response = requests.get(data["url"])
    img = Image.open(BytesIO(img_response.content))
    img.show()  # Isso abre no visualizador de imagem padrão do seu sistema
else:
    print("Erro ao acessar API:", response.status_code)
