import os
import subprocess
import sys

class JobManager:
    def __init__(self, python_script_path, parent_path, env_path, log_data_path, monitor_file_template, num_jobs, cpus_per_job, mem):
        self.python_script_path = python_script_path
        self.parent_path = parent_path
        self.env_path = env_path
        self.log_data_path = log_data_path
        self.monitor_file_template = monitor_file_template
        self.num_jobs = num_jobs
        self.cpus_per_job = cpus_per_job
        self.mem = mem
        self.job_scripts = []
        self.job_ids = []

    def create_job_script(self, job_index):
        # Replace "X" in the template with the current job_index
        monitor_file = self.monitor_file_template.replace("X", str(job_index))
        job_script_name = os.path.join(self.log_data_path, f"job_script_{job_index}.sh")
        with open(job_script_name, 'w') as script_file:
            script_file.write("#!/bin/bash\n")
            script_file.write(f"#SBATCH --job-name=multi_job_{job_index}\n")
            script_file.write(f"#SBATCH --cpus-per-task={self.cpus_per_job}\n")
            script_file.write(f"#SBATCH --output={os.path.join(self.log_data_path, f'%j_job_output_{job_index}.txt')}\n")
            script_file.write(f"#SBATCH --mem={self.mem}G\n")
            script_file.write(f"export PYTHONPATH={self.parent_path}:$PYTHONPATH\n")
            script_file.write(f"{self.env_path} {self.python_script_path} {job_index} {monitor_file}\n")
        # print(monitor_file)
        return job_script_name

    def create_jobs(self):
        for job_index in range(self.num_jobs):
            job_script_name = self.create_job_script(job_index)
            self.job_scripts.append(job_script_name)
        self.submit_jobs()
        self.cleanup()

    def submit_jobs(self):
        for script in self.job_scripts:
            result = subprocess.run(['sbatch', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            job_id = result.stdout.strip().split()[-1]
            self.job_ids.append(job_id)
        print("Submitted jobs with IDs:", self.job_ids, flush=True)

    def cleanup(self):
        for script in self.job_scripts:
            os.remove(script)
        # print("Cleaned up job script files.")

class JobManagerSocket:
    def __init__(self, python_script_path, parent_path, env_path, log_data_path, num_jobs, cpus_per_job, mem):
        self.python_script_path = python_script_path
        self.parent_path = parent_path
        self.env_path = env_path
        self.log_data_path = log_data_path
        self.num_jobs = num_jobs
        self.cpus_per_job = cpus_per_job
        self.mem = mem
        self.job_scripts = []
        self.job_ids = []

    def create_job_script(self, job_index):
        # Replace "X" in the template with the current job_index
        job_script_name = os.path.join(self.log_data_path, f"job_script_{job_index}.sh")
        with open(job_script_name, 'w') as script_file:
            script_file.write("#!/bin/bash\n")
            script_file.write(f"#SBATCH --job-name=multi_job_{job_index}\n")
            script_file.write(f"#SBATCH --cpus-per-task={self.cpus_per_job}\n")
            script_file.write(f"#SBATCH --output={os.path.join(self.log_data_path, f'%j_job_output_{job_index}.txt')}\n")
            script_file.write(f"#SBATCH --mem={self.mem}G\n")
            script_file.write(f"export PYTHONPATH={self.parent_path}:$PYTHONPATH\n")
            script_file.write(f"{self.env_path} {self.python_script_path}\n")
        return job_script_name

        
    def create_jobs(self):
        for job_index in range(self.num_jobs):
            job_script_name = self.create_job_script(job_index)
            self.job_scripts.append(job_script_name)
        self.submit_jobs()
        self.cleanup()

    def submit_jobs(self):
        for script in self.job_scripts:
            result = subprocess.run(['sbatch', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            job_id = result.stdout.strip().split()[-1]
            self.job_ids.append(job_id)
        print("Submitted jobs with IDs:", self.job_ids)

    def cleanup(self):
        for script in self.job_scripts:
            os.remove(script)
            
if __name__ == "__main__":
    icarus_directory = os.getcwd()
    python_script_path = os.path.join(icarus_directory, "task_monitor.py")
    parent_path = icarus_directory
    env_path = sys.executable
    log_data_path = os.path.join(icarus_directory, "logs")
    monitor_file_template = os.path.join(icarus_directory, "icarus_simulator/temp_data/run_X.txt")

    num_jobs = 40
    cpus_per_job = 16
    mem = 120

    manager = JobManager(python_script_path, parent_path, env_path, log_data_path, monitor_file_template, num_jobs, cpus_per_job, mem)
    manager.create_jobs()
