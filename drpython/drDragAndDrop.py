#   Copyright 2003-2010 Daniel Pozmanter
#   Distributed under the terms of the GPL (GNU Public License)
#

#Drag and Drop

#*******************************************************************************************************
#Submitted by Slim Amamou
#Modified by Daniel Pozmanter
#Modified again by Dan for 3.7.0
#   Reworked to add Text Drag and Drop Support
#   Thanks to Robin Dunn for the code.

import wx, wx.stc

class drDropTarget(wx.DropTarget):
    def __init__(self, window):
        wx.DropTarget.__init__(self)
        self.window = window.grandparent

        window.Bind(wx.stc.EVT_STC_START_DRAG, self.OnStartDrag, id=window.GetId())

        self.data = wx.DataObjectComposite()
        self.dtext = wx.TextDataObject()
        self.dfilename = wx.FileDataObject()
        self.data.Add(self.dtext, True)
        self.data.Add(self.dfilename)

        self.draginitiatedfromstc = False

        self.moddown = False

        self.SetDataObject(self.data)

    def DropFiles(self, filenames):
        filenames = list(map(lambda x: x.replace('\\', '/'), filenames))

        for fname in filenames:
            self.window.OpenOrSwitchToFile(fname)

    def DropText(self, text, point):
        if self.window.prefs.draganddropmode != 2:
            if self.draginitiatedfromstc:
                if ((self.window.prefs.draganddroptextmode == 0) and self.moddown) or \
                ((self.window.prefs.draganddroptextmode == 1) and (not self.moddown)):
                    self.window.txtDocument.SetSelectedText("")
            position = self.window.txtDocument.PositionFromPoint(point)
            self.window.txtDocument.InsertText(position, text)
            self.window.txtDocument.GotoPos(position + len(text))


    def OnDrop(self, x, y):
        if self.draginitiatedfromstc == 1 and self.window.prefs.draganddropmode == 2:
            return False
        else:
            return True

    def OnData(self, x, y, theData):
        self.GetData()
        if self.dtext.GetTextLength() > 1:
            self.DropText(self.dtext.GetText(), wx.Point(x, y))
            self.dtext.SetText("")
        else:
            self.DropFiles(self.dfilename.GetFilenames())

        self.draginitiatedfromstc = False

        return theData

    def OnStartDrag(self, event):
        self.draginitiatedfromstc = True

    def SetModifierDown(self, moddown):
        self.moddown = moddown
