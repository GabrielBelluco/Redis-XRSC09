import json
import os
import time
import uuid

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "192.168.0.8")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

REQUEST_CHANNEL = "redis_requests"
RESPONSE_CHANNEL = "redis_responses"
RESPONSE_TIMEOUT_SECONDS = 10

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def verificar_conexao():
    try:
        r.ping()
    except redis.exceptions.RedisError as erro:
        print(f"Erro: nao foi possivel conectar ao Redis em {REDIS_HOST}:{REDIS_PORT}.")
        print(f"Detalhes: {erro}")
        return False
    return True


def enviar_requisicao(requisicao):
    request_id = str(uuid.uuid4())
    requisicao["request_id"] = request_id

    pubsub = r.pubsub(ignore_subscribe_messages=True)

    try:
        pubsub.subscribe(RESPONSE_CHANNEL)
        r.publish(REQUEST_CHANNEL, json.dumps(requisicao, ensure_ascii=False))
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

            status = resposta.get("status", "erro")
            result = resposta.get("result", "")
            if status == "ok":
                print("Resposta do servidor:", result)
            else:
                print("Erro do servidor:", result)
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

    elif opcao == "0":
        print("Cliente encerrado.")
        break

    else:
        print("Opcao invalida.")
