#   Programmer:  Franz Steinhaeusler
#   E-mail:      francescoa@users.sourceforge.net
#   Note:        Initial Release 18/7/2004
#
#   Copyright 2004-2005 Franz Steinhaeusler
#
#   Distributed under the terms of the GPL (GNU Public License)
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

#Version: 0.0.1:
# - no global variables, new DrFrame member variables in form of DrFrame.<PluginNme>_var

#Version: 0.0.2:
# - Added Popup function

#Version: 0.0.3, 08.04.2007.

#Plugin
#PositionMarker

#This plugin allows to to set, clear, goto next, goto previous and clear all position markers.

import wx
import drScrolledMessageDialog


def OnAbout(DrFrame):
    Version = "0.0.3"
    NameAndVersion = "PositionMarker:\n\nVersion: " + Version + "\n"
    AboutString = NameAndVersion + "By Franz Steinhaeusler\n\nReleased under the GPL."
    drScrolledMessageDialog.ShowMessage(DrFrame, AboutString, "About")

def OnHelp(DrFrame):
    drScrolledMessageDialog.ShowMessage(DrFrame, "Set and get postions in text.", "Help")

def Plugin(DrFrame):

    DrFrame.PositionMarker_BOOKMARKMASK = 4
    #DrFrame.PositionMarker_BOOKMARKMASK = 4 must be four; else it doesn't work; curious
    DrFrame.PositionMarker_BOOKMARKNUMBER = 2

    def OnTogglePositionMarker (event):
        DrFrame.txtDocument.MarkerDefine(DrFrame.PositionMarker_BOOKMARKNUMBER, wx.stc.STC_MARK_ARROW, 'blue', 'blue')
        #reason: each file has its DrFrame.txtDocument object
        #therefore it should be initalised

        lineNo = DrFrame.txtDocument.GetCurrentLine()
        if DrFrame.txtDocument.MarkerGet(lineNo) & DrFrame.PositionMarker_BOOKMARKMASK:
            DrFrame.txtDocument.MarkerDelete(lineNo, DrFrame.PositionMarker_BOOKMARKNUMBER)
            DrFrame.SetStatusText("Position marker cleared at line %s"% str(lineNo+1), 2)
        else:
            DrFrame.txtDocument.MarkerAdd(lineNo, DrFrame.PositionMarker_BOOKMARKNUMBER)
            DrFrame.SetStatusText("Position marker added at line %s"% str(lineNo+1), 2)

    def OnGotoNextPositionMarker (event):
        lineNo = DrFrame.txtDocument.GetCurrentLine()
        newLineNo = DrFrame.txtDocument.MarkerNext(lineNo + 1, DrFrame.PositionMarker_BOOKMARKMASK)
        if newLineNo != -1:
            DrFrame.txtDocument.GotoLine(newLineNo)
        else:
            lineNo = DrFrame.txtDocument.GetLineCount()
            newLineNo = DrFrame.txtDocument.MarkerNext(0, DrFrame.PositionMarker_BOOKMARKMASK)
            if newLineNo != -1:
                DrFrame.txtDocument.GotoLine(newLineNo)
        DrFrame.txtDocument.EnsureVisible(DrFrame.txtDocument.GetCurrentLine())
        DrFrame.txtDocument.EnsureCaretVisible()

    def OnGotoPreviousPositionMarker (event):
        lineNo = DrFrame.txtDocument.GetCurrentLine()
        newLineNo = DrFrame.txtDocument.MarkerPrevious(lineNo - 1, DrFrame.PositionMarker_BOOKMARKMASK)
        if newLineNo != -1:
            DrFrame.txtDocument.GotoLine(newLineNo)
        else:
            lineNo = DrFrame.txtDocument.GetLineCount()
            newLineNo = DrFrame.txtDocument.MarkerPrevious(lineNo, DrFrame.PositionMarker_BOOKMARKMASK)
            if newLineNo != -1:
                DrFrame.txtDocument.GotoLine(newLineNo)
        DrFrame.txtDocument.EnsureVisible(DrFrame.txtDocument.GetCurrentLine())
        DrFrame.txtDocument.EnsureCaretVisible()

    def OnClearAllPositionMarkers (event):
        DrFrame.txtDocument.MarkerDeleteAll(DrFrame.PositionMarker_BOOKMARKNUMBER)

    ID_SETPOSITIONMARKER = DrFrame.GetNewId()
    ID_GOTONEXTPOSITIONMARKER = DrFrame.GetNewId()
    ID_GOTOPREVIOUSPOSITIONMARKER = DrFrame.GetNewId()
    ID_CLEARALLPOSITIONMARKER = DrFrame.GetNewId()


    DrFrame.Bind(wx.EVT_MENU, OnTogglePositionMarker, id=ID_SETPOSITIONMARKER)
    DrFrame.Bind(wx.EVT_MENU, OnGotoNextPositionMarker, id=ID_GOTONEXTPOSITIONMARKER)
    DrFrame.Bind(wx.EVT_MENU, OnGotoPreviousPositionMarker, id=ID_GOTOPREVIOUSPOSITIONMARKER)
    DrFrame.Bind(wx.EVT_MENU, OnClearAllPositionMarkers, id=ID_CLEARALLPOSITIONMARKER)

    DrFrame.AddPluginShortcutFunction("PositionMarker", "Toggle Position Marker", OnTogglePositionMarker)
    DrFrame.AddPluginShortcutFunction("PositionMarker", "Goto Next Position Marker", OnGotoNextPositionMarker)
    DrFrame.AddPluginShortcutFunction("PositionMarker", "Goto Previous Position Marker", OnGotoPreviousPositionMarker)
    DrFrame.AddPluginShortcutFunction("PositionMarker", "Clear All Position Markers", OnClearAllPositionMarkers)

    DrFrame.AddPluginPopUpMenuFunction("PositionMarker", "Toggle Position Marker", OnTogglePositionMarker)
    DrFrame.AddPluginPopUpMenuFunction("PositionMarker", "Goto Next Position Marker", OnGotoNextPositionMarker)
    DrFrame.AddPluginPopUpMenuFunction("PositionMarker", "Goto Previous Position Marker", OnGotoPreviousPositionMarker)
    DrFrame.AddPluginPopUpMenuFunction("PositionMarker", "Clear All Position Markers", OnClearAllPositionMarkers)

    DrFrame.LoadPluginShortcuts('PositionMarker')

    positionmarkermenu = wx.Menu()
    positionmarkermenu.Append(ID_SETPOSITIONMARKER, DrFrame.GetPluginMenuLabel('PositionMarker', 'Toggle Position Marker', 'Toggle Position Marker'))
    positionmarkermenu.Append(ID_GOTONEXTPOSITIONMARKER, DrFrame.GetPluginMenuLabel('PositionMarker', 'Goto Next Position Marker', 'Goto Next Position Marker'))
    positionmarkermenu.Append(ID_GOTOPREVIOUSPOSITIONMARKER, DrFrame.GetPluginMenuLabel('PositionMarker', 'Goto Previous Position Marker', 'Goto Previous Position Marker'))
    positionmarkermenu.Append(ID_CLEARALLPOSITIONMARKER, DrFrame.GetPluginMenuLabel('PositionMarker', 'Clear All Position Markers', 'Clear All Position Markers'))

    DrFrame.viewmenu.AppendSeparator()
    DrFrame.viewmenu.AppendSubMenu(positionmarkermenu, "Position Marker")


