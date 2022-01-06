import os
import paho.mqtt.client as mqtt_client

broker = '192.168.86.243'
port = 1883
topic = "/turnouts"
# generate client ID with pub prefix randomly
client_id = "mqttTamNorth"


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()

# def on_message(client, userdata, message):
#     print("message received " ,str(message.payload.decode("utf-8")))
#     print("message topic=",message.topic)
#     print("message qos=",message.qos)
#     print("message retain flag=",message.retain)


# def on_log(client, userdata, level, buf):
#   print("log: ", buf)

# def on_connect(client, userdata, flags, rc):

#     def on_message(client, userdata, msg):
#         print(msg.topic+" "+str(msg.payload))

#     print("Connected with result code "+str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     ret = client.subscribe('/turnouts')
#     print("Subscribed return = " + str(ret))
#     client.on_message=on_message


# print("Creating new MQTT instance")


# client = mqtt.Client("mqttMain") #create new instance
# client.on_connect=on_connect
# client.on_log=on_log
# print("Connecting to MQTT broker")
# client.connect("192.168.86.243") #connect to broker
# client.loop_forever()
    
# print('Loaded MQTT')
# config.initializeMQTT()
