import pika, json

params = pika.URLParameters('amqp://rabbitmq-svc.default.svc.cluster.local:5672')

def publish(method, body):
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)
    connection.close()