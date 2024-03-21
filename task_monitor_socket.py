import sys

import socket
import pickle
import portalocker

import asyncio
from aiofiles import open as async_open

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.job_process.edge_job import EdgeJob
from icarus_simulator.job_process.routing_job import RouteJob
from icarus_simulator.job_process.link_attack_job import LinkAttackJob
from icarus_simulator.job_process.zone_attack_job import ZoneAttackJob


# Define a mapping from job type names to the classes
JOB_TYPE_TO_CLASS = {
    "BaseJob": BaseJob,
    "EdgeJob": EdgeJob,
    "RouteJob": RouteJob,
    "LinkAttackJob": LinkAttackJob,
    "ZoneAttackData": ZoneAttackJob,
}

def receive_all(conn):
    data = b""
    while True:
        part = conn.recv(4096)  # Receive data in 4096-byte chunks
        data += part
        if len(part) < 4096:  # If less data than the chunk size is received, it's likely the end of the data
            break
    return data


def start_server(port=12345, host='0.0.0.0'):  # Listen on all network interfaces
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}", flush=True)
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}", flush=True)
                data = receive_all(conn)
                print(type(data))
                print(f"len data {len(data)}", flush=True)
                if data:
                    try:
                        job_class_name, data, params = pickle.loads(data)
                        print(f"Executing job: {job_class_name}", flush=True)
                        if job_class_name in JOB_TYPE_TO_CLASS:
                            job_class = JOB_TYPE_TO_CLASS[job_class_name]
                            job_object = job_class()
                            output = job_object.run_multiprocessor(data, params)
                            # serialized_output = pickle.dumps(output)  # Ensure output is serialized
                            conn.sendall(output)
                            print(f"Completed Job", flush=True)
                        else:
                            print(f"Unknown job class: {job_class_name}", flush=True)
                            conn.sendall(pickle.dumps("Error: Unknown job class"))
                    except Exception as e:
                        print(f"Error during job execution: {e}")
                        conn.sendall(pickle.dumps(f"Error during job execution: {e}"))
                else:
                    print("No data received.", flush=True)
                    

async def write_to_file(filename, data):
    async with async_open(filename, "a") as f:
        await f.write(data)
        
def write_ip(port_num, update_ip_file):
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
    asyncio.run(write_to_file(update_ip_file, entry))
    # # Append the entry to the file with locking
    # with open(update_ip_file, "a") as f:
    #     portalocker.lock(f, portalocker.LOCK_EX)
    #     f.write(entry)

def get_free_port(job_index, start_port=49152, end_port=65535):
    job_index_str = f"0{job_index}"  # Format job_index as required
    
    for port in range(start_port, end_port + 1):
        if str(port).endswith(job_index_str):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(('0.0.0.0', port))
                    # If bind is successful, return the port
                    return port
            except OSError:
                # This port is already in use, continue checking
                continue

    raise RuntimeError(f"No free port ending with '{job_index_str}' found between {start_port} and {end_port}.")


if __name__ == "__main__":
    job_index = sys.argv[1]
    update_ip_file = sys.argv[2]
    port_num = get_free_port(job_index)
    write_ip(port_num, update_ip_file)
    start_server(port_num)