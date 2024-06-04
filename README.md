# 一、介绍

TCP一种面向连接的、可靠的、基于字节流的传输层协议。

三次握手：

1.  客户端发送服务端连接请求，等待服务端的回复。
1.  服务端收到请求，服务端回复客户端，可以建立连接，并等待。
1.  客户端收到回复并发送，确认连接。服务端收到回复。连接成功。
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/06d0b266f0884a87bb4ac7b48f14b760~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1362&h=1014&s=106899&e=png&b=ffffff)
四次挥手：

与三次握手不同，客户端和服务端都可以主动断开连接。

1.  服务A向服务B发送FIN报文段，表示没有数据要传输
1.  服务B收到报文段，回复一个ACK报文段，表示也没有数据需要传输了。
1.  服务B发送FIN报文段，请求关闭连接。
1.  服务A收到报文段，服务B发送ACK报文段，服务B收到报文段后直接关闭连接，服务A没有收到回复，也开始断开连接。
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/25caeaf9fd484ae8ab8df8ac9e9a2a29~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1376&h=910&s=98314&e=png&b=ffffff)

因为复杂的三次握手和四次挥手，保证了数据的可靠性和安全性。因此也造成了更大的开销。

# 二、产生的问题

由于TCP的可靠性传输，可以理解为客户端和服务端之间建立了一个传输管道，可以互相不断的传输数据。但是可能由于数据的传输与接收之间存在差异。使用在服务端和客户端之间，存在一个缓冲区，用于数据的缓冲。数据传输之前会先到缓冲区。

例如服务端A和客户端B。A不断向服务端传输数据，B不断处理服务A传输的数据。服务A发送数据到缓冲区，服务B从缓冲区获取数据来处理。由于服务B处理的速度比较慢，就会导致缓冲区堆积多个数据包。当服务B处理完再取时，取出的可能是多个数据包粘在一起的数据包，这时候处理就会出现问题。
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a78450f1db6e448587f402f387323e1a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1390&h=860&s=148154&e=png&b=fffdfd)
# 三、解决方案

设置包长、包头包尾、消息分隔符解决粘包和拆包问题。这些方法通过明确消息边界，确保接收端能够准确地解析每个完整的消息。这里举例数据包分隔符。

## 1、设置包头包尾

现在我们模拟粘包情况，也就是客户端数据堆积。

**Server**

```python
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
```

**Client**

```python
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
```

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/542f4eabe33d4d118bf5245273f57c8a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1263&h=258&s=79008&e=png&b=25456b)

根据服务端输出可以看到，缓冲区已经出现粘包，多个数据包堆积到一起，这里利用包头包尾进行拆包，确保数据的完整性。

## 2、设置包长

**Server**

```python
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
```

**Client**

```python
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
```

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d5e9cf87e7ab4d48b901bda1782b44c4~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1258&h=414&s=94784&e=png&b=24456b)

可以看到由于处理的时间过长，导致数据堆积在缓冲区形成粘包。通过在消息头部设置包长，确定数据包的完整性。通过包长将粘包进行拆包。

## 3、设置包分隔符

**Server**

```python
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
```

**Client**

```python
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
```

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ba520f5fc38e47afa28ad3c0e1bac882~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=979&h=226&s=66627&e=png&b=25456b)

可以看到也是出现了数据堆积，粘包，但是最后打印的结果是正确的。通过使用数据包分隔符，保证数据的完整性。

# 四、总结
TCP粘包问题是由于TCP的流式传输特点导致的，在传输过程中多个数据包可能会粘在一起。粘包问题会导致接收端无法正确解析数据包，因为接收端无法区分哪些字节属于哪个数据包，可能会出现数据包内容混乱或不完整的情况。为了解决这个问题，可以使用固定长度消息、消息分隔符、消息头加消息体、应用层协议等方法。具体选择哪种方法需要根据应用场景和需求来确定。