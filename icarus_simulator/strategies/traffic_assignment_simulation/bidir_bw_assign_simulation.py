#  2020 Tommaso Ciussani and Giacomo Giuliari
from typing import List

from icarus_simulator.strategies.traffic_assignment_simulation.base_bw_assig_simulation import (
    BaseBwAssignSimulation,
)
from icarus_simulator.structure_definitions import (
    BwData,
    PathData,
    EdgeData,
    PathIdCost,
    BwInfo,
)
from icarus_simulator.utils import get_edges


class BidirBwAssignSimulation(BaseBwAssignSimulation):
    def __init__(self, isl_bw: int, udl_bw: int, utilisation: float, **kwargs):
        super().__init__()
        self.isl_bw = isl_bw
        self.udl_bw = udl_bw
        self.utilisation = utilisation
        if len(kwargs) > 0:
            pass  # Appease the unused param inspection

    @property
    def name(self) -> str:
        return "bidi_simulator"

    @property
    def param_description(self) -> str:
        return f"i{self.isl_bw}ud{self.udl_bw}u{self.utilisation}"

    def compute(
        self, path_data: PathData, path_list: List[PathIdCost], edge_data: EdgeData, prints = False
    ) -> BwData:
        allocated, dropped = 0, 0
        max_updown = int(self.udl_bw * self.utilisation)
        max_isl = int(self.isl_bw * self.utilisation)
        bw_data: BwData = {
            ed: (BwInfo(0, self.isl_bw) if -1 not in ed else BwInfo(0, self.udl_bw))
            for ed in edge_data
        }
        actual_traffic = []
        # Allocate one quantum per path
        for path_id in path_list:
            path = path_data[(path_id[0], path_id[1])][path_id[2]][0]
            data_amount = path_id[3]
            # Convert to -1 notation
            first, last = -path[0], -path[-1]
            path[0], path[-1], path_fits = -1, -1, True
            eds = list(get_edges(path))
            # Swap last and second edges: optimisation, moved the downlink check at the beginning
            dlink, sec = eds[-1], eds[1]
            eds[1], eds[-1] = dlink, sec
            # Check if the addition of this communication would fit in the involved edges
            for ed in eds:
                max_link = max_isl
                if -1 in ed:
                    max_link = max_updown
                if len(ed) == 2:
                    if bw_data[ed].idle_bw + 2 * data_amount >= max_link:
                        path_fits = False
                        break
                if bw_data[ed].idle_bw + data_amount >= max_link:  # Can be equal, we have utilisation
                    path_fits = False
                    break
            # If the path fits, add it to the current bandwidths
            if path_fits:
                allocated += 1
                for ed in get_edges(path):
                    inv_ed = (ed[1], ed[0])
                    bw_data[ed].idle_bw += data_amount
                    bw_data[inv_ed].idle_bw += data_amount
                    actual_traffic.append(path_id)
            else:
                dropped += 1
            # Swap back the extremes
            path[0], path[-1] = first, last

        # Interesting data prints
        if prints:
            print(f"Alloc, drop: {allocated}, {dropped}")
        return bw_data, actual_traffic
