import json


def processar_history(redis_client):
    try:
        historico = redis_client.lrange("request_history", 0, 9)
    except Exception:
        return "Erro ao buscar historico no Redis."

    if not historico:
        return "Historico vazio."

    linhas = []
    for item in historico:
        try:
            dados = json.loads(item)
        except json.JSONDecodeError:
            continue
        linhas.append(
            f"[{dados.get('processed_at')}] "
            f"{dados.get('operation')} ({dados.get('status')}) - "
            f"{dados.get('result')}"
        )

    return "\n".join(linhas)
