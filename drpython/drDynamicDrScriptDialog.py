#   Copyright 2003-2010 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#


#Dynamic DrScript Dialog

import os.path
import wx
import drScrolledMessageDialog
from drText import DrText

class drDynamicDrScriptDialog(wx.Dialog):

    def __init__(self, parent, text):
        wx.Dialog.__init__(self, parent, -1, ("Dynamic DrScript"), wx.DefaultPosition, (600, 400), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.parent = parent

        self.txtScript = DrText(self, -1, self.parent, 1)
        self.txtScript.SetText(text)
        self.txtScript.SetupPrefsDocument()
        self.theSizer.Add(self.txtScript, 9, wx.EXPAND)

        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnClose = wx.Button(self, 101, "&Close")
        self.btnOk = wx.Button(self, 102, "&Ok")
        self.theSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnClose, 0,  wx.SHAPED | wx.ALIGN_CENTER)
        self.commandSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnOk, 0,  wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.commandSizer, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.btnOk.SetDefault()

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.Bind(wx.EVT_CLOSE, self.OnCloseW)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id=101)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnOk, id=102)

        self.parent.LoadDialogSizeAndPosition(self, "dynamicdrscriptdialog.sizeandposition.dat")

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, "dynamicdrscriptdialog.sizeandposition.dat")
        if event is not None:
            event.Skip()

    def OnbtnClose(self, event):
        self.Close(1)

    def OnbtnOk(self, event):
        value = self.txtScript.GetText()
        if value.find("DrFilename") > -1:
            value = value.replace("DrFilename", "self.parent.txtDocument.filename")
        #if value.find("DrScript") > -1:
        #    value = value.replace("DrScript", "self.parent.DrScript")
        if value.find("DrDocument") > -1:
            value = value.replace("DrDocument", "self.parent.txtDocument")
        if value.find("DrPrompt") > -1:
            value = value.replace("DrPrompt", "self.parent.txtPrompt")
        if value.find("DrFrame") > -1:
            value = value.replace("DrFrame", "self.parent")

        try:
            #Bug-Report/Fix (Submitted, Edited) Franz Steinhausier
            value = value.replace('\r', '\n')
            code = compile((value + '\n'), "Dynamic DrScript", "exec")
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, ("Error compiling dynamic script."), "Error", wx.DefaultPosition, (550,300))
            return

        try:
            exec(code)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, ("Error running dynamic script."), "Error", wx.DefaultPosition, (550,300))
            return

    def GetText(self):
        return self.txtScript.GetText()
