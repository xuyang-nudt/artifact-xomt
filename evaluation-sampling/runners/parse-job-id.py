import sys


job_id = int(sys.argv[1])
total_files = int(sys.argv[2])
total_reps = int(sys.argv[3])
total_values = int(sys.argv[4])
key = sys.argv[5]

assert key in ["file", "rep", "value"]
assert total_values >= 1

id_map = dict()

current_id = 0
for f in range(0, total_files):
    for r in range(0, total_reps):
        for v in range(0, total_values):
            id_map[current_id] = (f, r, v)
            current_id += 1

if key == "file":
    assert id_map[job_id][0] < total_files
    print(id_map[job_id][0])
elif key == "rep":
    print(id_map[job_id][1])
elif key == "value":
    print(id_map[job_id][2])