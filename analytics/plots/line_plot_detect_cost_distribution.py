import sys
import os

# Add the parent directory (analytics) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from sim_data_loader import SimulationDataLoader
import matplotlib.pyplot as plt

def plot_hist(dict_detectability, save_path, title_name,x_label):
    plt.hist(dict_detectability, bins=50, edgecolor='black', alpha=0.7)
    # Add title and labels
    plt.title(f'Distribution of {title_name}')
    plt.xlabel(f'{x_label}')
    plt.ylabel('Frequency')
    # Show the plot
    plt.savefig(save_path)
    
    plt.close()
    
def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    counter = 0
    
    
    save_snapshot_detect = '/home/roeeidan/icarus_framework/analytics/outputs/line_dstribution/distribution_detectability_snap_shot_line.png'
    save_scenario_detect = '/home/roeeidan/icarus_framework/analytics/outputs/line_dstribution/distribution_detectability_scenario_shot_line.png'
    save_snapshot_cost = '/home/roeeidan/icarus_framework/analytics/outputs/line_dstribution/distribution_cost_snap_shot_line.png'
    save_scenario_cost = '/home/roeeidan/icarus_framework/analytics/outputs/line_dstribution/distribution_cost_scenario_shot_line.png'
    
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                scenario_detectability = []
                scenario_cost = []
                scenario_no_attacks_counter = 0
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        counter +=1
                        if counter % 5 == 0:
                            print(f"Current step: {counter}", flush=True)
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("LAtk")
                        snapshot_detectability = []
                        snapshot_cost = []
                        snapshot_no_attack_counter = 0
                        if "LAtk" in loader.data_cache:
                            datas = loader.data_cache["LAtk"][0]
                            for data in datas.values():
                                if data is None:
                                    snapshot_no_attack_counter +=1
                                    continue
                                detectability = data.detectability
                                cost = data.cost
                                snapshot_detectability.append(detectability)
                                snapshot_cost.append(cost)
                                
                        scenario_detectability.extend(snapshot_detectability)
                        scenario_cost.extend(snapshot_cost)
                        scenario_no_attacks_counter += snapshot_no_attack_counter
                        
                        plot_hist(snapshot_detectability,save_snapshot_detect, "Snapshot Attack Detect",'Detection Metric')
                        plot_hist(snapshot_cost, save_snapshot_cost, "Snapshot Attack Cost",'Cost Metric' )
                        print(f"Snapshot number of no attacks {snapshot_no_attack_counter} / {len(datas)}")
                plot_hist(scenario_detectability, save_scenario_detect, "Scenario Attack Detect",'Detection Metric')
                plot_hist(scenario_cost, save_scenario_cost, "Scenario Attack Cost", 'Cost Metric')
                print(f"Scenario number of no attacks {scenario_no_attacks_counter}")
                return             
                        
                        
                        
                        


# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)