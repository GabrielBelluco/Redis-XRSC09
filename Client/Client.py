import json
import uuid
import redis
from datetime import datetime

from Server.common import (
    get_redis,
    setup_logging,
    ensure_consumer_group,
    REQUESTS_STREAM,
    RESPONSES_STREAM,
    CLIENT_GROUP,
)

r = get_redis()
log = setup_logging("client")

ensure_consumer_group(r, RESPONSES_STREAM, CLIENT_GROUP)

CONSUMER_NAME = f"client-{uuid.uuid4().hex[:8]}"


def send_request(operation, **kwargs):
    request_id = str(uuid.uuid4())
    payload = {
        "request_id": request_id,
        "reply_to": RESPONSES_STREAM,
        "operation": operation,
        **kwargs,
    }
    r.xadd(REQUESTS_STREAM, payload)
    log("info", "Request sent", request_id=request_id, operation=operation)
    return request_id


def wait_for_response(request_id, timeout_ms=10000):
    end_time = datetime.now().timestamp() * 1000 + timeout_ms
    while datetime.now().timestamp() * 1000 < end_time:
        entries = r.xreadgroup(
            groupname=CLIENT_GROUP,
            consumername=CONSUMER_NAME,
            streams={RESPONSES_STREAM: ">"},
            count=10,
            block=1000,
        )
        for _, msgs in entries:
            for msg_id, data in msgs:
                r.xack(RESPONSES_STREAM, CLIENT_GROUP, msg_id)
                if data.get("request_id") == request_id:
                    return data
    return None


while True:
    print("\n===== Cliente Redis (Streams) =====")
    print("1 - Enviar mensagem de texto")
    print("2 - Alterar arquivo texto no servidor")
    print("3 - Realizar cálculo")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        mensagem = input("Digite uma mensagem: ")
        rid = send_request("message", content=mensagem)
        resp = wait_for_response(rid)
        if resp:
            print("Resposta do servidor:", resp.get("result"))
        else:
            print("Timeout: nenhuma resposta recebida.")

    elif opcao == "2":
        texto = input("Digite o texto para salvar no arquivo do servidor: ")
        rid = send_request("file", content=texto)
        resp = wait_for_response(rid)
        if resp:
            print("Resposta do servidor:", resp.get("result"))
        else:
            print("Timeout: nenhuma resposta recebida.")

    elif opcao == "3":
        a = float(input("Digite o primeiro número: "))
        operador = input("Digite o operador (+, -, *, /): ")
        b = float(input("Digite o segundo número: "))
        rid = send_request("calc", a=a, b=b, operator=operador)
        resp = wait_for_response(rid)
        if resp:
            print("Resposta do servidor:", resp.get("result"))
        else:
            print("Timeout: nenhuma resposta recebida.")

    elif opcao == "0":
        print("Cliente encerrado.")
        break

    else:
        print("Opção inválida.")
