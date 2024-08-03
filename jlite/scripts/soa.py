#!/usr/bin/env python3
import json
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

res = cursor.execute(f'''--sql
SELECT
    ADDR0,ID
FROM 
    TIMELINE
WHERE TYPE = {ord('n')}
                     ''').fetchall()
addr2class = {}
for r in res:
    addr2class[r[0]] = r[1]

res = cursor.execute(f'''--sql
SELECT
    ADDR0, LINE, CLASSNAME, TYPE
FROM 
    TIMELINE
JOIN
    CLASSNAME ON CLASSNAME.ID = CLASS_NAME_ID + 1
WHERE
    TYPE  in ( {ord('n')} , {ord('a')}, {ord('p')}, {ord('u')}, {ord('c')})
    AND ADDR0 < 0x80000000
ORDER BY TIME
               ''').fetchall()


constructing = []

use_in_constructing = {}

class Record:
    def __init__(self, addr, line, classname, type):
        self.addr = int(addr)
        self.line = int(line)
        self.classname = classname
        self.type = int(type)
    def is_type(self, ch):
        return self.type == ord(ch)
    def is_construct(self):
        return self.is_type('c')
    def is_new(self):
        return self.is_type('n')
    def is_use(self):
        return self.is_type('u')
    def find_same_class(self, l: list["Record"]):
        for r in reversed(l):
            if r.addr != self.addr and addr2class[r.addr] == addr2class[self.addr]:
                return r
        return None
    def get_pos(self):
        return f'{self.classname}:{self.line}'
    
    def __repr__(self) -> str:
        return f'[{chr(self.type)}]-{self.addr} {self.classname}:{self.line}'
all_new = {}
for data in res:
    r = Record(*data)
    if r.addr == ((1<<32)-1):
        continue
    if r.is_new():
        constructing.append(r)
        all_new.setdefault(r.get_pos(), 0)
        all_new[r.get_pos()] += 1
        # print(f'[NEW] {r.addr}')
    elif r.is_use():
        # print(f'[USE] {r.addr}')
        if r in use_in_constructing:
            use_in_constructing.pop(r)
        new = r.find_same_class(constructing)
        if new is not None:
            use_in_constructing[r] = new
    elif r.is_construct():
        constructing.pop()
        # print(f'[CONSTRUCT] {r.addr}')



# print(str(use_in_constructing).replace(',', '\n'))
superfluous_report = {}

for k, v in use_in_constructing.items():
    superfluous_report.setdefault(v.get_pos(), 0)
    superfluous_report[v.get_pos()] += 1
for x in sorted(superfluous_report, key=lambda x: superfluous_report[x], reverse=True):
    print(f'{x}, {superfluous_report[x]}, {all_new[x]}')


        



