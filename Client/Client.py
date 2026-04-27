import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('redis_responses')

mensagem = input("Digite uma mensagem: ")
r.publish('redis_requests', mensagem)

print("Aguardando resposta...")

for message in pubsub.listen():
    if message['type'] == 'message':
        print("Resposta do servidor:", message['data'])
        break