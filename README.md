# Seminario Redis - Sistemas Distribuidos

Tema: Redis - Data Sharing / PubSub

## Objetivo

Demonstrar a comunicacao entre processos distribuidos utilizando Redis como middleware.

## Funcionalidades do prototipo

1. Resposta a uma mensagem de texto
2. Alteracao de um arquivo texto no servidor (file.txt)
3. Calculo de funcoes matematicas
4. Consulta de historico via Pub/Sub ou direto do Redis

## Arquitetura

- **Pub/Sub puro** (nao usa Redis Streams)
- 3 workers independentes:
  - `calc_worker`: processa operacoes matematicas
  - `message_worker`: processa mensagens de texto e historico
  - `file_worker`: altera arquivo texto
- Data Sharing via Redis: `last_calc`, `last_message`, `request_history`, `calc_requests`

## Tecnologias

- Python 3.12 LTS
- Redis 8.6
- Docker

## Como executar

### 1. Configurar o Redis

Copie o arquivo de exemplo para `.env`:

```bash
cp .env.example .env
```

No servidor, deixe o `.env` assim:

```text
REDIS_HOST=localhost
REDIS_PORT=6379
```

No cliente (outro notebook), coloque o IP do servidor:

```text
REDIS_HOST=IP_DO_SERVIDOR
REDIS_PORT=6379
```

### 2. Rodar em um unico notebook

Terminal 1 (sobe Redis + workers):

```bash
docker compose up -d
```

Terminal 2 (cliente):

```bash
python -m pip install -r requirements.txt
python Client/Client.py
```

### 3. Rodar em dois notebooks

No notebook servidor:

```bash
docker compose up -d
```

No notebook cliente:

```bash
python -m pip install -r requirements.txt
python Client/Client.py
```

O cliente usa o `REDIS_HOST` configurado no arquivo `.env`.

## Configuracao

Os scripts leem `REDIS_HOST` e `REDIS_PORT` do arquivo `.env`.

Como `.env` esta no `.gitignore`, cada maquina pode ter sua propria configuracao sem
alterar o codigo.

Se `REDIS_HOST` ou `REDIS_PORT` nao estiverem definidos, o programa mostra erro
e encerra.


## Toda documentação do trabalho (Relatório e Slides) está presente na pasta "docs"