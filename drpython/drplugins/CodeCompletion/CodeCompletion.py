#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com

#   Copyright 2004-2005

#   Programmer: Tom De Muer
#   E-mail:     tomdemuer@users.sourceforge.net
#
#   Copyright 2004 Tom De Muer
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   The DrPython License:
#
#    DrPython is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Credits :
#    This code is based on the original AutoComplete code from
#    Daniel Pozmanter released under the GPL.  You can find the original
#    AutoComplete code on the project site of DrPython.
#    Thanks to Daniel Pozmanter and Franz Steinhaeusler for their support.
#
# Changelog:
#    15/7/04 :   0.0.0  first public release
#                0.0.0a expanded choice for different keyboards
#    16/7/04 :   0.0.0b Reorganized the event binding of the plugin.
#                       Now the plugin binds to shortcuts.
#                       Thx to Daniel Pozmanter for the suggestions!
#    17/7/04 :   0.0.0c If no documentation is found the signature is shown
#    18/7/04 :   0.0.1  Local import aliases are recognized
#                       Local functions are recognized
#                       Fixed bug where ident[len(... doesn't get recognized as
#                       trigger for 'len', now searching for identifiers instead of
#                       non-whitespace
#    19/7/04 :   0.0.1a Local imports without alias are recognized
#    20/7/04 :   0.0.2  Bug fix in function signature rendering
#    21/7/04 :   0.0.2a Global variables eliminated to avoid pollution of namespace
#                       Added some documentation, no functional changes

#**************************************************

#As of 0.0.3, By Daniel Pozmanter.
#Versions 0.0.0 - 0.0.2 by Tom (Original CallTips Code by Tom) (Original Autocomplete Code by Dan).

#0.0.3 Changelog:
#Bug Report, Thanks Klaus O.
#Bugfix, thanks Franz Steinhausler
#I cleaned up help and about a bit.
#Plus you can now update th namespace from the pop up menu
#or the toolbar.

#0.1.0:  Now works in the Active Styled Text Control (DrFrame.GetActiveSTC).
#Bug-Report/Feature Request, Thanks Rene Aguirre
#Updated with 3.9.x changes.
#Now uses manually set shortcuts for autocomplete and calltips,
#to make things simpler.
#Updated the documentation.

#0.2.0:
#Removed parsing code, now uses faster re method.
#Optional toggle codecompletion shortcut added.
#Removed manual update namespace, it is now automatic.
#Indentation Type is now tabs.
#Cleaned Up Imports, Documentation.
#Only does autocomplete for python files (bug-report, thanks Franz Steinhausler).

#0.2.1:
#Now shows the shortcut in the menu.
#Bug-Report with Fix from Franz
#Minor help typo fixed.

#0.2.2:
# update for wxPython 2.8 and DrPython 1.65.

#**************************************************

#The version 0.0.3 mentioned below was not released.
#(or if it was, it was integrated into 0.0.2).
#version 0.0.3 is 0.0.2 modified by Dan
#using the bugfix given by Franz in the forums.

#    06/8/04 :   0.0.3  Complete rewrite, functionality now also include AutoComplete
#                       The python parser module is used to extract information
#    10/8/04 :   0.0.3a Added shortcut for manual update of parse info
#                       Preferences
#    18/8/04 :   0.0.3b Fixed preferences bug
#                       Fixed bug in calltips on variables
#    26/8/04 :   0.0.3c Support for hiding the "__" methods
#    26/8/04 :   0.0.0  Renamed to CodeCompletion
#    06/9/04 :   0.0.1  Only active when document is identified as Python (thx Franz Steinhaeusler)
#                       Turned of the debug log by default
#    25/9/04 :   0.0.2  Possible to bind to other keys than "." and "(" by ignoring them (thx Dan Kruger)
#                       CodeCompletion now sees more functions (thx Dan Kruger)
#
#    This plugin for DrPython can show calltips and autocompletion info

import wx
import sys, re, os.path, inspect

#Global Regular Expressions

reword = re.compile('(\w+\.)*\w+\Z', re.I | re.M)

reas = re.compile('[a-zA-Z.]*\s* as \s*[a-zA-Z.]*', re.M)
reassignments = re.compile('[a-zA-Z.]*\s*=\s*[a-zA-Z.]*', re.M)

