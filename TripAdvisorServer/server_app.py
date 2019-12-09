import socket
import selectors
import types 

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 54000        # The port used by the server
class User():
    def __init__(self, user_no, start_date, return_date, preferred_hotel, preferred_airline,  people_count):
        self.user_no = user_no 
        self.preferred_airline = preferred_airline 
        self.preferred_hotel = preferred_hotel 
        self.start_date = start_date 
        self.return_date = return_date 
        self.people_count = people_count 
        
sel = selectors.DefaultSelector()
def GenerateGetRequest(user):

    host=HOST
    port = 50000
    headers = """\
GET /auth HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

    body = 'user_no={user_no}&start_date={start_date}&return_date={return_date}&preferred_airline={preferred_airline}'                                 
    body_bytes = body.format(
        user_no=user.user_no,
        start_date=user.start_date,
        return_date=user.return_date,
        preferred_airline=user.preferred_airline
    ).encode('ascii')
    header_bytes = headers.format(
        content_type="application/x-www-form-urlencoded",
        content_length=len(body_bytes),
        host=str(host) + ":" + str(port)
    ).encode('iso-8859-1')

    payload = header_bytes + body_bytes
    return payload

def CheckPreferredOrOffer(user):
    get_request_str = GenerateGetRequest(user)

    return (False, None)

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Connection accepted from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    trip_result = b""

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(4096)

            new_user = User(data.addr[1], *recv_data.decode().split(";"))
            preferred_check = CheckPreferredOrOffer(user=new_user)

            if(preferred_check[0]):
                trip_result += recv_data
            elif(preferred_check[1]):
                trip_result += preferred_check[1]
            else:
                trip_result += b"None"

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


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Socket server is listening on {HOST}:{PORT}")
lsock.setblocking(False)

sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)



