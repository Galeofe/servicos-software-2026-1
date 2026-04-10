import io
import requests
from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
from PIL import Image

app = FastAPI()

print("Carregando modelo de visão...")
classificador = pipeline("image-classification", model="google/vit-base-patch16-224")

TRADUCOES = {
    "malinois": "Pastor-belga malinois",
    "german shepherd": "Pastor alemão",
    "golden retriever": "Golden retriever",
    "labrador retriever": "Labrador retriever",
    "beagle": "Beagle",
    "pug": "Pug",
    "chihuahua": "Chihuahua",
    "border collie": "Border collie",
    "siberian husky": "Husky siberiano",
    "tabby": "Gato rajado",
    "tabby cat": "Gato rajado",
    "tiger cat": "Gato tigrado",
    "persian cat": "Gato persa",
    "siamese cat": "Gato siamês",
    "egyptian cat": "Gato egípcio",
    "web site": "Site",
    "website": "Site",
    "internet site": "Site",
    "site": "Site",
    "computer keyboard": "Teclado",
    "keyboard": "Teclado",
    "laptop": "Notebook",
    "notebook": "Notebook",
    "desktop computer": "Computador",
    "screen": "Tela",
    "monitor": "Monitor",
    "cellular telephone": "Celular",
    "mobile phone": "Celular",
    "smartphone": "Celular",
    "banana": "Banana",
    "orange": "Laranja",
    "lemon": "Limão",
    "pineapple": "Abacaxi",
    "pizza": "Pizza",
    "cheeseburger": "Hambúrguer",
    "hotdog": "Cachorro-quente",
    "espresso": "Café expresso",
    "cup": "Copo",
    "coffee mug": "Caneca",
    "bottle": "Garrafa",
    "water bottle": "Garrafa de água",
    "car wheel": "Roda de carro",
    "sports car": "Carro esportivo",
    "minivan": "Minivan",
    "pickup": "Caminhonete",
    "bicycle": "Bicicleta",
    "motor scooter": "Scooter",
    "airliner": "Avião",
    "traffic light": "Semáforo",
    "street sign": "Placa de trânsito",
    "tree frog": "Perereca",
    "birdhouse": "Casinha de passarinho",
    "balloon": "Balão",
    "backpack": "Mochila",
    "book jacket": "Capa de livro",
    "bookcase": "Estante de livros",
    "toilet tissue": "Papel higiênico",
    "torch": "Tocha",
    "seashore": "Praia",
    "mountain bike": "Bicicleta de montanha",
}

def traduzir_rotulo(label: str) -> str:
    chave = label.strip().lower()
    if chave in TRADUCOES:
        return TRADUCOES[chave]

    # fallback bonito se não estiver no dicionário
    return (
        label.replace("_", " ")
             .replace("-", " ")
             .strip()
             .capitalize()
    )

@app.get("/")
def raiz():
    return {"status": "ok"}

@app.post("/analisar")
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()
    imagem = Image.open(io.BytesIO(conteudo)).convert("RGB")

    resultados = classificador(imagem)
    top3 = resultados[:3]

    rotulo_predito_en = top3[0]["label"]
    rotulo_predito_pt = traduzir_rotulo(rotulo_predito_en)

    files = {"file": (file.filename, conteudo, file.content_type)}
    data = {"rotulo": rotulo_predito_pt}

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
        "rotulo": rotulo_predito_pt,
        "rotulo_original": rotulo_predito_en,
        "status_db": status_db,
        "top3": [
            {
                "label": traduzir_rotulo(item["label"]),
                "label_original": item["label"],
                "score": round(item["score"] * 100, 2)
            }
            for item in top3
        ]
    }