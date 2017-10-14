# mongo.py

from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'hotel'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/hotel'

mongo = PyMongo(app)

@app.route('/V1/hotels', methods=['GET'])
def get_all_hotels():
  collection = mongo.db.hoteles
  output = []
  for hotel in collection.find():
    print "------------------------------------------"
    print hotel
    output.append({'result' :[{"Hotel" : hotel['Hotel']},{"Rooms" :hotel['Habitaciones']}]})
  return jsonify(output)

@app.route('/V1/rooms/', methods=['GET'])
def get_rooms():
  parametro = request.args.get('room_type')
  collection = mongo.db.hoteles
  response = collection.find_one({'Habitaciones.Tipo' : parametro})
  print "------------------------------------------"
  print response
  if response:
    rooms = []
    for room in response['Habitaciones']:
      if room['Tipo']==parametro:
        rooms.append({"Room" :room['Numero']}) 
        pass 
      pass
    
    output = {'result' :[{"Hotel" : response['Hotel']},rooms]}
  else:
    output = "No such comunidad"
  return jsonify(output)

'''
@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})'''

if __name__ == '__main__':
    app.run(debug=True)