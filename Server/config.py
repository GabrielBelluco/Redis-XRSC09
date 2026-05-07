import os
from pathlib import Path


def carregar_config():
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")

    if redis_host and redis_port:
        return redis_host, int(redis_port)

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        print("Erro: arquivo .env nao encontrado e variaveis de ambiente REDIS_HOST/REDIS_PORT nao definidas.")
        raise SystemExit(1)

    config = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    if "REDIS_HOST" not in config or "REDIS_PORT" not in config:
        print("Erro: .env precisa ter REDIS_HOST e REDIS_PORT.")
        raise SystemExit(1)

    return config["REDIS_HOST"], int(config["REDIS_PORT"])
