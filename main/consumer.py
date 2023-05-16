import pika

params = pika.URLParameters('amqps://tdetwkla:LN5DfpbG_YOvHSdSK8PXIjiE4D6aT0_X@dingo.rmq.cloudamqp.com/tdetwkla')

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='main')

def callback(ch, method, properties, body):
    print('Received in main')
    print(body)

channel.basic_consume(queue='main', on_message_callback=callback)

print('Started Consuming')

channel.start_consuming()

channel.close()