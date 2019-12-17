import socket
import selectors
import types 

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 54000        # The port used by the server
PORT_AIRLINE = 55000
PORT_HOTEL = 56000

# User object for storing the request.
# We will use socket port that is connected to Trip Advisor Server as user_no.
class User():
    def __init__(self, user_no, start_date, return_date, preferred_hotel, preferred_airline,  people_count, method_requested):
        self.user_no = user_no 
        self.preferred_airline = preferred_airline 
        self.preferred_hotel = preferred_hotel 
        self.start_date = start_date 
        self.return_date = return_date 
        self.people_count = people_count 
        self.method_requested = method_requested 

# Create a selector object   
sel = selectors.DefaultSelector()

#* Airline Socket Connection
airline_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_error = None
try:
    airline_socket.connect((HOST, PORT_AIRLINE))
except socket.gaierror as e:
    print(f"Address-related error connection to Airline server: {e}")
except socket.error as e:
    socket_error = "Server socket is closed."
    print(f"Connection error: {e}")
#*****

#! Hotel Socket Connection
hotel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_error = None
try:
    hotel_socket.connect((HOST, PORT_HOTEL))
except socket.gaierror as e:
    print(f"Address-related error connection to Hotel server: {e}")
except socket.error as e:
    socket_error = "Server socket is closed."
    print(f"Connection error: {e}")
#!!!!!!!!

# Generates a GET request to send to the airline and hotel sockets.
def GenerateGetRequest(user):

    host= HOST
    port = 50000
    headers = """\
GET /{method_requested} HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

    body = 'user_no={user_no}&start_date={start_date}&return_date={return_date}&preferred_airline={preferred_airline}&preferred_hotel={preferred_hotel}&people_count={people_count}'                                 
    body_bytes = body.format(
        user_no=user.user_no,
        start_date=user.start_date,
        return_date=user.return_date,
        preferred_airline=user.preferred_airline,
        preferred_hotel=user.preferred_hotel,
        people_count=user.people_count
    ).encode('ascii')
    header_bytes = headers.format(
        method_requested=user.method_requested,
        content_type="text/html; charset=UTF-8",
        content_length=len(body_bytes),
        host=str(host) + ":" + str(port)
    ).encode('iso-8859-1')

    payload = header_bytes + body_bytes
    return payload

# Parses a HTTP response and returns status code and body.
def ParseHTTPResponse(response):
    res_splitted = response.split(" ")
    status_code = res_splitted[1]
    body = response.split("\r\n")[-1].replace(" ", "").split("=")[-1]
    return status_code, body

# Checks the requested time for airline and hotels and sends a GET
# request to them. Result will be Success, Failure or Alternatives.
# It will return the response.
# Also user Client Web Server can send check_dates or accept_dates
# requests, it will behave differently by these preferences. 
def CheckPreferredOrOffer(user):
    if(user.method_requested == "check_dates"):

        user.method_requested = "check_airline_dates"
        get_request_airline = GenerateGetRequest(user)
        user.method_requested = "check_hotel_dates"
        get_request_hotel = GenerateGetRequest(user)

        airline_socket.sendall(get_request_airline)
        hotel_socket.sendall(get_request_hotel)

        airline_response = airline_socket.recv(4096)
        hotel_response = hotel_socket.recv(4096)

        airline_status, airline_body = ParseHTTPResponse(airline_response.decode())

        if(airline_status == "200"):
            airline_response=airline_body
        else:
            airline_response = "Failure"

        hotel_status, hotel_body = ParseHTTPResponse(hotel_response.decode())

        if(hotel_status == "200"):
            hotel_response=hotel_body
        else:
            hotel_response = "Failure"



        return "||".join([airline_response, hotel_response])

    elif(user.method_requested == "accept_dates"):

        user.method_requested = "accept_airline_dates"
        get_request_airline = GenerateGetRequest(user)
        user.method_requested = "accept_hotel_dates"
        get_request_hotel = GenerateGetRequest(user)

        airline_socket.sendall(get_request_airline)
        hotel_socket.sendall(get_request_hotel)

        airline_response = airline_socket.recv(4096)
        hotel_response = hotel_socket.recv(4096)

        airline_status, airline_body = ParseHTTPResponse(airline_response.decode())

        if(airline_status == "200"):
            airline_response=airline_body
        else:
            airline_response = "Failure"

        hotel_status, hotel_body = ParseHTTPResponse(hotel_response.decode())

        if(hotel_status == "200"):
            hotel_response=hotel_body
        else:
            hotel_response = "Failure"
        
        return "||".join([airline_response, hotel_response])

    return b"Failure||Failure"

# It will accept the socket and register the socket descriptor to the selector object
# This will ensure that no more one socket gets the keys for the request.  
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Connection accepted from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# Services to a client request.
# Parses the recieved socket data, creates a new User object with it.
# It will also unregister and closes the socket if there is any error recieving the data.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    trip_result = b""

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(4096)

            new_user = User(data.addr[1], *recv_data.decode().split(";"))
            preferred_check = CheckPreferredOrOffer(user=new_user)
            trip_result += preferred_check.encode()
                
        except ConnectionResetError as e:
            print(f"{data.addr} closed connection.")
            sel.unregister(sock)
            sock.close()
            return 
        if recv_data:
            data.outb += trip_result
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            return 
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# Create the socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Make the socket reusable.
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to HOST and PORT
lsock.bind((HOST, PORT))
# Listen the connection requests
lsock.listen()
print(f"Trip Advisor Socket server is listening on {HOST}:{PORT}")
# We will set the blocking state to False, because we will use selector object to make it non-blocking
lsock.setblocking(False)


# Register the listening socket into the selector object.
# We will set the data to None to later understand if it is a listneing socket or already accepted one.
sel.register(lsock, selectors.EVENT_READ, data=None)

# Server forever;
# For every event(from registered sockets)
##: If data is None, it is from listening socket
##: Else it is an already accepted socket so we need to serve it.
while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)



