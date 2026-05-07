import json
from datetime import datetime

RESULT_TTL_SECONDS = 300
HISTORY_KEY = "historico_requisicoes"
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
