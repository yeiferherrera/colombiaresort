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
    hotel = hotels.find({Id_hotel: room['Id_Hotel']})
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
                      "hotel" :"test"}})
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
  for room in collection_rooms.find({"Id_Hotel":responseHotels['Id_Hotel'], "Hosts": int(hosts_param) , "Room_Type" : room_type_param}):

      add = True
      for reserve in collection_reservations.find({"Number_Room": room['Number_Room'], "State": "Active"}):
         
          Arrive_Date = datetime.strptime(reserve['Arrive_Date'], '%Y-%m-%d')
          Leave_Date = datetime.strptime(reserve['Leave_Date'], '%Y-%m-%d')

          if ((Arrive_Date <= arrive_date_param <= Leave_Date) or (Arrive_Date <= leave_date_param <= Leave_Date)) :
              add = False 


      if add:
        beds = {"simple": room['Single_Bed'],"double": room['Double_Bed']}
        validator = True
        for dato in responseRooms:
          if dato['beds'] == beds :
            validator = False
            break
            pass
          pass
        if validator:
          responseRooms.append({"room_type" : room['Room_Type'],"capacity" :room['Hosts'],"price" :room['Price'],"currency" :responseHotels['Currency'],"room_thumbnail" :room['Room_Thumbnail'],"beds" :{"simple": room['Single_Bed'],"double": room['Double_Bed']}})
          pass
        
  response = {"hotel_id" : responseHotels['Id_Hotel'],
                        "hotel_name" :responseHotels['Name'],
                        "hotel_location":{"address":responseHotels['Address'],
                                          "lat":responseHotels['Latitude'],
                                          "long":responseHotels['Longitude']},
                        "hotel_thumbnail" :responseHotels['Hotel_Thumbnail'],
                        "check_in" :responseHotels['Check_In'],
                        "check_out" :responseHotels['Check_Out'],
                        "hotel_website" :responseHotels['Hotel_Website'],
                        "rooms":responseRooms}
  return jsonify(response)


@app.route('/V1/reservar', methods=['POST'])
def add_reserva():
  collection_rooms = mongo.db.rooms
  collection_reservations = mongo.db.reservations

  arrive_date = request.json['arrive_date']
  leave_date = request.json['leave_date']
  room_type = request.json['room_type']
  capacity = request.json['capacity']
  simple = request.json['beds']['simple']
  double = request.json['beds']['double']
  hotel_id = request.json['hotel_id']
  doc_type = request.json['user']['doc_type']
  doc_id = request.json['user']['doc_id']
  email = request.json['user']['email']
  phone_number = request.json['user']['phone_number']

  date_arrive_date = datetime.strptime(arrive_date, '%Y-%m-%d')
  date_leave_date = datetime.strptime(leave_date, '%Y-%m-%d')
  response = []
  for room in collection_rooms.find({"Id_Hotel":hotel_id , "Hosts": capacity , "Room_Type" : room_type, "Single_Bed" : simple,"Double_Bed" : double}):
      
      add = True
      for reserve in collection_reservations.find({"Number_Room": room['Number_Room'], "State": "Active"}):
         
          Arrive_Date = datetime.strptime(reserve['Arrive_Date'], '%Y-%m-%d')
          Leave_Date = datetime.strptime(reserve['Leave_Date'], '%Y-%m-%d')
          response.append({ "room" : room['Number_Room'],"Arrive_DateRes" : Arrive_Date,"date_arrive_date" : date_arrive_date,"Leave_DateRes" : Leave_Date})
          if ((Arrive_Date <= date_arrive_date <= Leave_Date) or (Arrive_Date <= date_leave_date <= Leave_Date)) :
              add = False 



      if add:
        reserva = collection_reservations.insert(
        {"Id_Reserva":"CR170002",
        "State":"Active",
        "Id_Hotel":hotel_id,
        "Number_Room":room['Number_Room'],
        "Arrive_Date":arrive_date,
        "Leave_Date":leave_date,
        "Document_Type":doc_type,
        "Identification":doc_id,
        "Email":email,
        "Cell_Phone":phone_number})
        return jsonify({"reservation_id":"CR170002"})
        break
  
  return jsonify({"message": "Reserva no realizada"})


if __name__ == '__main__':
    app.run(debug=True)