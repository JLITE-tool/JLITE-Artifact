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

##cursor.execute(f'''--sql
##SELECT
##        COUNT(*) AS CN,
##        HID,
##        RID
##    FROM OWNER
##    GROUP BY HID, RID
##    ORDER BY CN DESC
##               ''')
##
##res = cursor.fetchmany(10)
##hid_list = [str(x[1]) for x in res if x[1] is not None]
##print(hid_list)
##cursor.execute(f'''--sql
##SELECT 
##        COUNT(*) AS CN,
##        HID,
##        RID,
##        CLASSNAME.CLASSNAME AS N,
##        TIMELINE.LINE AS L,
##        TID,
##        TIMELINE.TYPE,
##        TIMELINE.ADDR0,
##        TIMELINE.ADDR1,
##        TIMELINE.TIME,
##        COUNT(DISTINCT HID)
##    FROM OWNER
##    JOIN TIMELINE USING(TID)
##    JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID+1
##    WHERE HID in ({",".join(hid_list)}) 
##    GROUP BY N,L
##    ORDER BY CN DESC
##               ''')
##
##res = cursor.fetchall()
##print(res)

#cursor.execute(f'''--sql
#SELECT SUM(CN_1) AS CN_S, N, L FROM (
#    SELECT COUNT(*)-1 AS CN_1, N, L FROM OWNER JOIN(
#        SELECT
#            RID,
#            CLASSNAME.CLASSNAME AS N,
#            TIMELINE.LINE AS L
#        FROM OWNER
#        JOIN TIMELINE USING(TID)
#        JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID + 1
#        WHERE OWNER.TYPE = {ord('n')}
#    ) USING (RID)
#    WHERE OWNER.TYPE = {ord('a')} OR OWNER.TYPE = {ord('p')}
#    GROUP BY HID, RID, N, L
#) GROUP BY N, L
#HAVING CN_S != 0
#ORDER BY CN_S DESC
#               ''')

cursor.execute(f'''---sql
SELECT SUM(CN_1) AS CN_2, N, L FROM
(
    SELECT 
        COUNT(*)-1 AS CN_1, HID, RID,
        CLASSNAME.CLASSNAME AS N,
        TIMELINE.LINE AS L
    FROM OWNER
    JOIN TIMELINE USING(TID)
    JOIN CLASSNAME ON CLASSNAME.ID = TIMELINE.CLASS_NAME_ID + 1
    WHERE OWNER.TYPE = {ord('a')} OR OWNER.TYPE = {ord('p')}
    GROUP BY HID, RID, N, L
) GROUP BY N, L
ORDER BY CN_2 DESC
    
               ''')
res = cursor.fetchmany(20)
for line in res:
    print(line)
