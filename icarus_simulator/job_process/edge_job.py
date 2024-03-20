# 2020 Tommaso Ciussani and Giacomo Giuliari

import sys
import pickle
from typing import List, Tuple, Dict

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.phases.edge_phase import EdgeMultiproc
from icarus_simulator.structure_definitions import (
    PathData,
    GridPos,
    Pname,
    EdgeData,
    EdgeInfo,
    SatPos,
    Path,
    PathId,
    Edge,
    TempEdgeInfo,
)

class EdgeJob(BaseJob):
    def run_multiprocessor(self, data_path, process_params_path, output_path):
        # Deserialize the input data
        with open(data_path, 'rb') as data_file:
            all_paths = pickle.load(data_file)

        # Deserialize the process parameters
        with open(process_params_path, 'rb') as params_file:
            (ed_strat,) = pickle.load(params_file)  # Assuming a single strategy object for simplicity

        # Instantiate EdgeMultiproc with deserialized data and parameters
        multi = EdgeMultiproc(
            num_procs=self.num_procs,  # Use the inherited num_procs value from BaseJob
            num_batches=self.num_batches,  # Use the inherited num_batches value from BaseJob
            samples=all_paths,
            process_params=(ed_strat,),
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

    job = EdgeJob()
    job.run_multiprocessor(data_file_path, process_params_file_path, output_file_path)
