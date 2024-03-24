#  2020 Tommaso Ciussani and Giacomo Giuliari

from typing import List, Tuple

from icarus_simulator.phases.base_phase import BasePhase
from icarus_simulator.strategies.base_strat import BaseStrat
from icarus_simulator.strategies.traffic_select_attack_simulation.base_attack_select_simulation import (
    BaseAttackSelectSimulation,
)
from icarus_simulator.strategies.traffic_assignment_simulation.base_bw_assig_simulation import (
    BaseBwAssignSimulation,
)
from icarus_simulator.structure_definitions import (
    GridPos,
    Pname,
    BwData,
    PathData,
    EdgeData,
    ZoneAttackData,
    TrafficData,
)


class SimulatedAttackTrafficPhase(BasePhase):
    def __init__(
        self,
        read_persist: bool,
        persist: bool,
        select_strat: BaseAttackSelectSimulation,
        assign_strat: BaseBwAssignSimulation,
        paths_in: Pname,
        edges_in: Pname,
        zattack_in: Pname,
        traffic_in: Pname,
        attack_traffic_out: Pname,
    ):
        super().__init__(read_persist, persist)
        self.select_strat: BaseAttackSelectSimulation = select_strat
        self.assign_strat: BaseBwAssignSimulation = assign_strat
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
        result = []
        counter = 0
        for zatk in zone_attack_data.values():
            if zatk is None:
                result.append(None)
                continue
            atkflowset = zatk.atkflowset
            chosen_paths = self.select_strat.compute(path_data, atkflowset, traffic_data['paths'])
            # Assign the paths sequentially
            bw_data = self.assign_strat.compute(path_data, chosen_paths, edge_data)
            #TODO extract more data (on the actual paths)
            result.append({"paths": chosen_paths,"bw_data": bw_data})    
            counter +=1
            if counter == 3:
                break
        return (result,)

    def _check_result(self, result: Tuple[TrafficData]) -> None:
        for data in result:
            if data is None:
                continue
            bw_data = data['bw_data']
            break
        for bd in bw_data.values():
            assert bd.idle_bw <= bd.capacity
        return
