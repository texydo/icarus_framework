import os
import random
import shutil

def move_adjacent_files(src_directory, dst_directory, total_files=5000):
    # List all files in the source directory
    print("a")
    files = os.listdir(src_directory)
    files.sort()  # Make sure the files are sorted to match pairs correctly
    print("b")
    # Filter out to ensure we only have files (in case there are directories)
    files = [file for file in files if os.path.isfile(os.path.join(src_directory, file))]
    print("c")
    # Ensure we have an even number for pairing
    assert len(files) >= total_files, "Not enough files to move"
    assert total_files % 2 == 0, "Total files to move must be an even number"
    print("d")
    # Generate pairs
    pairs = []
    for i in range(0, len(files) - 1, 2):  # Increment by 2 for pairing
        # Append pair (i, i+1) to ensure one is odd and the next is even in order
        pairs.append((files[i], files[i+1]))
    print("e")
    # Randomly select half the amount of total files since we're moving pairs
    selected_pairs = random.sample(pairs, total_files // 2)
    print("f")
    # Move selected files
    for file1, file2 in selected_pairs:
        shutil.move(os.path.join(src_directory, file1), os.path.join(dst_directory, file1))
        shutil.move(os.path.join(src_directory, file2), os.path.join(dst_directory, file2))
    print(f"Moved {total_files} files in {total_files // 2} pairs.")


def move_files_module(source_dir, destination_dir):
    """
    Move files from source_dir to destination_dir based on the criteria:
    Keep files where file index i % 6 == 1 or i % 6 == 2, move the rest.
    Assumes file names are in the format 'graph_i.pt' where i is an integer.
    """
    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # Iterate over all files in the source directory
    for filename in os.listdir(source_dir):
        if filename.startswith("graph_") and filename.endswith(".pt"):
            # Extract the index i from the file name
            try:
                i = int(filename.split("_")[1].split(".")[0])
            except ValueError:
                # Skip files where the index cannot be extracted
                continue

            # Check the condition for moving the file
            if not (i % 6 == 1 or i % 6 == 2):
                # Construct full file paths
                src_path = os.path.join(source_dir, filename)
                dest_path = os.path.join(destination_dir, filename)
                
                # Move the file
                shutil.move(src_path, dest_path)
                print(f"Moved: {filename}")
                
                
# Example usage
src_directory = "/dt/shabtaia/DT_Satellite/icarus_data/graphs/weightedDetectability/raw/"
dst_directory = "/dt/shabtaia/DT_Satellite/icarus_data/graphs/weightedDetectability/raw_spare/"
move_files_module(src_directory, dst_directory)
# move_files(dst_directory, src_directory)

