import sys

import socket
import pickle
import struct
import time
import asyncio
from aiofiles import open as async_open

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.job_process.edge_job import EdgeJob
from icarus_simulator.job_process.routing_job import RouteJob
from icarus_simulator.job_process.link_attack_job import LinkAttackJob
from icarus_simulator.job_process.zone_attack_job import ZoneAttackJob

import time
# Define a mapping from job type names to the classes
JOB_TYPE_TO_CLASS = {
    "BaseJob": BaseJob,
    "EdgeJob": EdgeJob,
    "RouteJob": RouteJob,
    "LinkAttackJob": LinkAttackJob,
    "ZoneAttackData": ZoneAttackJob,
}

def recv_all(sock, n):
    """Helper function to receive n bytes or return None if EOF is hit"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def receive_data_from_server(client_socket):
    raw_msglen = recv_all(client_socket, 4)
    if not raw_msglen:
        print("Unable to receive the message length", flush=True)
        return None

    msglen = struct.unpack('>I', raw_msglen)[0]
    serialized_data = recv_all(client_socket, msglen)
    if not serialized_data:
        print("Failed to receive the full data", flush=True)
        return None

    # Deserialize the received data
    try:
        data = pickle.loads(serialized_data)
    except (pickle.PickleError, EOFError) as e:
        print(f"Error deserializing data: {e}", flush=True)
        return None

    return data

def client():
    while True:
        try:
            while True:
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect(('132.72.65.234', 40900))
                    print("Connected to server.", flush=True)
                    break
                except ConnectionRefusedError:
                    # print("Connection refused by the server. Retrying in 0.3 seconds...")
                    time.sleep(0.3)
            start_time = time.time()
            job_class_name, data, params = receive_data_from_server(client_socket)
            print(f"Getting Data time took for {job_class_name} was {time.time()-start_time}", flush=True)
            output = calc_process(job_class_name, data, params)
            result_data = pickle.dumps(output)
            client_socket.sendall(len(result_data).to_bytes(4, 'big'))
            client_socket.sendall(result_data)
            print(f"Total time took of {job_class_name} was {time.time()-start_time}", flush=True)
        except Exception as e:
            print(f"An error occurred: {e}", flush=True)


        
        
def calc_process(job_class_name, data, params):
    output = None
    print(f"Executing job: {job_class_name}", flush=True)
    if job_class_name in JOB_TYPE_TO_CLASS:
        job_class = JOB_TYPE_TO_CLASS[job_class_name]
        job_object = job_class()
        output = job_object.run_multiprocessor_server(data, params)
        # serialized_output = pickle.dumps(output)  # Ensure output is serialized
        print(f"Completed Job", flush=True)
    else:
        print(f"Unknown job class: {job_class_name}", flush=True)
    return output


if __name__ == "__main__":
    # server_ip = sys.argv[1]
    client()