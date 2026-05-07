import json

import redis

from config import carregar_config
from data_sharing import salvar_resultado_compartilhado
from operations.file_operation import processar_arquivo


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

try:
    r.ping()
except redis.exceptions.RedisError as erro:
    print(f"Erro: nao foi possivel conectar ao Redis em {REDIS_HOST}:{REDIS_PORT}.")
    print(f"Detalhes: {erro}")
    raise SystemExit(1)

pubsub = r.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe(REQUEST_CHANNEL)

print(f"file_worker conectado em {REDIS_HOST}:{REDIS_PORT}.")
print(f"Aguardando mensagens no canal '{REQUEST_CHANNEL}'...")

try:
    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])
            request_id = data.get("request_id")
            operation = data.get("operation")

            if operation != "file":
                continue

            if not request_id:
                raise ValueError("Requisicao sem request_id.")

            print(f"file_worker recebido: {data}")
            resultado = processar_arquivo(data)
            result_key = salvar_resultado_compartilhado(
                r, request_id, operation, "ok", resultado
            )

            resposta = {
                "request_id": request_id,
                "status": "ok",
                "result_key": result_key,
            }
            r.publish(RESPONSE_CHANNEL, json.dumps(resposta, ensure_ascii=False))

        except json.JSONDecodeError:
            print("Erro: requisicao com JSON invalido.")
        except Exception as erro:
            print(f"Erro ao processar requisicao: {erro}")
            if request_id:
                result_key = salvar_resultado_compartilhado(
                    r, request_id, operation, "erro", f"Erro: {erro}"
                )
                resposta = {
                    "request_id": request_id,
                    "status": "erro",
                    "result_key": result_key,
                }
                r.publish(RESPONSE_CHANNEL, json.dumps(resposta, ensure_ascii=False))

except KeyboardInterrupt:
    print("\nfile_worker encerrado.")
finally:
    pubsub.close()
