import socket
import struct
import time

def receive_message(sock):
    buffer = b""
    while True:
        packet = sock.recv(1024)
        if not packet:
            break
        buffer += packet
        print(f"缓冲区数据 : {buffer}")
        
        while len(buffer) >= 4:  
            header = buffer[:4]
            message_length = struct.unpack('>I', header)[0]
            print(f"包长为: {message_length}")

            if len(buffer) < 4 + message_length:
                break

            start_index = 4
            end_index = 4 + message_length
            message = buffer[start_index:end_index]
            buffer = buffer[end_index:] 
            print(f"收到客户端消息: {message.decode()} ")
        time.sleep(5)  

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('localhost', 8888))
server_sock.listen(1)
client_sock, _ = server_sock.accept()
receive_message(client_sock)
client_sock.close()
server_sock.close()
