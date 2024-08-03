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
'''--sql
'''
print("CN, NAME, LINE, LIFESPAN")
cursor.execute(f'''---sql
SELECT
        COUNT(*) AS CN,
        CLASSNAME.CLASSNAME AS NAME,
        TIMELINE.LINE,
        TYPEMAP.TYPE
    FROM OWNER
    JOIN TIMELINE USING(TID)
    JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID+1
    JOIN TYPEMAP ON TYPEMAP.ID = TIMELINE.ID
    WHERE OWNER.TYPE={ord("n")} AND RID NOT IN (
        SELECT
                DISTINCT RID
            FROM OWNER
            WHERE TYPE = {ord("a")} or TYPE = {ord("p")}
    ) 
    GROUP BY LINE, TIMELINE.CLASS_NAME_ID
    ORDER BY CN DESC
               ''')
res = cursor.fetchmany(20)
for line in res:
    print(line)