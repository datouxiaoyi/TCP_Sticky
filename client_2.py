import socket
import struct
import time

def send_message(sock, message):
    message_bytes = message.encode()
    message_length = len(message_bytes)
    header = struct.pack('>I', message_length)
    packet = header + message_bytes
    sock.sendall(packet)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

for i in range(1, 11):
    message = "Hello, world!--" + str(i)
    send_message(sock, message)
    print(f"发送消息:{message}" )
    time.sleep(1)

sock.close()
