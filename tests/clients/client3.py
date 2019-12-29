import socket
import sys

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket has been created")
except socket.error as err:
    print("Scoket was not created due to the following errors:")
    print(err)

host = '127.0.0.8'
port = 8000

s.connect((host, port))

s.sendall("GET /tests/html/cars/tesla.html HTTP/1.1\r\nHost: 127.0.0.8:8000\r\n Conection: keep-alive\r\n".encode("utf-8"))
data = s.recv(1024)
while not data.decode('utf-8') == '':
    print('Received', repr(data))
    data = s.recv(1024)
s.close()