import os
import random
import shutil

def move_files(src_directory, dst_directory, total_files=5000):
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

# Example usage
src_directory = "/dt/shabtaia/DT_Satellite/icarus_data/graphs/basic/raw/"
dst_directory = "/dt/shabtaia/DT_Satellite/icarus_data/graphs/basic/spare_raw/"
move_files(src_directory, dst_directory)
# move_files(dst_directory, src_directory)