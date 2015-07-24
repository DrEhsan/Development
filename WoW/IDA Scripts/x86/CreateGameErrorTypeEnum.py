# Copyright (c) 2015 Multi-Emu.

from idautils import *
from idc import *
from collections import OrderedDict
from string import *
from Helper import *

GameErrorTypes = dict()

# Build 19342
def CreateGameErrorTypeEnum():
    CGGameUI_DisplayError = FindBinary(ScreenEA(), SEARCH_DOWN, "55 8B EC 81 EC B8 0C 00 00 81 7D 08 ? ? 00 00 0F 8D ? ? ? ? 83 7D 08 0B")
    
    errInvFull = FindBinary(ScreenEA(), SEARCH_DOWN, "45 52 52 5F 49 4E 56 5F 46 55 4C 4C")
    errNotEnoughCorrency = FindBinary(errInvFull, SEARCH_DOWN, "45 52 52 5F 4E 4F 54 5F 45 4E 4F 55 47 48 5F 43 55 52 52 45 4E 43 59")
    
    ea = DfirstB(errInvFull)
    eaEnd = DfirstB(errNotEnoughCorrency) + 0x14
    value = 0

    if CGGameUI_DisplayError != BADADDR:
        PrintFound("CGGameUI_DisplayError", CGGameUI_DisplayError)

        # Create new enum
        enumId = AddEnum(-1, "GAME_ERROR_TYPE", idaapi.decflag())
        
        # Name CGGameUI::DisplayError function
        MakeNameEx(CGGameUI_DisplayError, "__ZN8CGGameUI12DisplayErrorE15GAME_ERROR_TYPEz", SN_NOCHECK)
        SetType(CGGameUI_DisplayError, "void __usercall CGGameUI__DisplayError(GAME_ERROR_TYPE gameErrorType, signed int a2, char a3);")
        
        while ea <= eaEnd:
            enumMemberName = GetString(Dword(ea))
            
            GameErrorTypes[value] = enumMemberName
        
            value = value + 1
            ea = ea + 0x14
        
        for k, v in OrderedDict(sorted(GameErrorTypes.items())).iteritems():        
            # Add enum members
            AddConstEx(enumId, v, k, -1)
        
        print "CreateGameErrorTypeEnum done."
    else:
        print "CreateGameErrorTypeEnum failed!!!"

CreateGameErrorTypeEnum()
