import os
import sqlite3
from datetime import datetime
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
            rotulo TEXT,
            data_hora TEXT
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
    nome_arquivo = file.filename
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, nome_arquivo)

    with open(caminho_arquivo, "wb") as f:
        f.write(await file.read())

    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imagens (nome_arquivo, rotulo, data_hora) VALUES (?, ?, ?)",
        (nome_arquivo, rotulo, data_hora),
    )
    conn.commit()
    conn.close()

    return {
        "mensagem": "Imagem e rótulo armazenados com sucesso",
        "data_hora": data_hora
    }

@app.get("/historico")
def listar_historico():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome_arquivo, rotulo, data_hora
        FROM imagens
        ORDER BY id DESC
        LIMIT 10
    """)
    resultados = cursor.fetchall()
    conn.close()

    historico = [
        {
            "nome_arquivo": linha[0],
            "rotulo": linha[1],
            "data_hora": linha[2]
        }
        for linha in resultados
    ]

    return {"historico": historico}