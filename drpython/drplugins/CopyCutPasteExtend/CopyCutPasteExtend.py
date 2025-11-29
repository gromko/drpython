#   Programmer:  Franz Steinhaeusler
#   E-mail:      francescoa@users.sourceforge.net
#   Note:        Initial Release 14/7/2004
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

#Version: 1.0.1:
# - removed Clear alternative copy/cut/paste keys
# - no global variables, new DrFrame member variables in form of DrFrame.<PluginNme>_var
# - used drScrolledMessageDialog
# - cleared some old comments

#Version: 1.0.2:
# - Added Popup function

#Version: 1.0.3:
# - Option Select after paste
# - rectangular paste after rectangular selection

#Version: 1.0.4:
# - three options on paste:

#Version: 1.0.5, 04.11.2004:
#Version: 1.0.6, 25.11.2004:
#Version: 1.0.7, 16.12.2004:
#Version: 1.0.8, 21.01.2005:
#Version: 1.0.8, 07.04.2007:

#for changes please see ChangeLog,txt


#Plugin
#CopyCutPasteExtend

#This plugin offers extended functions for copy/cut/paste

#todo: comment this out again
#for pychecker
#import sys
#sys.path.append('c:/Eigene Dateien/python/drpython')


import wx
import os.path
import drPrefsFile
import drScrolledMessageDialog
import re
import string

def OnAbout(DrFrame):
    Version = "CopyCutPasteExtend: Version: 1.0.9\n"
    AboutString = Version + "By Franz Steinhaeusler\n\nReleased under the GPL."
    drScrolledMessageDialog.ShowMessage(DrFrame, AboutString, "About")

def OnHelp(DrFrame):
    try:
        drScrolledMessageDialog.ShowMessage(DrFrame, "Please see Changelog.txt", "Help")
    except:
        drScrolledMessageDialog.ShowMessage(DrFrame, "No help available", "Help")

def OnPreferences(DrFrame):

    def GetIntFromBool (b):
        if b:
            return 1
        else:
            return 0

    d = wx.Dialog(DrFrame, -1, ("Customize CopyCutPasteExtend"), wx.DefaultPosition, wx.Size(320, 320), wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME)
    chkPutCursorToFirstRow = wx.CheckBox(d, -1, "Put cursor to first row after line copy/cut", wx.Point(20, 20))
    chkCopyCutAppendWholeLine = wx.CheckBox(d, -1, "Copy whole line in copy/cut append", wx.Point(20, 40))

    chkSelectAfterPaste =  wx.RadioBox(d, -1, "After Paste:", wx.Point(20, 60), wx.DefaultSize, ["Paste and select (leave cursor before pasted text)", "Paste (leave cursor before pasted text)", "Paste (leave cursor behind pasted text) (default)"], 1, wx.RA_SPECIFY_COLS)

    chkUseMultipleClipBoards = wx.CheckBox(d, -1, "Use Multiple Clipboards", wx.Point(20, 160))
    chkSaveMultipleClipBoards = wx.CheckBox(d, -1, "Save Multiple Clipboards", wx.Point(20, 180))
    chkAdjustText = wx.CheckBox(d,-1,"AdjustText",wx.Point(20,200))

    #default before
    chkPutCursorToFirstRow.SetValue(DrFrame.CopyCutPasteExtend_PutCursorToFirstRow)
    chkCopyCutAppendWholeLine.SetValue(DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine)
    chkSelectAfterPaste.SetSelection(DrFrame.CopyCutPasteExtend_SelectAfterPaste)
    chkUseMultipleClipBoards.SetValue(DrFrame.CopyCutPasteExtend_UseMultipleClipBoards)
    chkSaveMultipleClipBoards.SetValue(DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards)
    chkAdjustText.SetValue(DrFrame.CopyCutPasteExtend_AdjustText)

    wx.Button(d, wx.ID_CANCEL, "Cancel", wx.Point(20, 240))
    wx.Button(d, wx.ID_OK, "Ok", wx.Point(150, 240))

    if d.ShowModal() == wx.ID_OK:
        f = file(DrFrame.pluginspreferencesdirectory + "/CopyCutPasteExtend.preferences.dat", 'w')
        DrFrame.CopyCutPasteExtend_PutCursorToFirstRow = GetIntFromBool (chkPutCursorToFirstRow.GetValue())
        f.write("<copycutpasteextend.putcursortofirstrow>" + str(DrFrame.CopyCutPasteExtend_PutCursorToFirstRow) + "</copycutpasteextend.putcursortofirstrow>\n")
        DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine = GetIntFromBool (chkCopyCutAppendWholeLine.GetValue())
        f.write("<copycutpasteextend.copycutappendwholeline>" + str(DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine) + "</copycutpasteextend.copycutappendwholeline>\n")
        DrFrame.CopyCutPasteExtend_SelectAfterPaste = chkSelectAfterPaste.GetSelection()
        f.write("<copycutpasteextend.selectafterpaste>" + str(DrFrame.CopyCutPasteExtend_SelectAfterPaste) + "</copycutpasteextend.selectafterpaste>\n")
        DrFrame.CopyCutPasteExtend_UseMultipleClipBoards = GetIntFromBool (chkUseMultipleClipBoards.GetValue())
        f.write("<copycutpasteextend.usemultipleclipboards>" + str(DrFrame.CopyCutPasteExtend_UseMultipleClipBoards) + "</copycutpasteextend.usemultipleclipboards>\n")
        DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards = GetIntFromBool (chkSaveMultipleClipBoards.GetValue())
        f.write("<copycutpasteextend.savemultipleclipboards>" + str(DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards) + "</copycutpasteextend.savemultipleclipboards>\n")
        DrFrame.CopyCutPasteExtend_AdjustText = GetIntFromBool(chkAdjustText.GetValue())
        f.write("<copycutpasteextend.adjusttext>"+str(DrFrame.CopyCutPasteExtend_AdjustText)+"</copycutpasteextend.adjusttext>\n")
        f.close()
    d.Destroy()

