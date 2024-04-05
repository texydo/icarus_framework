#  2020 Tommaso Ciussani and Giacomo Giuliari

"""
This file introduces the special mechanism of the configuration file.
The dictionary CONFIG includes entries with all the strategies used in the current simulation definition.
Each entry contains the parameters passed, by name, to the strategy constructors, in a list format.
If you wish to run multiple simulations, you can add the needed parameters to the corresponding list, and the script
will automatically create new instances of the configuration by extending the last elements of all other lists.
For example, setting CONFIG['lsn']['orbits'] = [72, 50] will run two identical simulations, except for this parameter.
If you change a strategy class across simulations, just put the union of all parameters needed. At runtime, unneeded
parameters will be automatically discarded by the different strategy classes.

Running simulations with this method is NOT mandatory, phases can be configured manually every time.
"""
from typing import List, Dict
from icarus_simulator.strategies import *
import random
import json
from datetime import datetime, timedelta

CONFIG = {
    "lsn": {
        "strat": [ManhLSNStrat],
        "inclination": [53],
        "sats_per_orbit": [22],
        "orbits": [72],
        "f": [11],
        "elevation": [550000],
        "hrs": [0],
        "mins": [2],
        "secs": [17],  # list(range(0, 130))
        "millis": [0],
        "epoch": ["2020/01/01 00:00:00"],
    },
    "grid": {"strat": [GeodesicGridStrat], "repeats": [22]},
    "gweight": {"strat": [GDPWeightStrat], "dataset_file": [None]},
    "cover": {"strat": [AngleCovStrat], "min_elev_angle": [40]},
    "rout": {
        "strat": [SSPRoutStrat],
        "desirability_stretch": [2.3],
        "k": [5],
        "esx_theta": [0.5],
    },
    "edges": {"strat": [BidirEdgeStrat]},
    "bw_sel": {"strat": [SampledBwSelectStrat], "sampled_quanta": [250000]},
    "bw_asg": {
        "strat": [BidirBwAssignStrat],
        "isl_bw": [2000],
        "udl_bw": [400],
        "utilisation": [0.9],
    },
    "atk_constr": {
        "strat": [NoConstrStrat],
        "geo_names": [["USA", "RUS"]],
        "grid_points": [[1549, 1530]],
    },
    "atk_filt": {"strat": [DirectionalFilteringStrat]},
    "atk_feas": {
        "strat": [LPFeasStrat],
        "beta": [0.1],
    },
    "atk_optim": {"strat": [BinSearchOptimStrat], "rate": [1.0]},
    "zone_select": {"strat": [RandZoneStrat], "samples": [5000]},
    "zone_build": {"strat": [KclosestZoneStrat], "size": [6]},
    "zone_edges": {
        "strat": [ISLZoneStrat],
    },
    "zone_bneck": {
        "strat": [DetectBneckStrat],
    },
    "traffic_routing_select_simulation":{
        "strat":[RandomTrafficSelectStrat],
        "actual_quanta": [200000],
        "max_data_per_user":[200],
        "average_data_per_user": [5],
    },
    "traffic_routing_asg_simulation":{
        "strat":[BidirTrafficAssignSimulation],
        "isl_bw": [2000],
        "udl_bw": [400],
        "utilisation": [0.9],
        "routing_fix_strat": [1],
        "tries_routing_fix": [0]
    },
    "traffic_attack_select_simulation":{
        "strat":[AttackTrafficSelectStrat]
    }
}


