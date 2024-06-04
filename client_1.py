import socket
import time

def send_message(sock, message):
    packet = b"StartPackage" + message.encode() + b"EndPackage"  
    sock.sendall(packet)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

for i in range(1,11,1):
    message = "Hello, world!--"+str(i)
    send_message(sock, message)
    print("发送消息 "+message)
    time.sleep(1)
sock.close()