import socket
import time
import sys

def client(job_numeric_id):
    while True:  # Infinite loop to keep trying to connect
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('132.72.65.234', 40900))  # Adjust the IP if necessary
            print("Connected to server.")
            break  # Break out of the loop once connected

        except ConnectionRefusedError:
            print("Connection refused by the server. Retrying in 0.3 seconds...")
            time.sleep(0.3)  # Shorter wait time before retrying

    # Once connected, proceed with the rest of the code
    # Receiving data from the server
    data_from_server = client_socket.recv(1024)
    print(f"Received from server: {data_from_server.decode()}")

    # Simulate calculation and send a result back to the server
    ip_data = print_ip()
    calculation_result = f"{ip_data} {job_numeric_id}"
    client_socket.sendall(calculation_result.encode())

    client_socket.close()

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
    return IP


if __name__ == "__main__":
    if len(sys.argv) != 2:
        client(job_numeric_id=1)
    job_numeric_id = int(sys.argv[1])
    client(job_numeric_id)
    client(job_numeric_id)
