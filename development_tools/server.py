import socket
from multiprocessing import Process

def handle_client(client_socket: socket):
    try:
        # Sending initial data to client for calculation
        initial_data = "Calculate this"
        client_socket.sendall(initial_data.encode())
        
        # Waiting for the client's response
        client_response = client_socket.recv(1024)
        print(f"Received calculation result: {client_response.decode()}")
    finally:
        client_socket.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 40900))
    server_socket.listen(50)
    print("Server listening on port 40900...")

    try:
        while True:
            client_sock, address = server_socket.accept()
            print(f"Accepted connection from {address}")
            client_process = Process(target=handle_client, args=(client_sock,))
            client_process.start()
    finally:
        server_socket.close()

def print_ip(port_num=40900):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    entry = f"{IP}:{port_num}\n"
    print(entry)


if __name__ == "__main__":
    print_ip()
    server()
