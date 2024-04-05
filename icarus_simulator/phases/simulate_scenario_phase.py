#  2020 Tommaso Ciussani and Giacomo Giuliari

from typing import List, Tuple, Dict
import networkx
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
from icarus_simulator.multiprocessor import Multiprocessor
from icarus_simulator.structure_definitions import (
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
        self.ins: List[Pname] = [grid_in, paths_in, edges_in, zattack_in]
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
        return "SimScenario"

    def _compute(
        self, grid_pos: GridPos, path_data: PathData, edge_data: EdgeData, zone_attack_data: ZoneAttackData
    ) -> Tuple[Dict[PathData,BwData]]:
        # TODO turn this into multple jobs / process will probably be smart and faster?
        index = 0
        samples = []
        for zatk in zone_attack_data.values():
            if zatk is None:
                continue
            samples.append([zatk, index])
            index +=1
            if index < 20:
                break
            
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
        print(f"It took {time.time() - start_time}")
        result = [ret_dict[i] for i in range(len(ret_dict))]
        # TODO edit the results to the way i want it to be
        return result #TODO

    def _check_result(self, result: Tuple[Dict[PathData,BwData]]) -> None:
        bw_data = result[0]['bw_data']
        for bd in bw_data.values():
            assert bd.idle_bw <= bd.capacity
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
        import time
        start_time = time.time()
        # Creates normal simulated traffic TODO update bw_data into networkx
        wanted_paths = select_strat.compute(grid_pos, path_data)
        print(f"Part A1 {time.time() - start_time}")
        start_time = time.time()
        bw_data, actual_traffic = assign_strat.compute(path_data, wanted_paths, edge_data)
        print(f"Part A2 {time.time() - start_time}")
        start_time = time.time()
        # Creates attack  simulated traffic TODO update bw_data into networkx
        atkflowset = zatk.atkflowset
        chosen_paths = attack_select_strat.compute(path_data, atkflowset, wanted_paths)
        print(f"Part B1 {time.time() - start_time}")
        start_time = time.time()
        bw_data, actual_traffic = assign_strat.compute(path_data, chosen_paths, edge_data)
        print(f"Part B2 {time.time() - start_time}")
        # TODO create a random routing scenario
        # TODO insert the attack
        # TODO make them networkx
        process_result[index] = {"bw_data": bw_data,"actual_traffic": actual_traffic}
