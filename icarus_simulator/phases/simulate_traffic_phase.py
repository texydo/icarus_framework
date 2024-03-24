#  2020 Tommaso Ciussani and Giacomo Giuliari

from typing import List, Tuple

from icarus_simulator.phases.base_phase import BasePhase
from icarus_simulator.strategies.base_strat import BaseStrat

from icarus_simulator.strategies.traffic_select_simulation.base_bw_select_simulation import(
    BaseBwSelectSimulation,
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
)


class SimulatedTrafficPhase(BasePhase):
    def __init__(
        self,
        read_persist: bool,
        persist: bool,
        select_strat: BaseBwSelectSimulation,
        assign_strat: BaseBwAssignSimulation,
        grid_in: Pname,
        paths_in: Pname,
        edges_in: Pname,
        traffic_out: Pname,
    ):
        super().__init__(read_persist, persist)
        self.select_strat: BaseBwSelectSimulation = select_strat
        self.assign_strat: BaseBwAssignSimulation = assign_strat 
        self.ins: List[Pname] = [grid_in, paths_in, edges_in]
        self.outs: List[Pname] = [traffic_out]

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
        return "RegTraffic"

    def _compute(
        self, grid_pos: GridPos, path_data: PathData, edge_data: EdgeData
    ) -> Tuple[BwData]:
        
        # TODO: Initialize and get wanted networks
        # TODO: Simulate bw allocation according to wanted desire
        # TODO: return routing_paths bw_routing_paths, bw_with_attack_routing paths
        chosen_paths = self.select_strat.compute(grid_pos, path_data)

        # Assign the paths sequentially
        bw_data = self.assign_strat.compute(path_data, chosen_paths, edge_data)
        return ({"paths": chosen_paths,"bw_data": bw_data},)

    def _check_result(self, result: Tuple[BwData]) -> None:
        bw_data = result[0]['bw_data']
        for bd in bw_data.values():
            assert bd.idle_bw <= bd.capacity
        return
