#!/usr/bin/env python3
import sqlite3
import os
import argparse
#pid = 58371

# parser = argparse.ArgumentParser()
# parser.add_argument('pid', type=int, help='pid of jvm')
# args = parser.parse_args()
# pid = args.pid
pid = os.path.abspath('.').split('-')[-1]
int(pid)

db_name = f'{pid}.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
#cursor.execute('''---sql
#SELECT HID, TID, CLASSNAME.CLASSNAME, TIMELINE.LINE, TIMELINE.TIME 
#    FROM OWNER JOIN TIMELINE USING(TID) 
#    JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID
#               ''')
print('NAME LINE CN')
cursor.execute(f'''--sql
SELECT 
        CLASSNAME.CLASSNAME AS NAME, 
        TIMELINE.LINE AS LN, 
        COUNT(*) AS CN
    FROM TIMELINE 
    JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID+1
    WHERE TIMELINE.TYPE = {ord('n')} AND TID NOT IN (
        SELECT NEW_TID FROM NEW_USE
    )
    GROUP BY NAME, LN
    ORDER BY CN DESC
               ''')
res = cursor.fetchall()
for l in res:
    print(l)
