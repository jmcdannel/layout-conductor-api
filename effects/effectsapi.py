import os
from flask import json, jsonify, abort, request
from config import config
# from . import soundfx

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/effects.json'
actionQueue = ''

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

def _queueCommand(cmd):
  global actionQueue
  if actionQueue != '':
    actionQueue = actionQueue + ','
  actionQueue = actionQueue + '{ "action": "pin", "payload":' + cmd + '}'

def execQueue(interface):
  global actionQueue
  print('cmd: %s' % actionQueue)
  if interface is not None and actionQueue != '':
    actionQueue = '[' + actionQueue + ']'
    interface.write(actionQueue.encode())
  actionQueue = ''

def _sendCommand(cmd, interface):
  print('cmd: %s' % cmd)
  if interface is not None:
    interface.write(cmd.encode())

def _sendMQTTCommand(cmd, interface):
  turnoutCommand = '{ "action": "effect", "payload":' + cmd + '}'
  print('mqttCmd: %s' % turnoutCommand)
  if interface is not None:
    pubRes = interface.publish('lc_cmd', turnoutCommand)
    print(pubRes)

def init():
  data = get_file()
  # soundfx.init()

  for efx in data:
    for action in efx['actions']:
      actionInterface = config.getInterfaceById(turnout['relay']['interface'])
      if actionInterface.settings['type'] == 'GPIO':
        actionInterface.setup(action['pin'], actionInterface.OUT)

def get(effect_id=None):
  data = get_file()
  if effect_id is not None:
    efx = [efx for efx in data if efx['effectId'] == effect_id]
    
    if len(efx) == 0:
      abort(404)
    return jsonify(efx[0])
  else:
    return jsonify(data)

def put(effect_id):
  data = get_file()
  efx = [efx for efx in data if efx['effectId'] == effect_id]
  state = request.json['state']

  # validate
  if len(efx) == 0:
    abort(404)
  if not request.json:
    abort(400)

  efx = efx[0]

  efx['state'] = state

  print('effect put %d', effect_id)
  
  for action in efx['actions']:
    efxInterface = config.getInterfaceById(action['interface'])
    print('effect action ' + action['interface'])
    if(efxInterface.settings['type'] == 'DCCOutput'):
      # DCC Output Command
      _sendCommand('<Z %d %s>' % (action['pin'], state), efxInterface.interface)
    elif(efxInterface.settings['type'] == 'serial'):
      # Arduino Serail JSON Output
      if (efx['type'] == 'signal'):
        signalState = 1 if state == action['actionId'] else 0
        # _queueCommand('')
        # _sendCommand('[{ "pin": %d, "value": %d, "type": "signal" }]' % (action['pin'], signalState), efxInterface.interface)      
      else:
        _queueCommand('{ "pin": %d, "value": %d }' % (action['pin'], state))
    elif(efxInterface.settings['type'] == 'GPIO'):
      # RPi GPIO Output
      efxInterface.interface.output(action['pin'], action['state'])
    elif(efxInterface.settings['type'] == 'Python' and efxInterface.id == 'playsound' and state == 1):
      wavFile = os.path.dirname(__file__) + '/../sounds/' + action['file']
      print(wavFile)
      efxInterface.interface(wavFile)
    elif efxInterface.settings['type'] == 'mqtt' and state == 1:
        _sendMQTTCommand('{ "command": "effect", "type": "%s", "value": %s }' % (efx['type'], action), efxInterface.interface)
    
    execQueue(efxInterface.interface)

  # save
  with open(path, 'w') as json_file:
    json.dump(data, json_file)

  return jsonify(efx)

def getActionState(efx, action, state):
  if 'states' not in efx:
    return state
  elif efx['states'][str(state)] is None:
    return state
  elif efx['states'][str(state)][action] is None:
    return state
  else:
    return efx['states'][str(state)][action]
    

def runEffect(effect):
  if effect['type'] == 'sound':
    player = config.getInterfaceById(effect['value']['player'])
    print(player.interface['id'])
    print(effect['value']['file'])
    player.interface(effect['value']['file'])
