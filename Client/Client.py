import json
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def enviar_requisicao(requisicao):
    pubsub = r.pubsub()
    pubsub.subscribe('redis_responses')

    r.publish('redis_requests', json.dumps(requisicao, ensure_ascii=False))

    print("Aguardando resposta...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            resposta = json.loads(message['data'])
            print("Resposta do servidor:", resposta['result'])
            pubsub.close()
            break

while True:
    print("\n===== Cliente Redis =====")
    print("1 - Enviar mensagem de texto")
    print("2 - Alterar arquivo texto no servidor")
    print("3 - Realizar cálculo")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        mensagem = input("Digite uma mensagem: ")

        enviar_requisicao({
            "operation": "message",
            "content": mensagem
        })

    elif opcao == "2":
        texto = input("Digite o texto para salvar no arquivo do servidor: ")

        enviar_requisicao({
            "operation": "file",
            "content": texto
        })

    elif opcao == "3":
        a = float(input("Digite o primeiro número: "))
        operador = input("Digite o operador (+, -, *, /): ")
        b = float(input("Digite o segundo número: "))

        enviar_requisicao({
            "operation": "calc",
            "a": a,
            "b": b,
            "operator": operador
        })

    elif opcao == "0":
        print("Cliente encerrado.")
        break

    else:
        print("Opção inválida.")