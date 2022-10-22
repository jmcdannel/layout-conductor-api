import os
from flask import json, jsonify, abort, request
from config import config

appConfig = config.getConfig()

path = os.path.dirname(__file__) + '/../config/' + config.appConfig['layoutId'] + '/routes.json'
actionQueue = ''

def get_file():
  with open(path) as json_file:
    data = json.load(json_file)
  return data

def get(route_id=None):
  data = get_file()
  if route_id is not None:
    rte = [rte for rte in data if rte['id'] == route_id]
    
    if len(rte) == 0:
      abort(404)
    return jsonify(rte[0])
  else:
    return jsonify(data)
