from flask import Flask, render_template, request
import socket
import sys

app = Flask(__name__)
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 54000        # Port to listen on (non-privileged ports are > 1023)

# Create a socket for connection with the Trip Advisor Server.
date_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_error = None

try:
    # Connect with the Trip Advisor Server
    date_socket.connect((HOST, PORT))
except socket.gaierror as e:
    print(f"Address-related error connection to server: {e}")
except socket.error as e:
    socket_error = "Server socket is closed."
    print(f"Connection error: {e}")

# Get tables from table_names.txt.
# For dynamic airline and hotel adding.
def GetTables():
    try:
        f= open("table_names.txt","r")
        fl =f.readlines()
        hotel_names = fl[0].strip().split(";")
        airline_names = fl[1].strip().split(";")
        f.close()
    except Exception as e:
        print(e)
        return None, None
    return hotel_names, airline_names

# check_dates route is for sending the request to Trip Advisor Server form that filled by 
# user in front-end.
@app.route("/check_dates", methods=["POST"])
def CheckDates():

    start_date = request.form['starting_date']
    return_date = request.form['return_date']
    preferred_hotel = request.form['preferred_hotel']
    preferred_airline = request.form['preferred_airline']
    people_count = request.form['people_count']
    req_method="check_dates"
    date_socket.send(f"{start_date};{return_date};{preferred_hotel};{preferred_airline};{people_count};{req_method}".encode())
    result = date_socket.recv(4096)
    return result
    
# accept_dates route will send accept request to Trip Advisor Server.
# So that Trip Advisor Server can send the accept request to airline and hotels databases to
# insert the specified date.
@app.route("/accept_dates", methods=["POST"])
def AcceptDates():

    start_date = request.form['starting_date']
    return_date = request.form['return_date']
    preferred_hotel = request.form['preferred_hotel']
    preferred_airline = request.form['preferred_airline']
    people_count = request.form['people_count']
    req_method="accept_dates"
    date_socket.send(f"{start_date};{return_date};{preferred_hotel};{preferred_airline};{people_count};{req_method}".encode())
    result = date_socket.recv(4096)
    return result

# Main route, it will get the table names and render the HTML.
@app.route("/")
def home():
    hotel_names, airline_names = GetTables()
    if not hotel_names:
        hotel_names = ["MarmaraHotel","SheratonHotel","HolidayInn","KocaoglanHotel"]
    if not airline_names:
        airline_names = ["Pegasus","TurkishAirlines","EmiratesAirlines","EasyJet","RyanAir"]
    return render_template("index.html",socket_error=socket_error, hotel_names=hotel_names, airline_names=airline_names)
    