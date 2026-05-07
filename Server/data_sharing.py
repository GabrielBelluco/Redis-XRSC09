import json
from datetime import datetime

RESULT_TTL_SECONDS = 300
HISTORY_KEY = "request_history"
HISTORY_LIMIT = 10


def salvar_resultado_compartilhado(redis_client, request_id, operation, status, result):
    result_key = f"resultado:{request_id}"
    dados = {
        "request_id": request_id,
        "operation": operation or "desconhecida",
        "status": status,
        "result": result,
        "result_key": result_key,
        "processed_at": datetime.now().isoformat(timespec="seconds"),
    }

    pipe = redis_client.pipeline()
    pipe.hset(result_key, mapping=dados)
    pipe.expire(result_key, RESULT_TTL_SECONDS)
    pipe.lpush(HISTORY_KEY, json.dumps(dados, ensure_ascii=False))
    pipe.ltrim(HISTORY_KEY, 0, HISTORY_LIMIT - 1)
    pipe.execute()

    return result_key


def set_last_calc(redis_client, result):
    redis_client.set("last_calc", result)


def set_last_message(redis_client, message):
    redis_client.set("last_message", message)


def increment_calc_requests(redis_client):
    redis_client.incr("calc_requests")
