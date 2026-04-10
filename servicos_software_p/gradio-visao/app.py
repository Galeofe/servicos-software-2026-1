import base64
import html
import tempfile

import gradio as gr
import requests

API_VISAO = "http://api-visao:8081"
API_ARMAZENAMENTO = "http://api-armazenamento:8082"


def analisar_imagem(imagem_path):
    if imagem_path is None:
        return """
        <div class="result-empty">
            Nenhuma imagem enviada.
        </div>
        """, ""

    with open(imagem_path, "rb") as f:
        files = {"file": f}

        try:
            response = requests.post(
                f"{API_VISAO}/analisar",
                files=files
            )

            if response.status_code == 200:
                dados = response.json()

                rotulo = html.escape(dados.get("rotulo", "Não identificado"))
                rotulo_original = html.escape(dados.get("rotulo_original", "Não identificado"))
                status_db = html.escape(dados.get("status_db", "Sem status"))
                descricao_automatica = html.escape(
                    dados.get("descricao_automatica", "Descrição não disponível.")
                )
                explicacao_visual = html.escape(
                    dados.get("explicacao_visual", "Explicação não disponível.")
                )
                top3 = dados.get("top3", [])

                top3_html = ""
                top3_texto = []

                if top3:
                    for i, item in enumerate(top3, start=1):
                        label_pt = html.escape(item["label"])
                        label_original = html.escape(item["label_original"])
                        score = item["score"]

                        top3_html += f"""
                        <div class="top-item">
                            <span class="top-rank">#{i}</span>
                            <span class="top-label">{label_pt}</span>
                            <span class="top-score">{score}%</span>
                        </div>
                        <div class="top-original">Original: {label_original}</div>
                        """

                        top3_texto.append(
                            f"Opção {i}: {item['label']}, com {item['score']} por cento de confiança"
                        )

                resumo_acessivel = (
                    f"{dados.get('descricao_automatica', 'Descrição não disponível.')} "
                    f"{dados.get('explicacao_visual', 'Explicação não disponível.')} "
                    f"O rótulo principal foi {dados.get('rotulo', 'Não identificado')}. "
                    f"O rótulo original retornado pelo modelo foi {dados.get('rotulo_original', 'Não identificado')}. "
                    f"O status do armazenamento foi {dados.get('status_db', 'Sem status')}. "
                )

                if top3_texto:
                    resumo_acessivel += "Top 3 previsões: " + ". ".join(top3_texto) + "."

                html_resultado = f"""
                <div class="result-card">
                    <div class="result-badge">Análise concluída</div>
                    <h3>Resultado da classificação</h3>

                    <div class="result-line">
                        <span class="result-label">Rótulo principal</span>
                        <span class="result-value">{rotulo}</span>
                    </div>

                    <div class="result-line">
                        <span class="result-label">Rótulo original</span>
                        <span class="result-value">{rotulo_original}</span>
                    </div>

                    <div class="result-line">
                        <span class="result-label">Status do banco</span>
                        <span class="result-value success">{status_db}</span>
                    </div>

                    <div class="description-box">
                        <h4>Descrição automática da imagem</h4>
                        <p>{descricao_automatica}</p>
                    </div>

                    <div class="description-box secondary">
                        <h4>Explicação mais humana do conteúdo visual</h4>
                        <p>{explicacao_visual}</p>
                    </div>

                    <div class="top3-box">
                        <h4>Top 3 previsões da IA</h4>
                        {top3_html}
                    </div>

                    <div class="accessible-summary">
                        {html.escape(resumo_acessivel)}
                    </div>
                </div>
                """

                return html_resultado, resumo_acessivel

            return f"""
            <div class="result-card error">
                <h3>Erro no servidor</h3>
                <p>Status HTTP: {response.status_code}</p>
            </div>
            """, ""

        except Exception as e:
            return f"""
            <div class="result-card error">
                <h3>Erro de comunicação</h3>
                <p>{html.escape(str(e))}</p>
            </div>
            """, ""


