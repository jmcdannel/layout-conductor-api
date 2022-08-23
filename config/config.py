import os
from flask import json, jsonify, request, abort
from termcolor import colored, cprint


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
  for interface in appConfig['interfaces']:
    device = getDeviceById(interface['device'])
    
    # Import Arduino Sertal
    if (interface['type'] == 'serial'):
      try:
        import serial
        interfaces.append(LayoutInterface(interface['id'], interface, serial.Serial(interface['serial'], interface['baud'])))
        cprint('Serial Connection Established [%s]...' % interface['id'], 'green')
      except ImportError as error:
        cprint('serial ImportError [%s]' % interface['id'], 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('serial Exception', 'red')
        cprint(exception, 'red')

    # Import RPi GPIO
    if (interface['type'] == 'GPIO'):
      try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        interfaces.append(LayoutInterface(interface['id'], interface, GPIO))
        cprint('GPIO Mode set to BOARD', 'green')
      except ImportError as error:
        cprint('RPi.GPIO ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('RPi.GPIO Exception', 'red')
        cprint(exception, 'red')

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'PCA9685'):
      try:
        import Adafruit_PCA9685
        pcaInterface = Adafruit_PCA9685.PCA9685()
        pcaInterface.set_pwm_freq(60)
        interfaces.append(LayoutInterface(interface['id'], interface, pcaInterface))
        cprint('Adafruit_PCA9685 PWM board initialized', 'green')
      except ImportError as error:
        cprint('Adafruit_PCA9685 ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('Adafruit_PCA9685 Exception', 'red')
        cprint(exception, 'red')

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'ServoKit'):
      try:
        from adafruit_servokit import ServoKit
        interfaces.append(LayoutInterface(interface['id'], interface, ServoKit(channels=16)))
        cprint('Loaded adafruit_servokit', 'green')
      except ImportError as error:
        cprint('adafruit_servokit ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('adafruit_servokit Exception', 'red')
        cprint(exception, 'red')

    # Import Playsound Python Library
    if (interface['type'] == 'Python' and interface['id'] == 'playsound'):
      try:
        from playsound import playsound
        interfaces.append(LayoutInterface(interface['id'], interface, playsound))
        cprint('Loaded Python playsound', 'green')
      except ImportError as error:
        cprint('Python playsound ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('Python playsound Exception', 'red')
        cprint(exception, 'red')

    # Import paho.mqtt.client Library
    if (interface['type'] == 'mqtt'):
      try:
        import paho.mqtt.client as mqtt #import the client
        cprint("Creating new MQTT instance", 'cyan')
        client = mqtt.Client(interface['id']) #create new instance
        cprint("Connecting to MQTT broker", 'green')
        client.connect(interface['address']) #connect to broker
        interfaces.append(LayoutInterface(interface['id'], interface, client))
        print('Loaded MQTT')
      except ImportError as error:
        cprint('MQTTImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('MQTT Exception', 'red')
        cprint(exception, 'red')

def initializeInterfaces(device_id):


  # print(appConfig['interfaces'])

  local_device = getDeviceById(device_id)

  # interfaceConfig = getInterfaceConfigByDevice(device)

  for interface in appConfig['interfaces']:

    device = getDeviceById(interface['device'])
    
    if (device_id == device['id'] or ('connectedDevices' in local_device and device['id'] in local_device['connectedDevices'])):
      cprint('INITIALIZING interface ' + interface['id'], 'cyan')
    else:
      cprint('SKIPPING interface ' + interface['id'], 'orange')
      continue

    # Import Arduino Sertal
    if (interface['type'] == 'serial'):
      try:
        import serial
        interfaces.append(LayoutInterface(interface['id'], interface, serial.Serial(interface['serial'], interface['baud'])))
        cprint('Serial Connection Established...', 'green')
      except ImportError as error:
        cprint('serial ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('serial Exception', 'red')
        cprint(exception, 'red')

    # Import RPi GPIO
    if (interface['type'] == 'GPIO'):
      try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        interfaces.append(LayoutInterface(interface['id'], interface, GPIO))
        cprint('GPIO Mode set to BOARD', 'green')
      except ImportError as error:
        cprint('RPi.GPIO ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('RPi.GPIO Exception', 'red')
        cprint(exception, 'red')

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'PCA9685'):
      try:
        import Adafruit_PCA9685
        pcaInterface = Adafruit_PCA9685.PCA9685()
        pcaInterface.set_pwm_freq(60)
        interfaces.append(LayoutInterface(interface['id'], interface, pcaInterface))
        cprint('Adafruit_PCA9685 PWM board initialized', 'green')
      except ImportError as error:
        cprint('Adafruit_PCA9685 ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('Adafruit_PCA9685 Exception', 'red')
        cprint(exception, 'red')

    # Import RPi PWM Controller
    if (device['type'] == 'pi' and interface['type'] == 'ServoKit'):
      try:
        from adafruit_servokit import ServoKit
        interfaces.append(LayoutInterface(interface['id'], interface, ServoKit(channels=16)))
        cprint('Loaded adafruit_servokit', 'green')
      except ImportError as error:
        cprint('adafruit_servokit ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('adafruit_servokit Exception', 'red')
        cprint(exception, 'red')

    # Import Playsound Python Library
    if (interface['type'] == 'Python_playsound'):
      try:
        from playsound import playsound
        interfaces.append(LayoutInterface(interface['id'], interface, playsound))
        cprint('Loaded Python playsound', 'green')
      except ImportError as error:
        cprint('Python playsound ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('Python playsound Exception', 'red')
        cprint(exception, 'red')

    # Import PyGame Python Library
    if (interface['type'] == 'Python_pygame'):
      try:
        from pygame import mixer
        mixer.init()
        interfaces.append(LayoutInterface(interface['id'], interface, mixer))
        cprint('Loaded Python PyGame', 'green')
      except ImportError as error:
        cprint('Python PyGame ImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('Python PyGame Exception', 'red')
        cprint(exception, 'red')

    # Import paho.mqtt.client Library
    if (interface['type'] == 'mqtt'):
      try:
        import paho.mqtt.client as mqtt #import the client
        cprint("Creating new MQTT instance", 'cyan')
        client = mqtt.Client(interface['id']) #create new instance
        cprint("Connecting to MQTT broker", 'cyan')
        client.connect(interface['address']) #connect to broker
        interfaces.append(LayoutInterface(interface['id'], interface, client))
        cprint('Loaded MQTT', 'green')
      except ImportError as error:
        cprint('MQTTImportError', 'red')
        cprint(error, 'red')
      except Exception as exception:
        interfaces.append(LayoutInterface(interface['id'], interface, None))
        cprint('MQTT Exception', 'red')
        cprint(exception, 'red')

  
        

  cprint('Interfaces initialized', 'cyan')


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