class MultipleSelectiondlg(wx.Dialog):
    def __init__ (self, parent, choices):
        wx.Dialog.__init__ (self, parent, -1, "Multiple ClipBoard", wx.DefaultPosition,  wx.Size(400, 300), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)
        self.btnOk = wx.Button(self, wx.ID_OK, "&Ok", pos = (290, 50))
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "&Cancel", pos = (290, 100))
        self.list = wx.ListBox(self, 403, pos = (20, 35), size = (250, 200), choices = choices)

        self.Bind(wx.EVT_BUTTON,  self.OnbtnOk, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnCancel, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnbtnOk)
        self.list.SetSelection (0)
        self.list.SetFocus ()
        self.btnOk.SetDefault()

    def OnbtnOk (self, event):
        self.EndModal(1)

    def OnbtnCancel (self, event):
        self.EndModal(0)

def Plugin(DrFrame):

    DrFrame.CopyCutPasteExtend_PutCursorToFirstRow = 1
    DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine = 1
    DrFrame.CopyCutPasteExtend_SelectAfterPaste = 2
    DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
    DrFrame.CopyCutPasteExtend_oldcursorpos = -1
    DrFrame.CopyCutPasteExtend_multiclipptr = 0
    DrFrame.CopyCutPasteExtend_multiclipbuffer = []
    DrFrame.CopyCutPasteExtend_newcliptext = ""
    DrFrame.CopyCutPasteExtend_UseMultipleClipBoards = 0
    DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards = 0
    DrFrame.CopyCutPasteExtend_AdjustText = 0



    if os.path.exists(DrFrame.pluginspreferencesdirectory + "/CopyCutPasteExtend.preferences.dat"):
        f = file(DrFrame.pluginspreferencesdirectory + "/CopyCutPasteExtend.preferences.dat", 'r')
        text = f.read()
        f.close()
        DrFrame.CopyCutPasteExtend_PutCursorToFirstRow = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_PutCursorToFirstRow, text, "copycutpasteextend.putcursortofirstrow", True)
        DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine, text, "copycutpasteextend.copycutappendwholeline", True)
        DrFrame.CopyCutPasteExtend_SelectAfterPaste = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_SelectAfterPaste, text, "copycutpasteextend.selectafterpaste", True)
        DrFrame.CopyCutPasteExtend_UseMultipleClipBoards = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_UseMultipleClipBoards, text, "copycutpasteextend.usemultipleclipboards", True)
        DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards, text, "copycutpasteextend.savemultipleclipboards", True)
        DrFrame.CopyCutPasteExtend_AdjustText = drPrefsFile.GetPrefFromText(DrFrame.CopyCutPasteExtend_AdjustText,text,"copycutpasteextend.adjusttext",True)

    if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
        if DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards:
            if os.path.exists (DrFrame.pluginsdatdirectory + "/MultiClip.log"):
                f = file (DrFrame.pluginsdatdirectory+ "/MultiClip.log", "r")
                DrFrame.CopyCutPasteExtend_multiclipbuffer = f.read().strip().split('\n\n\r\r\r\n')

    def GetEolLen ():
        return len (DrFrame.txtDocument.GetEndOfLineCharacter())

    def AppendMultiClip (replace = 0):
        if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            tmp = wx.TheClipboard.GetData(do)
            if tmp:
                text = do.GetText()
                if replace:
                    DrFrame.CopyCutPasteExtend_multiclipbuffer.pop (0)
                if text in DrFrame.CopyCutPasteExtend_multiclipbuffer:
                    idx = DrFrame.CopyCutPasteExtend_multiclipbuffer.index (text)
                    DrFrame.CopyCutPasteExtend_multiclipbuffer.pop (idx)
                DrFrame.CopyCutPasteExtend_multiclipbuffer.insert (0, text)
                DrFrame.CopyCutPasteExtend_multiclipbuffer = DrFrame.CopyCutPasteExtend_multiclipbuffer[0:20]
            wx.TheClipboard.Close()
            if DrFrame.CopyCutPasteExtend_SaveMultipleClipBoards:
                f = file(DrFrame.pluginsdatdirectory + "/MultiClip.log", 'w')
                #code from Sessions plugin (enable to write entries with lineendings
                for x in DrFrame.CopyCutPasteExtend_multiclipbuffer:
                    f.write(x + '\n\n\r\r\r\n')
                f.close()




    def OnCopySpecial (event):
        x, y = DrFrame.txtDocument.GetSelection()
        DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
        #nothing selected
        if x == y:
            lin = DrFrame.txtDocument.GetCurrentLine()
            text = DrFrame.txtDocument.GetLine (lin)
            if text == "":
                return

            #bit complicated, but it works
            endlinepos = DrFrame.txtDocument.GetLineEndPosition(lin)
            if text[-1] != '\n':
                text += DrFrame.txtDocument.GetEndOfLineCharacter()
            if DrFrame.CopyCutPasteExtend_PutCursorToFirstRow:
                DrFrame.txtDocument.HomeDisplay()
                DrFrame.txtDocument.SetAnchor(endlinepos)
            else:
                if lin == 0:
                    beglinepos = 0
                else:
                    beglinepos = DrFrame.txtDocument.GetLineEndPosition(lin-1)+GetEolLen()
                DrFrame.txtDocument.SetSelection(beglinepos, endlinepos)

            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            DrFrame.SetStatusText("Copy Special", 2)
        else:
            DrFrame.txtDocument.CmdKeyExecute(wx.stc.STC_CMD_COPY)
            DrFrame.CopyCutPasteExtend_sel_is_rectangle = DrFrame.txtDocument.SelectionIsRectangle()
        AppendMultiClip (0)
        DrFrame.CopyCutPasteExtend_newcliptext = ""

    def OnCutSpecial (event):
        x, y = DrFrame.txtDocument.GetSelection()
        DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
        if x == y:
            lin = DrFrame.txtDocument.GetCurrentLine()
            text, posinline = DrFrame.txtDocument.GetCurLine()
            if text == "":
                return
            endlinepos = DrFrame.txtDocument.GetLineEndPosition(lin)
            offset = 0
            if text[-1] == '\n':
                offset = 1
                if DrFrame.txtDocument.GetEOLMode() == wx.stc.STC_EOL_CRLF:
                    offset = 2
            else:
                text += DrFrame.txtDocument.GetEndOfLineCharacter()
            if DrFrame.CopyCutPasteExtend_PutCursorToFirstRow:
                DrFrame.txtDocument.HomeDisplay()
                DrFrame.txtDocument.SetAnchor(endlinepos+offset)
            else:
                if lin == 0:
                    beglinepos = 0
                else:
                    beglinepos = DrFrame.txtDocument.GetLineEndPosition(lin-1)+GetEolLen()
                DrFrame.txtDocument.SetSelection(beglinepos, endlinepos+offset)
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            DrFrame.txtDocument.ReplaceSelection('')
            if not DrFrame.CopyCutPasteExtend_PutCursorToFirstRow:
                DrFrame.txtDocument.GotoPos (DrFrame.txtDocument.GetCurrentPos() + posinline)
            DrFrame.SetStatusText("Cut Special", 2)
        else:
            DrFrame.txtDocument.CmdKeyExecute(wx.stc.STC_CMD_CUT)
        AppendMultiClip (0)
        DrFrame.CopyCutPasteExtend_newcliptext = ""

    def OnCopyAppend (event):
        DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
        wx.TheClipboard.Open()
        do = wx.TextDataObject()
        cur_clip_data = ""
        tmp = wx.TheClipboard.GetData(do)
        if tmp:
            cur_clip_data = do.GetText()
        x, y = DrFrame.txtDocument.GetSelection()
        to_append = True
        if x == y and DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine:
            lin = DrFrame.txtDocument.GetCurrentLine()
            text = DrFrame.txtDocument.GetLine (lin)
            if text != "":
                endlinepos = DrFrame.txtDocument.GetLineEndPosition(lin)
                if text[-1] != '\n':
                    text += DrFrame.txtDocument.GetEndOfLineCharacter()
                cur_clip_data += text
                if DrFrame.CopyCutPasteExtend_PutCursorToFirstRow:
                    DrFrame.txtDocument.HomeDisplay()
                    DrFrame.txtDocument.SetAnchor(endlinepos)
                else:
                    if lin == 0:
                        beglinepos = 0
                    else:
                        beglinepos = DrFrame.txtDocument.GetLineEndPosition(lin-1)+GetEolLen()
                    DrFrame.txtDocument.SetSelection(beglinepos, endlinepos)
            else:
                to_append = False
        else:
            cur_clip_data += DrFrame.txtDocument.GetSelectedText()
        if to_append:
            wx.TheClipboard.SetData(wx.TextDataObject(cur_clip_data))
            wx.TheClipboard.Close()
            DrFrame.SetStatusText("Copy/Append", 2)
            AppendMultiClip (1)
        DrFrame.CopyCutPasteExtend_newcliptext = ""

    def OnCutAppend (event):
        DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
        wx.TheClipboard.Open()
        do = wx.TextDataObject()
        cur_clip_data = ""
        tmp = wx.TheClipboard.GetData(do)
        if tmp:
            cur_clip_data = do.GetText()
        x, y = DrFrame.txtDocument.GetSelection()
        to_append = True
        line_cut = False
        if x == y and DrFrame.CopyCutPasteExtend_CopyCutAppendWholeLine:
            lin = DrFrame.txtDocument.GetCurrentLine()
            text,posinline = DrFrame.txtDocument.GetCurLine()
            endlinepos = DrFrame.txtDocument.GetLineEndPosition(lin)
            offset = 0
            if text != "":
                if text[-1] == '\n':
                    offset = 1
                    if DrFrame.txtDocument.GetEOLMode() == wx.stc.STC_EOL_CRLF:
                        offset = 2
                else:
                    text += DrFrame.txtDocument.GetEndOfLineCharacter()

                if DrFrame.CopyCutPasteExtend_PutCursorToFirstRow:
                    DrFrame.txtDocument.HomeDisplay()
                    DrFrame.txtDocument.SetAnchor(endlinepos+offset)
                else:
                    if lin == 0:
                        beglinepos = 0
                    else:
                        beglinepos = DrFrame.txtDocument.GetLineEndPosition(lin-1)+GetEolLen()
                    DrFrame.txtDocument.SetSelection(beglinepos, endlinepos+offset)
                cur_clip_data += text
                line_cut = True

            else:
                to_append = False
        else:
            cur_clip_data += DrFrame.txtDocument.GetSelectedText()
        if to_append:
            wx.TheClipboard.SetData(wx.TextDataObject(cur_clip_data))
            wx.TheClipboard.Close()
            DrFrame.txtDocument.ReplaceSelection ('')
            if not DrFrame.CopyCutPasteExtend_PutCursorToFirstRow and line_cut:
                DrFrame.txtDocument.GotoPos (DrFrame.txtDocument.GetCurrentPos() + posinline)
            DrFrame.SetStatusText("Cut/Append", 2)
            AppendMultiClip (1)
        DrFrame.CopyCutPasteExtend_newcliptext = ""

    #code from drpython.py
    def AdjustText (text):
        #todo option
        #correct line endings
        emode = DrFrame.txtDocument.GetEOLMode()
        if emode == wx.stc.STC_EOL_CR:
            text = DrFrame.FormatMacReTarget.sub('\r', text)
        elif emode == wx.stc.STC_EOL_CRLF:
            text = DrFrame.FormatWinReTarget.sub('\r\n', text)
        else:
            text = DrFrame.FormatUnixReTarget.sub('\n', text)


        #set correct indentation
        eol = DrFrame.txtDocument.GetEndOfLineCharacter()
        regex = re.compile('(\S)|' + eol)
        x = DrFrame.txtDocument.GetTabWidth()
        lines = text.split(eol)
        new_lines = []
        if DrFrame.txtDocument.GetUseTabs():
            #Create Target String
            oof = x * " "

            for line in lines:
                result = regex.search(line + eol)
                if result is not None:
                    end = result.start()
                    newline = line[0:end].replace(oof, "\t") + line[end:]
                    new_lines.append(newline)
                else:
                    new_lines.append(line)
        else:
            #or GetIndentWidth?
            new_lines = []
            for line in lines:
                result = regex.search(line + eol)
                if result is not None:
                    end = result.start()
                    new_lines.append(line[0:end].expandtabs(x) + line[end:])
                else:
                    new_lines.append(line)
        return string.join(new_lines, eol)

    def OnAlternativePaste (event):
        if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
            if DrFrame.CopyCutPasteExtend_newcliptext != '':
                wx.TheClipboard.Open()
                do = wx.TextDataObject()
                wx.TheClipboard.SetData(wx.TextDataObject(DrFrame.CopyCutPasteExtend_newcliptext))
                wx.TheClipboard.Close()

                #reorder
                if DrFrame.CopyCutPasteExtend_newcliptext in DrFrame.CopyCutPasteExtend_multiclipbuffer:
                    idx = DrFrame.CopyCutPasteExtend_multiclipbuffer.index (DrFrame.CopyCutPasteExtend_newcliptext)
                    DrFrame.CopyCutPasteExtend_multiclipbuffer.pop (idx)
                DrFrame.CopyCutPasteExtend_multiclipbuffer.insert (0, DrFrame.CopyCutPasteExtend_newcliptext)
                DrFrame.CopyCutPasteExtend_newcliptext = ""

        wx.TheClipboard.Open()
        do = wx.TextDataObject()
        tmp = wx.TheClipboard.GetData(do)
        if tmp:
            if DrFrame.CopyCutPasteExtend_sel_is_rectangle:
                text = do.GetText()
                ind = 0
                pos = DrFrame.txtDocument.GetCurrentPos()
                oldpos = pos
                line = DrFrame.txtDocument.GetCurrentLine()
                col = DrFrame.txtDocument.GetColumn(DrFrame.txtDocument.GetCurrentPos())
                newselpos = oldpos
                DrFrame.txtDocument.BeginUndoAction()
                #selection end and selection begin
                #better paste?insert spaces
                #gotopos ohne line down
                #begin end undoaction
                while text.find('\n', ind) != -1:
                    newind = text.find('\n', ind)
                    temp = text [ind:newind-1]
                    DrFrame.txtDocument.AddText(temp)
                    #line down
                    newselpos = DrFrame.txtDocument.GetCurrentPos()
                    DrFrame.txtDocument.GotoPos(pos)
                    DrFrame.txtDocument.CmdKeyExecute (wx.stc.STC_CMD_LINEDOWN)
                    newcol = DrFrame.txtDocument.GetColumn(DrFrame.txtDocument.GetCurrentPos())
                    while newcol < col:
                        DrFrame.txtDocument.AddText(' ')
                        newcol = DrFrame.txtDocument.GetColumn(DrFrame.txtDocument.GetCurrentPos())

                    pos = DrFrame.txtDocument.GetCurrentPos()
                    ind = newind+1

                DrFrame.txtDocument.GotoPos (newselpos)
                tempos = newselpos
                while tempos > oldpos:
                    DrFrame.txtDocument.CmdKeyExecute(wx.stc.STC_CMD_CHARLEFTRECTEXTEND)
                    tempos = DrFrame.txtDocument.GetCurrentPos()
                DrFrame.txtDocument.EndUndoAction()
            else:
                text = do.GetText()
                if DrFrame.CopyCutPasteExtend_AdjustText:
                    text = AdjustText (text)

                if DrFrame.CopyCutPasteExtend_SelectAfterPaste == 2:
                    DrFrame.txtDocument.AddText(text)
                else:
                    DrFrame.txtDocument.InsertText(DrFrame.txtDocument.GetCurrentPos(), text)

                if DrFrame.CopyCutPasteExtend_SelectAfterPaste == 2:
                    pass
                elif DrFrame.CopyCutPasteExtend_SelectAfterPaste == 1:
                    DrFrame.txtDocument.SetSelection(DrFrame.txtDocument.GetCurrentPos(), DrFrame.txtDocument.GetCurrentPos())
                else:
                    DrFrame.txtDocument.SetSelection(DrFrame.txtDocument.GetCurrentPos() + len (text), DrFrame.txtDocument.GetCurrentPos())
            wx.TheClipboard.Close()

    def OnNextMultiClip (event):
        if len(DrFrame.CopyCutPasteExtend_multiclipbuffer) <= 1:
            return
        x, y = DrFrame.txtDocument.GetSelection()
        curpos = min (x, y)
        if DrFrame.CopyCutPasteExtend_oldcursorpos != curpos:
            DrFrame.CopyCutPasteExtend_oldcursorpos = curpos
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            tmp = wx.TheClipboard.GetData(do)
            text = ""
            if tmp:
                text = do.GetText()
            wx.TheClipboard.Close()
            if text == DrFrame.CopyCutPasteExtend_multiclipbuffer [0]:
                DrFrame.CopyCutPasteExtend_multiclipptr = 0
            else:
                DrFrame.CopyCutPasteExtend_multiclipptr = -1
        DrFrame.CopyCutPasteExtend_multiclipptr += 1
        if DrFrame.CopyCutPasteExtend_multiclipptr >= len (DrFrame.CopyCutPasteExtend_multiclipbuffer):
            DrFrame.CopyCutPasteExtend_multiclipptr = 0
        text = DrFrame.CopyCutPasteExtend_multiclipbuffer [DrFrame.CopyCutPasteExtend_multiclipptr]
        text = AdjustText (text)
        x, y = DrFrame.txtDocument.GetSelection()
        if x != y:
            DrFrame.txtDocument.ReplaceSelection (text)
        else:
            DrFrame.txtDocument.AddText (text)
        DrFrame.txtDocument.SetSelection (DrFrame.CopyCutPasteExtend_oldcursorpos + len (text), DrFrame.CopyCutPasteExtend_oldcursorpos)
        DrFrame.SetStatusText("Ptr: %d/%d '%s'" % (DrFrame.CopyCutPasteExtend_multiclipptr + 1, len(DrFrame.CopyCutPasteExtend_multiclipbuffer),  text), 2)
        DrFrame.CopyCutPasteExtend_newcliptext = text
        #bei naechstem paste cur_text != clipboard ===> cur_text => clipborard, und auf 0 pos setzen (duplicate beachten)

    def OnPreviousMultiClip (event):
        if len(DrFrame.CopyCutPasteExtend_multiclipbuffer) <= 1:
            return
        x, y = DrFrame.txtDocument.GetSelection()
        curpos = min (x, y)
        if DrFrame.CopyCutPasteExtend_oldcursorpos != curpos:
            DrFrame.CopyCutPasteExtend_oldcursorpos = curpos
            DrFrame.CopyCutPasteExtend_multiclipptr = len (DrFrame.CopyCutPasteExtend_multiclipbuffer)
        DrFrame.CopyCutPasteExtend_multiclipptr -= 1
        if DrFrame.CopyCutPasteExtend_multiclipptr < 0:
            DrFrame.CopyCutPasteExtend_multiclipptr = len (DrFrame.CopyCutPasteExtend_multiclipbuffer) - 1
        text = DrFrame.CopyCutPasteExtend_multiclipbuffer [DrFrame.CopyCutPasteExtend_multiclipptr]
        text = AdjustText (text)
        x, y = DrFrame.txtDocument.GetSelection()
        if x != y:
            DrFrame.txtDocument.ReplaceSelection (text)
        else:
            DrFrame.txtDocument.AddText (text)
        DrFrame.txtDocument.SetSelection (DrFrame.CopyCutPasteExtend_oldcursorpos + len (text), DrFrame.CopyCutPasteExtend_oldcursorpos)
        DrFrame.SetStatusText("Ptr: %d/%d '%s'" % (DrFrame.CopyCutPasteExtend_multiclipptr + 1, len(DrFrame.CopyCutPasteExtend_multiclipbuffer), text), 2)
        DrFrame.CopyCutPasteExtend_newcliptext = text

    def OnShowMultiClip (event):
        x, y = DrFrame.txtDocument.GetSelection()
        curpos = min (x, y)
        if DrFrame.CopyCutPasteExtend_oldcursorpos != curpos:
            DrFrame.CopyCutPasteExtend_oldcursorpos = curpos
            DrFrame.CopyCutPasteExtend_multiclipptr = 0
        idx = 0
        if len(DrFrame.CopyCutPasteExtend_multiclipbuffer) > 1:
            dlg = MultipleSelectiondlg(DrFrame, DrFrame.CopyCutPasteExtend_multiclipbuffer)
        else:
            d = wx.MessageBox("Nothing to do!", "Show Multiple Clipboard", wx.ICON_INFORMATION)
            return

        if dlg.ShowModal() == 0:
            return
        if not dlg.list.GetSelections():
            return
        text = DrFrame.CopyCutPasteExtend_multiclipbuffer[dlg.list.GetSelections()[0]]
        x, y = DrFrame.txtDocument.GetSelection()
        if x != y:
            DrFrame.txtDocument.ReplaceSelection (text)
        else:
            DrFrame.txtDocument.AddText (text)
        DrFrame.txtDocument.SetSelection (DrFrame.CopyCutPasteExtend_oldcursorpos + len (text), DrFrame.CopyCutPasteExtend_oldcursorpos)
        DrFrame.SetStatusText("Ptr: %d/%d '%s'" % (DrFrame.CopyCutPasteExtend_multiclipptr + 1, len(DrFrame.CopyCutPasteExtend_multiclipbuffer), text), 2)
        DrFrame.CopyCutPasteExtend_newcliptext = text

    def OnCopyCurrentWordToClip (event):
        gcp = DrFrame.txtDocument.GetCurrentPos()
        st = DrFrame.txtDocument.WordStartPosition(gcp, 1)
        end = DrFrame.txtDocument.WordEndPosition(gcp, 1)
        #is there any word under cursor?
        if st != end:
            DrFrame.CopyCutPasteExtend_sel_is_rectangle = False
            DrFrame.txtDocument.SetSelection(st, end)
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            wx.TheClipboard.SetData(wx.TextDataObject(DrFrame.txtDocument.GetSelectedText()))
            wx.TheClipboard.Close()
            DrFrame.SetStatusText("Copied word under cursor: '%s'" % DrFrame.txtDocument.GetSelectedText(), 2)
            AppendMultiClip (0)
            DrFrame.CopyCutPasteExtend_newcliptext = ""
        else:
            DrFrame.SetStatusText("Cursor not under word", 2)


    ID_COPYSPECIAL = DrFrame.GetNewId()
    ID_CUTSPECIAL = DrFrame.GetNewId()
    ID_COPYAPPEND = DrFrame.GetNewId()
    ID_CUTAPPEND = DrFrame.GetNewId()
    ID_ALTERNATIVEPASTE = DrFrame.GetNewId()
    ID_NEXTMULTICLIP = DrFrame.GetNewId()
    ID_PREVIOUSMULTICLIP = DrFrame.GetNewId()
    ID_SHOWMULTICLIP = DrFrame.GetNewId()
    ID_COPYCURRENTWORDTOCLIPBOARD = DrFrame.GetNewId()



    DrFrame.Bind(wx.EVT_MENU, OnCopySpecial, id = ID_COPYSPECIAL)
    DrFrame.Bind(wx.EVT_MENU, OnCutSpecial, id = ID_CUTSPECIAL)
    DrFrame.Bind(wx.EVT_MENU, OnCopyAppend, id = ID_COPYAPPEND)
    DrFrame.Bind(wx.EVT_MENU, OnCutAppend, id = ID_CUTAPPEND)
    DrFrame.Bind(wx.EVT_MENU, OnAlternativePaste, id = ID_ALTERNATIVEPASTE)
    DrFrame.Bind(wx.EVT_MENU, OnCopyCurrentWordToClip, id = ID_COPYCURRENTWORDTOCLIPBOARD)
    if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
        DrFrame.Bind(wx.EVT_MENU, OnNextMultiClip, id = ID_NEXTMULTICLIP)
        DrFrame.Bind(wx.EVT_MENU, OnPreviousMultiClip, id = ID_PREVIOUSMULTICLIP)
        DrFrame.Bind(wx.EVT_MENU, OnShowMultiClip, id = ID_SHOWMULTICLIP)

    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Copy Special", OnCopySpecial)
    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Cut Special", OnCutSpecial)
    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Copy Append", OnCopyAppend)
    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Cut Append", OnCutAppend)
    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Alternative Paste", OnAlternativePaste)
    DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Copy Current Word", OnCopyCurrentWordToClip)
    if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
        DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Next MultiClip", OnNextMultiClip)
        DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Previous MultiClip", OnPreviousMultiClip)
        DrFrame.AddPluginShortcutFunction("CopyCutPasteExtend", "Show MultiClip", OnShowMultiClip)

    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Copy Special", OnCopySpecial)
    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Cut Special", OnCutSpecial)
    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Copy Append", OnCopyAppend)
    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Cut Append", OnCutAppend)
    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Alternative Paste", OnAlternativePaste)
    DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Copy Current Word", OnCopyCurrentWordToClip)
    if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
        DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Next MultiClip", OnNextMultiClip)
        DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Previous MultiClip", OnPreviousMultiClip)
        DrFrame.AddPluginPopUpMenuFunction("CopyCutPasteExtend", "Show MultiClip", OnShowMultiClip)

    DrFrame.LoadPluginShortcuts('CopyCutPasteExtend')

    copycutpasteextend = wx.Menu()
    copycutpasteextend.Append(ID_COPYSPECIAL, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Copy Special', 'Copy Special'))
    copycutpasteextend.Append(ID_CUTSPECIAL, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Cut Special', 'Cut Special'))
    copycutpasteextend.Append(ID_COPYAPPEND, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Copy Append', 'Copy Append'))
    copycutpasteextend.Append(ID_CUTAPPEND, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Cut Append', 'Cut Append'))
    copycutpasteextend.Append(ID_COPYCURRENTWORDTOCLIPBOARD, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Copy Current Word', 'Copy Current Word'))
    copycutpasteextend.Append(ID_ALTERNATIVEPASTE, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Alternative Paste', 'Alternative Paste'))
    copycutpasteextend.AppendSeparator()
    if DrFrame.CopyCutPasteExtend_UseMultipleClipBoards:
        copycutpasteextend.Append(ID_NEXTMULTICLIP, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Next MultiClip', 'Next MultiClip'))
        copycutpasteextend.Append(ID_PREVIOUSMULTICLIP, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Previous MultiClip', 'Previous MultiClip'))
        copycutpasteextend.Append(ID_SHOWMULTICLIP, DrFrame.GetPluginMenuLabel('CopyCutPasteExtend', 'Show MultiClip', 'Show MultiClip'))
        #TODO!!!should it be handled a new clipstring, if the position is changed?

    DrFrame.editmenu.AppendSeparator()
    DrFrame.editmenu.AppendMenu(DrFrame.GetNewId(), "Copy/Cut/Paste Extend", copycutpasteextend)