def gerar_gif(imagem_path):
    if imagem_path is None:
        return """
        <div class="gif-empty">
            Envie uma imagem para gerar o GIF animado.
        </div>
        """, None

    with open(imagem_path, "rb") as f:
        files = {"file": ("imagem.png", f, "image/png")}

        try:
            response = requests.post(
                f"{API_VISAO}/gerar-gif",
                files=files
            )

            if response.status_code == 200:
                gif_bytes = response.content
                gif_base64 = base64.b64encode(gif_bytes).decode("utf-8")

                arquivo_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
                arquivo_tmp.write(gif_bytes)
                arquivo_tmp.flush()
                arquivo_tmp.close()

                html_gif = f"""
                <div class="gif-card">
                    <div class="gif-badge">Novo GIF gerado</div>
                    <h3>Prévia do GIF animado</h3>
                    <img
                        src="data:image/gif;base64,{gif_base64}"
                        alt="GIF animado gerado a partir da imagem enviada"
                        class="gif-preview"
                    />
                    <p class="gif-tip">
                        O GIF abaixo foi criado automaticamente com um efeito suave de zoom e movimento.
                    </p>
                </div>
                """

                return html_gif, arquivo_tmp.name

            return f"""
            <div class="gif-card error">
                <h3>Erro ao gerar GIF</h3>
                <p>Status HTTP: {response.status_code}</p>
            </div>
            """, None

        except Exception as e:
            return f"""
            <div class="gif-card error">
                <h3>Erro de comunicação</h3>
                <p>{html.escape(str(e))}</p>
            </div>
            """, None


def ver_historico():
    try:
        response = requests.get(f"{API_ARMAZENAMENTO}/historico")

        if response.status_code == 200:
            dados = response.json().get("historico", [])

            if not dados:
                return [["Nenhum arquivo", "-", "-"]]

            return [
                [item["nome_arquivo"], item["rotulo"], item["data_hora"]]
                for item in dados
            ]

        return [["Erro ao buscar histórico", "-", "-"]]

    except Exception as e:
        return [[f"Erro: {str(e)}", "-", "-"]]


