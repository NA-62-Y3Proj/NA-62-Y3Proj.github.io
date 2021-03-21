#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

@author: Filippo Falezza
<filippo dot falezza at outlook dot it>
<fxf802 at student dot bham dot ac dot uk>

Released under GPLv3 and followings
"""

from sys import argv as sysargv
import shlex
import math
import numpy as np
"""
file format:
   C_filtered.py signal_input.C output.cir
note that .cir is the ngspice file to produce

Note: for brevity, parsing mistakes will not be handled
"""

def target_write(targetfile, datatext):
    """
    Parameters
    ----------
    targetfile: string, target file to write
    datatext: array, input data extracted from signal_input.C
    """
    #fixed text
    
    #fill the header here
    header = f''
    
    #fill the footer below. Only a section of the footer has not been omitted.
    footer = f'
    .CONTROL\n\
    TRAN  1n 500ns\n\
    set hcopydevtype=postscript\n\
    set hcopypscolor=1\n\
    set color0=rgb:0/0/0\n\
    set color1=rgb:F/F/F\n\
    set color2=rgb:0/0/0\n\
    PLOT      V(gauss_out)\n\
    HARDCOPY {targetfile}.ps V(gauss_out)\n\
    .PLOT    V(gauss_out)\n\
.ENDC\n\
.END\n'

    #target file
    target = open(targetfile, "x")
    target.write(header)
    #print(datatext)
    for item in datatext:
        target.write("%s\n" % item)
    #target.write(datatext)
    target.write(footer)
    target.close()
    return("Target file correctly written")

def source_read():
    #source file
    line_array = []
    source = open(sysargv[1])
    #check for line 25 if empty
    for line in source:
        line = line.strip()
        if line.startswith("hSignal__0_copy__1->SetBinContent"):
            #print(str(line.split("("))[1].split(")")[0])
            #array_line = (str(str(line.split("(")[1]).split(")")[0]).split())
            array_line = (str(str(line.split("(")[1]).split(")")[0]).split(","))
            #print(str(str(line.split("(")[1]).split(")")[0]).split(","))
            #print(array_line)
            #"""

            #DONE?: yes, done. TODO: need to convert the units appropriately, we are using nS and uA, but need to be given as S and A
            # DONE: wrong index specified. TODO: saturated signal due to missing "-" sign... why it is not preserved?
            float_array = np.array([np.format_float_scientific(np.float32(array_line[0])*10**-9, unique=False, precision=6),\
                np.format_float_scientific(np.float32(array_line[1])*10**-6, unique=False, precision=6)])
            #print(float_array)
            line_array.append(f'+ ({float_array[0]}, {float_array[1]})')
            #"""

            #TODO: fix error in simulation...
            #doAnalyses: TRAN:  Timestep too small; time = 1.32997e-07, timestep = 1.25e-21: trouble with x_x2:diode-instance d.x_x2.dvoutp

    source.close()
    return line_array

if __name__=='__main__':
    #if len(sysargv)< 3:
    if len(sysargv)< 2:
        print("specify the files, please")
        exit(1)
    #print(sysargv)
    datatext = source_read()
    #print(datatext)
    target_write(sysargv[2], datatext)
