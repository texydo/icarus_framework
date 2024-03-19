import sys
import os
import time
from icarus_simulator.job_process.base_job import BaseJob
from icarus_simulator.job_process.edge_job import EdgeMultiproc
from icarus_simulator.job_process.routing_job import RouteJob
from icarus_simulator.job_process.link_attack_job import LineAttackJob
from icarus_simulator.job_process.zone_attack_job import ZoneAttackData


# Define a mapping from job type names to the classes
JOB_TYPE_TO_CLASS = {
    "BaseJob": BaseJob,
    "EdgeMultiproc": EdgeMultiproc,
    "RouteJob": RouteJob,
    "LineAttackJob": LineAttackJob,
    "ZoneAttackData": ZoneAttackData,
}

def monitor_file_and_execute_job(job_numeric_id, file_to_monitor):
    while True:
        # Check if the file exists
        if os.path.exists(file_to_monitor):
            try:
                with open(file_to_monitor, 'r') as file:
                    job_type_name = file.read().strip()  # Read job type from file

                # Define paths based on numeric ID
                data_path = f"same/folder/data_{job_numeric_id}.pkl"
                params_path = "same/folder/params.pkl"
                output_path = f"same/folder/output_{job_numeric_id}.pkl"

                # Get the job class from the mapping
                job_class = JOB_TYPE_TO_CLASS.get(job_type_name)

                if job_class:
                    print(f"Executing job: {job_type_name} with ID: {job_numeric_id}")
                    # Assume all job classes have a method run_multiprocessor
                    job_class.run_multiprocessor(data_path, params_path, output_path)

                    # After execution, delete the job_type file
                    os.remove(file_to_monitor)
                    print(f"Deleted {file_to_monitor} after successful execution.")
                else:
                    print(f"No valid job class found for job type: {job_type_name} of {job_type_name}")

            except FileNotFoundError:
                print("The job type file does not exist.")
            except Exception as e:
                print(f"An error occurred: {e}")

        time.sleep(1)  # Check every second for the file's presence

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_monitor.py <job_numeric_id> <file_to_monitor>")
        sys.exit(1)
    
    # Convert the first argument to an integer and use the second as is
    job_numeric_id = int(sys.argv[1])
    file_to_monitor = sys.argv[2]
    monitor_file_and_execute_job(job_numeric_id, file_to_monitor)