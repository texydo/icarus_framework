import sys



import os
import time
from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.job_process.edge_job import EdgeJob
from icarus_simulator.job_process.routing_job import RouteJob
from icarus_simulator.job_process.link_attack_job import LinkAttackJob
from icarus_simulator.job_process.zone_attack_job import ZoneAttackJob


# Define a mapping from job type names to the classes
JOB_TYPE_TO_CLASS = {
    "BaseJob": BaseJob,
    "EdgeJob": EdgeJob,
    "RouteJob": RouteJob,
    "LinkAttackJob": LinkAttackJob,
    "ZoneAttackData": ZoneAttackJob,
}

def monitor_file_and_execute_job(job_numeric_id, file_to_monitor):
    print(f"monitoring file {file_to_monitor}", flush=True)
    counter = 0
    while True:
        # Check if the file exists
        if os.path.exists(file_to_monitor):
            start_time = time.time()
            try:
                with open(file_to_monitor, 'r') as file:
                    job_type_name = file.read().strip()  # Read job type from file

                # Define paths based on numeric ID
                file_directory = os.path.dirname(file_to_monitor)
                data_path = os.path.join(file_directory, f"data_{job_numeric_id}.pkl")
                params_path = os.path.join(file_directory, "params.pkl")
                output_path = os.path.join(file_directory, f"output_{job_numeric_id}.pkl")

                # Get the job class from the mapping
                job_class = JOB_TYPE_TO_CLASS.get(job_type_name)

                if job_class:
                    print(f"Executing job: {job_type_name} with ID: {job_numeric_id}", flush=True)
                    # Assume all job classes have a method run_multiprocessor
                    job_object = job_class()
                    job_object.run_multiprocessor(data_path, params_path, output_path)
                    del job_object
                    # After execution, delete the job_type file
                    os.remove(file_to_monitor)
                    print(f"Completed Job", flush=True)
                else:
                    print(f"No valid job class found for job type: {job_type_name} of {job_type_name}", flush=True)
                end_time = time.time()
                print(f"Run time of job {job_type_name} was {end_time-start_time}", flush=True)
                print(f"time start {time.strftime("%H:%M:%S", time.localtime(start_time))} time end {time.strftime("%H:%M:%S", time.localtime(end_time))}", flush=True)
            except FileNotFoundError:
                counter += 1
                if counter % 600 == 0:
                    print("The job type file does not exist.", flush=True)
            # except Exception as e:
            #     print(f"An error occurred: {e}", flush=True)

        time.sleep(1)  # Check every second for the file's presence

if __name__ == "__main__":
    if len(sys.argv) != 3:
        job_numeric_id = 0
        file_to_monitor = "/home/roeeidan/icarus_framework/icarus_simulator/temp_data/run_0.txt"
        print("Usage: python task_monitor.py <job_numeric_id> <file_to_monitor>", flush=True)
        # sys.exit(1)
    else:
        # Convert the first argument to an integer and use the second as is
        job_numeric_id = int(sys.argv[1])
        file_to_monitor = sys.argv[2]
    monitor_file_and_execute_job(job_numeric_id, file_to_monitor)