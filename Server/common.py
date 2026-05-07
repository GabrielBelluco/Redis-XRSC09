import json
import os
import time
import redis
from datetime import datetime

REDIS_HOST = os.getenv("REDIS_HOST", "192.168.0.8")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

REQUESTS_STREAM = "requests_stream"
RESPONSES_STREAM = "responses_stream"
DEAD_LETTER_STREAM = "dead_letter_stream"

CALC_GROUP = "calc_group"
MESSAGE_GROUP = "message_group"
FILE_GROUP = "file_group"
CLIENT_GROUP = "client_group"

IDEMPOTENCY_TTL = 30
RETRY_TTL = 60
MAX_RETRIES = 3
AUTOCLAIM_IDLE_MS = 30000


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def setup_logging(name):
    def log(level, msg, **kwargs):
        entry = {
            "time": datetime.now().isoformat(),
            "worker": name,
            "level": level,
            "message": msg,
        }
        entry.update(kwargs)
        print(json.dumps(entry, ensure_ascii=False))

    return log


def is_duplicate(r, request_id):
    key = f"idempotency:{request_id}"
    created = r.setnx(key, "1")
    if created:
        r.expire(key, IDEMPOTENCY_TTL)
    return not created


def get_retry_count(r, request_id):
    key = f"retry:{request_id}"
    val = r.get(key)
    return int(val) if val else 0


def increment_retry(r, request_id):
    key = f"retry:{request_id}"
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, RETRY_TTL)
    pipe.execute()


def reset_retry(r, request_id):
    r.delete(f"retry:{request_id}")


def move_to_dlq(r, msg_data, error):
    entry = {
        "original_data": json.dumps(msg_data, ensure_ascii=False),
        "error": str(error),
        "failed_at": datetime.now().isoformat(),
    }
    r.xadd(DEAD_LETTER_STREAM, entry)


def ensure_consumer_group(r, stream, group):
    try:
        r.xgroup_create(stream, group, id="0", mkstream=True)
    except redis.exceptions.ResponseError:
        pass


def claim_pending(r, stream, group, consumer, idle_ms=AUTOCLAIM_IDLE_MS):
    try:
        stream_key = stream
        _, entries = r.xautoclaim(stream_key, group, consumer, min_idle_time=idle_ms, count=10)
        return entries if entries else []
    except Exception:
        return []


def handle_processing(r, msg_id, msg_data, group, consumer, process_fn, log):
    request_id = msg_data.get("request_id")

    if not request_id:
        log("error", "Message missing request_id, skipping", msg_id=msg_id)
        r.xack(REQUESTS_STREAM, group, msg_id)
        return

    if is_duplicate(r, request_id):
        log("warn", "Duplicate request_id, skipping", request_id=request_id)
        r.xack(REQUESTS_STREAM, group, msg_id)
        return

    retries = get_retry_count(r, request_id)
    if retries >= MAX_RETRIES:
        log("error", "Max retries reached, moving to DLQ", request_id=request_id, retries=retries)
        move_to_dlq(r, msg_data, f"Max retries ({MAX_RETRIES}) exceeded")
        r.xack(REQUESTS_STREAM, group, msg_id)
        return

    try:
        result = process_fn(msg_data)
        reset_retry(r, request_id)
        response = {
            "request_id": request_id,
            "status": "ok",
            "result": result,
        }
        r.xadd(RESPONSES_STREAM, response)
        log("info", "Processed successfully", request_id=request_id, result=result)
    except Exception as e:
        increment_retry(r, request_id)
        log("error", "Processing failed, will retry", request_id=request_id, error=str(e), retries=retries + 1)
        raise

    r.xack(REQUESTS_STREAM, group, msg_id)
