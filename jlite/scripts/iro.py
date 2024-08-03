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
    ADDR0, LINE, CLASSNAME, TYPE, TIMELINE.ID
FROM 
    TIMELINE
JOIN
    CLASSNAME ON CLASSNAME.ID = CLASS_NAME_ID + 1
WHERE
    TYPE  in ( {ord('n')} , {ord('a')}, {ord('p')}, {ord('u')}, {ord('c')})
    AND ADDR0 < 0x80000000
ORDER BY TIME
               ''').fetchall()



class Record:
    def __init__(self, addr, line, classname, type, _id):
        self.addr = int(addr)
        self.line = int(line)
        self.classname = classname
        self.type = int(type)
        self.id = int(_id)
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

    def is_getfield(self):
        return self.id == 2
    def is_putfield(self):
        return self.id == 1
constructing_addrs = set()
read_only_new = {}
all_new = {}
for data in res:
    r = Record(*data)
    if r.addr == ((1<<32)-1):
        continue
    if r.is_new():
        all_new.setdefault(r.get_pos(), 0)
        all_new[r.get_pos()] += 1
        constructing_addrs.add(r.addr)
        read_only_new[r.addr] = r
        # print(f'[NEW] {r.addr}')
    elif r.is_use():
        # print(f'[USE] {r.addr}')
        continue
        if r.addr in constructing_addrs:
            continue
        if r.is_putfield() and r.addr in read_only_new:
            read_only_new.pop(r.addr)

    elif r.is_construct():
        constructing_addrs.remove(r.addr)
        # print(f'[CONSTRUCT] {r.addr}')

read_only_report = {}
for k in read_only_new:
    data = read_only_new[k]
    read_only_report.setdefault(data.get_pos(), 0)
    read_only_report[data.get_pos()] += 1
for k in sorted(read_only_report, key=lambda x: -read_only_report[x]):
    print(f'{k}, {read_only_report[k]}, {all_new[k]}')

# print(str(read_only_report).replace(',', '\n'))



        



