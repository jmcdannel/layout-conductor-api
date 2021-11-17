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

def get():
  data = getConfig()
  return jsonify(data)

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
