import requests
from bs4 import BeautifulSoup

URL = "https://www.jovemprogramador.com.br/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

paragrafos = soup.find_all("p")
texto_extraido = "\n".join([p.get_text(strip=True) for p in paragrafos])

with open("dados.txt", "w", encoding="utf-8") as f:
    f.write(texto_extraido)

print("✅ Dados coletados e salvos no 'dados.txt'")