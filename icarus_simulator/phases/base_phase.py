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
        self.num_jobs = 20
        self.temp_data_path = "icarus_simulator/temp_data"

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
        self.serialize_data(process_params, f"params.pkl")
        for i, chunk in enumerate(data_chunks):
            self.serialize_data(chunk, f"data_{i}.pkl")
            self.creat_run_file(i, job_name)
        self.wait_for_jobs_completion()
        results = self.aggregate_results()
        self.cleanup()
        return results