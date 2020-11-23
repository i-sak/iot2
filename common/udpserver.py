import socket

HOSTs = socket.gethostbyname_ex(socket.gethostname())
HOST = HOSTs[2][0] # "192.168.219.100"
PORT = 8282

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 소켓 생성
sock.bind( (HOST, PORT) )  # 서버의 아이피와 포트번호를 고정

while True :
    data, addr = sock.recvfrom(200)
    print("received data :",data.decode())
    print("Client IP :", addr[0])   # IP출력
    print("Client Port:", addr[1])  # 포트 출력
