# Projeto Final - Reconhecimento de Imagens com IA

Este projeto foi desenvolvido a partir da estrutura da pasta `servicos_software_p` e implementa uma aplicação distribuída em containers Docker para classificação de imagens com inteligência artificial.

## Visão geral

A aplicação é composta por três containers:

- **gradio-visao**: frontend com interface web para envio de imagens;
- **api-visao**: backend responsável por receber a imagem, executar a classificação com um modelo de visão computacional e retornar o resultado;
- **api-armazenamento**: serviço responsável por salvar a imagem enviada e registrar os dados da análise em banco SQLite.

## Funcionalidades

O sistema permite:

- enviar uma imagem pela interface web;
- classificar automaticamente a imagem com um modelo de IA;
- exibir o **rótulo principal** identificado;
- exibir o **top 3 de previsões** com porcentagens;
- apresentar os resultados de forma mais amigável;
- salvar a imagem enviada em volume compartilhado;
- registrar no banco de dados:
  - nome do arquivo;
  - rótulo identificado;
  - data e hora da análise;
- consultar o histórico das últimas análises realizadas.

## Arquitetura

```text
Usuário
   |
   v
gradio-visao (frontend)
   |
   v
api-visao (backend de classificação)
   |
   v
api-armazenamento (persistência de arquivos e banco SQLite).
```

## Estrutura do projeto

servicos_software_p/
├── api-armazenamento/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── api-visao/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── gradio-visao/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── compose.yaml

## Tecnologias utilizadas

Python
Gradio
FastAPI
Transformers
Pillow
SQLite
Docker Compose

## Como usar

Faça upload de uma imagem;
Clique em Analisar imagem;
Veja o rótulo principal e o top 3 de previsões da IA;
Clique em Ver histórico para consultar as últimas análises salvas.

## Comandos úteis

# Subir os containers
docker compose up
# Subir reconstruindo as imagens
docker compose up --build
# Rodar em segundo plano
docker compose up -d
# Ver logs
docker compose logs -f
# Parar os containers
docker compose down
# Parar e apagar também o volume do banco
docker compose down -v

## Comunicação entre os serviços

O frontend gradio-visao envia a imagem para a API api-visao via REST;
A api-visao classifica a imagem com um modelo de visão computacional;
Em seguida, envia os dados para a api-armazenamento;
A api-armazenamento salva o arquivo no volume compartilhado e registra os dados no banco SQLite;
O resultado é devolvido ao frontend.

## Modelo utilizado

O projeto utiliza um modelo de visão computacional de terceiros para classificação de imagens, atendendo à proposta da atividade.

## Resultado esperado

Após enviar uma imagem, o sistema deve exibir:

o rótulo principal;
o top 3 de previsões com porcentagem;
o status do salvamento no banco;
o histórico das últimas análises.

## Autor

Projeto desenvolvido para a disciplina, com base no repositório fornecido pelo professor e adaptado para a entrega final.