import pika, json

params = pika.URLParameters('amqps://tdetwkla:LN5DfpbG_YOvHSdSK8PXIjiE4D6aT0_X@dingo.rmq.cloudamqp.com/tdetwkla')

connection = pika.BlockingConnection(params)

channel = connection.channel()

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)