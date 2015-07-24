# Copyright (c) 2015 Multi-Emu.

from idautils import *
from idc import *
from collections import OrderedDict
from string import *
from Helper import *
from idaapi import *
from sys import *
import re

path = ""

baseObjDescriptorsStart = "43 47 4F 62 6A 65 63 74 44 61 74 61 3A 3A"
baseItemDescriptorsStart = "43 47 49 74 65 6D 44 61 74 61 3A 3A"
baseContainerDescriptorsStart = "43 47 43 6F 6E 74 61 69 6E 65 72 44 61 74 61 3A 3A"
baseUnitDescriptorsStart = "43 47 55 6E 69 74 44 61 74 61 3A 3A"
basePlayerDescriptorsStart = " 43 47 50 6C 61 79 65 72 44 61 74 61 3A 3A"
baseGameObjectDescriptorsStart = "43 47 47 61 6D 65 4F 62 6A 65 63 74 44 61 74 61 3A 3A"
baseDynamicObjectDescriptorsStart = "43 47 44 79 6E 61 6D 69 63 4F 62 6A 65 63 74 44 61 74 61 3A 3A"
baseCorpseDescriptorsStart = " 43 47 43 6F 72 70 73 65 44 61 74 61 3A 3A"
baseAreaTriggerDescriptorsStart = "43 47 41 72 65 61 54 72 69 67 67 65 72 44 61 74 61 3A 3A"
baseSceneObjectDescriptorsStart = "43 47 53 63 65 6E 65 4F 62 6A 65 63 74 44 61 74 61 3A 3A"
baseConversationDescriptorsStart = " 43 47 43 6F 6E 76 65 72 73 61 74 69 6F 6E 44 61 74 61 3A 3A"

MirrorFlags = { 0x0 : "None", 0x1 : "All", 0x2 : "Self", 0x4 : "Owner", 0x10 : "Empath",
                0x20 : "Party", 0x40 : "UnitAll", 0x80 : "ViewerDependet", 0x200 : "Urgent",
                0x400 : "UrgentSelfOnly" }
                
def GetFlags(value):
    ret = ""
    
    for k, v in MirrorFlags.iteritems():
        if k & value:
            ret = ret + "MirrorFlags." + v + " | "
            
    return ret[0:len(ret) - 3]

class DescriptorField:
    def __init__(self, name, size, flags, value):
        self.name = name
        self.size = size
        self.flags = flags
        self.value = value

    def __repr__(self):
        return repr((self.name, self.v, self.flags, value))
        
def DumpDescriptors(pattern, baseDescriptor = "CGObjectData", enum = False):
    initializeFunction = FindBinary(ScreenEA(), SEARCH_DOWN, pattern)

    if initializeFunction == BADADDR:
        return

    segStart = SegStart(initializeFunction)
    segEnd = SegEnd(initializeFunction)

    namespace = split(GetString(initializeFunction), "::")[0]
    tempDict = dict()

    initializeFunction = DfirstB(initializeFunction)
    pCode = decompile(initializeFunction)

    initializeFunctionStart = GetFunctionAttr(initializeFunction, FUNCATTR_START)
    initializeFunctionEnd = GetFunctionAttr(initializeFunction, FUNCATTR_END)

    nameEA = segStart

    while nameEA != BADADDR:
        nameEA = FindBinary(nameEA, SEARCH_DOWN, pattern)

        if nameEA == BADADDR:
            break

        name = Capitalize(str(split(GetString(nameEA), "::")[1]).replace("m_", "").replace("local.", ""))

        offset = Dword(DfirstB(nameEA) + 2)
        
        field = DescriptorField(name, 0, 0, 0)
        
        nameEA = nameEA + 2
        
        tempDict[offset] = field

    for s in re.finditer(r"(dword|word)_(.*) = ([0-9]+);", "{:s}".format(pCode)):
        offset = int(split(s.group(2), "[")[0], 16)
        value = int(s.group(3))
        
        if s.group(1) == "dword":
            tempDict[offset - 4].size = value
        if s.group(1) == "word":
            tempDict[offset - 8].flags = value

    sortedDict = OrderedDict(sorted(tempDict.items()))

    value = 0

    for k, v in sortedDict.iteritems():
        if value == 0:
            sortedDict[k].value = 0;

            value = v.size

            continue

        sortedDict[k].value = value

        value = v.size + value

    file = open(path, "a")
    
    if enum:
        file.write("public enum {:s}\n{}\n".format(namespace, "{"))

        for k, v in sortedDict.iteritems():
            if baseDescriptor != "":
                file.write("    {:s} = {:s}.End + 0x{:X}, // Size: 0x{:X}, Flags: 0x{:X}\n".format(v.name, baseDescriptor, v.value, v.size, v.flags))
            else:
                file.write("    {:s} = 0x{:X}, // Size: 0x{:X}, Flags: 0x{:X}\n".format(v.name, v.value, v.size, v.flags))

        if baseDescriptor != "":
            file.write("    {:s} = {:s}.End + 0x{:X}\n".format("End", baseDescriptor, value))
        else:
            file.write("    {:s} = 0x{:X}\n".format("End", value))

        file.write("{}\n\n".format("}"))
    else:
        file.write("class {:s} : DescriptorBase\n{}\n".format(namespace[2:len(namespace)], "{"))

        if baseDescriptor != "":
            file.write("    public {:s}() : base({:s}.End) {}\n\n".format(namespace[2:len(namespace)], baseDescriptor[2:len(baseDescriptor)], "{}"))

        for k, v in sortedDict.iteritems():
            file.write("    public DescriptorField {:s} => base[0x{:X}, 0x{:X}, {:}];\n".format(v.name, v.value, v.size, GetFlags(v.flags)))

        file.write("\n")

        if baseDescriptor != "":
            file.write("    public static new int End => {:s}.End + 0x{:X};\n".format(baseDescriptor[2:len(baseDescriptor)], value))
        else:
            file.write("    public static new int End => 0x{:X};\n".format(value))

        file.write("{}\n\n".format("}"))
        
    file.close();

path = os.path.dirname(os.path.abspath(__file__)) + "/Descriptors.cs"

print "Dumping Descriptors to: " + path

DumpDescriptors(baseObjDescriptorsStart, "")
DumpDescriptors(baseItemDescriptorsStart)
DumpDescriptors(baseContainerDescriptorsStart, "CGItemData")
DumpDescriptors(baseUnitDescriptorsStart)
DumpDescriptors(basePlayerDescriptorsStart, "CGUnitData")
DumpDescriptors(baseGameObjectDescriptorsStart)
DumpDescriptors(baseDynamicObjectDescriptorsStart)
DumpDescriptors(baseCorpseDescriptorsStart)
DumpDescriptors(baseAreaTriggerDescriptorsStart)
DumpDescriptors(baseSceneObjectDescriptorsStart)
DumpDescriptors(baseConversationDescriptorsStart)

print "Done."
