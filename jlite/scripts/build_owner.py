#!/usr/bin/env python3
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


class Item:
    GC_START_EVENT = 1
    GC_END_EVENT = 2
    def __init__(self, data):
        self.data = data
        self.type = self.get_type()
    def get_obj_size(self):
        return self.data[2]
    def get_new_addr(self):
        return self.data[1]
    def get_free_addr(self):
        return self.data[1]
    def get_src_addr(self):
        return self.data[1]
    def get_holder_addr(self):
        return self.data[1]
    def get_ref_addr(self):
        return self.data[2]
    def get_dest_addr(self):
        return self.data[2]
    def get_line(self):
        return self.data[4]
    def get_class_name_id(self):
        return self.data[5]
    def get_time(self):
        return self.data[0]
    def get_field(self):
        return self.data[3]
    def get_array_id(self):
        return self.data[3]
    def get_type(self):
        return chr(int(self.data[-2]))
    def get_tid(self):
        return self.data[-1]
    def get_use_addr(self):
        return self.data[1]
    def get_event_id(self):
        return self.data[3]
class GCLifeRecorder:
    def __init__(self):
        self.var_list = []
        self.var_life_map = {}
        self.gc()
    
    def gc(self):
        self.var_list.append({
            "index": len(self.var_list),
            "vars": set()
        })
    def new(self, rid):
        self.var_list[-1]["vars"].add(rid)
        self.var_life_map[rid] = len(self.var_list)-1
    def free(self, rid):
        if rid not in self.var_life_map:
            return -1
        index = self.var_life_map[rid]
        self.var_list[index]["vars"].remove(rid)
        gc_life = len(self.var_list) - 1 - index
        self.var_life_map.pop(rid)
        return gc_life
    
    def free_all(self):
        res = []
        for rid in list(self.var_life_map):
            life = self.free(rid)
            if life >= 0:
                res.append((rid, life))
        return res
    
if __name__ == "__main__":
    gc_recorder = GCLifeRecorder()
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    c1 = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS OWNER')
    cursor.execute('DROP TABLE IF EXISTS LIFE')
    cursor.execute('''---sql
    CREATE TABLE IF NOT EXISTS OWNER(
        TID INTEGER,
        HID INTEGER,
        RID INTEGER,
        TYPE CHAR
    );
                   ''')
    cursor.execute('''---sql
    CREATE TABLE IF NOT EXISTS LIFE(
        RID INTEGER,
        LIFE INTEGER
    );
                   ''')

    c1.execute('''--sql
    SELECT * FROM TIMELINE ORDER BY TIME
                              ''')
    hid = 0
    holder_map = {}
    ref_map = {}
    _rid = 0
    def next_rid():
        global _rid
        _rid += 1
        return _rid - 1
    while True:
        timeline = c1.fetchmany(1000_000)
        if len(timeline) == 0:
            break
    
        holder_map = {}
        pointer_map = {}
    
        '''
        OWNER
        | TID   | HID   | RID   |
        tid: TIMELINE.TID
        for new, only use tid and rid, hid is NULL
        holder addr + field + ref addr + change-tid(aastore/putfield) 
        (holder + field) -> HID
        ref -> RID
    
        '''
        cursor.execute('BEGIN;')    
        for data in timeline:
            item = Item(data)
            if item.type == 'n':
                #pointer_map[item.get_new_addr()] = {}
                addr = item.get_new_addr()
                rid = next_rid()
                ref_map[addr] = rid
                tid = item.get_tid()
                gc_recorder.new(rid)
                cursor.execute('INSERT INTO OWNER (TID, RID, TYPE) VALUES (?,?,?)', (tid, rid, ord('n')))
            elif item.type == 'g':
                src = item.get_src_addr()
                dest = item.get_dest_addr()
                if src in ref_map:
                    rid = ref_map[src]
                    ref_map[dest] = rid
                    ref_map.pop(src)

                    tid = item.get_tid()
                    cursor.execute('INSERT INTO OWNER (TID, RID, TYPE) VALUES (?,?,?)', (tid, rid, ord('g')))
                else:
                    rid = next_rid()
                    ref_map[dest] = rid
                    tid = item.get_tid()
                    cursor.execute('INSERT INTO OWNER (TID, RID, TYPE) VALUES (?,?,?)', (tid, rid, ord('g')))
                if src in holder_map:
                    holder_map[dest] = holder_map[src] 
                    holder_map.pop(src)
            elif item.type == 'a':
                holder = item.get_holder_addr()
                array_index = item.get_array_id()
                ref = item.get_ref_addr()
                holder_map.setdefault(holder, {})
                if array_index not in holder_map[holder]:
                    holder_map[holder][array_index] = hid
                    hid += 1
                if ref not in ref_map:
                    rid = next_rid()
                    ref_map[ref] = rid
                line = (item.get_tid(), holder_map[holder][array_index], ref_map[ref], ord('a'))
                cursor.execute('INSERT INTO OWNER (TID, HID, RID, TYPE) VALUES(?,?,?, ?)', line)

            elif item.type == 'p':
                holder = item.get_holder_addr()
                field = item.get_field()
                ref = item.get_ref_addr()
                holder_map.setdefault(holder, {})
                if field not in holder_map[holder]:
                    holder_map[holder][field] = hid
                    hid += 1
                if ref not in ref_map:
                    rid = next_rid()
                    ref_map[ref] = rid
                line = (item.get_tid(), holder_map[holder][field], ref_map[ref], ord('p'))
                cursor.execute('INSERT INTO OWNER (TID, HID, RID,TYPE) VALUES(?,?,?,?)', line)
            elif item.type == 'f':
                addr = item.get_free_addr()
                if addr in ref_map:
                    rid = ref_map[addr]
                    line = (item.get_tid(), rid, ord('f'))
                    cursor.execute('INSERT INTO OWNER (TID, RID, TYPE) VALUES(?,?,?)', line)
                    life = gc_recorder.free(rid)
                    if life >= 0:
                        cursor.execute('INSERT INTO LIFE (RID, LIFE) VALUES(?,?)', (rid, life))
            elif item.type == 'e':
                if item.get_event_id() == Item.GC_START_EVENT:
                    gc_recorder.gc()
        

        cursor.execute('END;')    
    res = gc_recorder.free_all()
    for line in res:
        cursor.execute('INSERT INTO LIFE (RID, LIFE) VALUES(?,?)', line)
    cursor.close()
    conn.commit()
    conn.close()
    

