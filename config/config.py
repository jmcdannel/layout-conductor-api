import os
from flask import json, jsonify, request, abort


def getConfig():
  config_path = os.path.dirname(__file__) + '/local/config.json'
  with open(config_path) as json_file:
    data = json.load(json_file)
  return data

def getCurrentConfig():
  config_path = os.path.dirname(__file__) + '/local/config.json'
  with open(config_path) as json_file:
    data = json.load(json_file)
  return data

appConfig = getCurrentConfig()
interfaces = []

def getDeviceById(deviceId):
  return next((device for device in appConfig['devices'] if device['id'] == deviceId), None)

def getDevicesByType(type):
  return (device for device in appConfig['devices'] if device['type'] == type)

def getInterfaceById(ifaceId):
  for iface in interfaces:
    if (iface.id == ifaceId):
      break
  else:
    iface = None
  return iface
  
def getInterfacesByType(type):
  return (iface for iface in interfaces if iface['settings']['type'] == type)

def getInterfaceConfigByDevice(device):
  deviceInterfaces = (iface for iface in appConfig['interfaces'] if iface['device'] == device['id'])
  if ('connectedDevices' in device):
    for connected_device in device['connectedDevices']:
      deviceInterfaces.append((iface for iface in appConfig['interfaces'] if iface['device'] == connected_device['id']))
  
  return deviceInterfaces

def get():
  data = getConfig()
  return jsonify(data)

class LayoutInterface(object):
  def __init__(self, id, settings, interface):
    self.id = id
    self.settings = settings
    self.interface = interface

def on_log(client, userdata, level, buf):
  print("log: ", buf)

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  ret = client.subscribe('/turnouts')
  print("Subscribed return = " + str(ret))

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  
def initializeMQTT():
  
  for interface in appConfig['interfaces']:
    device = getDeviceById(interface['device'])
    # Import paho.mqtt.client Library
    if (interface['type'] == 'mqtt'):
      try:
        import paho.mqtt.client as mqtt #import the client
        print("Creating new MQTT instance")

        

        client = mqtt.Client(interface['id']) #create new instance
        client.on_connect=on_connect
        client.on_message=on_message
        client.on_log=on_log
        print("Connecting to MQTT broker")
        client.connect(interface['address']) #connect to broker
        client.loop_forever()
        interfaces.append(LayoutInterface(interface['id'], interface, client))
        
        print('Loaded MQTT')
        
      except ImportError as error:
        print('MQTTImportError')
        print(error, False)
      except Exception as exception:
        print('MQTT Exception')
        print(exception, False)
        

