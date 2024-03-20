import subprocess
import re

def get_running_jobs(job_name_pattern, valid_user):
    """Get a list of running jobs with names matching the specified pattern and validate the user."""
    try:
        # Run the squeue command and capture its output, including the user name
        output = subprocess.check_output(['squeue', '-o', '%.18i %.50j %u', '--noheader'], text=True)
        # print(f"Squeue output:\n{output}")
        
        # Construct the regular expression pattern based on the input
        # The pattern now also captures the user name
        pattern = rf'\s*(\d+)\s+{job_name_pattern}_\d+\s+(\w+)\s*'
        # print(f"Using pattern: {pattern}")
        
        # Use a regular expression to find jobs that match the naming pattern and capture the user names
        matches = re.findall(pattern, output)
        
        # Filter job IDs by validating the user name
        job_ids = [job_id for job_id, user in matches if user == valid_user]
        print(f"Found job IDs for user '{valid_user}': {job_ids}")
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
    job_name_pattern = "multi_job"
    # Assuming you want to validate jobs for this user
    valid_user = "roeeidan"
    job_ids = get_running_jobs(job_name_pattern, valid_user)
    if job_ids:
        cancel_jobs(job_ids)
    else:
        print(f"No matching jobs found for user '{valid_user}'.")

if __name__ == '__main__':
    main()
