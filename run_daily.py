import subprocess, sys
for cmd in [
    ["python", "feature_engineering.py"],  # tomorrow’s slate
    ["python", "build_historical.py"],     # rebuild historical once a day
    ["python", "train_xgb.py"],
    ["python", "edges.py"],
]:
    print("Running", cmd)
    if subprocess.call(cmd):
        sys.exit(1)
