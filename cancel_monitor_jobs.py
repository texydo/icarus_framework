import subprocess
import re

def get_running_jobs(job_name_pattern):
    """Get a list of running jobs with names matching the specified pattern."""
    try:
        # Run the squeue command and capture its output
        output = subprocess.check_output(['squeue', '-o', '%.18i %.50j', '--noheader'], text=True)
        # Construct the regular expression pattern based on the input
        pattern = rf'(\d+) {job_name_pattern}_\d+'
        # Use a regular expression to find jobs that match the naming pattern
        job_ids = re.findall(pattern, output)
        return job_ids
    except subprocess.CalledProcessError as e:
        print(f"Failed to run squeue: {e}")
        return []

def cancel_jobs(job_ids):
    """Cancel the jobs with the given IDs."""
    for job_id in job_ids:
        try:
            subprocess.check_call(['scancel', job_id])
            print(f"Cancelled job {job_id}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to cancel job {job_id}: {e}")

def main():
    # Input the job name pattern
    # job_name_pattern = input("Enter the job name pattern (e.g., 'multi_job'): ")
    job_name_pattern = "multi_job"
    job_ids = get_running_jobs(job_name_pattern)
    if job_ids:
        cancel_jobs(job_ids)
    else:
        print("No matching jobs found.")

if __name__ == '__main__':
    main()
