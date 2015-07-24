# Copyright (c) 2015 Multi-Emu.

from __builtin__ import *
from idautils import *
from idc import *

def GetXRefToCount(ea):
    i = 0
    for xr in XrefsTo(ea):
        i = i + 1

    return i

def PrintXRefs(ea):
    for xr in XrefsTo(ea):
        print("Xref {{ EA: 0x{:00000008X}, Type: {:} ({:s}) }}".format(xr.frm, xr.type, XrefTypeName(xr.type)))

def GetFunctionChunk(ea, index):
    for i, xr in enumerate(Chunks(ea)):
        if i == index:
            return (xr[0], xr[1])

    return None

def PrintFound(name, ea):
    print("Found {:s} at 0x{:00000008X}".format(name, ea))

def Capitalize(line):
    return ' '.join(s[0].upper() + s[1:] for s in line.split(' '))