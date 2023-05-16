import pika

params = pika.URLParameters('amqps://tdetwkla:LN5DfpbG_YOvHSdSK8PXIjiE4D6aT0_X@dingo.rmq.cloudamqp.com/tdetwkla')

connection = pika.BlockingConnection(params)

channel = connection.channel()

def publish():
    channel.basic_publish(exchange='', routing_key='admin', body='hello')
