import socket, struct, threading

PROXY_HOST, PROXY_PORT = '0.0.0.0', 8989

def handle(cs, addr):
    print(f"[+] {addr}")
    cs.recv(262); cs.send(b'\x05\x00')
    data = cs.recv(262)
    if data[1] == 1:
        if data[3] == 1:  
            host, port = socket.inet_ntoa(data[4:8]), struct.unpack('>H', data[8:10])[0]
        elif data[3] == 3:  
            host, port = data[4:4+data[4]].decode(), struct.unpack('>H', data[5+data[4]:7+data[4]])[0]
        else:
            cs.close(); return
        print(f"{host}:{port}")
        ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts.connect((socket.gethostbyname(host), port))
        cs.send(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + struct.pack('>H', 0))
        def f(s, d): [d.send(c) for c in iter(lambda: s.recv(8192), b'')]
        threading.Thread(target=f, args=(cs, ts)).start()
        threading.Thread(target=f, args=(ts, cs)).start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((PROXY_HOST, PROXY_PORT))
s.listen(50)
print(f"SOCKS5 on {PROXY_HOST}:{PROXY_PORT}")
while True:
    threading.Thread(target=handle, args=s.accept()).start()