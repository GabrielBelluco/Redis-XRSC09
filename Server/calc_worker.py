import time

try:
    from Server.common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        handle_processing,
        claim_pending,
        REQUESTS_STREAM,
        CALC_GROUP,
    )
except ModuleNotFoundError:
    from common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        handle_processing,
        claim_pending,
        REQUESTS_STREAM,
        CALC_GROUP,
    )

r = get_redis()
log = setup_logging("calc_worker")

ensure_consumer_group(r, REQUESTS_STREAM, CALC_GROUP)
CONSUMER_NAME = f"calc-{int(time.time()) % 10000}"


def process_calc(msg_data):
    a = float(msg_data["a"])
    b = float(msg_data["b"])
    operator = msg_data["operator"]

    if operator == "+":
        result = a + b
    elif operator == "-":
        result = a - b
    elif operator == "*":
        result = a * b
    elif operator == "/":
        if b == 0:
            raise ValueError("Nao e possivel dividir por zero.")
        result = a / b
    else:
        raise ValueError("Operador invalido.")

    return f"Resultado: {a} {operator} {b} = {result}"


def process_message(msg_id, msg_data):
    if msg_data.get("operation") != "calc":
        r.xack(REQUESTS_STREAM, CALC_GROUP, msg_id)
        return

    try:
        handle_processing(r, msg_id, msg_data, CALC_GROUP, CONSUMER_NAME, process_calc, log)
    except Exception as e:
        log("error", "Failed to process message", msg_id=msg_id, error=str(e))


log("info", "Calc worker started", group=CALC_GROUP, consumer=CONSUMER_NAME)

while True:
    try:
        entries = r.xreadgroup(
            groupname=CALC_GROUP,
            consumername=CONSUMER_NAME,
            streams={REQUESTS_STREAM: ">"},
            count=10,
            block=1000,
        )
        for _, msgs in entries:
            for msg_id, data in msgs:
                process_message(msg_id, data)

        pending = claim_pending(r, REQUESTS_STREAM, CALC_GROUP, CONSUMER_NAME)
        for msg_id, data in pending:
            process_message(msg_id, data)
    except Exception as e:
        log("error", "Worker loop error", error=str(e))
        time.sleep(1)
