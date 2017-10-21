# mongo.py

from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'colombiaresort'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/colombiaresort'

mongo = PyMongo(app)

@app.route('/V1/AllRooms', methods=['GET'])
def get_all_hotels():
  hotels = mongo.db.hotels
  rooms = mongo.db.rooms
  response = []
  responseHotels = []
  responseRooms = []
  
  for hotel in hotels.find():
    #hotel = hotels.find({Id_hotel: room['Id_Hotel']})
    for room in rooms.find({"Id_Hotel":hotel['Id_Hotel']}):
      responseRooms.append({"room_type" : room['Room_Type'],
                        "capacity" :room['Hosts'],
                        "price" :room['Price'],
                        "currency" :hotel['Currency'],
                        "room_thumbnail" :room['Room_Thumbnail'],
                        "beds" :{"simple": room['Single_Bed'],
                                  "double": room['Double_Bed']}}
                        )

    responseHotels.append({"hotel_id" : hotel['Id_Hotel'],
                        "hotel_name" :hotel['Name'],
                        "hotel_location":{"address":hotel['Address'],
                                          "lat":hotel['Latitude'],
                                          "long":hotel['Longitude']},
                        "hotel_thumbnail" :hotel['Hotel_Thumbnail'],
                        "check_in" :hotel['Check_In'],
                        "check_out" :hotel['Check_Out'],
                        "hotel_website" :hotel['Hotel_Website'],
                        "rooms":responseRooms}

      )

  response.append({'result' : {
                      "hotel" :responseHotels}})
  return jsonify(response)

@app.route('/V1/rooms/', methods=['GET'])
def get_rooms():

  arrive_date_param = datetime.strptime(request.args.get('arrive_date'), '%Y-%m-%d')
  leave_date_param = datetime.strptime(request.args.get('leave_date'), '%Y-%m-%d')
  city_param = request.args.get('city')
  hosts_param = request.args.get('hosts')
  room_type_param = request.args.get('room_type')
  
  collection_hotels = mongo.db.hotels
  collection_rooms = mongo.db.rooms
  collection_reservations = mongo.db.reservations

  responseRooms = []
  response = []
  responseHotels = collection_hotels.find_one({'Area_Code' : city_param})
  
  for room in collection_rooms.find({"Id_Hotel":responseHotels['Id_Hotel'], "Hosts": hosts_param , "Room_Type" : room_type_param}):
      
      add = True
      for reserve in collection_reservations.find({"Number_Room": room['Number_Room'], "State": "Active"}):
         
          Arrive_Date = datetime.strptime(reserve['Arrive_Date'], '%Y-%m-%d')
          Leave_Date = datetime.strptime(reserve['Leave_Date'], '%Y-%m-%d')

          if ((Arrive_Date < arrive_date_param < Leave_Date) or (Arrive_Date < leave_date_param < Leave_Date)) :
              add = False 

      if add:
        responseRooms.append({"room_type" : room['Room_Type'],"capacity" :room['Hosts'],"price" :room['Price'],"currency" :responseHotels['Currency'],"room_thumbnail" :room['Room_Thumbnail'],"beds" :{"simple": room['Single_Bed'],"double": room['Double_Bed']}})

  response.append({"hotel_id" : responseHotels['Id_Hotel'],
                        "hotel_name" :responseHotels['Name'],
                        "hotel_location":{"address":responseHotels['Address'],
                                          "lat":responseHotels['Latitude'],
                                          "long":responseHotels['Longitude']},
                        "hotel_thumbnail" :responseHotels['Hotel_Thumbnail'],
                        "check_in" :responseHotels['Check_In'],
                        "check_out" :responseHotels['Check_Out'],
                        "hotel_website" :responseHotels['Hotel_Website'],
                        "rooms":responseRooms})
  return jsonify(response)


@app.route('/V1/reservar', methods=['POST'])
def add_reserva():
  collection = mongo.db.hoteles
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True)