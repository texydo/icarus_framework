#  2020 Tommaso Ciussani and Giacomo Giuliari

from typing import List, Tuple, Dict

from icarus_simulator.phases.base_phase import BasePhase
from icarus_simulator.strategies.base_strat import BaseStrat
from icarus_simulator.strategies.traffic_select_attack_simulation.base_attack_select_simulation import (
    BaseAttackSelectSimulation,
)
from icarus_simulator.strategies.traffic_assignment_simulation.base_bw_assig_simulation import (
    BaseTrafficAssignSimulation,
)
from icarus_simulator.multiprocessor import Multiprocessor
from icarus_simulator.structure_definitions import (
    GridPos,
    Pname,
    BwData,
    PathData,
    EdgeData,
    ZoneAttackData,
    TrafficData,
    ZoneAttackInfo,
)


class SimulatedAttackTrafficPhase(BasePhase):
    def __init__(
        self,
        read_persist: bool,
        persist: bool,
        num_procs: int,
        num_batches: int,
        run_jobs: bool,
        select_strat: BaseAttackSelectSimulation,
        assign_strat: BaseTrafficAssignSimulation,
        paths_in: Pname,
        edges_in: Pname,
        zattack_in: Pname,
        traffic_in: Pname,
        attack_traffic_out: Pname,
    ):
        super().__init__(read_persist, persist)
        self.num_procs = num_procs
        self.num_batches = num_batches
        self.run_jobs = run_jobs
        self.select_strat: BaseAttackSelectSimulation = select_strat
        self.assign_strat: BaseTrafficAssignSimulation = assign_strat
        self.ins: List[Pname] = [paths_in, edges_in, zattack_in, traffic_in]
        self.outs: List[Pname] = [attack_traffic_out]

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
        return "AttackTraffic"

    def _compute(
        self, path_data: PathData, edge_data: EdgeData, zone_attack_data: ZoneAttackData, traffic_data: TrafficData 
    ) -> Tuple[List[Tuple[TrafficData]]]:
        # TODO make it into jobs
        index = 0
        samples = []
        for zatk in zone_attack_data.values():
            if zatk is None:
                continue
            samples.append([zatk,index])
            index +=1
            if index > 40:
                break
        if len(samples) ==0:
            return (None,)
        if self.run_jobs:
            job_name = "AttackTrafficSimulatJob"
            process_params=(path_data, edge_data, traffic_data, self.select_strat, self.assign_strat)
            ret_dict = self.initate_jobs(samples, process_params, job_name)
        else:
            # Start a multithreaded computation
            multi = AttackTrafficSimulateMultiproc(
                self.num_procs,
                self.num_batches,
                samples,
                process_params=process_params,
            )
            ret_dict = multi.process_batches()  # It must be a tuple!
        result = [ret_dict[i] for i in range(len(ret_dict))]
        return (result,)

    def _check_result(self, result: Tuple[TrafficData]) -> None:
        for data in result[0]:
            if data is None:
                continue
            bw_data = data['bw_data']
            break
        if bw_data is None:
            return
        for bd in bw_data.values():
            assert bd.idle_bw <= bd.capacity
        return
    
class AttackTrafficSimulateMultiproc(Multiprocessor):
    def _single_sample_process(
        self, sample: List, process_result: Dict, params: Tuple
    ) -> None:
        zatk: ZoneAttackInfo
        select_strat: BaseAttackSelectSimulation
        assign_strat: BaseTrafficAssignSimulation
        zatk = sample[0]
        index = sample[1]
        path_data, edge_data, traffic_data, select_strat, assign_strat = params
        if zatk is None:
                process_result[index] = None
        else:
            atkflowset = zatk.atkflowset
            chosen_paths = select_strat.compute(path_data, atkflowset, traffic_data['paths'])
            bw_data, actual_traffic = assign_strat.compute(path_data, chosen_paths, edge_data)
            process_result[index] = {"bw_data": bw_data,"actual_traffic": actual_traffic}