def generate_default_dict(
    lsn_strat=ManhLSNStrat,
    lsn_inclination=53,
    lsn_sats_per_orbit=22,
    lsn_orbits=72,
    lsn_f=11,
    lsn_elevation=550000,
    lsn_hrs=0,
    lsn_mins=2,
    lsn_secs=17,
    lsn_millis=0,
    lsn_epoch="2020/01/01 00:00:00",
    grid_strat=GeodesicGridStrat,
    grid_repeats=22,
    gweight_strat=GDPWeightStrat,
    gweight_dataset_file=None,
    cover_strat=AngleCovStrat,
    cover_min_elev_angle=40,
    rout_strat=SSPRoutStrat,
    rout_desirability_stretch=2.3,
    rout_k=5,
    rout_esx_theta=0.5,
    edges_strat=BidirEdgeStrat,
    bw_sel_strat=SampledBwSelectStrat,
    bw_sel_sampled_quanta=250000,
    bw_asg_strat=BidirBwAssignStrat,
    bw_asg_isl_bw=20000,
    bw_asg_udl_bw=4000,
    bw_asg_utilisation=0.9,
    atk_constr_strat=GeoConstrStrat,
    atk_constr_geo_names=[["USA", "RUS"]],
    atk_constr_grid_points=[[1549, 1530]],
    atk_filt_strat=DirectionalFilteringStrat,
    atk_feas_strat=LPFeasStrat,
    atk_feas_beta=0.1,
    atk_optim_strat=BinSearchOptimStrat,
    atk_optim_rate=1.0,
    zone_select_strat=RandZoneStrat,
    zone_select_samples=5000,
    zone_build_strat=KclosestZoneStrat,
    zone_build_size=6,
    zone_edges_strat=ISLZoneStrat,
    zone_bneck_strat=DetectBneckStrat,
    traffic_routing_select_simulation_strat=RandomTrafficSelectStrat,
    traffic_routing_select_simulation_actual_quanta=50000,
    traffic_routing_select_simulation_max_data_per_user=200,
    traffic_routing_select_simulation_average_data_per_user=5,
    traffic_routing_asg_simulation_strat=BidirTrafficAssignSimulation,
    traffic_routing_asg_simulation_isl_bw=20000,
    traffic_routing_asg_simulation_udl_bw=4000,
    traffic_routing_asg_simulation_utilisation=0.9,
    traffic_routing_asg_simulation_routing_fix_strat=1,
    traffic_routing_asg_simulation_tries_routing_fix=0,
    traffic_attack_select_simulation_strat=AttackTrafficSelectStrat,
):
    return {
        "lsn": {
            "strat": [lsn_strat],
            "inclination": [lsn_inclination],
            "sats_per_orbit": [lsn_sats_per_orbit],
            "orbits": [lsn_orbits],
            "f": [lsn_f],
            "elevation": [lsn_elevation],
            "hrs": [lsn_hrs],
            "mins": [lsn_mins],
            "secs": [lsn_secs],
            "millis": [lsn_millis],
            "epoch": [lsn_epoch],
        },
        "grid": {"strat": [grid_strat], "repeats": [grid_repeats]},
        "gweight": {"strat": [gweight_strat], "dataset_file": [gweight_dataset_file]},
        "cover": {"strat": [cover_strat], "min_elev_angle": [cover_min_elev_angle]},
        "rout": {
            "strat": [rout_strat],
            "desirability_stretch": [rout_desirability_stretch],
            "k": [rout_k],
            "esx_theta": [rout_esx_theta],
        },
        "edges": {"strat": [edges_strat]},
        "bw_sel": {"strat": [bw_sel_strat], "sampled_quanta": [bw_sel_sampled_quanta]},
        "bw_asg": {
            "strat": [bw_asg_strat],
            "isl_bw": [bw_asg_isl_bw],
            "udl_bw": [bw_asg_udl_bw],
            "utilisation": [bw_asg_utilisation],
        },
        "atk_constr": {
            "strat": [atk_constr_strat],
            "geo_names": [atk_constr_geo_names],
            "grid_points": [atk_constr_grid_points],
        },
        "atk_filt": {"strat": [atk_filt_strat]},
        "atk_feas": {"strat": [atk_feas_strat], "beta": [atk_feas_beta]},
        "atk_optim": {"strat": [atk_optim_strat], "rate": [atk_optim_rate]},
        "zone_select": {"strat": [zone_select_strat], "samples": [zone_select_samples]},
        "zone_build": {"strat": [zone_build_strat], "size": [zone_build_size]},
        "zone_edges": {"strat": [zone_edges_strat]},
        "zone_bneck": {"strat": [zone_bneck_strat]},
        "traffic_routing_select_simulation": {
            "strat": [traffic_routing_select_simulation_strat],
            "actual_quanta": [traffic_routing_select_simulation_actual_quanta],
            "max_data_per_user": [traffic_routing_select_simulation_max_data_per_user],
            "average_data_per_user": [traffic_routing_select_simulation_average_data_per_user],
        },
        "traffic_routing_asg_simulation": {
            "strat": [traffic_routing_asg_simulation_strat],
            "isl_bw": [traffic_routing_asg_simulation_isl_bw],
            "udl_bw": [traffic_routing_asg_simulation_udl_bw],
            "utilisation": [traffic_routing_asg_simulation_utilisation],
            "routing_fix_strat": [traffic_routing_asg_simulation_routing_fix_strat],
            "tries_routing_fix": [traffic_routing_asg_simulation_tries_routing_fix],
        },
        "traffic_attack_select_simulation": {"strat": [traffic_attack_select_simulation_strat]},
    }

