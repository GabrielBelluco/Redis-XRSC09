import time

from Server.common import (
    get_redis,
    setup_logging,
    ensure_consumer_group,
    handle_processing,
    claim_pending,
    REQUESTS_STREAM,
    MESSAGE_GROUP,
)

r = get_redis()
log = setup_logging("message_worker")

ensure_consumer_group(r, REQUESTS_STREAM, MESSAGE_GROUP)
CONSUMER_NAME = f"message-{int(time.time()) % 10000}"


def process_message_op(msg_data):
    content = msg_data.get("content", "")
    return f"Mensagem recebida pelo servidor: {content}"


def process_message(msg_id, msg_data):
    if msg_data.get("operation") != "message":
        r.xack(REQUESTS_STREAM, MESSAGE_GROUP, msg_id)
        return

    try:
        handle_processing(r, msg_id, msg_data, MESSAGE_GROUP, CONSUMER_NAME, process_message_op, log)
    except Exception as e:
        log("error", "Failed to process message", msg_id=msg_id, error=str(e))


log("info", "Message worker started", group=MESSAGE_GROUP, consumer=CONSUMER_NAME)

while True:
    try:
        entries = r.xreadgroup(
            groupname=MESSAGE_GROUP,
            consumername=CONSUMER_NAME,
            streams={REQUESTS_STREAM: ">"},
            count=10,
            block=1000,
        )
        for _, msgs in entries:
            for msg_id, data in msgs:
                process_message(msg_id, data)

        pending = claim_pending(r, REQUESTS_STREAM, MESSAGE_GROUP, CONSUMER_NAME)
        for msg_id, data in pending:
            process_message(msg_id, data)
    except Exception as e:
        log("error", "Worker loop error", error=str(e))
        time.sleep(1)
