import pika, json

params = pika.URLParameters('amqp://192.168.56.100:5672')

def publish(method, body):
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)
    connection.close()