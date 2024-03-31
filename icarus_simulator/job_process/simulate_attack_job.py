# 2020 Tommaso Ciussani and Giacomo Giuliari
import sys
import pickle
from typing import List, Tuple, Dict

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.phases.simulate_attack_phase import AttackTrafficSimulateMultiproc
from icarus_simulator.structure_definitions import (
    PathData,
    GridPos,
    Coverage,
    SdPair,
    Pname,
    LbSet,
)



class AttackTrafficSimulatJob(BaseJob):
    def run_multiprocessor(self, data_path, process_params_path, output_path):
        # Deserialize the input data
        with open(data_path, 'rb') as data_file:
            samples = pickle.load(data_file)

        # Deserialize the process parameters
        with open(process_params_path, 'rb') as params_file:
            path_data, edge_data, traffic_data, select_strat, assign_strat = pickle.load(params_file)

        # Instantiate AttackTrafficSimulatJob with deserialized data and parameters
        multi = AttackTrafficSimulateMultiproc(
            num_procs=self.num_procs,
            num_batches=self.num_batches,
            samples=samples,
            process_params=(path_data, edge_data, traffic_data, select_strat, assign_strat),
        )

        # Process batches and store the results
        result = multi.process_batches()
        with open(output_path, 'wb') as output_file:
            pickle.dump(result, output_file)
            
    def run_multiprocessor_server(self, data, process_params):
        samples = data
        path_data, edge_data, traffic_data, select_strat, assign_strat = process_params
        multi = AttackTrafficSimulateMultiproc(
            num_procs=self.num_procs,
            num_batches=self.num_batches,
            samples=samples,
            process_params=(path_data, edge_data, traffic_data, select_strat, assign_strat),
        )

        # Process batches and store the results
        result = multi.process_batches()
        return result

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py data_file_path process_params_file_path output_file_path")
        sys.exit(1)

    data_file_path = sys.argv[1]
    process_params_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    job = AttackTrafficSimulatJob()
    job.run_multiprocessor(data_file_path, process_params_file_path, output_file_path)
