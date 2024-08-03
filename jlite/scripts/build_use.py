#!/usr/bin/env python3
from build_owner import Item
import sqlite3
import os
import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('pid', type=int, help='pid of jvm')
# args = parser.parse_args()
# pid = args.pid
pid = os.path.abspath('.').split('-')[-1]
int(pid)
#pid = 58371
dbname = f'{pid}.db'
import sqlite3

conn = sqlite3.connect(dbname)
cursor = conn.cursor()
c1 = conn.cursor()

cursor.execute('''---sql
CREATE TABLE IF NOT EXISTS NEW_USE(
    NEW_TID INTEGER,
    USE_TID INTEGER,
    GC_COUNT INTEGER
);
               ''')
c1.execute('''--sql
SELECT * FROM TIMELINE ORDER BY TIME
                          ''')

addr2tid = {}
notused = set()
current_gc_count = 0
addr2gc = {}
while True:
    timeline = c1.fetchmany(1000_000)
    if len(timeline) == 0:
        break
    cursor.execute('BEGIN;')
    for data in timeline:
        item = Item(data)
        if item.type == 'n':
            addr2tid[item.get_new_addr()] = item.get_tid()
            #notused.add(item.get_tid())
            addr2gc[item.get_new_addr()] = current_gc_count
        elif item.type == 'g':
            src = item.get_src_addr()
            dst = item.get_dest_addr()
            if src in addr2tid:
                addr2tid[dst] = addr2tid[src]
                addr2tid.pop(src)
        elif item.type == 'u':
            if item.get_use_addr() in addr2tid:
                line = (addr2tid[item.get_use_addr()], item.get_tid(), current_gc_count-addr2gc[item.get_use_addr()])
                cursor.execute('INSERT INTO NEW_USE (NEW_TID, USE_TID, GC_COUNT) VALUES(?,?,?)', line)
        elif item.type == 'e':
            if item.get_event_id() == item.GC_START_EVENT:
                current_gc_count += 1
            #if item.get_use_addr() in notused:
            #    notused.pop(item.get_use_addr())
    #print(notused)

    cursor.execute('END;')
