#  2020 Tommaso Ciussani and Giacomo Giuliari

from typing import List, Tuple, Dict
from icarus_simulator.phases.base_phase import BasePhase
from icarus_simulator.strategies.base_strat import BaseStrat

from icarus_simulator.strategies.traffic_select_simulation.base_bw_select_simulation import(
    BaseBwSelectSimulation,
)
from icarus_simulator.strategies.traffic_assignment_simulation.base_bw_assig_simulation import (
    BaseTrafficAssignSimulation,
)
from icarus_simulator.strategies.traffic_select_attack_simulation.base_attack_select_simulation import (
    BaseAttackSelectSimulation,
)
from icarus_simulator.strategies.training_data_creation.base_training_data import (
    BaseDataCreation
)
from icarus_simulator.multiprocessor import Multiprocessor
from icarus_simulator.structure_definitions import (
    SatPos,
    GridPos,
    Pname,
    BwData,
    PathData,
    EdgeData,
    ZoneAttackData,
    ZoneAttackInfo,
)


class SimulatedScenarioPhase(BasePhase):
    def __init__(
        self,
        read_persist: bool,
        persist: bool,
        num_procs: int,
        num_batches: int,
        num_jobs: int,
        run_jobs: bool,
        run_server: bool,
        select_strat: BaseBwSelectSimulation,
        assign_strat: BaseTrafficAssignSimulation,
        attack_select_strat: BaseAttackSelectSimulation,
        training_data_strat : BaseDataCreation,
        sat_in: Pname,
        grid_in: Pname,
        paths_in: Pname,
        edges_in: Pname,
        zattack_in: Pname,
        scenario_out: Pname,
    ):
        super().__init__(read_persist, persist)
        self.num_procs = num_procs
        self.num_batches = num_batches
        self.num_jobs = num_jobs
        self.run_jobs = run_jobs
        self.run_server = run_server
        self.select_strat: BaseBwSelectSimulation = select_strat
        self.assign_strat: BaseTrafficAssignSimulation = assign_strat 
        self.attack_select_strat: BaseAttackSelectSimulation = attack_select_strat
        self.training_data_strat : BaseDataCreation = training_data_strat
        self.ins: List[Pname] = [sat_in, grid_in, paths_in, edges_in, zattack_in]
        self.outs: List[Pname] = [scenario_out]

    @property
    def input_properties(self) -> List[Pname]:
        return self.ins

    @property
    def output_properties(self) -> List[Pname]:
        return self.outs

    @property
    def _strategies(self) -> List[BaseStrat]:
        return [self.select_strat, self.assign_strat]

    @property
    def name(self) -> str:
        return "SimScenarioWeightedDetectability"

    def _compute(
        self, sat_pos: SatPos, grid_pos: GridPos, path_data: PathData, edge_data: EdgeData, zone_attack_data: ZoneAttackData
    ) -> Tuple[Dict[PathData,BwData]]:
        index = 0
        samples = []
        filtered_and_sorted_zatk_objects = sorted((zatk for zatk in zone_attack_data.values() if zatk is not None),
                                                  key=lambda zatk: zatk.detectability,reverse=True)
        indexed_zatk_list = [[zatk, index] for index, zatk in enumerate(filtered_and_sorted_zatk_objects)]
        samples = indexed_zatk_list[:5]
        # for zatk in zone_attack_data.values():
        #     if zatk is None:
        #         continue
        #     samples.append([zatk, index])
        #     index +=1
        #     if index >= 10:
        #         break
        print(f"Number of scenarios:{len(samples)}")
        process_params = (grid_pos, path_data, edge_data,
                          self.select_strat, self.assign_strat, self.attack_select_strat)
        import time
        start_time = time.time()
        if self.run_jobs:
            job_name = "ScenarioSimulatJob"
            ret_dict = self.initate_jobs(samples, process_params, job_name)
        else:
            # Start a multithreaded computation
            multi = ScenarioSimulateMultiproc(
                self.num_procs,
                self.num_batches,
                samples,
                process_params=process_params
            )
            ret_dict = multi.process_batches()  # It must be a tuple!
        results = [ret_dict[i] for i in range(len(ret_dict))]
        for res in results:
            reg_bw = res["reg_bw_data"]
            self.training_data_strat.compute(sat_pos=sat_pos, bw_data=reg_bw, y=0)
            atk_bw = res["atk_bw_data"]
            self.training_data_strat.compute(sat_pos=sat_pos, bw_data=atk_bw, y=1)
        transformed_list = [{"atk_actual_traffic": d["atk_actual_traffic"], "reg_actual_traffic": d["reg_actual_traffic"]} for d in results]
        return (transformed_list,)

    def _check_result(self, result: Tuple[Dict[PathData,BwData]]) -> None:
        return

class ScenarioSimulateMultiproc(Multiprocessor):
    def _single_sample_process(
        self, sample: List, process_result: Dict, params: Tuple
    ) -> None:
        zatk: ZoneAttackInfo
        select_strat: BaseBwSelectSimulation
        assign_strat: BaseTrafficAssignSimulation
        attack_select_strat: BaseAttackSelectSimulation
        zatk = sample[0]
        index = sample[1]
        grid_pos, path_data, edge_data, select_strat, assign_strat, attack_select_strat = params
        wanted_traffic = select_strat.compute(grid_pos, path_data)
        reg_bw_data, reg_actual_traffic = assign_strat.compute(path_data, wanted_traffic, edge_data)
        atkflowset = zatk.atkflowset
        chosen_paths = attack_select_strat.compute(path_data, atkflowset, wanted_traffic)
        atk_bw_data, atk_actual_traffic = assign_strat.compute(path_data, chosen_paths, edge_data)
        process_result[index] = {"atk_bw_data": atk_bw_data, "atk_actual_traffic": atk_actual_traffic,
                                 "reg_bw_data": reg_bw_data, "reg_actual_traffic": reg_actual_traffic}