def initializeApi():

  

  # print(appConfig['interfaces'])


  for interface in appConfig['interfaces']:
    device = getDeviceById(interface['device'])
    
    # Import Arduino Sertal
    if (interface['type'] == 'serial'):
      try:
        import serial
        interfaces.append(LayoutInterface(interface['id'], interface, serial.Serial(interface['serial'], interface['baud'])))
        print('Serial Connection Established...')
      except ImportError as error:
        print('serial ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('serial Exception')
        print(exception, False)

    # Import RPi GPIO
    if (interface['type'] == 'GPIO'):
      try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        interfaces.append(LayoutInterface(interface['id'], interface, GPIO))
        print('GPIO Mode set to BOARD')
      except ImportError as error:
        print('RPi.GPIO ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('RPi.GPIO Exception')
        print(exception, False)

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'PCA9685'):
      try:
        import Adafruit_PCA9685
        pcaInterface = Adafruit_PCA9685.PCA9685()
        pcaInterface.set_pwm_freq(60)
        interfaces.append(LayoutInterface(interface['id'], interface, pcaInterface))
        print('Adafruit_PCA9685 PWM board initialized')
      except ImportError as error:
        print('Adafruit_PCA9685 ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('Adafruit_PCA9685 Exception')
        print(exception, False)

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'ServoKit'):
      try:
        from adafruit_servokit import ServoKit
        interfaces.append(LayoutInterface(interface['id'], interface, ServoKit(channels=16)))
        print('Loaded adafruit_servokit')
      except ImportError as error:
        print('adafruit_servokit ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('adafruit_servokit Exception')
        print(exception, False)

    # Import Playsound Python Library
    if (interface['type'] == 'Python' and interface['id'] == 'playsound'):
      try:
        from playsound import playsound
        interfaces.append(LayoutInterface(interface['id'], interface, playsound))
        print('Loaded Python playsound')
      except ImportError as error:
        print('Python playsound ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('Python playsound Exception')
        print(exception, False)

    # Import paho.mqtt.client Library
    if (interface['type'] == 'mqtt'):
      try:
        import paho.mqtt.client as mqtt #import the client
        print("Creating new MQTT instance")
        client = mqtt.Client(interface['id']) #create new instance
        print("Connecting to MQTT broker")
        client.connect(interface['address']) #connect to broker
        interfaces.append(LayoutInterface(interface['id'], interface, client))
        print('Loaded MQTT')
      except ImportError as error:
        print('MQTTImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('MQTT Exception')
        print(exception, False)

def initializeInterfaces(device_id):


  # print(appConfig['interfaces'])

  local_device = getDeviceById(device_id)

  # interfaceConfig = getInterfaceConfigByDevice(device)

  for interface in appConfig['interfaces']:

    device = getDeviceById(interface['device'])
    
    if (device_id == device['id'] or ('connectedDevices' in local_device and device['id'] in local_device['connectedDevices'])):
      print('found interface' + interface['id'])
    else:
      print('skip interface ' + interface['id'])
      continue

    print('init interace ' + interface['id'])
    


    # Import Arduino Sertal
    if (interface['type'] == 'serial'):
      try:
        import serial
        interfaces.append(LayoutInterface(interface['id'], interface, serial.Serial(interface['serial'], interface['baud'])))
        print('Serial Connection Established...')
      except ImportError as error:
        print('serial ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('serial Exception')
        print(exception, False)

    # Import RPi GPIO
    if (interface['type'] == 'GPIO'):
      try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        interfaces.append(LayoutInterface(interface['id'], interface, GPIO))
        print('GPIO Mode set to BOARD')
      except ImportError as error:
        print('RPi.GPIO ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('RPi.GPIO Exception')
        print(exception, False)

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'PCA9685'):
      try:
        import Adafruit_PCA9685
        pcaInterface = Adafruit_PCA9685.PCA9685()
        pcaInterface.set_pwm_freq(60)
        interfaces.append(LayoutInterface(interface['id'], interface, pcaInterface))
        print('Adafruit_PCA9685 PWM board initialized')
      except ImportError as error:
        print('Adafruit_PCA9685 ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('Adafruit_PCA9685 Exception')
        print(exception, False)

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'ServoKit'):
      try:
        from adafruit_servokit import ServoKit
        interfaces.append(LayoutInterface(interface['id'], interface, ServoKit(channels=16)))
        print('Loaded adafruit_servokit')
      except ImportError as error:
        print('adafruit_servokit ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('adafruit_servokit Exception')
        print(exception, False)

    # Import Playsound Python Library
    if (interface['type'] == 'Python_playsound'):
      try:
        from playsound import playsound
        interfaces.append(LayoutInterface(interface['id'], interface, playsound))
        print('Loaded Python playsound')
      except ImportError as error:
        print('Python playsound ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('Python playsound Exception')
        print(exception, False)

    # Import PyGame Python Library
    if (interface['type'] == 'Python_pygame'):
      try:
        from pygame import mixer
        mixer.init()
        interfaces.append(LayoutInterface(interface['id'], interface, mixer))
        print('Loaded Python PyGame')
      except ImportError as error:
        print('Python PyGame ImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('Python PyGame Exception')
        print(exception, False)

    # Import paho.mqtt.client Library
    if (interface['type'] == 'mqtt'):
      try:
        import paho.mqtt.client as mqtt #import the client
        print("Creating new MQTT instance")
        client = mqtt.Client(interface['id']) #create new instance
        print("Connecting to MQTT broker")
        client.connect(interface['address']) #connect to broker
        interfaces.append(LayoutInterface(interface['id'], interface, client))
        print('Loaded MQTT')
      except ImportError as error:
        print('MQTTImportError')
        print(error, False)
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        print('MQTT Exception')
        print(exception, False)

  
        

  print('Interfaces initialized')


# def getConfig():
#     pathLocal = os.path.dirname(__file__) + '/../../src/config/config.local.json'
#     pathDefault = os.path.dirname(__file__) + '/../../src/config/config.default.json'
#     try:
#         with open(pathLocal) as local_config:
#             localConfigData = json.load(local_config)
#         return localConfigData
#     except:
#         with open(pathDefault) as default_config:
#             defaultConfigData = json.load(default_config)
#         return defaultConfigData

# def getHost():
#     config = getConfig()
#     return config['apiHost']
