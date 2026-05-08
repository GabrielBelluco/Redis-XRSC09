import json
import socket
from pathlib import Path

import redis

from data_sharing import salvar_resultado_compartilhado
from operations.calc_operation import processar_calculo
from operations.file_operation import processar_arquivo
from operations.message_operation import processar_mensagem


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


def enviar_resposta(request_id, status, result_key):
    resposta = {
        "request_id": request_id,
        "status": status,
        "result_key": result_key,
    }
    r.publish(RESPONSE_CHANNEL, json.dumps(resposta, ensure_ascii=False))


def processar_requisicao(data):
    operation = data.get("operation")

    if operation == "message":
        return processar_mensagem(data)

    if operation == "file":
        return processar_arquivo(data)

    if operation == "calc":
        return processar_calculo(data)

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
        operation = None
        try:
            data = json.loads(message["data"])
            request_id = data.get("request_id")
            operation = data.get("operation")

            if not request_id:
                raise ValueError("Requisicao sem request_id.")

            print(f"Recebido: {data}")
            resultado = processar_requisicao(data)
            result_key = salvar_resultado_compartilhado(
                r,
                request_id,
                operation,
                "ok",
                resultado,
            )
            enviar_resposta(request_id, "ok", result_key)

        except json.JSONDecodeError:
            print("Erro: requisicao com JSON invalido.")
        except Exception as erro:
            print(f"Erro ao processar requisicao: {erro}")
            if request_id:
                result_key = salvar_resultado_compartilhado(
                    r,
                    request_id,
                    operation,
                    "erro",
                    f"Erro ao processar requisicao: {erro}",
                )
                enviar_resposta(
                    request_id,
                    "erro",
                    result_key,
                )
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    pubsub.close()
