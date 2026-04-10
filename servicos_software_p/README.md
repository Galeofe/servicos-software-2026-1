# VisionAI Studio

<p align="center">
  <strong>Classificação de imagens com IA, histórico inteligente, acessibilidade por voz e geração automática de GIF animado.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue" alt="Python">
  <img src="https://img.shields.io/badge/Gradio-Frontend-orange" alt="Gradio">
  <img src="https://img.shields.io/badge/FastAPI-Backend-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED" alt="Docker">
  <img src="https://img.shields.io/badge/SQLite-Banco%20de%20dados-003B57" alt="SQLite">
  <img src="https://img.shields.io/badge/IA-Vis%C3%A3o%20Computacional-purple" alt="IA">
</p>

---

## Sobre o projeto

O **VisionAI Studio** é uma aplicação distribuída em containers Docker para análise inteligente de imagens.

O sistema foi desenvolvido a partir da estrutura da pasta `servicos_software_p` e possui dois grandes recursos principais:

- **Classificação automática de imagens com inteligência artificial**
- **Geração automática de GIF animado a partir da imagem enviada**

Além disso, a aplicação também oferece:

- histórico persistente de análises;
- leitura em voz do resultado;
- interface visual aprimorada;
- tradução dos rótulos retornados pelo modelo.

---

## Funcionalidades principais

### Classificação inteligente de imagens
A aplicação analisa a imagem enviada pelo usuário e exibe:

- rótulo principal identificado;
- rótulo original retornado pelo modelo;
- top 3 previsões com porcentagens;
- status do armazenamento no banco de dados.

### Geração automática de GIF animado
A aplicação também gera um **GIF animado** automaticamente a partir da imagem enviada, criando uma animação suave com efeito visual de movimento.

### Histórico persistente
Todas as análises são registradas em banco SQLite com:

- nome do arquivo;
- rótulo identificado;
- data e hora da análise.

### Recurso de acessibilidade
Após a análise, o sistema pode **ler o resultado em voz alta** diretamente no navegador.

---

## Arquitetura da aplicação

```text
Usuário
   |
   v
gradio-visao (frontend)
   |
   v
api-visao (backend de classificação + geração de GIF)
   |
   v
api-armazenamento (persistência de arquivos e banco SQLite)