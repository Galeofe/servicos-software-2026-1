import io
import requests
from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
from PIL import Image

app = FastAPI()

print("Carregando modelo de visão...")
classificador = pipeline("image-classification", model="google/vit-base-patch16-224")

@app.get("/")
def raiz():
    return {"status": "ok"}

@app.post("/analisar")
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()
    imagem = Image.open(io.BytesIO(conteudo))

    resultados = classificador(imagem)
    rotulo_predito = resultados[0]["label"]

    files = {"file": (file.filename, conteudo, file.content_type)}
    data = {"rotulo": rotulo_predito}

    try:
        res_db = requests.post(
            "http://api-armazenamento:8082/salvar",
            files=files,
            data=data
        )
        status_db = "Salvo com sucesso" if res_db.status_code == 200 else "Erro ao salvar"
    except Exception:
        status_db = "Falha na comunicação com api-armazenamento"

    return {
        "rotulo": rotulo_predito,
        "status_db": status_db
    }