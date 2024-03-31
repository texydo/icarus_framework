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
        self.num_jobs = 16
        self.run_server = False
        self.temp_data_path = "icarus_simulator/temp_data"
        self.port = 40900
        self.shared_dict = Manager().dict()
        self.server_socket = None

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

    def wait_for_jobs_completion(self):
        """
        Waits until all output files have been created for all job indices.
        """
        print(f"Waiting for all jobs to complete...")
        all_files_exist = False
        while not all_files_exist:
            all_files_exist = True
            for i in range(self.num_jobs):
                output_file_path = os.path.join(self.temp_data_path, f"output_{i}.pkl")
                if not os.path.exists(output_file_path):
                    all_files_exist = False
                    break
            if not all_files_exist:
                time.sleep(5)  # Wait for 5 seconds before checking again
        
        print("All jobs completed.")
        
    def aggregate_results(self):
        aggregated_results = {}
        for i in range(self.num_jobs):
            output_path = os.path.join(self.temp_data_path, f"output_{i}.pkl")
            with open(output_path, 'rb') as file:
                job_results = pickle.load(file)
                aggregated_results.update(job_results)
        return aggregated_results

    def cleanup(self):
        # Remove all created files in the temp_data_path
        for filename in os.listdir(self.temp_data_path):
            file_path = os.path.join(self.temp_data_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
    def initate_jobs(self, data, process_params, job_name):
        data_chunks = [data[i::self.num_jobs] for i in range(self.num_jobs)]        
        if self.run_server:
            start_time = time.time()
            try:
                data_list = [(job_name, chunk, process_params) for chunk in data_chunks]
                self.server(data_list)        
                print(f"{self.name} computed computed AAAAA in {time.time() - start_time}")
                results = self.aggregate_results_socket()
                
            except Exception as inner_error:
                if self.server_socket is not None:
                    self.server_socket.close()
                raise RuntimeError("An error occurred") from inner_error
        else:
            self.serialize_data(process_params, f"params.pkl")
            for i, chunk in enumerate(data_chunks):
                self.serialize_data(chunk, f"data_{i}.pkl")
                self.creat_run_file(i, job_name)
            self.wait_for_jobs_completion()
            results = self.aggregate_results()
            self.cleanup()
        return results
    
    def aggregate_results_socket(self):
        aggregated_results = {}
        for job_results in self.shared_dict:
            aggregated_results.update(self.shared_dict[job_results])
        self.shared_dict = {}
        return aggregated_results
    
    def server(self, data_list):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(50)
        print("Server listening on port 40900...", flush=True)

        processes = []  # List to hold references to the client processes
        counter = 0
        try:
            for data_part in data_list:
                # print("Waiting for a client connection...")
                client_sock, client_addr = self.server_socket.accept()
                # print(f"Accepted connection from {client_addr}")
                client_process = Process(target=self.handle_client, args=(client_sock, client_addr, data_part, counter))
                client_process.start()
                processes.append(client_process)  # Store the reference to the client process
                counter += 1

            # Wait for all client processes to complete
            for p in processes:
                p.join()
        finally:
            self.server_socket.close()
            self.server_socket = None
    
    def recv_all(self, sock, n):
        """Helper function to receive n bytes or return None if EOF is hit"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    def receive_data_from_client(self, client_socket):
        """Read data sent by the client"""
        raw_msglen = self.recv_all(client_socket, 4)
        if not raw_msglen:
            # print("Unable to receive the message length from the client")
            return None

        msglen = struct.unpack('>I', raw_msglen)[0]
        serialized_data = self.recv_all(client_socket, msglen)
        data = pickle.loads(serialized_data)
        return data
    
    def handle_client(self, client_socket: socket, client_address, data_to_send, id):
        # print(f"Sending data to {client_address}")
        
        serialized_data = pickle.dumps(data_to_send)
        client_socket.sendall(len(serialized_data).to_bytes(4, 'big'))
        client_socket.sendall(serialized_data)

        # Read data sent by the client
        self.shared_dict[id] = self.receive_data_from_client(client_socket)
        # Close the client socket
        client_socket.close()