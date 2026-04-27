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

## Como Executar

### 1. Subir o Redis

```bash
docker compose up -d
```

Verificar se está rodando:

```bash
docker ps
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o servidor

```bash
python server/server.py
```

### 4. Rodar o cliente

```bash
python client/client.py
```