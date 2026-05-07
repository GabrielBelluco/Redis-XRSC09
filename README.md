# Seminario Redis - Sistemas Distribuidos

Tema: Redis - Data Sharing / PubSub

## Objetivo

Demonstrar a comunicacao entre processos distribuidos utilizando Redis como middleware.

## Funcionalidades do prototipo

1. Resposta a uma mensagem de texto
2. Alteracao de um arquivo texto no servidor
3. Calculo de funcoes

## Tecnologias

- Python
- Redis
- Docker

## Como executar

### 1. Subir o Redis

No notebook que vai hospedar o Redis:

```bash
docker compose up -d
```

Verifique se esta rodando:

```bash
docker ps
```

### 2. Instalar dependencias

Em cada notebook que for rodar algum script Python:

```bash
python -m pip install -r requirements.txt
```

### 3. Configurar o Redis

Copie o arquivo de exemplo para `.env`:

```powershell
Copy-Item .env.example .env
```

No notebook servidor, deixe o `.env` assim:

```text
REDIS_HOST=localhost
REDIS_PORT=6379
```

No notebook cliente, coloque o IP do notebook servidor:

```text
REDIS_HOST=IP_DO_NOTEBOOK_SERVIDOR
REDIS_PORT=6379
```

Exemplo:

```text
REDIS_HOST=192.168.0.8
REDIS_PORT=6379
```

Se mudar de rede, basta trocar o `REDIS_HOST` do `.env` no notebook cliente.

### 4. Rodar em um unico notebook

Em um terminal:

```bash
python Server/Server.py
```

Em outro terminal:

```bash
python Client/Client.py
```

### 5. Rodar em dois notebooks

No notebook servidor, suba o Redis e rode o servidor:

```bash
docker compose up -d
python Server/Server.py
```

No notebook cliente, rode:

```bash
python -m pip install -r requirements.txt
python Client/Client.py
```

O cliente usa o `REDIS_HOST` configurado no arquivo `.env`.

## Configuracao

Os scripts leem `REDIS_HOST` e `REDIS_PORT` do arquivo `.env`.

Como `.env` esta no `.gitignore`, cada notebook pode ter seu proprio IP sem
alterar o codigo.

Se `REDIS_HOST` ou `REDIS_PORT` nao estiverem definidos, o programa mostra erro
e encerra.
