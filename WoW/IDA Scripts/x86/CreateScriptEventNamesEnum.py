# Copyright (c) 2015 Multi-Emu.

from idautils import *
from idc import *
from collections import OrderedDict
from string import *
from Helper import *

ScriptEventNames = dict()

# Build 19342
def CreateScriptEventNamesEnum():
    InitializeScriptEventNamesEA = FindBinary(ScreenEA(), SEARCH_DOWN, "68 ? ? 00 00 6A 00 68 ? ? ? ? E8 ? ? ? ? 83 C4 0C 6A 05 33 C0")#0x1405E3590
    FrameScript_SignalEventEA = FindBinary(ScreenEA(), SEARCH_DOWN, "55 8B EC 6A 00 8D 45 10 50 FF 75 0C FF 75 08 E8 ? ? ? ? 83 C4 10 5D")

    ea = InitializeScriptEventNamesEA

    if InitializeScriptEventNamesEA != BADADDR and FrameScript_SignalEventEA != BADADDR:
        PrintFound("InitializeScriptEventNames", InitializeScriptEventNamesEA)
        PrintFound("FrameScript_SignalEvent", FrameScript_SignalEventEA)

        chunk = GetFunctionChunk(ea, 1)

        if chunk != None:
            funcStart = chunk[0]
            funcEnd = chunk[1]

            PrintFound("Chunk start", funcStart)
            PrintFound("Chunk end", funcEnd)

            ea = funcStart

            value = 0
                
            # Create new enum
            enumId = AddEnum(-1, "SCRIPT_EVENT", idaapi.decflag())
        
            # Name FrameScript_SignalEvent function
            MakeNameEx(FrameScript_SignalEventEA, "__Z23FrameScript_SignalEventjPKcz", SN_NOCHECK)
            SetType(FrameScript_SignalEventEA, "int __fastcall FrameScript_SignalEvent(SCRIPT_EVENT event, int a2, char a3);")

            # Get not used enum members
            while 1:
                eaSkip = FindBinary(ea, SEARCH_DOWN, "A3 ? ? ? 01")
        
                if ea == BADADDR or ea > funcEnd:
                    break
            
                skipEA = Dword(eaSkip + 1)
        
                ScriptEventNames[skipEA] = None
        
                ea = eaSkip + 4
        
            ea = funcStart
        
            # Get used enum members
            while 1:
                ea = FindBinary(ea, SEARCH_DOWN, "C7 05 ? ? ? 01 ? ? ? 00")
            
                if ea == BADADDR or ea > funcEnd:
                    break
            
                varEA = Dword(ea + 2)
                nameEA = Dword(ea + 6)
        
                ScriptEventNames[varEA] = GetString(nameEA)
        
                ea = ea + 1
        
            # Sort enum members by offset and skip the not used ones
            for k, v in OrderedDict(sorted(ScriptEventNames.items())).iteritems():
                if v == None:
                    value = value + 1
                    continue
                        
                # Add enum members
                AddConstEx(enumId, v, value, -1)
        
                value = value + 1

            print "CreateScriptEventNamesEnum done."
        else:
            print "CreateScriptEventNamesEnum failed!!!"

CreateScriptEventNamesEnum()
