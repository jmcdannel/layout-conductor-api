import os
from flask import json, jsonify, request, abort
from config import config

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/turnouts.json'

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

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
  if interface is not None:
    interface.publish(clientId, turnoutCommand)

def init():
  data = get_file()
  for turnout in data:
    if 'relay' in turnout:
      relayInterface = config.getInterfaceById(turnout['relay']['interface'])
      if relayInterface is not None:
        relayInterface.interface.setup(turnout['relay']['pin'], relayInterface.interface.OUT)
        if 'relayCrossover' in turnout:
          relayXInterface = config.getInterfaceById(turnout['relayCrossover']['interface'])
          if relayXInterface is not None:
            relayXInterface.interface.setup(turnout['relayCrossover']['pin'], relayXInterface.interface.OUT)
      

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
  turnoutInterface = config.getInterfaceById(turnout['interface'])
  
  for key in request.json:
    turnout[key] = request.json.get(key, turnout[key])

  if turnout['type'] == 'kato' and turnoutInterface.settings['type'] == 'serial':
    if (turnout['current'] == 1):
      _sendCommand('[{ "pin": %d, "value": %d }, { "pin": %d, "value": %d }]' % (turnout['pinB'], 0, turnout['pinA'], 1), turnoutInterface.interface)
    elif (turnout['current'] == 0):
      _sendCommand('[{ "pin": %d, "value": %d }, { "pin": %d, "value": %d }]' % (turnout['pinB'], 1, turnout['pinA'], 0), turnoutInterface.interface)
 
  if turnout['type'] == 'servo':
    if 'servo' in turnout:
      if turnoutInterface.settings['type'] == 'ServoKit':
        turnoutInterface.interface.servo[turnout['servo']].angle = turnout['current']
      if turnoutInterface.settings['type'] == 'PCA9685':
        turnoutInterface.interface.set_pwm(turnout['servo'], 0, turnout['current'])
      if turnoutInterface.settings['type'] == 'serial':
        _sendActionCommand('{ "servo": %d, "value": %d }' % (turnout['servo'], turnout['current']), turnoutInterface.interface)
      if turnoutInterface.settings['type'] == 'mqtt':
        _sendMQTTCommand('{ "servo": %d, "value": %d }' % (turnout['servo'], turnout['current']), turnoutInterface.interface, turnoutInterface.settings['id'])
    if 'pin' in turnout:
      _sendCommand('{ "pin": %d, "value": %d }' % (turnout['pin'], turnout['current']), turnoutInterface.interface)

  if 'relay' in turnout:
    relay(turnout['relay'], turnout['current'] == turnout['straight'])
  # Toggle crossover relay if present
  if 'relayCrossover' in turnout:
    relay(turnout['relayCrossover'], turnout['current'] == turnout['straight'])
  # save all keys
  
  with open(path, 'w') as turnout_file:
    json.dump(data, turnout_file)

  return jsonify(turnout)

def relay(relay, isStraight):
  relayInterface = config.getInterfaceById(relay['interface'])
  if relayInterface is not None:
    if isStraight is True:
      print('change relay %d to straight (%s)' % (relay['pin'], relay['straight']))
      relayInterface.interface.output(relay['pin'], relay['straight'])
    else:
      print('change relay %d to divergent (%s)' % (relay['pin'], relay['divergent']))
      relayInterface.interface.output(relay['pin'], relay['divergent'])
