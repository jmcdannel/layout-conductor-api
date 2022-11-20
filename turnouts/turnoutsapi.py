import os
from flask import json, jsonify, request, abort
from config import config
from effects import effectsapi

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/turnouts.json'
actionQueue = ''

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

def _queueCommand(cmd, action):
  global actionQueue
  print('_queueCommand')
  print(actionQueue)
  if actionQueue != '':
    actionQueue = actionQueue + ','
  actionQueue = actionQueue + '{ "action": "' + action + '", "payload":' + cmd + '}'

def _queueEffect(effectId, state):
  global actionQueue
  if actionQueue != '':
    actionQueue = actionQueue + ','
  effectCommands = effectsapi.queueCommands(effectId, state)
  print(effectCommands)
  actionQueue = actionQueue + effectCommands

def execQueue(interface):
  global actionQueue
  print('execQueue')
  print(actionQueue)
  print('cmd: %s' % actionQueue)
  if interface is not None and actionQueue != '':
    actionQueue = '[' + actionQueue + ']'
    interface.write(actionQueue.encode())
  actionQueue = ''

def _sendCommand(cmd, interface):
  print('cmd: %s' % cmd)
  if interface is not None:
    interface.write(cmd.encode())

def _sendActionCommand(cmd, interface):
  turnoutCommand = '{ "action": "servo", "payload":' + cmd + '}'
  print('actionCmd: %s' % turnoutCommand)
  if interface is not None:
    interface.write(turnoutCommand.encode())

def _sendMQTTCommand(cmd, interface, clientId):
  turnoutCommand = '{ "action": "servo", "payload":' + cmd + '}'
  print('mqttCmd: %s' % turnoutCommand)
  print('mqttClient: %s' % clientId)
  if interface is not None:
    pubRes = interface.publish('lc_cmd', turnoutCommand)
    print(pubRes)

def init():
  data = get_file()
  # for turnout in data:
  #   if 'relay' in turnout:
  #     relayInterface = config.getInterfaceById(turnout['relay']['interface'])
  #     if relayInterface is not None and relayInterface.settings['type'] == 'GPIO':
  #       relayInterface.interface.setup(turnout['relay']['pin'], relayInterface.interface.OUT)
  #       if 'relayCrossover' in turnout:
  #         relayXInterface = config.getInterfaceById(turnout['relayCrossover']['interface'])
  #         if relayXInterface is not None and relayXInterface.settings['type'] == 'GPIO':
  #           relayXInterface.interface.setup(turnout['relayCrossover']['pin'], relayXInterface.interface.OUT)
      

def get(turnout_id=None):
  data = get_file()
  if turnout_id is not None:
    turnout = [turnout for turnout in data if turnout['turnoutId'] == turnout_id]
    
    if len(turnout) == 0:
      abort(404)
    return jsonify(turnout[0])
  else:
    return jsonify(data)

def put(turnout_id):
  data = get_file()
  turnouts = [turnout for turnout in data if turnout['turnoutId'] == turnout_id]

  if len(turnouts) == 0:
    abort(404)
  if not request.json:
    abort(400)

  turnout = turnouts[0]
  turnoutInterface = config.getInterfaceById(turnout['config']['interface'])
  
  for key in request.json:
    turnout[key] = request.json.get(key, turnout[key])

  # if 'effects' in turnout:
  #   for effectId in turnout['effects']:
  #     _queueEffect(effectId, turnout['state'])

  if turnout['config']['type'] == 'kato' and turnoutInterface.settings['type'] == 'serial':
    _queueCommand('{ "turnoutIdx": %d, "state": %d }' % (turnout['config']["turnoutIdx"], turnout['state']), 'turnout')
    
  if turnout['config']['type'] == 'servo':
    if 'servo' in turnout['config']:
      if turnoutInterface is not None and turnoutInterface.settings['type'] == 'ServoKit':
        # if turnout['state']
        turnoutInterface.interface.servo[turnout['config']['servo']].angle = turnout['current']
      if turnoutInterface is not None and turnoutInterface.settings['type'] == 'PCA9685':
        print('setting PCA9685')
        print(turnout['servo'])
        print(turnoutInterface.interface)
        print(turnoutInterface.interface.set_pwm)
        turnoutInterface.interface.set_pwm(turnout['servo'], 0, turnout['current'])
      if turnoutInterface is not None and turnoutInterface.settings['type'] == 'serial':
        # _sendActionCommand('{ "servo": %d, "value": %d }' % (turnout['servo'], turnout['current']), turnoutInterface.interface)
        _queueCommand('{ "servo": %d, "pwm": "%s", "value": %d }' % (turnout['servo'], turnout['pwm'], turnout['current']), 'servo')
      if turnoutInterface is not None and turnoutInterface.settings['type'] == 'mqtt':
        _sendMQTTCommand('{ "servo": %d, "pwm": "%s", "value": %d }' % (turnout['servo'], turnout['pwm'], turnout['current']), turnoutInterface.interface, turnoutInterface.settings['id'])
    if 'pin' in turnout:
      _sendCommand('{ "pin": %d, "value": %d }' % (turnout['pin'], turnout['current']), turnoutInterface.interface)

  # if 'relay' in turnout:
  #   relay(turnout['relay'], turnout['current'] == turnout['straight'])
  # # Toggle crossover relay if present
  # if 'relayCrossover' in turnout:
  #   relay(turnout['relayCrossover'], turnout['current'] == turnout['straight'])
  
  execQueue(turnoutInterface.interface)

  # save all keys
  with open(path, 'w') as turnout_file:
    json.dump(data, turnout_file)

  return jsonify(turnout)


  # _queueCommand('{ "pin": %d, "value": %d }' % (relay['pin'], relay['straight']), 'pin')

# def relay(relay, isStraight):
#   relayInterface = config.getInterfaceById(relay['interface'])
#   if relayInterface is not None:
#     if isStraight is True:
#       print('change relay %d to straight (%s)' % (relay['pin'], relay['straight']))
#       _queueCommand('{ "pin": %d, "value": %d }' % (relay['pin'], relay['straight']), 'pin')
#     else:
#       print('change relay %d to divergent (%s)' % (relay['pin'], relay['divergent']))
#       _queueCommand('{ "pin": %d, "value": %d }' % (relay['pin'], relay['divergent']), 'pin')
