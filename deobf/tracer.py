import os
import sys
from deobf.ins_helper import *
from deobf.cfg import addr_in_blocks

def get_ins_bytes_by_line(line):
    p = line.find(")")
    subline = line[p:]
    p1 = subline.find("[")
    p2 = subline.find("]")
    bytes_str = subline[p1+1:p2]
    return bytearray([int(x, 16) for x in bytes_str.split()])
#

#标识指令运行的运行信息
class Tracer:


    def __init__(self, trace_path, lib_name, start_addr, end_addr, blocks_to_trace):
        self.__lib_name = lib_name
        self.__start_addr = start_addr
        self.__end_addr = end_addr

        self.__trace_list = []
        self.__condition_trace_map = {}
        self.__ins_count = {}

        detect_for_condition_come_true = False
        trace_for_condion_addr = 0
        trace_for_condion_next_prefer_addr = 0
        is_condition_come_true = False
        trace_for_true_jmp = False
        

        with open(trace_path, "r") as f:
            for line in f:
                line = line.strip()
                if (line.find(lib_name)<0):
                    continue
                #
                sa = line.split(":")
                start = sa[0].rfind("]")+1
                addr = int(sa[0][start:], 16)
                
                if (detect_for_condition_come_true):
                    #如果下一条指令，不等于上一条指令地址+指令大小，说明跳转了
                    is_condition_come_true = (addr != trace_for_condion_next_prefer_addr)
                    detect_for_condition_come_true = False
                #

                if (addr < start_addr or addr >= end_addr):
                    continue
                #
                #print("%x %r"%(addr, blocks_to_trace))
                if (not addr_in_blocks(addr, blocks_to_trace)):
                    continue
                #

                self.__trace_list.append(addr)
                if (addr in self.__ins_count):
                    count = self.__ins_count[addr]
                    self.__ins_count[addr] = count + 1
                #
                else:
                    self.__ins_count[addr] = 1
                #

                if (trace_for_true_jmp):
                    m = None
                    if (trace_for_condion_addr in self.__condition_trace_map):
                        m = self.__condition_trace_map[trace_for_condion_addr]
                    #
                    else:
                        m = [0, 0]
                    #
                    if (is_condition_come_true):
                        m[0] = addr
                    #
                    else:
                        m[1] = addr
                    #
                    self.__condition_trace_map[trace_for_condion_addr] = m

                    trace_for_true_jmp = False
                #
                # 找到真实块中以b condition跳转到的另外一个真实块的真实地址，
                ins_str = sa[1]
                if (is_jmp_condition_str(ins_str)):
                    detect_for_condition_come_true = True
                    trace_for_true_jmp = True
                    trace_for_condion_addr = addr
                    
                    trace_for_condion_next_prefer_addr = addr + len(get_ins_bytes_by_line(line))
                #
            #
            #print (self.__condition_trace_map)
        #
        #print(self.__addr2trace)
    #

    def get_trace_index(self, addr):
        out = []
        l = len(self.__trace_list)
        for i in range(0, l):
            if (addr == self.__trace_list[i]):
                out.append(i)
            #
        #
        return out
    #

    def get_trace_by_index(self, index):
        l = len(self.__trace_list)
        if (index >= l):
            return None
        return self.__trace_list[index]
    #


    def get_trace_next(self, addr):
        next_addrs = set()
        indexs = self.get_trace_index(addr)
        for i in indexs:
            addr = self.get_trace_by_index(i+1)
            if (addr != None):
                next_addrs.add(addr)
            #
        #
        return next_addrs
    #

    def get_ins_run_count(self, addr):
        if (addr in self.__ins_count):
            return self.__ins_count
        else:
            return 0
        #
    #
#