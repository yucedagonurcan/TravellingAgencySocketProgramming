from flask import Flask, render_template, request
import socket

app = Flask(__name__)
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 54000        # Port to listen on (non-privileged ports are > 1023)
date_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
date_socket.connect((HOST, PORT))


@app.route("/send_data", methods=["POST"])
def SendDataToServer():

    start_date = request.form['starting_date']
    return_date = request.form['return_date']
    date_socket.send(start_date.encode())
    return "Oldu."

@app.route("/")
def home():
    return render_template("index.html")
    