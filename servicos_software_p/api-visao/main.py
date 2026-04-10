import io
from pathlib import Path

import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps
from transformers import pipeline

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

    return label.replace("_", " ").replace("-", " ").strip().capitalize()


def inferir_categoria(rotulo_pt: str) -> str:
    texto = rotulo_pt.lower()

    if any(p in texto for p in ["pastor", "cachorro", "gato", "beagle", "husky", "perereca"]):
        return "animal"

    if any(p in texto for p in ["carro", "minivan", "caminhonete", "bicicleta", "avião", "scooter", "roda"]):
        return "veículo"

    if any(p in texto for p in [
        "pizza", "hambúrguer", "cachorro-quente", "banana",
        "laranja", "limão", "abacaxi", "café", "copo", "caneca"
    ]):
        return "alimento ou bebida"

    if any(p in texto for p in ["celular", "notebook", "computador", "monitor", "teclado", "site"]):
        return "tecnologia"

    if any(p in texto for p in ["mochila", "garrafa", "tocha", "papel higiênico", "estante", "capa de livro"]):
        return "objeto"

    return "elemento visual"


def gerar_descricao_automatica(rotulo_pt: str, score: float, categoria: str) -> str:
    nome = rotulo_pt.lower()

    if score >= 70:
        return f"A imagem provavelmente mostra {nome}, com forte correspondência visual na categoria de {categoria}."

    if score >= 45:
        return f"A imagem parece mostrar {nome}, com correspondência visual moderada na categoria de {categoria}."

    return f"A imagem pode estar relacionada a {nome}, mas a confiança visual foi mais baixa."


def gerar_explicacao_visual(top3_processado: list, categoria: str) -> str:
    if not top3_processado:
        return "Não foi possível gerar uma explicação visual."

    principal = top3_processado[0]
    score_principal = principal["score"]

    if len(top3_processado) > 1:
        score_segundo = top3_processado[1]["score"]
        diferenca = score_principal - score_segundo
    else:
        diferenca = score_principal

    alternativas = ", ".join(item["label"].lower() for item in top3_processado[1:])

    if diferenca >= 15:
        base = "A previsão principal ficou bem acima das demais"
    elif diferenca >= 7:
        base = "A previsão principal ficou um pouco acima das demais"
    else:
        base = "As previsões ficaram relativamente próximas entre si"

    if alternativas:
        return (
            f"{base}, o que indica que a imagem possui características visuais "
            f"da categoria de {categoria}. As alternativas mais próximas foram {alternativas}."
        )

    return (
        f"{base}, o que indica que a imagem possui características visuais "
        f"da categoria de {categoria}."
    )


def enquadrar_no_canvas(imagem: Image.Image, tamanho=(512, 512)) -> Image.Image:
    ajustada = ImageOps.contain(imagem, tamanho, Image.LANCZOS)
    canvas = Image.new("RGB", tamanho, (245, 248, 255))
    x = (tamanho[0] - ajustada.width) // 2
    y = (tamanho[1] - ajustada.height) // 2
    canvas.paste(ajustada, (x, y))
    return canvas


def criar_gif_animado(imagem: Image.Image, tamanho=(512, 512), frames=16, duracao=90) -> io.BytesIO:
    base = ImageOps.exif_transpose(imagem).convert("RGB")

    limite = 900
    if max(base.size) > limite:
        escala = limite / max(base.size)
        base = base.resize(
            (int(base.width * escala), int(base.height * escala)),
            Image.LANCZOS
        )

    w, h = base.size
    quadros = []

    for i in range(frames):
        progresso = i / (frames - 1) if frames > 1 else 0
        zoom = 1.0 + (0.18 * progresso)

        corte_w = max(1, int(w / zoom))
        corte_h = max(1, int(h / zoom))

        max_left = max(w - corte_w, 0)
        max_top = max(h - corte_h, 0)

        left = int(max_left * (0.15 + 0.55 * progresso))
        top = int(max_top * (0.10 + 0.45 * progresso))

        left = min(max(left, 0), max_left)
        top = min(max(top, 0), max_top)

        quadro = base.crop((left, top, left + corte_w, top + corte_h))
        quadro = enquadrar_no_canvas(quadro, tamanho=tamanho)
        quadros.append(quadro)

    if len(quadros) > 2:
        quadros.extend(quadros[-2:0:-1])

    buffer = io.BytesIO()
    quadros[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=quadros[1:],
        duration=duracao,
        loop=0,
        optimize=True,
    )
    buffer.seek(0)
    return buffer


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

    top3_processado = [
        {
            "label": traduzir_rotulo(item["label"]),
            "label_original": item["label"],
            "score": round(item["score"] * 100, 2)
        }
        for item in top3
    ]

    categoria = inferir_categoria(rotulo_predito_pt)
    descricao_automatica = gerar_descricao_automatica(
        rotulo_predito_pt,
        top3_processado[0]["score"],
        categoria
    )
    explicacao_visual = gerar_explicacao_visual(top3_processado, categoria)

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
        "descricao_automatica": descricao_automatica,
        "explicacao_visual": explicacao_visual,
        "top3": top3_processado
    }


@app.post("/gerar-gif")
async def gerar_gif(file: UploadFile = File(...)):
    conteudo = await file.read()
    imagem = Image.open(io.BytesIO(conteudo))

    gif_buffer = criar_gif_animado(imagem)

    nome_base = Path(file.filename or "imagem").stem
    nome_saida = f"{nome_base}_animado.gif"

    return StreamingResponse(
        gif_buffer,
        media_type="image/gif",
        headers={"Content-Disposition": f'inline; filename="{nome_saida}"'}
    )