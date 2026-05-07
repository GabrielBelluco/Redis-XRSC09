import time
from datetime import datetime

try:
    from Server.common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        handle_processing,
        claim_pending,
        REQUESTS_STREAM,
        FILE_GROUP,
    )
except ModuleNotFoundError:
    from common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        handle_processing,
        claim_pending,
        REQUESTS_STREAM,
        FILE_GROUP,
    )

r = get_redis()
log = setup_logging("file_worker")

ensure_consumer_group(r, REQUESTS_STREAM, FILE_GROUP)
CONSUMER_NAME = f"file-{int(time.time()) % 10000}"

# NOTE: This worker is designed for single-instance execution (no distributed lock).
# Running multiple instances will cause concurrent writes to arquivo_servidor.txt.


def process_file(msg_data):
    texto = msg_data.get("content", "")
    with open("arquivo_servidor.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {texto}\n")
    return "Arquivo texto do servidor atualizado com sucesso."


def process_message(msg_id, msg_data):
    if msg_data.get("operation") != "file":
        r.xack(REQUESTS_STREAM, FILE_GROUP, msg_id)
        return

    try:
        handle_processing(r, msg_id, msg_data, FILE_GROUP, CONSUMER_NAME, process_file, log)
    except Exception as e:
        log("error", "Failed to process message", msg_id=msg_id, error=str(e))


log("info", "File worker started (single instance)", group=FILE_GROUP, consumer=CONSUMER_NAME)

while True:
    try:
        entries = r.xreadgroup(
            groupname=FILE_GROUP,
            consumername=CONSUMER_NAME,
            streams={REQUESTS_STREAM: ">"},
            count=10,
            block=1000,
        )
        for _, msgs in entries:
            for msg_id, data in msgs:
                process_message(msg_id, data)

        pending = claim_pending(r, REQUESTS_STREAM, FILE_GROUP, CONSUMER_NAME)
        for msg_id, data in pending:
            process_message(msg_id, data)
    except Exception as e:
        log("error", "Worker loop error", error=str(e))
        time.sleep(1)