def _isastring(text):
    text = text.strip()
    return (text[0] == '"') or (text[0] == "'")

def _isacomment(text):
    text = text.strip()
    return text[0] == '#'


def OnAbout(DrFrame):
    AboutString = '''CodeCompletion:
Version: 0.2.2

By Daniel Pozmanter (As of Version 0.0.3)

By Tom De Muer (Versions 0.0.0 - 0.0.2)

Released under the GPL.

Credits (0.0.3 + ):
BugFix, Thanks Franz Steinhausler
Bug-Report, Thanks Franz Steinhausler
Bug-Report with Fix, Thanks Franz Steinhausler

Credits (0.0.0 - 0.0.2):Daniel Pozmanter
For useful suggestions and writing AutoComplete on which
the code for this plugin is based on.
Franz Steinhaeusler and Dan Kruger for bug fixes and improvements.'''
    DrFrame.ShowMessage(AboutString, "About")

def GetAlias(stc, word):
    #First, find interesting lines to look at:
    text = stc.GetText()

    p = word.find('.')
    if p > -1:
        wword = word[:p]
        wappend = word[p:]
    else:
        wword = word
        wappend = ''

    asmatches = reas.findall(text)
    assignmentmatches = reassignments.findall(text)

    for m in asmatches:
        if m.find(wword) > -1:
            if not _isastring(m) and not _isacomment(m):
                r = m.find('as')
                if m[r+2:].strip() == wword:
                    return m[:r].strip() + wappend

    for m in assignmentmatches:
        if m.find(wword) > -1:
            if not _isastring(m) and not _isacomment(m):
                r = m.find('=')
                if m[:r].strip() == wword:
                    return m[r+1:].strip() + wappend

    return word

def GetDoc(word, filename=''):
    try:
        exec(compile("doc = inspect.getdoc(" + word + ")", filename, 'exec'))

        return doc
    except:
        pass

    return ''

def GetMembers(word, filename='', prepend=''):
    try:
        try:
            exec(compile("import " + word, filename, 'exec'))
        except:
            pass
        exec(compile("members = dir(" + word + ")", filename, 'exec'))
    except:
        return ''

    if not prepend:
        prepend = word

    members.sort()
    members.reverse()

    results = ''

    for m in members:
        results = prepend + '.' + m + ' ' + results

    return results.rstrip()

def GetWordOfInterest(stc, AutoComplete=False):
    """GetWordOfInterest(stc) -> string
    Gives the identifier or module for which the calltip needs to be generated"""
    #Get The Current Word
    text = stc.GetText()
    pos = stc.GetCurrentPos()

    partext = text

    eol = stc.GetEndOfLineCharacter()
    #Get the left bit
    i = text[0:pos].rfind(eol)
    if i == -1:
        i = 0
    else:
        i = i + len(eol)
    #Get the right bit
    result = reword.search(text[i:pos])
    if result is None:
        start = i
    else:
        start = i + result.start()
    word = text[start:pos]

    if AutoComplete:
        return word, GetAlias(stc, word)
    return GetAlias(stc, word)

