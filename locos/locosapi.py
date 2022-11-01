import os
from flask import json, jsonify, abort, request
from config import config

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/locos.json'

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

def get(loco_id=None):
  data = get_file()
  print(data)
  if loco_id is not None:
    loco = [loco for loco in data if loco['address'] == loco_id]
    
    print(loco_id)
    print(len(loco))
    if len(loco) == 0:
      abort(404)
    return jsonify(loco[0])
  else:
    return jsonify(data)

def put(loco_id):
  data = get_file()
  locos = [loco for loco in data if loco['address'] == loco_id]
  payload = request.get_json()

  print('-----payload-----')
  print(payload)

  # validate
  if len(locos) == 0:
    abort(404)
  if not payload:
    abort(400)

  loco = locos[0]

  print('-----loco-----')
  print(loco)
  for key in payload:
    print('payloadkey %s = %s' % (key, payload[key]))
    # print('locokey %s = %s' % (key, loco[key]))
    loco[key] = payload[key]
    # loco[key] = request.json.get(key)

  print(loco)

  # save all keys  
  with open(path, 'w') as loco_file:
        json.dump(data, loco_file)

  return jsonify(loco)