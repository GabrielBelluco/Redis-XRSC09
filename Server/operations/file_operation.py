from datetime import datetime


def processar_arquivo(data):
    conteudo = data.get("content", "")

    with open("arquivo_servidor.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{datetime.now()}] {conteudo}\n")

    return "Arquivo texto do servidor atualizado com sucesso."
