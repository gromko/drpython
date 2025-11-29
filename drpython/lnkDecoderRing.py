#   Copyright 2003-2010 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#


# lnkDecoderRing

#This loverly little file
#let's people grab file attributes from the
#.lnk file format (windows shortcut).
#
#It does not require any libraries external to python.

# Adapted from the excellent perl code found in smb2web.
# (smb2web by Rolf Howarth)

import string, re

refile = re.compile(r'(\\\\|[A-Z]\:)(.+)', re.M)
reinvalid = re.compile(r'(\")|(\t)|(\n)|(\r)', re.M)

def IsFolder(text):
    return ord(text[0x18]) & 0x10

def IsNetwork(text):
    return (ord(text[0x18]) == 0x00) and (ord(text[0x14]) == 1)

def GetPrintableStrings(text):
    strings = []

    cs = ""

    for character in text:
        if character in string.printable:
            cs += character
        else:
            if cs:
                if (refile.search(cs) is not None) and (reinvalid.search(cs) is None):
                    if cs[0] != '/':
                        strings.append(cs)
            cs = ""

    return strings

def ReadLink(filename):
    f = open(filename, 'r',encoding="UTF-8")
    text = f.read()
    f.close()

    return GetPrintableStrings(text)[0].replace('\\', '/')
