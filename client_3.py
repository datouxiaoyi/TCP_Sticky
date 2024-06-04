import socket
import time

def send_message(sock, message):
    delimiter = b"<END>"
    packet = message.encode() + delimiter 
    sock.sendall(packet)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

for i in range(10):
    message = "Hello, world!--" + str(i)
    send_message(sock, message)
    print(f"发送消息: {message}")
    time.sleep(1)
sock.close()
