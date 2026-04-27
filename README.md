# Seminário Redis - Sistemas Distribuídos

Tema: Redis - Data Sharing / PubSub

## Objetivo
Demonstrar a comunicação entre processos distribuídos utilizando Redis como middleware.

## Funcionalidades do protótipo
1. Resposta a uma mensagem de texto
2. Alteração de um arquivo texto no servidor
3. Cálculo de funções

## Tecnologias
- Python
- Redis
- Docker

# Como Executar
1. Subir o Redis
docker compose up -dusar
Verificar se está rodando:
docker ps
2. Instalar dependências
pip install -r requirements.txt
3. Rodar o servidor
python server/server.py
4. Rodar o cliente
python client/client.py