css = """
:root {
    --bg-1: #f6f8fc;
    --bg-2: #eef3ff;
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --text: #111827;
    --muted: #6b7280;
    --card: rgba(255, 255, 255, 0.92);
    --border: #e5e7eb;
    --success: #0f9f6e;
    --shadow: 0 20px 60px rgba(17, 24, 39, 0.10);
    --radius: 24px;
}

.gradio-container {
    max-width: 1200px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 20px !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
    background:
        radial-gradient(circle at top left, #dbeafe 0%, transparent 28%),
        radial-gradient(circle at top right, #e9d5ff 0%, transparent 24%),
        linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

footer {
    display: none !important;
}

.hero {
    background: linear-gradient(135deg, rgba(79,70,229,0.95), rgba(37,99,235,0.92));
    border-radius: 28px;
    padding: 38px 34px;
    color: white;
    box-shadow: 0 18px 50px rgba(79, 70, 229, 0.28);
    margin-bottom: 24px;
}

.hero h1 {
    margin: 0 0 10px 0;
    font-size: 40px;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -0.02em;
}

.hero p {
    margin: 0;
    max-width: 760px;
    font-size: 17px;
    opacity: 0.95;
    line-height: 1.6;
}

.section-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 8px 0 14px 4px;
}

.card-wrap {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 18px;
    backdrop-filter: blur(12px);
    width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

.upload-card,
.result-panel,
.history-card,
.table-wrap,
.gif-panel {
    width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

.image-frame {
    border: 2px dashed #c7d2fe !important;
    border-radius: 20px !important;
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
}

button.primary-btn,
button.secondary-btn {
    border: none !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 14px 18px !important;
    min-height: 54px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

button.primary-btn {
    background: linear-gradient(135deg, var(--primary), #2563eb) !important;
    color: white !important;
}

button.secondary-btn {
    background: white !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

.result-box,
.gif-box {
    min-height: 320px;
    width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
}

.result-card,
.gif-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #dbe4ff;
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 14px 30px rgba(37, 99, 235, 0.08);
}

.result-card h3,
.gif-card h3 {
    margin: 8px 0 18px 0;
    font-size: 22px;
    color: var(--text);
}

.result-badge,
.gif-badge {
    display: inline-block;
    background: #eef2ff;
    color: #4338ca;
    font-size: 12px;
    font-weight: 700;
    padding: 8px 12px;
    border-radius: 999px;
}

.result-line {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    padding: 12px 0;
    border-bottom: 1px solid #edf2f7;
}

.result-label {
    color: var(--muted);
    font-weight: 600;
}

.result-value {
    color: var(--text);
    font-weight: 800;
    text-align: right;
}

.result-value.success {
    color: var(--success);
}

.description-box {
    margin-top: 18px;
    padding: 16px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
}

.description-box.secondary {
    background: #ffffff;
    border-left: 4px solid #2563eb;
}

.description-box h4 {
    margin: 0 0 10px 0;
    color: #111827;
    font-size: 16px;
}

.description-box p {
    margin: 0;
    color: #374151;
    line-height: 1.7;
    font-size: 14px;
}

.top3-box {
    margin-top: 20px;
    padding: 16px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
}

.top3-box h4 {
    margin: 0 0 12px 0;
    color: var(--text);
    font-size: 16px;
}

.top-item {
    display: grid;
    grid-template-columns: 50px 1fr auto;
    gap: 10px;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #e5e7eb;
}

.top-item:last-child {
    border-bottom: none;
}

.top-original {
    font-size: 12px;
    color: #6b7280;
    margin: -4px 0 8px 60px;
}

.top-rank {
    font-weight: 800;
    color: #4338ca;
}

.top-label {
    color: var(--text);
    font-weight: 600;
}

.top-score {
    color: #2563eb;
    font-weight: 800;
}

.accessible-summary {
    margin-top: 18px;
    padding: 16px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #4f46e5;
    border-radius: 16px;
    color: #111827;
    line-height: 1.6;
    font-size: 14px;
}

.gif-preview {
    width: 100%;
    max-height: 360px;
    object-fit: contain;
    border-radius: 18px;
    border: 1px solid #dbe4ff;
    background: #ffffff;
    display: block;
    margin-top: 14px;
}

.gif-tip {
    margin: 14px 0 0 0;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
}

.result-empty,
.gif-empty {
    background: #fff;
    border: 2px dashed #d1d5db;
    border-radius: 20px;
    padding: 28px;
    color: var(--muted);
    text-align: center;
    font-size: 16px;
}

.error {
    border-color: #fecaca;
    background: #fff7f7;
}

.table-wrap {
    overflow-x: auto !important;
}

.table-wrap table {
    width: 100% !important;
    table-layout: fixed !important;
}

.table-wrap th,
.table-wrap td {
    white-space: normal !important;
    word-break: break-word !important;
    overflow-wrap: anywhere !important;
    vertical-align: top !important;
    font-size: 14px !important;
}

.table-wrap th:nth-child(1),
.table-wrap td:nth-child(1) {
    width: 34% !important;
}

.table-wrap th:nth-child(2),
.table-wrap td:nth-child(2) {
    width: 42% !important;
}

.table-wrap th:nth-child(3),
.table-wrap td:nth-child(3) {
    width: 24% !important;
}

@media (max-width: 900px) {
    .gradio-container {
        padding: 14px !important;
    }

    .hero {
        padding: 22px 16px !important;
        border-radius: 20px !important;
    }

    .hero h1 {
        font-size: 28px !important;
        line-height: 1.15 !important;
    }

    .hero p {
        font-size: 15px !important;
    }

    .card-wrap {
        padding: 12px !important;
    }

    .result-line {
        flex-direction: column !important;
        align-items: flex-start !important;
    }

    .result-value {
        text-align: left !important;
    }

    .top-item {
        grid-template-columns: 1fr !important;
    }

    .top-original {
        margin: 4px 0 10px 0 !important;
    }
}
"""

theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
    radius_size="lg",
    text_size="md",
)

