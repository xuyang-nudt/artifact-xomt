#!/usr/bin/env python

import os
import random
import sys

current_directory = os.getcwd()

def ends_with(skipped, current):
    for s in skipped:
        if current.endswith(s):
            return True
    return False

def find_smt2_files(directory, skipped):
    smt2_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".smt2"):
                absolute_path = os.path.abspath(os.path.join(root, file))
                if not ends_with(skipped, absolute_path):
                    smt2_files.append(os.path.relpath(absolute_path, current_directory))
    # Sorting is required for determinisim across different machines.
    return sorted(smt2_files)

def print_random_files(file_list, n):
    if n > len(file_list):
        #print("Warning: N is greater than the number of available files.")
        n = len(file_list)

    random_files = list(file_list)
    random.shuffle(random_files)

    for file in random_files[:n]:
        print(file)

def read_lines_from_file(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file]
    return lines

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python script.py <directory_path> <N> <rng_seed>")
        sys.exit(1)

    directory_path = sys.argv[1]
    N = int(sys.argv[2])
    skip_file = sys.argv[3] if len(sys.argv) > 3 else None

    skipped_files = list()
    if skip_file is not None:
        assert os.path.exists(skip_file)
        skipped_files = read_lines_from_file(skip_file)

    # print("[add by yx] skipped files", skipped_files)

    rng_seed = 0xd7ad26af

    if not os.path.isdir(directory_path):
        print("Error: The specified path is not a directory.")
        sys.exit(1)

    random.seed(rng_seed)

    smt2_files = find_smt2_files(directory_path, skipped_files) # find all .smt2

    # print("[add by yx] Found %d skip files" % len(skipped_files))
    # print("[add by yx] Found %d smt2 files" % len(smt2_files))

    if not smt2_files:
        print("No .smt2 files found in the specified directory.")
        sys.exit(1)
    else:
        print_random_files(smt2_files, N) # n random .smt2

