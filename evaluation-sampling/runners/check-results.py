import sys
import os

folder = sys.argv[1]
template = sys.argv[2]
total_files = int(sys.argv[3])
total_reps = int(sys.argv[4])
total_values = int(sys.argv[5])
tool = sys.argv[6]

current_id=1
for f in range(0, total_files):
    for r in range(0, total_reps):
        for v in range(0, total_values):
            current_tag = template.replace("@ID", str(current_id))
            path = os.path.join(os.path.join(folder, current_tag), f"sampling-{tool}.zip")
            if not os.path.exists(path):
                print(f"{path} {current_id}")
            current_id+=1