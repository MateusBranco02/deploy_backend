import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    raise ValueError("A chave da API não foi carregada. Verifique o arquivo .env")


ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def perguntar_gemini(contexto, pergunta):
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": API_KEY
    }
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Baseado estritamente nas informações do programa Jovem Programador abaixo:\n\n---\n{contexto}\n---\n\nResponda à seguinte pergunta de forma direta e concisa:\n\nPergunta: {pergunta}"
                    }
                ]
            }
        ]
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, params=params, json=body)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return "Desculpe, ocorreu um erro ao processar sua pergunta."


def carregar_contexto():
    """Carrega o texto do arquivo dados.txt; se não existir, faz scraping do site e cria o arquivo."""
    caminho_arquivo = "dados.txt"

    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            return f.read()

    # Se o arquivo não existir, faz scraping simples do site
    try:
        from bs4 import BeautifulSoup

        url = "https://www.jovemprogramador.com.br/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        paragrafos = soup.find_all("p")
        texto_extraido = "\n".join([p.get_text(strip=True) for p in paragrafos])

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(texto_extraido)

        return texto_extraido
    except Exception as e:
        print(f"Erro ao fazer scraping do site Jovem Programador: {e}")
        return "Conteúdo oficial do site não pôde ser carregado no momento."


app = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pergunta(BaseModel):
    pergunta: str


@app.post("/perguntar")
def processar_pergunta(pergunta: Pergunta):
    """
    Recebe uma pergunta do front-end, processa com o Gemini e retorna a resposta.
    """
    contexto = carregar_contexto()
    resposta_do_bot = perguntar_gemini(contexto, pergunta.pergunta)
    return {"resposta": resposta_do_bot}


print("✅ Servidor FastAPI pronto. Acesse http://127.0.0.1:8000/docs para ver a documentação da API.")
