set -u
PID=`pwd | awk -v FS='-' '{print $NF}'`
csv2db $PID && csv2db.py $PID && build_owner.py $PID