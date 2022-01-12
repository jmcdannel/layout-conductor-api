import os
import paho.mqtt.client as mqtt_client
import simplejson as json
from turnouts import turnoutsapi
# from signals import signalsapi
from effects import effectsapi
from sensors import sensorsapi
from locos import locosapi
from config import config

broker = '192.168.86.243'
port = 1883
topic = "lc_cmd"
# generate client ID with pub prefix randomly
client_id = "mqttTamNorth"
device_id = "traincontrol"

config.initializeInterfaces(device_id)

def connect_mqtt() -> mqtt_client:
    print('connecting')
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            from playsound import playsound
            playsound('sounds/bike-horn-1.wav')
            
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    print('subscribing')
    def on_message(client, userdata, msg):
        parseMessage(msg)

    client.subscribe(topic)
    client.on_message = on_message

def parseMessage(msg):
    print("Received %s", msg.payload.decode())
    print("type %s", type(msg.payload))
    msgStr = msg.payload.decode('utf8').replace("'", '"')
    print('- ' * 20)

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(msgStr)
    effect = data['payload']
    s = json.dumps(data, indent=4, sort_keys=True)
    print(s)
    print(effect['command'])
    # payload = msg.payload
    # print(payload)
    if effect['command'] == 'effect':
        if effect['type'] == 'sound':
            player = config.getInterfaceById(effect['value']['player'])
            print(player.settings['id'])
            print(effect['value']['file'])
            sound = player.interface('sounds/' + effect['value']['file'])
            sound.play()

def run():
    print('running')
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

turnoutsapi.init()
# signalsapi.init()
# effectsapi.init()
# sensorsapi.init()

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
