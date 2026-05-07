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

## Como executar na branch atual

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
pip install -r requirements.txt
```

### 3. Rodar em um unico notebook

Abra terminais separados e execute:

```bash
python Server/message_worker.py
```

```bash
python Server/calc_worker.py
```

```bash
python Server/file_worker.py
```

Opcionalmente, para monitorar mensagens que falharam:

```bash
python Server/dlq_monitor.py
```

Em outro terminal, rode o cliente:

```bash
python Client/Client.py
```

### 4. Rodar em dois notebooks

No notebook 1, suba o Redis e rode os workers:

```bash
docker compose up -d
python Server/message_worker.py
python Server/calc_worker.py
python Server/file_worker.py
```

Descubra o IP do notebook 1:

```bash
ipconfig
```

No notebook 2, rode o cliente:

```powershell
python Client/Client.py
```

O codigo esta configurado para conectar por padrao em:

```text
192.168.0.8:6379
```

Se o IP do notebook 1 mudar, voce ainda pode sobrescrever pelo terminal:

```powershell
$env:REDIS_HOST="NOVO_IP_DO_NOTEBOOK_1"
python Client/Client.py
```

Se quiser rodar workers no notebook 2 tambem, use a mesma variavel `REDIS_HOST`
antes de iniciar cada worker.

## Configuracao do Redis

Por padrao, os scripts conectam em:

```text
192.168.0.8:6379
```

Voce pode alterar sem editar o codigo usando variaveis de ambiente:

```powershell
$env:REDIS_HOST="NOVO_IP_DO_NOTEBOOK_1"
$env:REDIS_PORT="6379"
```
