# 2020 Tommaso Ciussani and Giacomo Giuliari

import sys
import pickle

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.phases.link_attack_phase import AttackMultiproc
from icarus_simulator.structure_definitions import (
    GridPos,
    Pname,
    BwData,
    PathData,
    EdgeData,
    Edge,
    AttackInfo,
    AttackData,
)

class LinkAttackJob(BaseJob):
    def run_multiprocessor(self, data_path, process_params_path, output_path):
        # Deserialize the input data
        with open(data_path, 'rb') as data_file:
            edges = pickle.load(data_file)

        # Deserialize the process parameters
        with open(process_params_path, 'rb') as params_file:
            filter_strat, feas_strat, optim_strat, path_data, edge_data, bw_data, allowed_sources = pickle.load(params_file)

        # Instantiate AttackMultiproc with deserialized data and parameters
        multi = AttackMultiproc(
            num_procs=self.num_procs,
            num_batches=self.num_batches, 
            samples=edges,
            process_params=(
                filter_strat,
                feas_strat,
                optim_strat,
                path_data,
                edge_data,
                bw_data,
                allowed_sources,
            ),
        )

        # Process batches and store the results
        result = multi.process_batches()
        with open(output_path, 'wb') as output_file:
            pickle.dump(result, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py data_file_path process_params_file_path output_file_path")
        sys.exit(1)

    data_file_path = sys.argv[1]
    process_params_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    job = LinkAttackJob()
    job.run_multiprocessor(data_file_path, process_params_file_path, output_file_path)
