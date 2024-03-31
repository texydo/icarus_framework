# 2020 Tommaso Ciussani and Giacomo Giuliari

import sys
import pickle
from typing import List, Tuple, Dict

from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.phases.zone_attack_phase import ZoneAttackMultiproc
from icarus_simulator.structure_definitions import (
    GridPos,
    Pname,
    BwData,
    PathData,
    EdgeData,
    AttackData,
    ZoneAttackData,
    PathEdgeData,
    ZoneAttackInfo,
)

class ZoneAttackJob(BaseJob):
    def run_multiprocessor(self, data_path, process_params_path, output_path):
        # Deserialize the input data
        with open(data_path, 'rb') as data_file:
            zone_pairs = pickle.load(data_file)

        # Deserialize the process parameters
        with open(process_params_path, 'rb') as params_file:
            build_strat, edges_strat, bneck_strat, filter_strat, feas_strat, optim_strat, grid_pos, path_data, bw_data, edge_data, atk_data, allowed_sources = pickle.load(params_file)

        # Instantiate ZoneAttackMultiproc with deserialized data and parameters
        multi = ZoneAttackMultiproc(
            num_procs=self.num_procs,
            num_batches=self.num_batches,
            samples=zone_pairs,
            process_params=(
                build_strat,
                edges_strat,
                bneck_strat,
                filter_strat,
                feas_strat,
                optim_strat,
                grid_pos,
                path_data,
                bw_data,
                edge_data,
                atk_data,
                allowed_sources,
            ),
        )

        # Process batches and store the results
        result = multi.process_batches()
        with open(output_path, 'wb') as output_file:
            pickle.dump(result, output_file)
            
    def run_multiprocessor_server(self, data, process_params):
        zone_pairs = data
        build_strat, edges_strat, bneck_strat, filter_strat, feas_strat, optim_strat, grid_pos, path_data, bw_data, edge_data, atk_data, allowed_sources = process_params
        multi = ZoneAttackMultiproc(
            num_procs=self.num_procs,
            num_batches=self.num_batches,
            samples=zone_pairs,
            process_params=(
                build_strat,
                edges_strat,
                bneck_strat,
                filter_strat,
                feas_strat,
                optim_strat,
                grid_pos,
                path_data,
                bw_data,
                edge_data,
                atk_data,
                allowed_sources,
            ),
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

    job = ZoneAttackJob()
    job.run_multiprocessor(data_file_path, process_params_file_path, output_file_path)
