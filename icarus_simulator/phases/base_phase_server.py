#  2020 Tommaso Ciussani and Giacomo Giuliari
"""
This class defines the abstraction for a computation phase, passed to the IcarusSimulator class to be executed.
This class is open for custom extension, in order to create different phases.

The input and output parameters are identified in IcarusSimulator by string identifiers, which the phase should provide.
The _compute() method, which accepts any parameter in any number, contains the computation logic. Always returns tuple.
    _compute() is intended as a skeleton, where interchangeable steps are determined by BaseStrategy objects
The methods name() and strategies() are used by IcarusSimulator to manage inter-phase dependencies and filenames.
Moreover, this base class provides some basic logs and the resultfile dumping logic.

For an extension example, see any provided phase class. All files in this directory are library-provided phases.
"""
import os
import time
import pickle

import socket
from multiprocessing import Process, Manager
import struct

from abc import abstractmethod
from typing import List, Any, Tuple
from compress_pickle import compress_pickle

from icarus_simulator.strategies.base_strat import BaseStrat
from icarus_simulator.structure_definitions import Pname


class BasePhase:

    # Methods to override
    def __init__(self, read_persist: bool, persist: bool):
        self.read_persist: bool = read_persist
        self.persist: bool = persist
        self.num_jobs = 40
        self.port = 40900
        self.shared_list = Manager().list()

    @property
    def input_properties(self) -> List[Pname]:
        raise NotImplementedError

    @property
    def output_properties(self) -> List[Pname]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def _strategies(self) -> List[BaseStrat]:
        raise NotImplementedError

    @abstractmethod
    def _compute(self, *args) -> Tuple:
        # Compute the result here, and always return a tuple, even if it has just one element in it!
        raise NotImplementedError

    @abstractmethod
    def _check_result(self, result) -> None:
        # Assertions go here
        raise NotImplementedError

    # Non-override methods
    @property
    def description(self) -> str:
        return (
            self.name + "(" + "".join([st.description for st in self._strategies]) + ")"
        )

    def execute_phase(self, input_values: List[Any], fname: str):
        print(f"{self.name} phase")
        start = time.time()
        read = True
        # If a results file is present, read it. Else, compute the result.
        if self.read_persist and os.path.isfile(fname):
            print(f"{self.name} reading")
            result = compress_pickle.load(
                fname, compression="bz2", set_default_extension=False
            )
            print(f"{self.name} read in {time.time() - start}")
        else:
            read = False
            print(f"{self.name} computing")
            assert len(input_values) == len(self.input_properties)
            result = self._compute(*input_values)
            assert len(result) == len(self.output_properties)
            print(f"{self.name} computed in {time.time() - start}")

        # Check the consistency of the results
        self._check_result(result)

        # If the data has been computed and should be persisted, save it to file
        if self.persist and not read:
            st = time.time()
            compress_pickle.dump(
                result, fname, compression="bz2", set_default_extension=False
            )
            print(f"{self.name} write: {time.time() - st}")
        print(f"{self.name} finished in {time.time() - start}")
        print("")
        return result
    
    def serialize_data(self, data, file_name):
        with open(os.path.join(self.temp_data_path, file_name), 'wb') as file:
            pickle.dump(data, file)
    
    def creat_run_file(self, job_index, phase_name):
        file_name = f"run_{job_index}.txt"
        file_path = os.path.join(self.temp_data_path, file_name)
        with open(file_path, 'w') as file:
            file.write(phase_name)
        
    def aggregate_results_socket(self):
        aggregated_results = {}
        for job_results in self.shared_list:
            result_data = pickle.load(job_results)
            aggregated_results.update(result_data)
        return aggregated_results

                
    def initate_jobs(self, data, process_params, job_name):
        data_chunks = [data[i::self.num_jobs] for i in range(self.num_jobs)]        
        data_list = [(job_name, chunk, process_params) for chunk in data_chunks]
        self.server(data_list)        
        results = self.aggregate_results_socket()
        return results
    
    def server(self, data_list):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(50)
        print("Server listening on port 40900...")

        try:
            for data_part in data_list:
                print("Waiting for a client connection...")
                client_sock, client_addr = server_socket.accept()
                print(f"Accepted connection from {client_addr}")
                client_process = Process(target=self.handle_client, args=(client_sock, data_part))
                client_process.start()
        finally:
            server_socket.close()
    
    
    def recv_all(self, sock, n):
        """Helper function to receive n bytes or return None if EOF is hit"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    def handle_client(self, client_socket: socket, client_address, data_to_send):
        print(f"Sending data to {client_address}")
        # Assuming 'data_to_send' is a portion of your large dataset
        # You might need to serialize it before sending, especially if it's not a string
        client_socket.sendall(data_to_send.encode())

        # Wait for the client's response
        raw_msglen = self.recv_all(client_socket, 4)
        if not raw_msglen:
            print("Unable to receive the message length from the client")
            return

        msglen = struct.unpack('>I', raw_msglen)[0]
        data = self.recv_all(client_socket, msglen)
        if not data:
            print("Failed to receive the full message from the client")
            return
        print(f"Received message: {data}")
        self.shared_list.append(data)
        # It's a simplified example; consider how to return this data to the main process
        client_socket.close()