import pika

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    print("Conexión exitosa a RabbitMQ")
    connection.close()
except pika.exceptions.AMQPConnectionError:
    print("Error al conectar con RabbitMQ")
