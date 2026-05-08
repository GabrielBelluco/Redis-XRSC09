import json
import time
import uuid
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
RESPONSE_TIMEOUT_SECONDS = 30
HISTORY_KEY = "request_history"
HISTORY_LIMIT = 10

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=30,
    socket_timeout=30,
)


def verificar_conexao():
    try:
        r.ping()
    except redis.exceptions.RedisError as erro:
        print(f"Erro: nao foi possivel conectar ao Redis em {REDIS_HOST}:{REDIS_PORT}.")
        print(f"Detalhes: {erro}")
        return False
    return True


def buscar_resultado(result_key):
    try:
        return r.hgetall(result_key)
    except redis.exceptions.RedisError as erro:
        print(f"Erro ao buscar resultado compartilhado: {erro}")
        return {}


def enviar_requisicao(requisicao):
    request_id = str(uuid.uuid4())
    requisicao["request_id"] = request_id

    pubsub = r.pubsub(ignore_subscribe_messages=True)

    try:
        pubsub.subscribe(RESPONSE_CHANNEL)
        inscritos = r.publish(REQUEST_CHANNEL, json.dumps(requisicao, ensure_ascii=False))
        print(f"Requisicao publicada em '{REQUEST_CHANNEL}' para {inscritos} inscrito(s).")
        if inscritos == 0:
            print("Aviso: nenhum servidor inscrito no canal de requisicoes.")

        print("Aguardando resposta...")

        fim = time.time() + RESPONSE_TIMEOUT_SECONDS
        while time.time() < fim:
            message = pubsub.get_message(timeout=1)
            if not message:
                continue

            try:
                resposta = json.loads(message["data"])
            except json.JSONDecodeError:
                print("Erro: resposta invalida recebida do servidor.")
                continue

            if resposta.get("request_id") != request_id:
                continue

            result_key = resposta.get("result_key")
            if not result_key:
                print("Erro: servidor nao informou a chave do resultado.")
                return

            dados = buscar_resultado(result_key)
            if not dados:
                print(f"Erro: resultado nao encontrado no Redis ({result_key}).")
                return

            if dados.get("status") == "ok":
                print("Resposta do servidor:", dados.get("result", ""))
            else:
                print("Erro do servidor:", dados.get("result", ""))

            print(f"Resultado salvo no Redis em: {result_key}")
            return

        print("Timeout: nenhuma resposta recebida do servidor.")

    except redis.exceptions.RedisError as erro:
        print(f"Erro de comunicacao com o Redis: {erro}")
    finally:
        pubsub.close()


def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("Valor invalido. Digite um numero.")


if not verificar_conexao():
    raise SystemExit(1)


while True:
    print("\n===== Cliente Redis Pub/Sub =====")
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    print("1 - Enviar mensagem de texto")
    print("2 - Alterar arquivo texto no servidor")
    print("3 - Realizar calculo")
    print("4 - Ver historico")
    print("0 - Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        mensagem = input("Digite uma mensagem: ")
        enviar_requisicao({
            "operation": "message",
            "content": mensagem,
        })

    elif opcao == "2":
        texto = input("Digite o texto para salvar no arquivo do servidor: ")
        enviar_requisicao({
            "operation": "file",
            "content": texto,
        })

    elif opcao == "3":
        a = ler_float("Digite o primeiro numero: ")
        operador = input("Digite o operador (+, -, *, /): ")
        b = ler_float("Digite o segundo numero: ")

        enviar_requisicao({
            "operation": "calc",
            "a": a,
            "b": b,
            "operator": operador,
        })

    elif opcao == "4":
        enviar_requisicao({
            "operation": "history",
        })

    elif opcao == "0":
        print("Cliente encerrado.")
        break

    else:
        print("Opcao invalida.")
