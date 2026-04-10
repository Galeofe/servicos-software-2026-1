import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI()

DIRETORIO_DADOS = "/dados"
DB_PATH = f"{DIRETORIO_DADOS}/banco.db"

os.makedirs(DIRETORIO_DADOS, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT,
            rotulo TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def raiz():
    return {"status": "ok"}

@app.post("/salvar")
async def salvar_dados(file: UploadFile = File(...), rotulo: str = Form(...)):
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, file.filename)

    with open(caminho_arquivo, "wb") as f:
        f.write(await file.read())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imagens (nome_arquivo, rotulo) VALUES (?, ?)",
        (file.filename, rotulo),
    )
    conn.commit()
    conn.close()

    return {"mensagem": "Imagem e rótulo armazenados com sucesso"}