from datetime import datetime
from pathlib import Path


def processar_arquivo(data):
    conteudo = data.get("content", "")

    file_path = Path("/app/data/file.txt")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{datetime.now()}] {conteudo}\n")

    return "Arquivo file.txt atualizado com sucesso."
