#! /usr/bin/env python

from sys import argv
import re
p5rex =r"(p5\.[a-zA-Z]+[a-zA-Z0-9]*)"
p = re.compile(p5rex)

def no_p5(filename):
    with open(filename,"r") as f5:
        L = f5.readlines()
        P5 = []
        Lout = []
        for line in L:
            isp5 = re.findall(p, line)
            if isp5:
                line = line.replace('p5.','')
            Lout.append(line)
        Fout = "".join(Lout)
        return Fout
try:
    print(no_p5(argv[1]))
except:
    raise IndexError("Usage: no_p5 filename")
