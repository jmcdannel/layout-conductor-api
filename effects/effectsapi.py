import os
from flask import json, jsonify, abort, request
from config import config
# from . import soundfx

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/effects.json'

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

def _sendCommand(cmd, interface):
  print('cmd: %s' % cmd)
  if interface is not None:
    interface.write(cmd.encode())

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
  
  for action in efx['actions']:
    print(action)
    print(action['interface'])
    efxInterface = config.getInterfaceById(action['interface'])
    print(efxInterface)
    
    # actionState = getActionState(efx, action['actionId'], state)
    # print(action['type'])
    # print(action['pin'])
    # print(arduino is None)
    if(efxInterface.settings['type'] == 'DCCOutput'):
      # DCC Output Command
      _sendCommand('<Z %d %s>' % (action['pin'], state), efxInterface.interface)
    elif(efxInterface.settings['type'] == 'serial'):
      # Arduino Serail JSON Output
      _sendCommand('[{ "pin": %d, "value": %s }]' % (action['pin'], state), efxInterface.interface)
    elif(efxInterface.settings['type'] == 'GPIO'):
      # RPi GPIO Output
      efxInterface.interface.output(action['pin'], action['state'])

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
    