def Plugin(DrFrame):
    def GetAliases():
        stc = DrFrame.GetActiveSTC()
        return [], []

    def OnHideCallTip(event):
        event.Skip()
        stc = DrFrame.GetActiveSTC()
        stc.CallTipCancel()

    def OnCallTip(event):
        event.Skip()

        if not DrFrame.CodeCompletion:
            return

        stc = DrFrame.GetActiveSTC()
        if stc.filetype != 0:
            return
        #word,partext,origword = GetWordOfInterest(stc,True)

        word = GetWordOfInterest( stc )
        if (word.find("gtk") > -1) or (word.find("drpython") > -1):
            #This crashes wxPython resp. drPython
            return

        result = GetDoc(word)

        if result:
            if stc.CallTipActive():
                stc.CallTipCancel()
            stc.CallTipSetBackground('#FFFFB8')
            stc.CallTipShow(stc.GetCurrentPos(), result)

    def OnAutoComplete(event):
        event.Skip()

        if not DrFrame.CodeCompletion:
            return

        stc = DrFrame.GetActiveSTC()

        if stc.filetype != 0:
            return

        word, wordalias = GetWordOfInterest(stc, True)

        if (wordalias.find("gtk") > -1) or (wordalias.find("drpython") > -1):
            #This crashes wxPython resp. drPython
            return

        if wordalias != word:
            results = GetMembers(wordalias, prepend=word)
        else:
            results = GetMembers(word)

        if not results:
            return
        if stc.CallTipActive():
            stc.CallTipCancel()
        stc.AutoCompShow(len(word), results)

    def OnToggleCodeCompletion(event):
        DrFrame.CodeCompletion = not DrFrame.CodeCompletion
        if DrFrame.CodeCompletion:
            DrFrame.togglecodecompletion.SetItemLabel(DrFrame.GetPluginMenuLabel('CodeCompletion', 'Toggle Code Completion', 'Disable CodeCompletion'))
        else:
            DrFrame.togglecodecompletion.SetItemLabel(DrFrame.GetPluginMenuLabel('CodeCompletion', 'Toggle Code Completion', 'Enable CodeCompletion'))

    def CheckKey(event):
        if DrFrame.GetActiveSTC().AutoCompActive():
            event.Skip()
            return 1
        return 0

    DrFrame.CodeCompletion = True
    menutext = 'Disable CodeCompletion'

    #Prefs:
    pfile = DrFrame.pluginspreferencesdirectory + "/CodeCompletion.preferences.dat"
    if os.path.exists(pfile):
        f = open(pfile, 'r',encoding="UTF-8")
        t = f.read().strip()
        f.close()
        try:
            DrFrame.CodeCompletion = int(t)
            if not DrFrame.CodeCompletion:
                menutext = 'Enable CodeCompletion'
        except:
            pass

    #Override the way enter is handled, if in the prompt:
    DrFrame.AddKeyEvent(CheckKey, wx.WXK_UP)
    DrFrame.AddKeyEvent(CheckKey, wx.WXK_DOWN)
    DrFrame.AddKeyEvent(CheckKey, wx.WXK_RETURN)
    DrFrame.AddKeyEvent(OnAutoComplete, ord('.'))
    DrFrame.AddKeyEvent(OnCallTip, ord('8'), Shift=1)
    DrFrame.AddKeyEvent(OnHideCallTip, ord('9'), Shift=1)
    DrFrame.AddPluginFunction("CodeCompletion", "Toggle Code Completion", OnToggleCodeCompletion)

    DrFrame.LoadPluginShortcuts('CodeCompletion')

    menutext = DrFrame.GetPluginMenuLabel('CodeCompletion', 'Toggle Code Completion', menutext)

    ID_TOGGLE_CODE_COMPLETION = DrFrame.GetNewId()

    DrFrame.togglecodecompletion = wx.MenuItem(DrFrame.optionsmenu, ID_TOGGLE_CODE_COMPLETION, menutext)

    DrFrame.optionsmenu.AppendSeparator()
    DrFrame.optionsmenu.AppendItem(DrFrame.togglecodecompletion)

    DrFrame.Bind(wx.EVT_MENU, OnToggleCodeCompletion, id=ID_TOGGLE_CODE_COMPLETION)



def OnHelp(DrFrame):
    helpText = '''CodeCompletion Version 0.2.1

This plugin supports autocomplete (bound to the '.') and
calltips (bound to the '(').

The calltip issued is the documentation of the function you are calling.  If no
documentation is found, the signature of the function is used as a call tip.

You can toggle code completion (both autocomplete and calltips) on and
off via the options menu (or by assigning a shortcut, pop up menu entry, or toolbar button).

You can also set whether or not codecompletion is enabled by default at startup via plugin preferences.

Bug reports/suggestions are welcome at the DrPython forums.'''

    DrFrame.ShowMessage(helpText, "CodeCompletion Help")

def OnPreferences(DrFrame):
    answer = DrFrame.Ask('Would you like CodeCompletion Enabled by Default?', 'CodeCompletion')

    pfile = DrFrame.pluginspreferencesdirectory + "/CodeCompletion.preferences.dat"
    f = open(pfile, 'w',encoding="UTF-8")
    f.write(str(int(answer)))
    f.close()
