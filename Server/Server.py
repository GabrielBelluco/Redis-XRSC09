import json
import redis
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('redis_requests')

print("Servidor aguardando mensagens...")

def enviar_resposta(status, result):
    resposta = {
        "status": status,
        "result": result
    }

    r.publish('redis_responses', json.dumps(resposta, ensure_ascii=False))

def salvar_em_arquivo(texto):
    with open("arquivo_servidor.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{datetime.now()}] {texto}\n")

def calcular(a, b, operador):
    if operador == "+":
        return a + b
    elif operador == "-":
        return a - b
    elif operador == "*":
        return a * b
    elif operador == "/":
        if b == 0:
            raise ValueError("Não é possível dividir por zero.")
        return a / b
    else:
        raise ValueError("Operador inválido.")

for message in pubsub.listen():
    if message['type'] == 'message':
        try:
            data = json.loads(message['data'])
            print(f"Recebido: {data}")

            operation = data.get("operation")

            if operation == "message":
                conteudo = data.get("content", "")
                enviar_resposta(
                    "ok",
                    f"Mensagem recebida pelo servidor: {conteudo}"
                )

            elif operation == "file":
                conteudo = data.get("content", "")
                salvar_em_arquivo(conteudo)
                enviar_resposta(
                    "ok",
                    "Arquivo texto do servidor atualizado com sucesso."
                )

            elif operation == "calc":
                a = float(data.get("a"))
                b = float(data.get("b"))
                operador = data.get("operator")

                resultado = calcular(a, b, operador)

                enviar_resposta(
                    "ok",
                    f"Resultado: {a} {operador} {b} = {resultado}"
                )

            else:
                enviar_resposta(
                    "erro",
                    "Operação inválida."
                )

        except Exception as erro:
            enviar_resposta(
                "erro",
                f"Erro ao processar requisição: {erro}"
            )