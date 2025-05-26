import subprocess, sys
for cmd in [['python','feature_engineering.py'],['python','train_xgb.py'],['python','edges.py']]:
    print('Running',cmd)
    if subprocess.call(cmd)!=0:
        sys.exit(1)