with gr.Blocks(css=css, theme=theme, title="Reconhecimento de Imagens") as demo:
    gr.HTML("""
    <div class="hero">
        <h1>Reconhecimento de Imagens com IA</h1>
        <p>
            Envie uma imagem, receba a classificação gerada por inteligência artificial,
            veja uma descrição automática da cena, gere um GIF animado e acompanhe o histórico das últimas análises.
        </p>
    </div>
    """)

    gr.HTML('<div class="section-title">Painel principal</div>')

    with gr.Row(equal_height=True):
        with gr.Column(scale=6, min_width=420, elem_classes=["card-wrap", "upload-card"]):
            imagem = gr.Image(
                type="filepath",
                label="Escolha uma imagem",
                elem_classes=["image-frame"]
            )

        with gr.Column(scale=4, min_width=360, elem_classes=["card-wrap", "result-panel"]):
            resultado = gr.HTML(
                """
                <div class="result-empty">
                    O resultado da análise vai aparecer aqui.
                </div>
                """,
                label="Resultado",
                elem_classes=["result-box"]
            )
            texto_acessivel = gr.Textbox(visible=False)

    with gr.Row():
        botao_analisar = gr.Button("Analisar imagem", elem_classes=["primary-btn"])
        botao_gerar_gif = gr.Button("✨ Gerar GIF animado", elem_classes=["primary-btn"])

    with gr.Row():
        botao_ouvir = gr.Button("🔊 Ouvir resultado", elem_classes=["secondary-btn"])
        botao_parar = gr.Button("⏹ Parar leitura", elem_classes=["secondary-btn"])
        botao_historico = gr.Button("Ver histórico", elem_classes=["secondary-btn"])

    gr.HTML('<div class="section-title" style="margin-top: 24px;">GIF animado</div>')

    with gr.Row(equal_height=True):
        with gr.Column(scale=7, min_width=420, elem_classes=["card-wrap", "gif-panel"]):
            gif_preview = gr.HTML(
                """
                <div class="gif-empty">
                    A prévia do GIF vai aparecer aqui.
                </div>
                """,
                label="Prévia do GIF",
                elem_classes=["gif-box"]
            )

        with gr.Column(scale=3, min_width=280, elem_classes=["card-wrap", "gif-panel"]):
            gif_arquivo = gr.File(label="Baixar GIF gerado")

    gr.HTML('<div class="section-title" style="margin-top: 24px;">Últimas análises</div>')

    with gr.Column(elem_classes=["card-wrap", "history-card", "table-wrap"]):
        historico = gr.Dataframe(
            headers=["Nome do arquivo", "Rótulo", "Data/Hora"],
            datatype=["str", "str", "str"],
            row_count=10,
            column_count=3,
            label=None
        )

    botao_analisar.click(
        fn=analisar_imagem,
        inputs=imagem,
        outputs=[resultado, texto_acessivel]
    )

    botao_gerar_gif.click(
        fn=gerar_gif,
        inputs=imagem,
        outputs=[gif_preview, gif_arquivo]
    )

    botao_historico.click(
        fn=ver_historico,
        inputs=None,
        outputs=historico
    )

    botao_ouvir.click(
        fn=None,
        inputs=[texto_acessivel],
        outputs=None,
        js="""
        (texto) => {
            if (!texto || !texto.trim()) return;

            window.speechSynthesis.cancel();

            const fala = new SpeechSynthesisUtterance(texto);
            fala.lang = "pt-BR";
            fala.rate = 1.0;
            fala.pitch = 1.0;
            fala.volume = 1.0;

            const vozes = window.speechSynthesis.getVoices();
            const vozPt =
                vozes.find(v => v.lang && v.lang.toLowerCase().includes("pt-br")) ||
                vozes.find(v => v.lang && v.lang.toLowerCase().startsWith("pt"));

            if (vozPt) fala.voice = vozPt;

            window.speechSynthesis.speak(fala);
        }
        """
    )

    botao_parar.click(
        fn=None,
        inputs=None,
        outputs=None,
        js="() => { window.speechSynthesis.cancel(); }"
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)