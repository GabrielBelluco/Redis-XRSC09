def processar_mensagem(data):
    conteudo = data.get("content", "")
    return f"Mensagem recebida pelo servidor: {conteudo}"
