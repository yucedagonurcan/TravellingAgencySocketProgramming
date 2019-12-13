from flask import Flask, render_template, request
import socket
import sys
app = Flask(__name__)
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 54000        # Port to listen on (non-privileged ports are > 1023)

date_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_error = None
try:
    date_socket.connect((HOST, PORT))
except socket.gaierror as e:
    print(f"Address-related error connection to server: {e}")
except socket.error as e:
    socket_error = "Server socket is closed."
    print(f"Connection error: {e}")

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

@app.route("/")
def home():
    return render_template("index.html",socket_error=socket_error)
    