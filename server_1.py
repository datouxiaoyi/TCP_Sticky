import socket
import time

def receive_message(sock):
    buffer = b""
    while True:
        packet = sock.recv(1024)
        if not packet:
            break
        buffer += packet
        print("缓冲区数据 : "+ str(buffer))
        time.sleep(5)
        while True:
            start_index = buffer.find(b"StartPackage")
            end_index = buffer.find(b"EndPackage")
            if start_index != -1 and end_index != -1 and start_index < end_index:
                start_index += len(b"StartPackage")
                message = buffer[start_index:end_index]
                buffer = buffer[end_index + len(b"EndPackage"):]  
                print("收到客户端消息: "+message.decode())
            else:
                break 

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('localhost', 8888))
server_sock.listen(1)


client_sock, _ = server_sock.accept()

receive_message(client_sock)
client_sock.close()
server_sock.close()