def get_random_epoch():
    start_datetime = datetime(2020, 1, 1, 0, 0, 0)

    # Define the end datetime as "2023/12/31 00:00:00"
    end_datetime = datetime(2023, 12, 31, 0, 0, 0)

    # Calculate the difference in seconds between the current datetime and the end datetime
    time_diff_seconds = (end_datetime - start_datetime).total_seconds()

    # Generate a random number of seconds within the time difference
    random_seconds = random.uniform(0, time_diff_seconds)

    # Add the random number of seconds to the current datetime to get the random datetime
    random_datetime = start_datetime + timedelta(seconds=random_seconds)

    # Format the random datetime as a string in the same format as the epoch
    random_datetime_string = random_datetime.strftime("%Y/%m/%d %H:%M:%S")
    return random_datetime_string

def load_country_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # Extract the 3-letter ISO country codes
        codes = [feature['properties']['iso_a3'] for feature in data['features'] if feature['properties']['iso_a3'] != "-99"]
    return codes

def get_random_countries(file_path = "icarus_simulator/data/natural_earth_world_small.geo.json"):
    num_countries = random.randint(1,30)
    countries = load_country_names(file_path)
    selected_countries = random.sample(countries, num_countries)
    return selected_countries

def get_random_dict():
    lsn_hrs= random.randint(0,24)
    lsn_mins= random.randint(0,60)
    lsn_secs= random.randint(0,60)
    lsn_epoch = get_random_epoch()
    atk_constr_geo_names = get_random_countries()
    return generate_default_dict(lsn_hrs=lsn_hrs, lsn_mins=lsn_mins, lsn_secs=lsn_secs,
                                 lsn_epoch=lsn_epoch,atk_constr_geo_names=atk_constr_geo_names)


# Here follow methods used for the parsing.
def parse_config(config_lists) -> List[Dict]:
    """ Parse the configuration """
    # Parse the base elements
    # Get a list of all the lists and determine the longest
    full_config = []
    keys = config_lists.keys()
    base_list = []
    for key in keys:
        base_list.extend(list(config_lists[key].values()))
    num_runs = len(max(base_list, key=lambda k: len(k)))

    # Extend all the lists
    for key in keys:
        for inner_key, val in config_lists[key].items():
            val.extend([val[-1]] * (num_runs - (len(val))))

    # Turn lists in dict of dicts
    for idx in range(num_runs):
        run = {}
        for key in keys:
            run[key] = [
                dict(zip(config_lists[key], t))
                for t in zip(*config_lists[key].values())
            ][idx]
        full_config.append(run)
    return full_config


def get_strat(strat_id: str, conf: Dict):
    return conf[strat_id]["strat"](**conf[strat_id])
