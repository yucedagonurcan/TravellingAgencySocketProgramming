import sqlite3
import socket
import pandas as pd
import selectors
import types 

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 56000       
MAX_PEOPLE_ON_HOTEL=3

sel = selectors.DefaultSelector()
conn = sqlite3.connect('Hotels.db')
cur = conn.cursor()

def GetTableNames(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    result = cursor.fetchall()
    return [ row[0] for row in result if row[0] != "sqlite_sequence"]
def GenerateDateSequence(start_date, end_date, single_quotes=True):
    if single_quotes:
        date_list = [x.strftime("'%d/%m/%Y'") for x in pd.date_range(start=start_date, end=end_date).tolist() ]
    else:
        date_list = [x.strftime("%d/%m/%Y") for x in pd.date_range(start=start_date, end=end_date).tolist() ]
    return date_list
def GenerateQueryFromRequest(req_dict):
    new_bookings=[]
    date_sequence = GenerateDateSequence(req_dict["start_date"], req_dict["return_date"], single_quotes=False)
    for cur_date in date_sequence:
        for idx in range(int(req_dict["people_count"])):
            new_bookings.append((None, cur_date, req_dict["user_no"]))
    return new_bookings
def InsertNewBooking(req_dict):
    new_bookings = GenerateQueryFromRequest(req_dict)
    try:
        cur.executemany("INSERT INTO " + req_dict["preferred_hotel"] + " VALUES (?,?,?)", new_bookings)
        conn.commit()
    except Exception as e:
        print(e)
        return "Failure"
    return "Success"

def CheckHotelDates(req_dict):
    date_sequence = GenerateDateSequence(req_dict["start_date"], req_dict["return_date"])
    where_statement = "(" + ",".join(date_sequence) + ")"
    quey_string = f"SELECT * from {req_dict['preferred_hotel']} WHERE Date In {where_statement}"
    return pd.read_sql_query(quey_string, conn)

def CheckAlternativeHotels(req_dict):
    hotel_names =  [ hotel for hotel in GetTableNames(cursor=cur) if req_dict["preferred_hotel"] != hotel]
    alternative_hotels = []
    for cur_hotel in hotel_names:
        req_dict["preferred_hotel"] = cur_hotel
        dates_df = CheckHotelDates(req_dict)
        if(len(dates_df)<1):
           alternative_hotels.append(cur_hotel)
        else:
            max_booking_count = int(dates_df.groupby("Date").size().sort_values(ascending=False)[0])
            if(max_booking_count + int(req_dict["people_count"])  <= MAX_PEOPLE_ON_HOTEL):
                alternative_hotels.append(cur_hotel)
    return alternative_hotels

def RequestHandler(req_dict, method_requested):
    if(method_requested == "/check_hotel_dates" ):
        dates_df = CheckHotelDates(req_dict)
        if(int(req_dict["people_count"])  > MAX_PEOPLE_ON_HOTEL):
            return "Failure"
        if(len(dates_df)<1):
            return "Success"
        else:
            max_booking_count = int(dates_df.groupby("Date").size().sort_values(ascending=False)[0])
            if(max_booking_count + int(req_dict["people_count"])  > MAX_PEOPLE_ON_HOTEL):
                alternatives = CheckAlternativeHotels(req_dict=req_dict)
                if(len(alternatives)>0):
                    return ";".join(alternatives)
                else:
                    return "Failure"
            else:
                return "Success"
    elif(method_requested == "/accept_hotel_dates"):
        return InsertNewBooking(req_dict)
            
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
            req_dict = {}
            recv_data = sock.recv(4096)
            request = recv_data.decode()

            method_requested = request.split(" ")[1]
            request_body = request.split("\r\n")
            request_body_arr = request_body[-1].replace(" ", "").split("&")

            for cur_el in request_body_arr:
                key, val = cur_el.strip().split("=") 
                req_dict[key] = val
            
            req_result = RequestHandler(req_dict, method_requested)
            trip_result += req_result.encode()


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
print(f"Hotel Socket server is listening on {HOST}:{PORT}")
lsock.setblocking(False)


sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)