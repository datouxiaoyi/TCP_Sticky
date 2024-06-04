import socket
import time

def receive_message(sock):
    buffer = b""
    delimiter = b"<END>"
    while True:
        packet = sock.recv(1024)
        if not packet:
            break
        buffer += packet
        print("f缓冲区数据: {buffer} ")
        
        while True:
            end_index = buffer.find(delimiter)
            if end_index != -1:  
                message = buffer[:end_index]  
                buffer = buffer[(end_index + len(delimiter)):]  
                print(f"收到客户端消息: { message.decode()} ")
            else:
                break
        time.sleep(5)              

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('localhost', 8888))
server_sock.listen(1)
client_sock, _ = server_sock.accept()
receive_message(client_sock)
client_sock.close()
server_sock.close()
