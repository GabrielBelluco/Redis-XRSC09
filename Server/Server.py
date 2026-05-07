import json
import socket
from datetime import datetime
from pathlib import Path

import redis


def carregar_config():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        print("Erro: arquivo .env nao encontrado.")
        raise SystemExit(1)

    config = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    if "REDIS_HOST" not in config or "REDIS_PORT" not in config:
        print("Erro: .env precisa ter REDIS_HOST e REDIS_PORT.")
        raise SystemExit(1)

    return config["REDIS_HOST"], int(config["REDIS_PORT"])


REDIS_HOST, REDIS_PORT = carregar_config()

REQUEST_CHANNEL = "redis_requests"
RESPONSE_CHANNEL = "redis_responses"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def obter_ips_locais():
    ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except socket.gaierror:
        pass
    return ips


def enviar_resposta(request_id, status, result):
    resposta = {
        "request_id": request_id,
        "status": status,
        "result": result,
    }
    r.publish(RESPONSE_CHANNEL, json.dumps(resposta, ensure_ascii=False))


def salvar_em_arquivo(texto):
    with open("arquivo_servidor.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{datetime.now()}] {texto}\n")


def calcular(a, b, operador):
    if operador == "+":
        return a + b
    if operador == "-":
        return a - b
    if operador == "*":
        return a * b
    if operador == "/":
        if b == 0:
            raise ValueError("Nao e possivel dividir por zero.")
        return a / b
    raise ValueError("Operador invalido.")


def processar_requisicao(data):
    operation = data.get("operation")

    if operation == "message":
        conteudo = data.get("content", "")
        return f"Mensagem recebida pelo servidor: {conteudo}"

    if operation == "file":
        conteudo = data.get("content", "")
        salvar_em_arquivo(conteudo)
        return "Arquivo texto do servidor atualizado com sucesso."

    if operation == "calc":
        a = float(data["a"])
        b = float(data["b"])
        operador = data["operator"]
        resultado = calcular(a, b, operador)
        return f"Resultado: {a} {operador} {b} = {resultado}"

    raise ValueError("Operacao invalida.")


try:
    r.ping()
except redis.exceptions.RedisError as erro:
    print(f"Erro: nao foi possivel conectar ao Redis em {REDIS_HOST}:{REDIS_PORT}.")
    print(f"Detalhes: {erro}")
    raise SystemExit(1)


pubsub = r.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe(REQUEST_CHANNEL)

print(f"Servidor Pub/Sub conectado em {REDIS_HOST}:{REDIS_PORT}.")
ips_locais = obter_ips_locais()
if ips_locais:
    print("IPs deste notebook para usar no .env do cliente:", ", ".join(ips_locais))
print(f"Aguardando mensagens no canal '{REQUEST_CHANNEL}'...")

try:
    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        request_id = None
        try:
            data = json.loads(message["data"])
            request_id = data.get("request_id")

            if not request_id:
                raise ValueError("Requisicao sem request_id.")

            print(f"Recebido: {data}")
            resultado = processar_requisicao(data)
            enviar_resposta(request_id, "ok", resultado)

        except json.JSONDecodeError:
            print("Erro: requisicao com JSON invalido.")
        except Exception as erro:
            print(f"Erro ao processar requisicao: {erro}")
            if request_id:
                enviar_resposta(
                    request_id,
                    "erro",
                    f"Erro ao processar requisicao: {erro}",
                )
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    pubsub.close()
