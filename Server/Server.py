import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('redis_requests')

print("Servidor aguardando mensagens...")

for message in pubsub.listen():
    if message['type'] == 'message':
        data = message['data']
        print(f"Recebido: {data}")

        resposta = f"Mensagem recebida: {data}"
        r.publish('redis_responses', resposta)