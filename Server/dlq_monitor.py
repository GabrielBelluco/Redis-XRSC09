import time

try:
    from Server.common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        DEAD_LETTER_STREAM,
        CLIENT_GROUP,
    )
except ModuleNotFoundError:
    from common import (
        get_redis,
        setup_logging,
        ensure_consumer_group,
        DEAD_LETTER_STREAM,
        CLIENT_GROUP,
    )

r = get_redis()
log = setup_logging("dlq_monitor")

DLQ_GROUP = "dlq_monitor_group"
ensure_consumer_group(r, DEAD_LETTER_STREAM, DLQ_GROUP)
CONSUMER_NAME = f"dlq-monitor-{int(time.time()) % 10000}"

log("info", "DLQ monitor started", group=DLQ_GROUP, consumer=CONSUMER_NAME)

while True:
    try:
        entries = r.xreadgroup(
            groupname=DLQ_GROUP,
            consumername=CONSUMER_NAME,
            streams={DEAD_LETTER_STREAM: ">"},
            count=10,
            block=2000,
        )
        for _, msgs in entries:
            for msg_id, data in msgs:
                log(
                    "warn",
                    "Dead letter entry",
                    msg_id=msg_id,
                    original_data=data.get("original_data"),
                    error=data.get("error"),
                    failed_at=data.get("failed_at"),
                )
                r.xack(DEAD_LETTER_STREAM, DLQ_GROUP, msg_id)
    except Exception as e:
        log("error", "DLQ monitor loop error", error=str(e))
        time.sleep(1)
