#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2010 Daniel Pozmanter
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

#prefs dialog

import os, locale
import sys
import wx
import drScrolledMessageDialog
from drProperty import *
import drPrefsFile
import drFileDialog
from drStyleDialog import drStyleDialog, drSimpleStyleDialog
from drPreferences import drPreferences
import importlib



#Cause I want it to work MY way!
class drPrefsBook(wx.Panel):
    def __init__(self, parent, id, size):
        wx.Panel.__init__(self, parent, id, size=size)

        x, y = size

        self.pages = []
        self.labels = []

        self.ancestor = parent.parent

        self.listview = wx.ListView(self, id+1, pos=(0, 0), size=(150, y), style=wx.LC_SINGLE_SEL|wx.LC_LIST)

        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelected, id=id+1)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.oldpos = -1

    def AddPage(self, page, label):
        page.Show(False)
        self.pages.append(page)
        self.labels.append(label)

    def OnSelected(self, event):
        if self.oldpos > -1:
            self.pages[self.oldpos].Show(False)

        sel = self.listview.GetFocusedItem()

        self.ancestor.prefdialogposition = sel

        px, py = self.GetPosition()
        sx, sy = self.GetSize()

        self.pages[sel].Move((px+150, 0))
        self.pages[sel].SetSize((sx-150, sy))

        self.pages[sel].Show(True)

        self.oldpos = sel

    def OnSize(self, event):
        sel = self.listview.GetFocusedItem()

        px, py = self.GetPosition()
        sx, sy = self.GetSize()

        self.listview.SetSize((150, sy))

        self.pages[sel].Move((px+150, 0))
        self.pages[sel].SetSize((sx-150, sy))

    def SetSelection(self, selection):
        self.listview.Select(selection)
        self.listview.Focus(selection)

    def ShowPanel(self, selection=0):
        x = 0
        for label in self.labels:
            self.listview.InsertItem(x, label)
            x += 1
        self.listview.Select(selection)
        self.listview.Focus(selection)
        self.OnSelected(None)


#Cleaned up the sizing code, which was a tad ugly.
class PrefsPanel(wx.ScrolledWindow):
    def __init__(self, parent, id, name, NumberOfItems):
        wx.ScrolledWindow.__init__(self, parent, id)

        self.SetName(name)

        self.grandparent = parent.GetParent()

        self.drframe = self.grandparent.parent
        self.SetSize((600,500))
        self.EnableScrolling(True, True)
        self.SetScrollbars(10, NumberOfItems+3, 35, 62)
        self.btnResetPanel = wx.Button(self, self.grandparent.ID_RESET_PANEL, " Скинути панель ")

        #self.theSizer = wx.FlexGridSizer(NumberOfItems+2, 3, 5, 10)
        self.theSizer = wx.FlexGridSizer(0, 3, 5, 10)
        self.AddBuffer()
        self.Add(self.btnResetPanel, "Скинути налаштування цієї панелі:")

        self.Bind(wx.EVT_BUTTON,  self.grandparent.OnbtnResetPanel, id=self.grandparent.ID_RESET_PANEL)

        self.Show(False)

    def Add(self, wxitem, label=""):
        if label:
            self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, label), 1, wx.EXPAND)
            self.theSizer.Add(wxitem, 1, wx.SHAPED)
        else:
            self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
            self.theSizer.Add(wxitem, 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

    def AddBuffer(self):
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

    def AddLabel(self, label):
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, label), 1, wx.EXPAND)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

    def AddTwoItems(self, wxitem1, wxitem2):
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wxitem1, 1, wx.SHAPED)
        self.theSizer.Add(wxitem2, 1, wx.SHAPED)

    def SetPanelSizer(self):
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)


class BookmarksPanel(PrefsPanel):

    def __init__(self, parent, id, name):

        PrefsPanel.__init__(self, parent, id, name, 1)

        self.btnBStyle = wx.Button(self, self.grandparent.ID_BOOKMARKS_STYLE, " Змінити стилі закладок ")

        self.Add(self.btnBStyle)

        self.SetPanelSizer()

        self.Bind(wx.EVT_BUTTON, self.OnbtnBStyle, id=self.grandparent.ID_BOOKMARKS_STYLE)

    def OnbtnBStyle(self, event):
        d = drSimpleStyleDialog(self, -1, ("Стилі закладок"), self.grandparent.prefs.bookmarksstyle, self.grandparent.prefs.bookmarksstyle)

        d.ShowModal()
        if d.ClickedOk():
            self.grandparent.prefs.bookmarksstyle = d.GetStyleString()
        d.Destroy()

class DocumentPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 10)

        self.radusestyles = wx.RadioBox(self, -1, "Стилі:", wx.DefaultPosition, wx.DefaultSize, ["Don't Use Styles", "Use Styles", "Only Use \"Normal\", \"Caret Foreground\""], 1, wx.RA_SPECIFY_COLS)
        self.boxdefaultsyntaxhighlighting = wx.Choice(self, -1, wx.Point(225, 135), (-1, -1), ["Python", "C/C++", "HTML"])
        self.chkonlyusedefaultsyntaxhighlighting = wx.CheckBox(self, -1, "")
        self.btnStyle = wx.Button(self, self.grandparent.ID_FILE_STYLE, " Змінити стиль тексту ")
        self.btnApplyProperty = wx.Button(self, self.grandparent.ID_APPLY_PROPERTY, " Застосувати властивості тексту до всіх стилів ")
        self.raddocautoindent = wx.RadioBox(self, -1, "Автоматичні відступи:", wx.DefaultPosition, wx.DefaultSize, ["None", "Normal", "Context Sensitive"], 1, wx.RA_SPECIFY_COLS)
        self.chkdocshowlinenumbers = wx.CheckBox(self, -1, "")
        #self.chkdocremovetrailingwhitespace = wx.CheckBox(self, -1, "")
        self.chkdocautoreload = wx.CheckBox(self, -1, "")
        self.chkdocparenthesismatching = wx.CheckBox(self, -1, "")
        self.chkdocupdateindentation = wx.CheckBox(self, -1, "")
        self.chkdocusefileindentation = wx.CheckBox(self, -1, "")
        self.chkWhitespace = wx.CheckBox(self, -1, "")
        self.txtcaretwidth = wx.TextCtrl(self, self.grandparent.ID_DOC_CARET_WIDTH, str(self.grandparent.prefs.doccaretwidth), wx.Point(225, 215), (35, -1))
        self.chkhighlightcurrentline = wx.CheckBox(self, -1, "")
        self.chkignorectrlpageupdown = wx.CheckBox(self, -1, "")
        self.chkignoretextfunctionkeys = wx.CheckBox(self, -1, "")
        self.chkuseindentationguides = wx.CheckBox(self, -1, "")
        #Chris McDonough (I added txt prefix, update for local constants)
        self.txtdoclonglinecol = wx.TextCtrl(self, self.grandparent.ID_LONGLINE_COL, str(self.grandparent.prefs.doclonglinecol), wx.Point(225, 215), (35, -1))
        #/Chris McDonough

        self.chkscrollextrapage = wx.CheckBox(self, -1, "")
        self.raddoccommentmode = wx.RadioBox(self, -1, "Режим коментарів:", wx.DefaultPosition, wx.DefaultSize, ["Start of Line", "Start of Word"], 1, wx.RA_SPECIFY_COLS)

        self.Add(self.btnStyle)
        self.Add(self.btnApplyProperty)
        self.Add(self.radusestyles)
        self.Add(self.boxdefaultsyntaxhighlighting, "Виділення синтаксису:")
        self.Add(self.chkonlyusedefaultsyntaxhighlighting, "Виділяти тільки синтаксис за замовчуванням:")
        self.Add(self.chkdocshowlinenumbers, "Показувати номери рядків:")
        #self.Add(self.chkdocremovetrailingwhitespace, "Remove Trailing Whitespace:")
        self.Add(self.raddocautoindent)
        self.Add(self.chkdocautoreload, "Автоматичне перезавантаження:")
        self.Add(self.chkdocparenthesismatching, "Контроль парності дужок:")
        self.Add(self.chkdocupdateindentation, "Оновлювати відступи:")
        self.Add(self.chkdocusefileindentation, "Використання файлових відступів:")
        self.Add(self.chkWhitespace, "Пропуски видимі при запуску:")
        self.Add(self.chkuseindentationguides, "Використання ліній відступів:")
        self.Add(self.txtdoclonglinecol, "Позиція індикатора довгого рядка:")
        self.Add(self.chkscrollextrapage, "Прокручування сторінки:")
        self.Add(self.txtcaretwidth, "Товщина курсору:")
        self.Add(self.chkhighlightcurrentline, "Виділення поточного рядка:")
        self.Add(self.chkignorectrlpageupdown, "Ігнорувати Ctrl Pageup/down:")
        self.Add(self.chkignoretextfunctionkeys, "Ігнорувати клавіші Text Function:")
        self.Add(self.raddoccommentmode)

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON, self.OnbtnStyle, id=self.grandparent.ID_FILE_STYLE)
        self.Bind(wx.EVT_BUTTON, self.OnbtnApplyProperty, id=self.grandparent.ID_APPLY_PROPERTY)
        self.Bind(wx.EVT_TEXT, self.Ontxtcaretwidth, id=self.grandparent.ID_DOC_CARET_WIDTH)
        self.Bind(wx.EVT_TEXT, self.Ontxtdoclonglinecol, id=self.grandparent.ID_LONGLINE_COL)

    def reset(self):

        self.boxdefaultsyntaxhighlighting.SetSelection(self.grandparent.prefs.docdefaultsyntaxhighlighting)
        self.chkonlyusedefaultsyntaxhighlighting.SetValue(self.grandparent.prefs.doconlyusedefaultsyntaxhighlighting)
        self.radusestyles.SetSelection(self.grandparent.prefs.docusestyles)
        self.chkdocshowlinenumbers.SetValue(self.grandparent.prefs.docshowlinenumbers)
        #self.chkdocremovetrailingwhitespace.SetValue(self.grandparent.prefs.docremovetrailingwhitespace)
        self.raddocautoindent.SetSelection(self.grandparent.prefs.docautoindent)
        self.chkdocautoreload.SetValue(self.grandparent.prefs.docautoreload)
        self.chkdocparenthesismatching.SetValue(self.grandparent.prefs.docparenthesismatching)
        self.chkdocupdateindentation.SetValue(self.grandparent.prefs.docupdateindentation)
        self.chkdocusefileindentation.SetValue(self.grandparent.prefs.docusefileindentation)
        self.chkWhitespace.SetValue(self.grandparent.prefs.docwhitespaceisvisible)
        self.chkuseindentationguides.SetValue(self.grandparent.prefs.docuseindentationguides)
        self.chkscrollextrapage.SetValue(self.grandparent.prefs.docscrollextrapage)
        self.txtcaretwidth.SetValue(str(self.grandparent.prefs.doccaretwidth))
        self.chkhighlightcurrentline.SetValue(self.grandparent.prefs.dochighlightcurrentline)
        self.chkignorectrlpageupdown.SetValue(self.grandparent.prefs.docignorectrlpageupdown)
        self.chkignoretextfunctionkeys.SetValue(self.grandparent.prefs.docignoretextfunctionkeys)
        self.raddoccommentmode.SetSelection(self.grandparent.prefs.doccommentmode)

    def Ontxtdoclonglinecol(self, event):
        #Chris McDonough (Edited to allow for negative numbers)
        x = self.txtdoclonglinecol.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            if not x == "-":
                drScrolledMessageDialog.ShowMessage(self, ("Whatever you are trying to do... Stop it.\nIt won't work.  Actual Numbers only please.\nDrPython will reset to the value last loaded."), "Value Error")
                self.txtdoclonglinecol.SetValue(str(self.grandparent.prefs.doclonglinecol))
                return
            y = 0
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txtdoclonglinecol.SetValue(str(self.grandparent.prefs.doclonglinecol))
            return
        if y > 1024:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

    def Ontxtcaretwidth(self, event):
        x = self.txtcaretwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txtcaretwidth.SetValue(str(self.grandparent.prefs.doccaretwidth))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txtcaretwidth.SetValue(str(self.grandparent.prefs.doccaretwidth))
            return
        if y > 256:
            drScrolledMessageDialog.ShowMessage(self, "DrPython does not recommend going this high.  You can of course...", "Hmmmm")

    def OnbtnStyle(self, event):
        d = drStyleDialog(self, -1, "Змінити стилі")
        d.ShowModal()
        if d.ClickedOk():
            self.grandparent.prefs.PythonStyleDictionary, self.grandparent.prefs.CPPStyleDictionary, self.grandparent.prefs.HTMLStyleDictionary = d.GetArrays()
        d.Destroy()

    def OnbtnApplyProperty(self, event):
        d = wx.SingleChoiceDialog(self, "Select the property you wish to apply to all styles:", "Apply Property To All Styles", ["Font", "Size", "Background", "Foreground"], wx.OK|wx.CANCEL)
        answer = d.ShowModal()
        s = d.GetStringSelection()
        d.Destroy()
        if answer == wx.ID_OK:
            self.SetPropertyForStyleArray(self.grandparent.prefs.PythonStyleDictionary, s)
            self.SetPropertyForStyleArray(self.grandparent.prefs.CPPStyleDictionary, s)
            self.SetPropertyForStyleArray(self.grandparent.prefs.HTMLStyleDictionary, s)

    def SetPropertyForStyleArray(self, targetArray, s):
        #Ignore default text for all, and line number text for bg/fg (first two items)
        x = 2
        if s == "Font":
            prop = "face"
            dummy = ",face:terminal"
            x = 1
        elif s == "Size":
            prop = "size"
            dummy = ",size:10"
            x = 1
        elif s == "Background":
            prop = "back"
            dummy = ",back:#FFFFFF"
        elif s == "Foreground":
            prop = "fore"
            dummy = ",fore:#000000"
        newstring = getStyleProperty(prop, targetArray[0])

        #ignore caret foreground, selection, folding style, long line column, current line
        #(last five items).

        l = len(targetArray) - 5

        while x < l:
            tstring = targetArray[x]
            try:
                tstring.index(prop)
            except:
                tstring = tstring + dummy

            targetArray[x] = setStyleProperty(prop, tstring, newstring)

            x = x + 1

class DocumentationPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 8)

        self.btnBrowse = wx.Button(self, self.grandparent.ID_DOCUMENTATION_BROWSE, " Огляд ")

        self.btnBrowseP = wx.Button(self, self.grandparent.ID_DOCUMENTATION_BROWSE_P, " Огляд ")
        self.btnBrowseW = wx.Button(self, self.grandparent.ID_DOCUMENTATION_BROWSE_W, " Огляд ")
        self.btnBrowseR = wx.Button(self, self.grandparent.ID_DOCUMENTATION_BROWSE_R, " Огляд ")

        self.txtbrowser = wx.TextCtrl(self, -1, "", wx.Point(225, 215), (250, -1))
        self.txtpython = wx.TextCtrl(self, -1, "", wx.Point(225, 215), (250, -1))
        self.txtwxwidgets = wx.TextCtrl(self, -1, "", wx.Point(225, 215), (250, -1))
        self.txtrehowto = wx.TextCtrl(self, -1, "", wx.Point(225, 215), (250, -1))

        self.AddLabel("Вебпереглядач:")
        self.AddTwoItems(self.txtbrowser, self.btnBrowse)
        self.AddLabel("Документація Python:")
        self.AddTwoItems(self.txtpython, self.btnBrowseP)
        self.AddLabel("Документація WxWidgets:")
        self.AddTwoItems(self.txtwxwidgets, self.btnBrowseW)
        self.AddLabel("Посібник по регулярних виразах:")
        self.AddTwoItems(self.txtrehowto, self.btnBrowseR)
        self.SetPanelSizer()

        self.reset()
        if self.grandparent.prefs.platform_is_windows:
            self.wildcard = "Program File (*.exe)|*.exe|All files (*)|*"
        else:
            self.wildcard = "All files (*)|*"

        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowse, id=self.grandparent.ID_DOCUMENTATION_BROWSE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowseDoc, id=self.grandparent.ID_DOCUMENTATION_BROWSE_P)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowseDoc, id=self.grandparent.ID_DOCUMENTATION_BROWSE_W)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowseDoc, id=self.grandparent.ID_DOCUMENTATION_BROWSE_R)

    def reset(self):
        self.txtbrowser.SetValue(self.grandparent.prefs.documentationbrowser)
        self.txtpython.SetValue(self.grandparent.prefs.documentationpythonlocation)
        self.txtwxwidgets.SetValue(self.grandparent.prefs.documentationwxwidgetslocation)
        self.txtrehowto.SetValue(self.grandparent.prefs.documentationrehowtolocation)

    def OnbtnBrowse(self, event):
        dlg = drFileDialog.FileDialog(self.grandparent.parent, "Оберіть вебпереглядач", self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.txtbrowser.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnbtnBrowseDoc(self, event):
        eid = event.GetId()

        result = ""

        dlg = drFileDialog.FileDialog(self.grandparent.parent, "Розміщення документації", self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            result = dlg.GetPath()
        dlg.Destroy()

        if result:
            if eid == self.grandparent.ID_DOCUMENTATION_BROWSE_P:
                self.txtpython.SetValue(result)
            elif eid == self.grandparent.ID_DOCUMENTATION_BROWSE_W:
                self.txtwxwidgets.SetValue(result)
            elif eid == self.grandparent.ID_DOCUMENTATION_BROWSE_R:
                self.txtrehowto.SetValue(result)

class DragAndDropPanel(PrefsPanel):

    def __init__(self, parent, id, name):

        PrefsPanel.__init__(self, parent, id, name, 2)

        self.raddraganddropmode = wx.RadioBox(self, -1, "Drag and Drop Mode:", wx.DefaultPosition, wx.DefaultSize, ["Drag: Files Only, Drop: Files and Text", "Drag: Files and Text, Drop: Files and Text", "Drag and Drop Files Only"], 1, wx.RA_SPECIFY_COLS)
        self.raddraganddroptextmode = wx.RadioBox(self, -1, "Drag and Drop Text Mode:", wx.DefaultPosition, wx.DefaultSize, ["Copy by Default, Cut with Control", "Cut by Default, Copy with Control"], 1, wx.RA_SPECIFY_COLS)

        self.Add(self.raddraganddropmode)
        self.Add(self.raddraganddroptextmode)

        self.SetPanelSizer()

        self.reset()

    def reset(self):
        self.raddraganddropmode.SetSelection(self.grandparent.prefs.draganddropmode)
        self.raddraganddroptextmode.SetSelection(self.grandparent.prefs.draganddroptextmode)

class DrScriptPanel(PrefsPanel):

    def __init__(self, parent, id, name):

        PrefsPanel.__init__(self, parent, id, name, 2)

        self.txtdefaultdirectory = wx.TextCtrl(self, -1, self.grandparent.prefs.drscriptsdirectory,  wx.Point(15, 325), (250, -1))
        self.DrScriptbtnBrowse = wx.Button(self, self.grandparent.ID_DRSCRIPT_BROWSE, " Огляд ")
        self.btnDStyle = wx.Button(self, self.grandparent.ID_DRSCRIPT_STYLE, " Змінити стилі скриптів ")
        self.chkloadexamples = wx.CheckBox(self, -1, "")

        self.Add(self.btnDStyle)
        self.AddLabel("Поточна тека скриптів DrScript:")
        self.AddTwoItems(self.txtdefaultdirectory, self.DrScriptbtnBrowse)
        self.Add(self.chkloadexamples, "Завантажити приклади скриптів:")

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON,  self.OnbtnDBrowse, id=self.grandparent.ID_DRSCRIPT_BROWSE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnDStyle, id=self.grandparent.ID_DRSCRIPT_STYLE)

    def reset(self):
        self.txtdefaultdirectory.SetValue(self.grandparent.prefs.drscriptsdirectory)
        self.chkloadexamples.SetValue(self.grandparent.prefs.drscriptloadexamples)

    def OnbtnDBrowse(self, event):
        d = wx.DirDialog(self, "Оберіть поточну теку для скриптів DrScript:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON|wx.MAXIMIZE_BOX)
        if d.ShowModal() == wx.ID_OK:
            self.txtdefaultdirectory.SetValue(d.GetPath())
        d.Destroy()

    def OnbtnDStyle(self, event):
        d = drSimpleStyleDialog(self, -1, ("Стилі скриптів DrScript"), self.grandparent.prefs.drscriptstyle, self.grandparent.prefs.drscriptstyle)

        d.ShowModal()
        if d.ClickedOk():
            self.grandparent.prefs.drscriptstyle = d.GetStyleString()
        d.Destroy()

class FileDialogPanel(PrefsPanel):

    def __init__(self, parent, id, name):

        PrefsPanel.__init__(self, parent, id, name, 2)

        self.chkusewxfiledialog = wx.CheckBox(self, -1, "")
        self.chkdefaultextension = wx.CheckBox(self, -1, "")
        self.btnwildcard = wx.Button(self, self.grandparent.ID_BTN_WILDCARD, " Узагальнення типів файлів ")
        self.btnlnkreplacetable = wx.Button(self, self.grandparent.ID_BTN_LNK_REPLACE_TABLE, " Таблиця заміщень ярликів Windows ")

        self.Add(self.chkdefaultextension, "Розширення за замовчуванням ('.py'):")
        self.Add(self.chkusewxfiledialog, "Використовувати діалоги wx.FileDialog:")
        self.Add(self.btnwildcard)
        self.Add(self.btnlnkreplacetable)

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON, self.OnEditWildcard, id=self.grandparent.ID_BTN_WILDCARD)
        self.Bind(wx.EVT_BUTTON, self.OnReplaceTable, id=self.grandparent.ID_BTN_LNK_REPLACE_TABLE)

    def reset(self):
        self.chkusewxfiledialog.SetValue(self.grandparent.prefs.usewxfiledialog)
        self.chkdefaultextension.SetValue(self.grandparent.prefs.defaultextension)

    def OnEditWildcard(self, event):
        import drFileDialogPrefs
        d = drFileDialogPrefs.drFilePrefsDialog(self)
        answer = d.ShowModal()
        newwc = d.GetWildcard()
        cwc = d.GetConstantWildcard()
        d.Destroy()

        if answer == wx.ID_OK:
            self.grandparent.prefs.wildcard = newwc
            self.grandparent.prefs.constantwildcard = cwc

    def OnReplaceTable(self, event):
        import drFileDialogPrefs
        d = drFileDialogPrefs.drReplaceTableDialog(self)
        answer = d.ShowModal()
        newrt = d.GetReplaceTable()
        d.Destroy()

        if answer == wx.ID_OK:
            self.grandparent.prefs.windowsshortcutreplacetable = newrt

class FileTypesPanel(PrefsPanel):

    def __init__(self, parent, id, name):

        PrefsPanel.__init__(self, parent, id, name, 7)

        self.ID_FILETYPE = 701
        self.ID_EXTENSIONS = 702
        self.ID_USETABS = 703
        self.ID_TABWIDTH = 704
        self.ID_FOLDING = 705
        self.ID_EOLMODE = 706
        self.ID_COMMENTSTRING = 707
        self.ID_WORDWRAP = 708
        self.ID_USEINTELLIBACKSPACE = 709
        self.ID_REMOVETRAILINGWHITESPACE = 710

        self.cboFileType = wx.ComboBox(self, self.ID_FILETYPE, choices=["Python", "C/C++", "HTML", "Text"])

        self.filetype = self.drframe.txtDocument.filetype

        self.txtExtensions = wx.TextCtrl(self, self.ID_EXTENSIONS, "", wx.Point(225, 215), (225, -1))

        self.chkdocusetabs = wx.CheckBox(self, self.ID_USETABS, "")
        self.chkdocuseintellibackspace = wx.CheckBox(self, self.ID_USEINTELLIBACKSPACE, "")
        self.chkdocremovetrailingwhitespace = wx.CheckBox(self, self.ID_REMOVETRAILINGWHITESPACE, "")
        self.chkdocwordwrap = wx.CheckBox(self, self.ID_WORDWRAP, "")
        self.chkfolding = wx.CheckBox(self, self.ID_FOLDING, "")
        self.txtdoccommentstring = wx.TextCtrl(self, self.ID_COMMENTSTRING, "", wx.Point(225, 215), (35, -1))
        self.txttabwidth = wx.TextCtrl(self, self.ID_TABWIDTH, "", wx.Point(225, 215), (35, -1))
        self.radFormat = wx.Choice(self, self.ID_EOLMODE, wx.Point(15, 80), wx.DefaultSize, [" Unix ('\\n')  "," DOS/Windows ('\\r\\n')  "," Mac ('\\r')  "])

        self.Add(self.cboFileType, "Тип файлу:")
        self.Add(self.txtExtensions, "Розширення:")
        self.Add(self.txtdoccommentstring, "Символ коментаря:")
        self.Add(self.txttabwidth, "Ширина відступів:")
        self.Add(self.chkdocusetabs, "Використовувати відступи:")
        self.Add(self.chkdocuseintellibackspace, "Використовувати Intelli Backspace:")
        self.Add(self.chkdocremovetrailingwhitespace, "Видаляти непотрібні пропуски при збереженні:")
        self.Add(self.chkfolding, "Розгортання:")
        self.Add(self.chkdocwordwrap, "Перенесення слів:")
        self.Add(self.radFormat, "Кінець рядка:")

        self.SetPanelSizer()

        self.Bind(wx.EVT_COMBOBOX, self.OnFileType, id=self.ID_FILETYPE)
        self.Bind(wx.EVT_TEXT, self.Ontxttabwidth, id=self.ID_TABWIDTH)
        self.Bind(wx.EVT_TEXT, self.OnExtensions, id=self.ID_EXTENSIONS)
        self.Bind(wx.EVT_TEXT, self.OnCommentString, id=self.ID_COMMENTSTRING)
        self.Bind(wx.EVT_CHECKBOX, self.OnUseTabs, id=self.ID_USETABS)
        self.Bind(wx.EVT_CHECKBOX, self.OnUseIntelliBackspace, id=self.ID_USEINTELLIBACKSPACE)
        self.Bind(wx.EVT_CHECKBOX, self.OnRemoveTrailingWhitespace, id=self.ID_REMOVETRAILINGWHITESPACE)
        self.Bind(wx.EVT_CHECKBOX, self.OnFolding, id=self.ID_FOLDING)
        self.Bind(wx.EVT_CHECKBOX, self.OnWordWrap, id=self.ID_WORDWRAP)
        self.Bind(wx.EVT_CHOICE, self.OnEolMode, id=self.ID_EOLMODE)

        self.cboFileType.SetSelection(self.filetype)

        self.reset()

    def reset(self):
        self.extensions = self.grandparent.prefs.extensions.copy()
        self.docusetabs = self.grandparent.prefs.docusetabs.copy()
        self.docuseintellibackspace = self.grandparent.prefs.docuseintellibackspace.copy()
        self.docremovetrailingwhitespace= self.grandparent.prefs.docremovetrailingwhitespace.copy()
        self.doctabwidth = self.grandparent.prefs.doctabwidth.copy()
        self.doceolmode = self.grandparent.prefs.doceolmode.copy()
        self.docfolding = self.grandparent.prefs.docfolding.copy()
        self.doccommentstring = self.grandparent.prefs.doccommentstring.copy()
        self.docwordwrap = self.grandparent.prefs.docwordwrap.copy()

        self.OnFileType(None)

    def OnCommentString(self, event):
        self.doccommentstring[self.filetype] = self.txtdoccommentstring.GetValue()

    def OnEolMode(self, event):
        self.doceolmode[self.filetype] = self.radFormat.GetSelection()

    def OnExtensions(self, event):
        self.extensions[self.filetype] = self.txtExtensions.GetValue()

    def OnFileType(self, event):
        self.filetype = self.cboFileType.GetSelection()

        self.txtExtensions.SetValue(self.extensions[self.filetype])
        self.chkdocusetabs.SetValue(self.docusetabs[self.filetype])
        self.chkdocuseintellibackspace.SetValue(self.docuseintellibackspace[self.filetype])
        self.chkdocremovetrailingwhitespace.SetValue(self.docremovetrailingwhitespace[self.filetype])
        self.txttabwidth.SetValue(str(self.doctabwidth[self.filetype]))
        self.radFormat.SetSelection(self.doceolmode[self.filetype])
        self.chkfolding.SetValue(self.docfolding[self.filetype])
        self.txtdoccommentstring.SetValue(self.doccommentstring[self.filetype])
        self.chkdocwordwrap.SetValue(self.docwordwrap[self.filetype])

    def OnFolding(self, event):
        self.docfolding[self.filetype] = int(self.chkfolding.GetValue())

    def Ontxttabwidth(self, event):
        x = self.txttabwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.doctabwidth[self.filetype]))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.doctabwidth[self.filetype]))
            return
        if y > 1024:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")
            return
        self.doctabwidth[self.filetype] = y

    def OnWordWrap(self, event):
        self.docwordwrap[self.filetype] = int(self.chkdocwordwrap.GetValue())


    def OnUseTabs(self, event):
        self.docusetabs[self.filetype] = int(self.chkdocusetabs.GetValue())

    def OnUseIntelliBackspace(self, event):
        self.docuseintellibackspace[self.filetype] = int(self.chkdocuseintellibackspace.GetValue())

    def OnRemoveTrailingWhitespace(self, event):
        self.docremovetrailingwhitespace[self.filetype] = int(self.chkdocremovetrailingwhitespace.GetValue())


class FindReplacePanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 8)

        self.chkregularexpression = wx.CheckBox(self, -1, "")
        self.chkmatchcase = wx.CheckBox(self, -1, "")
        self.chkfindbackwards = wx.CheckBox(self, -1, "")
        self.chkwholeword = wx.CheckBox(self, -1, "")
        self.chkinselection = wx.CheckBox(self, -1, "")
        self.chkfromcursor = wx.CheckBox(self, -1, "")
        self.chkpromptonreplace = wx.CheckBox(self, -1, "")
        self.chkfindreplaceautowrap = wx.CheckBox(self, -1, "")
        self.chkundercursor = wx.CheckBox(self, -1, "")

        self.Add(self.chkregularexpression, "Регулярний вираз:")
        self.Add(self.chkmatchcase, "Враховувати регістр:")
        self.Add(self.chkfindbackwards, "Пошук назад:")
        self.Add(self.chkwholeword, "Слово цілком:")
        self.Add(self.chkinselection, "У обраному:")
        self.Add(self.chkfromcursor, "Від курсору:")
        self.Add(self.chkpromptonreplace, "Запит на заміну:")
        self.Add(self.chkfindreplaceautowrap, "Автоперенесення:")
        self.Add(self.chkundercursor, "До курсору:")

        self.SetPanelSizer()

        self.reset()

    def reset(self):

        self.chkregularexpression.SetValue(self.grandparent.prefs.findreplaceregularexpression)
        self.chkmatchcase.SetValue(self.grandparent.prefs.findreplacematchcase)
        self.chkfindbackwards.SetValue(self.grandparent.prefs.findreplacefindbackwards)
        self.chkwholeword.SetValue(self.grandparent.prefs.findreplacewholeword)
        self.chkinselection.SetValue(self.grandparent.prefs.findreplaceinselection)
        self.chkfromcursor.SetValue(self.grandparent.prefs.findreplacefromcursor)
        self.chkpromptonreplace.SetValue(self.grandparent.prefs.findreplacepromptonreplace)
        self.chkfindreplaceautowrap.SetValue(self.grandparent.prefs.findreplaceautowrap)
        self.chkundercursor.SetValue(self.grandparent.prefs.findreplaceundercursor)

class GeneralPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 8)

        self.ideModes = ["Класичний", "ЄPython"]

        self.chkrememberwindowsizeandposition = wx.CheckBox(self, -1, "")
        self.chkrememberdialogsizesandpositions = wx.CheckBox(self, -1, "")
        self.chkrememberpanelsizes = wx.CheckBox(self, -1, "")
        self.chkshowsplash = wx.CheckBox(self, -1, "")
        self.cboIdeMode = wx.ComboBox(self, -1, choices=self.ideModes)
        self.chksaveonrun = wx.CheckBox(self, -1, "")
        self.chkchecksyntaxonsave = wx.CheckBox(self, -1, "")
        self.txtchecksyntaxextensions = wx.TextCtrl(self, -1, self.grandparent.prefs.checksyntaxextensions, size=(55, -1))
        self.chkpromptonsaveall = wx.CheckBox(self, -1, "")
        self.chkdoubleclicktoclosetab = wx.CheckBox(self, -1, "")
        self.boxiconsize = wx.Choice(self, self.grandparent.ID_ICON_SIZE, wx.Point(225, 135), (-1, -1), ["0", "16", "24"])
        self.txtRecentFiles = wx.TextCtrl(self, self.grandparent.ID_TXT_RECENT_FILES, str(self.grandparent.prefs.recentfileslimit), wx.Point(225, 175), (35, -1))
        self.chkcheckindentation = wx.CheckBox(self, -1, "")
        self.txtpythonargs = wx.TextCtrl(self, -1, self.grandparent.prefs.pythonargs, wx.Point(225, 255), (55, -1))
        self.chkenablefeedback = wx.CheckBox(self, -1, "")
        self.chkdebugmodus = wx.CheckBox(self, -1, "")
        self.chkalwayspromptonexit = wx.CheckBox(self, -1, "")
        self.chkbackupfileonsave = wx.CheckBox(self, -1, "")
        self.chkCheckFormat = wx.CheckBox(self, -1, "")
        self.chkvieweol = wx.CheckBox(self, -1, "")


        self.txtdefaultuserprefsdirectory = wx.TextCtrl(self, -1, self.grandparent.GetParent().preferencesdirectory,  wx.Point(15, 325), (250, -1))
        self.btnBrowseUserPrefsDir = wx.Button(self, self.grandparent.ID_FILE_BROWSE_USER_PREFS_DIR, " Огляд ")
        self.txtdefaultcurdirdirectory = wx.TextCtrl(self, -1, self.grandparent.prefs.defaultdirectory,  wx.Point(15, 375), (250, -1))
        self.btnBrowseCurDir = wx.Button(self, self.grandparent.ID_FILE_BROWSE_CUR_DIR, " Огляд ")

        self.btnExportSetup = wx.Button(self, self.grandparent.ID_EXPORT_PREFS, " Експорт налаштувань ")
        self.btnImportSetup = wx.Button(self, self.grandparent.ID_IMPORT_PREFS, " Імпорт налаштувань ")

        self.Add(self.chkrememberwindowsizeandposition, "Пам'ятати розміщення та розмір вікна:")
        self.Add(self.chkrememberdialogsizesandpositions, "Пам'ятати розміщення та розмір діалогів:")
        self.Add(self.chkrememberpanelsizes, "Пам'ятати розміри панелей:")
        self.Add(self.chkshowsplash, "Показувати заставку під час запуску:")
        self.Add(self.cboIdeMode, "Вигляд інтерфейсу середовища")
        self.Add(self.chksaveonrun, "Зберегти при запуску:")
        self.Add(self.chkchecksyntaxonsave, "Перевірити синтаксис при збереженні:")
        self.Add(self.txtchecksyntaxextensions, "Перевірка синтаксису тільки для розширень:")
        self.Add(self.chkpromptonsaveall, "Запит на збереження всіх файлів:")
        self.Add(self.chkdoubleclicktoclosetab, "Подвійний клацок щоб закрити вкладку:")
        self.Add(self.txtRecentFiles, "Максимальна кількість файлів в Історії:")
        self.Add(self.chkvieweol, "Показувати кінці рядків з пропусками:")
        self.Add(self.chkCheckFormat, "Перевіряти формат закінчення рядків при відкритті:")
        self.Add(self.chkcheckindentation, "Перевіряти тип відступів при відритті:")
        self.Add(self.txtpythonargs, "Аргументи для Python (такі як \"-i\"):")
        self.Add(self.boxiconsize, "Розмір значків панелі:")
        self.AddBuffer()
        self.AddLabel("Поточна тека з налаштуваннями:")
        self.AddTwoItems(self.txtdefaultuserprefsdirectory, self.btnBrowseUserPrefsDir)
        self.AddBuffer()
        self.AddLabel("Поточна робоча тека:")
        self.AddTwoItems(self.txtdefaultcurdirdirectory, self.btnBrowseCurDir)
        self.AddBuffer()
        self.Add(self.chkenablefeedback, "Увімкнути зворотні сповіщення:")
        self.Add(self.chkdebugmodus, "Режим налагодження:")
        self.Add(self.chkalwayspromptonexit, "Завжди підтверджувати вихід:")
        self.Add(self.chkbackupfileonsave, "Резервна копія при збереженні:")
        self.Add(self.btnExportSetup)
        self.Add(self.btnImportSetup)

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowseUserPrefsDir, id=self.grandparent.ID_FILE_BROWSE_USER_PREFS_DIR)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowseCurDir, id=self.grandparent.ID_FILE_BROWSE_CUR_DIR)
        self.Bind(wx.EVT_TEXT,  self.OntxtRecentFiles, id=self.grandparent.ID_TXT_RECENT_FILES)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnExportPrefs, id=self.grandparent.ID_EXPORT_PREFS)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnImportPrefs, id=self.grandparent.ID_IMPORT_PREFS)

    def reset(self):
        self.txtdefaultuserprefsdirectory.SetValue(self.grandparent.GetParent().preferencesdirectory)
        self.txtdefaultcurdirdirectory.SetValue(self.grandparent.prefs.defaultdirectory)
        self.chkrememberwindowsizeandposition.SetValue(self.grandparent.prefs.rememberwindowsizeandposition)
        self.chkrememberdialogsizesandpositions.SetValue(self.grandparent.prefs.rememberdialogsizesandpositions)
        self.chkrememberpanelsizes.SetValue(self.grandparent.prefs.rememberpanelsizes)
        self.chkshowsplash.SetValue(self.grandparent.prefs.showsplash)
        self.chksaveonrun.SetValue(self.grandparent.prefs.saveonrun)
        self.chkchecksyntaxonsave.SetValue(self.grandparent.prefs.checksyntaxonsave)
        self.txtchecksyntaxextensions.SetValue(self.grandparent.prefs.checksyntaxextensions)
        self.chkpromptonsaveall.SetValue(self.grandparent.prefs.promptonsaveall)
        self.chkdoubleclicktoclosetab.SetValue(self.grandparent.prefs.doubleclicktoclosetab)
        self.txtRecentFiles.SetValue(str(self.grandparent.prefs.recentfileslimit))

        if self.grandparent.prefs.defaultidemode not in self.ideModes:
            self.ideModes.append(self.grandparent.prefs.defaultidemode)
            self.cboIdeMode.Append(self.grandparent.prefs.defaultidemode)
        self.cboIdeMode.SetSelection(self.ideModes.index(self.grandparent.prefs.defaultidemode))

        self.chkcheckindentation.SetValue(self.grandparent.prefs.checkindentation)

        if self.grandparent.prefs.iconsize == 24:
            self.boxiconsize.SetSelection(2)
        elif self.grandparent.prefs.iconsize == 16:
            self.boxiconsize.SetSelection(1)
        else:
            self.boxiconsize.SetSelection(0)

        self.txtpythonargs.SetValue(self.grandparent.prefs.pythonargs)
        self.chkenablefeedback.SetValue(self.grandparent.prefs.enablefeedback)
        self.chkdebugmodus.SetValue(self.grandparent.prefs.debugmodus)
        self.chkalwayspromptonexit.SetValue(self.grandparent.prefs.alwayspromptonexit)
        self.chkbackupfileonsave.SetValue(self.grandparent.prefs.backupfileonsave)

        self.chkvieweol.SetValue(self.grandparent.prefs.vieweol)

        self.chkCheckFormat.SetValue(self.grandparent.prefs.checkeol)

    def OnbtnBrowseUserPrefsDir(self, event):
        #bug fix by Antonio, 06.03.2007: (removed |wx.DD_NEW_DIR_BUTTON because the style wx.DD_DEFAULT_STYLE already includes  wx.DD_NEW_DIR_BUTTON)
        d = wx.DirDialog(self, "Оберіть теку для збереження налаштувань:", style=wx.DD_DEFAULT_STYLE)
        if d.ShowModal() == wx.ID_OK:
            self.txtdefaultuserprefsdirectory.SetValue(d.GetPath())
        d.Destroy()

    def OnbtnBrowseCurDir(self, event):
        d = wx.DirDialog(self, "Оберіть робочу теку:", style=wx.DD_DEFAULT_STYLE)
        if d.ShowModal() == wx.ID_OK:
            self.txtdefaultcurdirdirectory.SetValue(d.GetPath())
        d.Destroy()


    def OnbtnExportPrefs(self, event):
        import drZip
        import zipfile
        dlg = drFileDialog.FileDialog(self.drframe, "Export Preferences, Plugins, and DrScripts To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace('\\', '/')
            if not filename.endswith(".zip"): #AB: bug of drFileDialog
                filename=filename.split('.')[0] + ".zip"
            zf = zipfile.ZipFile(filename, 'w')
            drZip.AddDirectoryToZipFile(self.drframe.preferencesdirectory, "", zf)
            zf.close()
        dlg.Destroy()

    def OnbtnImportPrefs(self, event):
        import drZip
        if self.drframe.Ask("This will permanently overwrite all of your preferences, plugins, and drscript file.\n\nProceed?", "Warning"):
            dlg = drFileDialog.FileDialog(self.drframe, "Import Preferences, Plugins, and DrScripts From", "Zip File (*.zip)|*.zip")
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace('\\', '/')
                drZip.ImportPreferencesFrom(self.drframe.preferencesdirectory, filename)
                self.drframe.ShowMessage("Successfully imported preferences, plugins, and drscripts.", "Import Success")

            dlg.Destroy()

    def OntxtRecentFiles(self, event):
        x = self.txtRecentFiles.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txtRecentFiles.SetValue(str(self.grandparent.prefs.recentfileslimit))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txtRecentFiles.SetValue(str(self.grandparent.prefs.recentfileslimit))
            return
        if y > 25:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

class PluginsPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 1)

        self.txtdefaultdirectory = wx.TextCtrl(self, -1, self.grandparent.prefs.pluginsdirectory,  wx.Point(15, 325), (250, -1))
        self.PluginsbtnBrowse = wx.Button(self, self.grandparent.ID_PLUGINS_BROWSE, " Огляд ")

        self.AddLabel("Поточна тека:")
        self.AddTwoItems(self.txtdefaultdirectory, self.PluginsbtnBrowse)

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON,  self.OnbtnPBrowse, id=self.grandparent.ID_PLUGINS_BROWSE)

    def reset(self):
        self.txtdefaultdirectory.SetValue(self.grandparent.prefs.pluginsdirectory)

    def OnbtnPBrowse(self, event):
        d = wx.DirDialog(self, "Select Default Directory For Plugins:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON|wx.MAXIMIZE_BOX)
        if d.ShowModal() == wx.ID_OK:
            self.txtdefaultdirectory.SetValue(d.GetPath())
        d.Destroy()

class PrintPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 3)

        self.chkdoclinenumbers = wx.CheckBox(self, -1, "")
        self.chkpromptlinenumbers = wx.CheckBox(self, -1, "")
        self.txttabwidth = wx.TextCtrl(self, self.grandparent.ID_PRINT_TAB_WIDTH, str(self.grandparent.prefs.printtabwidth), wx.Point(225, 215), (35, -1))

        self.Add(self.chkdoclinenumbers, "Кількість рядків редактора:")
        self.Add(self.chkpromptlinenumbers, "Кількість рядків консолі:")
        self.Add(self.txttabwidth, "Ширина відступів:")

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_TEXT,  self.Ontxttabwidth, id=self.grandparent.ID_PRINT_TAB_WIDTH)

    def reset(self):
        self.chkdoclinenumbers.SetValue(self.grandparent.prefs.printdoclinenumbers)
        self.chkpromptlinenumbers.SetValue(self.grandparent.prefs.printpromptlinenumbers)
        self.txttabwidth.SetValue(str(self.grandparent.prefs.printtabwidth))

    def Ontxttabwidth(self, event):
        x = self.txttabwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.printtabwidth))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.printtabwidth))
            return
        if y > 32:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

class PromptPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 8)

        self.ID_TABWIDTH = 750

        self.radusestyles = wx.RadioBox(self, -1, "Стилі:", wx.DefaultPosition, wx.DefaultSize, ["Don't Use Styles", "Use Styles", "Only Use \"Normal\", \"Caret Foreground\""], 1, wx.RA_SPECIFY_COLS)
        self.btnStyle = wx.Button(self, self.grandparent.ID_PROMPT_STYLE, " Змінити текстові стилі ")
        self.btnApplyProperty = wx.Button(self, self.grandparent.ID_PROMPT_APPLY_PROPERTY, " Застосувати властивості тексту до всіх стилів ")
        self.txtmarginwidth = wx.TextCtrl(self, self.grandparent.ID_PROMPT_MARGIN_WIDTH, str(self.grandparent.prefs.promptmarginwidth), wx.Point(225, 215), (35, -1))
        self.chkVisible = wx.CheckBox(self, -1, "")
        self.chkpromptusetabs = wx.CheckBox(self, -1, "")
        self.chkwordwrap = wx.CheckBox(self, -1, "")
        self.txtcaretwidth = wx.TextCtrl(self, self.grandparent.ID_PROMPT_CARET_WIDTH, str(self.grandparent.prefs.promptcaretwidth), wx.Point(225, 215), (35, -1))
        self.chkWhitespace = wx.CheckBox(self, -1, "")
        self.chkscrollextrapage = wx.CheckBox(self, -1, "")
        self.sldrSize =  wx.Slider(self, -1, self.grandparent.prefs.promptsize, 25, 100, wx.Point(150, 55), (75, -1), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        #self.sldrSize.SetTickFreq(25, 1)
        self.txttabwidth = wx.TextCtrl(self, self.ID_TABWIDTH, "", wx.Point(225, 215), (35, -1))
        self.radFormat = wx.Choice(self, -1, wx.Point(15, 80), wx.DefaultSize, [" Unix ('\\n')  "," DOS/Windows ('\\r\\n')  "," Mac ('\\r')  "])
        self.txtStartupScript = wx.TextCtrl(self, -1, self.grandparent.prefs.promptstartupscript, wx.Point(225, 215), (250, 150), wx.TE_MULTILINE)

        self.Add(self.btnStyle)
        self.Add(self.btnApplyProperty)
        self.Add(self.radusestyles)
        self.Add(self.txtmarginwidth, "Ширина поля номерів рядків:")
        self.Add(self.chkVisible, "Зазвичай видимі:")
        self.Add(self.txttabwidth, "Ширина відступів:")
        self.Add(self.chkpromptusetabs, "Використовувати відступи:")
        self.Add(self.radFormat, "Переведення ряда:")
        self.Add(self.chkwordwrap, "Перенесення слів:")
        self.Add(self.txtcaretwidth, "Товщина курсору:")
        self.Add(self.chkWhitespace, "Пропуски видимі при запуску:")
        self.Add(self.chkscrollextrapage, "Прокручування сторінки:")
        self.Add(self.sldrSize, "Вериткальний розмір:")
        self.AddLabel("Початковий скрипт:")
        self.Add(self.txtStartupScript)

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON, self.OnbtnStyle, id=self.grandparent.ID_PROMPT_STYLE)
        self.Bind(wx.EVT_BUTTON, self.OnbtnApplyProperty, id=self.grandparent.ID_PROMPT_APPLY_PROPERTY)
        self.Bind(wx.EVT_TEXT,  self.Ontxtmarginwidth, id=self.grandparent.ID_PROMPT_MARGIN_WIDTH)
        self.Bind(wx.EVT_TEXT, self.Ontxtcaretwidth, id=self.grandparent.ID_PROMPT_CARET_WIDTH)

        self.Bind(wx.EVT_TEXT, self.Ontxttabwidth, id=self.ID_TABWIDTH)

    def reset(self):

        self.txttabwidth.SetValue(str(self.grandparent.prefs.prompttabwidth))
        self.radFormat.SetSelection(self.grandparent.prefs.prompteolmode)
        self.radusestyles.SetSelection(self.grandparent.prefs.promptusestyles)
        self.txtmarginwidth.SetValue(str(self.grandparent.prefs.promptmarginwidth))
        self.chkVisible.SetValue(self.grandparent.prefs.promptisvisible)
        self.chkpromptusetabs.SetValue(self.grandparent.prefs.promptusetabs)
        self.chkwordwrap.SetValue(self.grandparent.prefs.promptwordwrap)
        self.txtcaretwidth.SetValue(str(self.grandparent.prefs.promptcaretwidth))
        self.chkWhitespace.SetValue(self.grandparent.prefs.promptwhitespaceisvisible)
        self.sldrSize.SetValue(self.grandparent.prefs.promptsize)
        self.chkscrollextrapage.SetValue(self.grandparent.prefs.promptscrollextrapage)
        self.txtStartupScript.SetValue(self.grandparent.prefs.promptstartupscript)

    def OnbtnStyle(self, event):
        d = drStyleDialog(self, -1, "Зміна стилів консолі", True)
        d.ShowModal()
        if d.ClickedOk():
            self.grandparent.prefs.txtPromptStyleDictionary = d.GetArrays()
        d.Destroy()

    def OnbtnApplyProperty(self, event):
        d = wx.SingleChoiceDialog(self, "Select the property you wish to apply to all styles:", "Apply Property To All Styles", ["Font", "Size", "Background", "Foreground"], wx.OK|wx.CANCEL)
        answer = d.ShowModal()
        s = d.GetStringSelection()
        d.Destroy()
        if answer == wx.ID_OK:
            if s == "Font":
                prop = "face"
                dummy = ",face:terminal"
            elif s == "Size":
                prop = "size"
                dummy = ",size:10"
            elif s == "Background":
                prop = "back"
                dummy = ",back:#000000"
            elif s == "Foreground":
                prop = "fore"
                dummy = ",fore:#FFFFFF"
            l = len(self.grandparent.prefs.txtPromptStyleDictionary) - 3
            #ignore caret foreground, selections
            x = 2
            #Ignore default text, and line number text (0, and 1)
            bstring = getStyleProperty(prop, self.grandparent.prefs.txtPromptStyleDictionary[0])
            while x < l:
                tstring = self.grandparent.prefs.txtPromptStyleDictionary[x]
                #self.grandparent.prefs.txtPromptStyleDictionary.pop(x)
                try:
                    tstring.index(prop)
                except:
                    tstring = tstring + dummy
                self.grandparent.prefs.txtPromptStyleDictionary[x] = setStyleProperty(prop, tstring, bstring)
                x = x + 1

    def Ontxtcaretwidth(self, event):
        x = self.txtcaretwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txtcaretwidth.SetValue(str(self.grandparent.prefs.promptcaretwidth))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txtcaretwidth.SetValue(str(self.grandparent.prefs.promptcaretwidth))
            return
        if y > 256:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

    def Ontxtmarginwidth(self, event):
        x = self.txtmarginwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txtmarginwidth.SetValue(str(self.grandparent.prefs.promptmarginwidth))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txtmarginwidth.SetValue(str(self.grandparent.prefs.promptmarginwidth))
            return
        if y > 1024:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

    def Ontxttabwidth(self, event):
        x = self.txttabwidth.GetValue()
        if not x:
            return
        try:
            y = int(x)
        except ValueError:
            drScrolledMessageDialog.ShowMessage(self, ("Що б ви не намагалися зробити - зупиніть це.\nЦе не спрацює - мають бути тільки додатні числа.\nDrPython скине значення до останнього завантаженого."), "Помилка значення")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.prompttabwidth))
            return
        except TypeError:
            drScrolledMessageDialog.ShowMessage(self, ("\"" + y + "\" не є цілим числом (таким як 2, 4, 568)\nDrPython скине значення до останнього завантаженого."), "Помилка типу")
            self.txttabwidth.SetValue(str(self.grandparent.prefs.prompttabwidth))
            return
        if y > 1024:
            drScrolledMessageDialog.ShowMessage(self, ("DrPython не рекомендує підніматися так високо. Ви, звичайно, можете..."), "Хмммм...")

class SidePanelPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 4)

        self.sldrSizeLeft =  wx.Slider(self, -1, self.grandparent.prefs.sidepanelleftsize, 15, 100, wx.Point(150, 55), (75, -1), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        #self.sldrSizeLeft.SetTickFreq(25, 1)

        self.sldrSizeRight =  wx.Slider(self, -1, self.grandparent.prefs.sidepanelrightsize, 15, 100, wx.Point(150, 55), (75, -1), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        #self.sldrSizeRight.SetTickFreq(25, 1)

        self.sldrSizeTop =  wx.Slider(self, -1, self.grandparent.prefs.sidepaneltopsize, 15, 100, wx.Point(150, 55), (75, -1), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        self.sldrSizeTop.SetTick(15)
        #self.sldrSizeTop.SetTickFreq(25, 1)


        self.Add(self.sldrSizeLeft, "Розмір лівої панелі:")
        self.Add(self.sldrSizeRight, "Розмір правої панелі:")
        self.Add(self.sldrSizeTop, "Розмір верхньої панелі:")

        self.SetPanelSizer()

        self.reset()

    def reset(self):

        self.sldrSizeLeft.SetValue(self.grandparent.prefs.sidepanelleftsize)
        self.sldrSizeRight.SetValue(self.grandparent.prefs.sidepanelrightsize)
        self.sldrSizeTop.SetValue(self.grandparent.prefs.sidepaneltopsize)

class SourceBrowserPanel(PrefsPanel):

    def __init__(self, parent, id, name):
        PrefsPanel.__init__(self, parent, id, name, 4)

        self.btnCStyle = wx.Button(self, self.grandparent.ID_CLASS_BROWSER_STYLE, " Змінити стилі Навігатора структури ")
        self.positionchooser = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, ["Left", "Right", "Top"], 3, wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        self.sldrSize =  wx.Slider(self, -1, self.grandparent.prefs.sourcebrowsersize, 1, 100, wx.Point(150, 55), (75, -1), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        #self.sldrSize.SetTickFreq(1, 1)
        self.chkIsVisible = wx.CheckBox(self, -1, "")
        self.chkcloseonactivate = wx.CheckBox(self, -1, "")
        self.chkissorted = wx.CheckBox(self, -1, "")
        self.chkautorefreshonsave = wx.CheckBox(self, -1, "")
        self.chkautorefresh = wx.CheckBox(self, -1, "")
        self.chkuseimages = wx.CheckBox(self, -1, "")

        self.Add(self.btnCStyle)
        self.AddLabel("")
        self.AddLabel("Розміщення панелі:")
        self.Add(self.positionchooser)
        self.Add(self.sldrSize, "Розмір панелі:")
        self.Add(self.chkIsVisible, "Зазвичай видима:")
        self.Add(self.chkcloseonactivate, "Закрити при активації:")
        self.Add(self.chkissorted, "Впорядковано (за абеткою):")
        self.Add(self.chkautorefreshonsave, "Автоновлення при збереженні:")
        self.Add(self.chkautorefresh, "Автоновлення:")
        self.Add(self.chkuseimages, "З зображеннями:")

        self.SetPanelSizer()

        self.reset()

        self.Bind(wx.EVT_BUTTON, self.OnbtnCStyle, id=self.grandparent.ID_CLASS_BROWSER_STYLE)

    def reset(self):
        self.positionchooser.SetSelection(self.grandparent.prefs.sourcebrowserpanel)
        self.sldrSize.SetValue(self.grandparent.prefs.sourcebrowsersize)
        self.chkIsVisible.SetValue(self.grandparent.prefs.sourcebrowserisvisible)
        self.chkcloseonactivate.SetValue(self.grandparent.prefs.sourcebrowsercloseonactivate)
        self.chkissorted.SetValue(self.grandparent.prefs.sourcebrowserissorted)
        self.chkautorefreshonsave.SetValue(self.grandparent.prefs.sourcebrowserautorefreshonsave)
        self.chkautorefresh.SetValue(self.grandparent.prefs.sourcebrowserautorefresh)
        self.chkuseimages.SetValue(self.grandparent.prefs.sourcebrowseruseimages)

    def OnbtnCStyle(self, event):
        d = drSimpleStyleDialog(self, -1, ("Стиль Навігатора структури"), self.grandparent.prefs.sourcebrowserstyle, self.grandparent.prefs.sourcebrowserstyle)

        d.ShowModal()
        if d.ClickedOk():
            self.grandparent.prefs.sourcebrowserstyle = d.GetStyleString()

        d.Destroy()

class drPrefsDialog(wx.Dialog):

    def __init__(self, parent, id, title):

        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (660, 680), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

        self.parent = parent

        self.ID_PAGES = 100
        self.ID_CLOSE = 101
        self.ID_RESET = 102
        self.ID_UPDATE = 103
        self.ID_SAVE = 104
        self.ID_HELP = 105
        self.ID_FILE_BROWSE_USER_PREFS_DIR = 109
        self.ID_TEXT_TYPE = 110
        self.ID_FILE_STYLE = 111
        self.ID_APPLY_PROPERTY = 112
        self.ID_DOC_MARGIN_WIDTH = 113
        self.ID_FILE_BROWSE_CUR_DIR = 114
        self.ID_DOC_CARET_WIDTH = 1235
        self.ID_PROMPT_CARET_WIDTH = 1237
        self.ID_LONGLINE_COL = 116
        self.ID_ICON_SIZE = 350
        self.ID_PROMPT_STYLE = 1140
        self.ID_PROMPT_MARGIN_WIDTH = 115
        self.ID_PROMPT_TEXT_TYPE = 117
        self.ID_PROMPT_APPLY_PROPERTY = 118
        self.ID_CLASS_BROWSER_STYLE = 201
        self.ID_BOOKMARKS_STYLE = 202
        self.ID_DRSCRIPT_STYLE = 203
        self.ID_DRSCRIPT_BROWSE = 211
        self.ID_PLUGINS_BROWSE = 212
        self.ID_PRINT_TAB_WIDTH = 251
        self.ID_DOCUMENTATION_BROWSE = 231
        self.ID_DOCUMENTATION_BROWSE_P = 232
        self.ID_DOCUMENTATION_BROWSE_W = 233
        self.ID_DOCUMENTATION_BROWSE_R = 234
        self.ID_TXT_RECENT_FILES = 301
        self.ID_TXT_TAB_WIDTH = 302
        self.ID_USE_TABS = 303
        self.ID_RESET_PANEL = 405
        self.ID_LB_PREFS = 505

        self.ID_EXPORT_PREFS = 501
        self.ID_IMPORT_PREFS = 502

        self.ID_BTN_WILDCARD = 510
        self.ID_BTN_LNK_REPLACE_TABLE = 511

        self.prefs = drPreferences(self.parent, parent.PLATFORM_IS_WIN, parent.programdirectory)
        self.prefs.Copy(parent.prefs)
        self.oldprefs = drPreferences(self.parent, parent.PLATFORM_IS_WIN, parent.programdirectory)
        self.oldprefs.Copy(parent.prefs)

        self.lbPrefs = drPrefsBook(self, self.ID_LB_PREFS, (640, 680))

        self.pnlGeneral = GeneralPanel(self.lbPrefs, -1, "Загальне")
        self.pnlBookmarks = BookmarksPanel(self.lbPrefs, -1, "Закладки")
        self.pnlDocument = DocumentPanel(self.lbPrefs, -1, "Редактор")
        self.pnlDocumentation = DocumentationPanel(self.lbPrefs, -1, "Документація")
        self.pnlDragAndDrop = DragAndDropPanel(self.lbPrefs, -1, "Перетягування")
        self.pnlDrScript = DrScriptPanel(self.lbPrefs, -1, "Скрипти")
        self.pnlFileDialog = FileDialogPanel(self.lbPrefs, -1, "Діалоги")
        self.pnlFileTypes = FileTypesPanel(self.lbPrefs, -1, "Типи файлів")
        self.pnlFindReplace = FindReplacePanel(self.lbPrefs, -1, "Пошук/заміна")
        self.pnlPlugins = PluginsPanel(self.lbPrefs, -1, "Доповнення")
        self.pnlPrint = PrintPanel(self.lbPrefs, -1, "Друк")
        self.pnlPrompt = PromptPanel(self.lbPrefs, -1, "Консоль")
        self.pnlSidePanels = SidePanelPanel(self.lbPrefs, -1, "Панелі")
        self.pnlSourceBrowser = SourceBrowserPanel(self.lbPrefs, -1, "Навігатор")

        self.lbPrefs.AddPage(self.pnlGeneral, "Загальне")
        self.lbPrefs.AddPage(self.pnlBookmarks, "Закладки")
        self.lbPrefs.AddPage(self.pnlDocument, "Редактор")
        self.lbPrefs.AddPage(self.pnlDocumentation, "Документація")
        self.lbPrefs.AddPage(self.pnlDragAndDrop, "Перетягування")
        self.lbPrefs.AddPage(self.pnlDrScript, "Скрипти")
        self.lbPrefs.AddPage(self.pnlFileDialog, "Діалоги")
        self.lbPrefs.AddPage(self.pnlFileTypes, "Типи файлів")
        self.lbPrefs.AddPage(self.pnlFindReplace, "Пошук/заміна")
        self.lbPrefs.AddPage(self.pnlPlugins, "Доповнення")
        self.lbPrefs.AddPage(self.pnlPrint, "Друк")
        self.lbPrefs.AddPage(self.pnlPrompt, "Консоль")
        self.lbPrefs.AddPage(self.pnlSidePanels, "Панелі")
        self.lbPrefs.AddPage(self.pnlSourceBrowser, "Навігатор")


        self.lbPrefs.ShowPanel(parent.prefdialogposition)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnClose = wx.Button(self, self.ID_CLOSE, "   Закрити   ")

        self.btnClose.SetDefault()

        self.btnHelp = wx.Button(self, self.ID_HELP, "   Допомога   ")

        self.btnReset = wx.Button(self, self.ID_RESET, "   Скинути все   ")

        self.btnUpdate = wx.Button(self, self.ID_UPDATE, "   Оновити   ")

        self.btnSave = wx.Button(self, self.ID_SAVE, "   Зберегти   ")

        self.buttonSizer.Add(self.btnClose, 0, wx.ALL|wx.EXPAND, 4)
        self.buttonSizer.Add(self.btnHelp, 0, wx.ALL|wx.EXPAND, 4)
        self.buttonSizer.Add(self.btnReset, 0, wx.ALL|wx.EXPAND, 4)
        self.buttonSizer.Add(self.btnUpdate, 0, wx.ALL|wx.EXPAND, 4)
        self.buttonSizer.Add(self.btnSave, 0, wx.ALL|wx.EXPAND, 4)

        #self.theSizer.Add(self.lbPrefs, 1, wx.ALL|wx.EXPAND, 4)
        #if border is used, the right scrollbar doesn't show entirely (!)
        self.theSizer.Add(self.lbPrefs, 1, wx.EXPAND)


        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.buttonSizer, 0, wx.SHAPED | wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id=self.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnHelp, id=self.ID_HELP)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnReset, id=self.ID_RESET)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnUpdate, id=self.ID_UPDATE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnSave, id=self.ID_SAVE)

        parent.LoadDialogSizeAndPosition(self, "preferencesdialog.sizeandposition.dat")
        if parent.PLATFORM_IS_GTK: #does not get initially the focus (bug tracker #1903778, "Open Imported Module: focus problem", 29.02.2008: from Jon White, thanks.
            self.SetFocus()

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, "preferencesdialog.sizeandposition.dat")
        if event is not None:
            event.Skip()

    def OnbtnClose(self, event):
        self.OnCloseW(None)
        self.EndModal(0)

    def OnbtnHelp(self, event):
        self.parent.ViewURLInBrowser(os.path.join(self.parent.programdirectory, "documentation/preferences.html"))

    def OnbtnReset(self, event):
        answer = wx.MessageBox("Всі налаштування будуть скинуті до налаштувань програми за замовчуванням.\n(Вам буде потрібно клацнути Оновити/Зберегти)\nВи дійсно бажаєте зробити це?", "Скидання налаштувань", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            self.prefs.reset()
            self.pnlSourceBrowser.reset()
            self.pnlDocument.reset()
            self.pnlDocumentation.reset()
            self.pnlDrScript.reset()
            self.pnlFindReplace.reset()
            self.pnlFileTypes.reset()
            self.pnlGeneral.reset()
            self.pnlPlugins.reset()
            self.pnlPrint.reset()
            self.pnlPrompt.reset()
            self.pnlSidePanels.reset()

    def OnbtnResetPanel(self, event):
        answer = wx.MessageBox("Всі налаштування цієї панелі будуть скинуті до налаштувань програми за замовчуванням.\n\
(Вам буде потрібно клацнути Оновити/Зберегти)\nВи дійсно бажаєте зробити це?", "Скидання налаштувань панелі", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            panel = event.GetEventObject().GetParent()
            self.prefs.resetjust(panel.GetName())
            panel.reset()

    def OnbtnUpdate(self, event):
        self.parent.prefs = self.GetPreferences()
        self.parent.updatePrefs(self.oldprefs)
        self.oldprefs.Copy(self.prefs)
        if self.parent.prefs.enablefeedback:
            drScrolledMessageDialog.ShowMessage(self, ("Налаштування поточного екземпляру DrPython успішно оновлено.\nНатисніть Зберегти, щоб зробити їх постійними."), "Оновлення налаштувань")

    def OnbtnSave(self, event):
        self.parent.prefs = self.GetPreferences()
        self.parent.WriteUserPreferencesDirectoryFile()
        if not os.path.exists(self.parent.preferencesdirectory):
            drScrolledMessageDialog.ShowMessage(self, "Тека для збереження налаштувань '" + self.parent.preferencesdirectory + "' не існує.", "Помилка DrPython")
            return
        preffile = self.parent.prefsfile
        try:
            drPrefsFile.WritePreferences(self.GetPreferences(), preffile)
        except IOError:
            drScrolledMessageDialog.ShowMessage(self, "Виникли проблеми при збереженні до:\n"  + preffile, "Помилка запису")
            return
        self.parent.updatePrefs(self.oldprefs)
        self.oldprefs.Copy(self.prefs)
        if self.parent.prefs.enablefeedback:
            drScrolledMessageDialog.ShowMessage(self, ("Успішно збережено до:\n"  + preffile + "\nта оновлено поточний екземпляр DrPython."), "Налаштування збережено")

    def GetPreferences(self):
        #General
        self.prefs.rememberwindowsizeandposition = int(self.pnlGeneral.chkrememberwindowsizeandposition.GetValue())
        self.prefs.rememberdialogsizesandpositions = int(self.pnlGeneral.chkrememberdialogsizesandpositions.GetValue())
        self.prefs.rememberpanelsizes = int(self.pnlGeneral.chkrememberpanelsizes.GetValue())
        self.prefs.showsplash = int(self.pnlGeneral.chkshowsplash.GetValue())
        self.prefs.defaultidemode = self.pnlGeneral.cboIdeMode.GetValue()
        self.prefs.saveonrun = int(self.pnlGeneral.chksaveonrun.GetValue())
        self.prefs.checksyntaxonsave = int(self.pnlGeneral.chkchecksyntaxonsave.GetValue())
        self.prefs.checksyntaxextensions = self.pnlGeneral.txtchecksyntaxextensions.GetValue()
        self.prefs.promptonsaveall = int(self.pnlGeneral.chkpromptonsaveall.GetValue())
        self.prefs.doubleclicktoclosetab = int(self.pnlGeneral.chkdoubleclicktoclosetab.GetValue())

        self.prefs.recentfileslimit = self.pnlGeneral.txtRecentFiles.GetValue()
        if not self.prefs.recentfileslimit:
            self.prefs.recentfileslimit = self.oldprefs.recentfileslimit
        self.prefs.recentfileslimit = int(self.prefs.recentfileslimit)
        self.prefs.iconsize = int(self.pnlGeneral.boxiconsize.GetStringSelection())
        self.prefs.pythonargs = self.pnlGeneral.txtpythonargs.GetValue()


        self.parent.preferencesdirectory = self.pnlGeneral.txtdefaultuserprefsdirectory.GetValue().replace('\\', '/')
        self.prefs.defaultdirectory = self.pnlGeneral.txtdefaultcurdirdirectory.GetValue().replace('\\', '/')

        #Plugins
        self.prefs.pluginsdirectory = self.pnlPlugins.txtdefaultdirectory.GetValue().replace('\\', '/')

        #DrScript
        self.prefs.drscriptsdirectory = self.pnlDrScript.txtdefaultdirectory.GetValue().replace('\\', '/')
        self.parent.SetDrPythonDirectories()


        self.prefs.drscriptloadexamples = int(self.pnlDrScript.chkloadexamples.GetValue())

        self.prefs.enablefeedback = int(self.pnlGeneral.chkenablefeedback.GetValue())
        self.prefs.debugmodus = wx.GetApp().debugmodus = int(self.pnlGeneral.chkdebugmodus.GetValue())

        self.prefs.alwayspromptonexit = int(self.pnlGeneral.chkalwayspromptonexit.GetValue())
        self.prefs.backupfileonsave = int(self.pnlGeneral.chkbackupfileonsave.GetValue())
        self.prefs.checkindentation = int(self.pnlGeneral.chkcheckindentation.GetValue())
        self.prefs.checkeol = int(self.pnlGeneral.chkCheckFormat.GetValue())
        self.prefs.vieweol = int(self.pnlGeneral.chkvieweol.GetValue())

        #Drag and Drop
        self.prefs.draganddropmode = self.pnlDragAndDrop.raddraganddropmode.GetSelection()
        self.prefs.draganddroptextmode = self.pnlDragAndDrop.raddraganddroptextmode.GetSelection()

        #File Types:
        self.prefs.extensions = self.pnlFileTypes.extensions.copy()
        self.prefs.docusetabs = self.pnlFileTypes.docusetabs.copy()
        self.prefs.docuseintellibackspace = self.pnlFileTypes.docuseintellibackspace.copy()
        self.prefs.docremovetrailingwhitespace= self.pnlFileTypes.docremovetrailingwhitespace.copy()
        self.prefs.doctabwidth = self.pnlFileTypes.doctabwidth.copy()
        self.prefs.doceolmode = self.pnlFileTypes.doceolmode.copy()
        self.prefs.docfolding = self.pnlFileTypes.docfolding.copy()
        self.prefs.doccommentstring = self.pnlFileTypes.doccommentstring.copy()
        self.prefs.docwordwrap = self.pnlFileTypes.docwordwrap.copy()

        #File Dialog
        self.prefs.usewxfiledialog = int(self.pnlFileDialog.chkusewxfiledialog.GetValue())
        self.prefs.defaultextension = int(self.pnlFileDialog.chkdefaultextension.GetValue())

        #Document
        self.prefs.docshowlinenumbers = int(self.pnlDocument.chkdocshowlinenumbers.GetValue())
        self.prefs.docparenthesismatching = int(self.pnlDocument.chkdocparenthesismatching.GetValue())
        self.prefs.docupdateindentation = int(self.pnlDocument.chkdocupdateindentation.GetValue())
        self.prefs.docautoindent = self.pnlDocument.raddocautoindent.GetSelection()
        #self.prefs.docremovetrailingwhitespace = int(self.pnlDocument.chkdocremovetrailingwhitespace.GetValue())
        self.prefs.docautoreload = int(self.pnlDocument.chkdocautoreload.GetValue())
        self.prefs.docusefileindentation = int(self.pnlDocument.chkdocusefileindentation.GetValue())
        self.prefs.docwhitespaceisvisible = int(self.pnlDocument.chkWhitespace.GetValue())
        self.prefs.docusestyles = self.pnlDocument.radusestyles.GetSelection()
        self.prefs.docuseindentationguides = int(self.pnlDocument.chkuseindentationguides.GetValue())
        self.prefs.doccommentmode = self.pnlDocument.raddoccommentmode.GetSelection()

        self.prefs.doccaretwidth = self.pnlDocument.txtcaretwidth.GetValue()
        if not self.prefs.doccaretwidth:
            self.prefs.doccaretwidth = self.oldprefs.doccaretwidth
        self.prefs.doccaretwidth = int(self.prefs.doccaretwidth)

        self.prefs.dochighlightcurrentline = int(self.pnlDocument.chkhighlightcurrentline.GetValue())
        self.prefs.docignorectrlpageupdown = int(self.pnlDocument.chkignorectrlpageupdown.GetValue())
        self.prefs.docignoretextfunctionkeys = int(self.pnlDocument.chkignoretextfunctionkeys.GetValue())
        #Chris McDonough (I added the txt prefix)
        self.prefs.doclonglinecol = self.pnlDocument.txtdoclonglinecol.GetValue()
        if not self.prefs.doclonglinecol:
            self.prefs.doclonglinecol = self.oldprefs.doclonglinecol
        self.prefs.doclonglinecol = int(self.prefs.doclonglinecol)
        #/Chris McDonough
        self.prefs.docscrollextrapage = int(self.pnlDocument.chkscrollextrapage.GetValue())
        self.prefs.docdefaultsyntaxhighlighting = self.pnlDocument.boxdefaultsyntaxhighlighting.GetSelection()
        self.prefs.doconlyusedefaultsyntaxhighlighting = self.pnlDocument.chkonlyusedefaultsyntaxhighlighting.GetValue()

        #Prompt

        self.prefs.prompttabwidth = self.pnlPrompt.txttabwidth.GetValue()
        if not self.prefs.prompttabwidth:
            self.prefs.prompttabwidth = self.oldprefs.prompttabwidth
        self.prefs.prompttabwidth = int(self.prefs.prompttabwidth)
        self.prefs.prompteolmode = self.pnlPrompt.radFormat.GetSelection()

        self.prefs.promptmarginwidth = self.pnlPrompt.txtmarginwidth.GetValue()
        if not self.prefs.promptmarginwidth:
            self.prefs.promptmarginwidth = self.oldprefs.promptmarginwidth
        self.prefs.promptmarginwidth = int(self.prefs.promptmarginwidth)
        self.prefs.promptusetabs = int(self.pnlPrompt.chkpromptusetabs.GetValue())
        self.prefs.promptisvisible = int(self.pnlPrompt.chkVisible.GetValue())
        self.prefs.promptsize = int(self.pnlPrompt.sldrSize.GetValue())
        self.prefs.promptwordwrap = int(self.pnlPrompt.chkwordwrap.GetValue())

        self.prefs.promptcaretwidth = self.pnlPrompt.txtcaretwidth.GetValue()
        if not self.prefs.promptcaretwidth:
            self.prefs.promptcaretwidth = self.oldprefs.promptcaretwidth
        self.prefs.promptcaretwidth = int(self.prefs.promptcaretwidth)

        self.prefs.promptwhitespaceisvisible = int(self.pnlPrompt.chkWhitespace.GetValue())
        self.prefs.promptusestyles = self.pnlPrompt.radusestyles.GetSelection()
        self.prefs.promptscrollextrapage = int(self.pnlPrompt.chkscrollextrapage.GetValue())

        self.prefs.promptstartupscript = self.pnlPrompt.txtStartupScript.GetValue()

        #Find/Replace
        self.prefs.findreplaceregularexpression = int(self.pnlFindReplace.chkregularexpression.GetValue())
        self.prefs.findreplacematchcase = int(self.pnlFindReplace.chkmatchcase.GetValue())
        self.prefs.findreplacefindbackwards = int(self.pnlFindReplace.chkfindbackwards.GetValue())
        self.prefs.findreplacewholeword = int(self.pnlFindReplace.chkwholeword.GetValue())
        self.prefs.findreplaceinselection = int(self.pnlFindReplace.chkinselection.GetValue())
        self.prefs.findreplacefromcursor = int(self.pnlFindReplace.chkfromcursor.GetValue())
        self.prefs.findreplacepromptonreplace = int(self.pnlFindReplace.chkpromptonreplace.GetValue())
        self.prefs.findreplaceautowrap = int(self.pnlFindReplace.chkfindreplaceautowrap.GetValue())
        self.prefs.findreplaceundercursor = int(self.pnlFindReplace.chkundercursor.GetValue())

        #Side Panels
        self.prefs.sidepanelleftsize = int(self.pnlSidePanels.sldrSizeLeft.GetValue())
        self.prefs.sidepanelrightsize = int(self.pnlSidePanels.sldrSizeRight.GetValue())
        self.prefs.sidepaneltopsize = int(self.pnlSidePanels.sldrSizeTop.GetValue())

        #Source Browser
        self.prefs.sourcebrowserpanel = self.pnlSourceBrowser.positionchooser.GetSelection()
        self.prefs.sourcebrowsersize = self.pnlSourceBrowser.sldrSize.GetValue()
        self.prefs.sourcebrowserisvisible = int(self.pnlSourceBrowser.chkIsVisible.GetValue())
        self.prefs.sourcebrowsercloseonactivate = int(self.pnlSourceBrowser.chkcloseonactivate.GetValue())
        self.prefs.sourcebrowserissorted = int(self.pnlSourceBrowser.chkissorted.GetValue())
        self.prefs.sourcebrowserautorefreshonsave = int(self.pnlSourceBrowser.chkautorefreshonsave.GetValue())
        self.prefs.sourcebrowserautorefresh = int(self.pnlSourceBrowser.chkautorefresh.GetValue())
        self.prefs.sourcebrowseruseimages = int(self.pnlSourceBrowser.chkuseimages.GetValue())

        #Printing
        self.prefs.printdoclinenumbers = int(self.pnlPrint.chkdoclinenumbers.GetValue())
        self.prefs.printpromptlinenumbers = int(self.pnlPrint.chkpromptlinenumbers.GetValue())
        self.prefs.printtabwidth = self.pnlPrint.txttabwidth.GetValue()
        if not self.prefs.printtabwidth:
            self.prefs.printtabwidth = self.oldprefs.printtabwidth
        self.prefs.printtabwidth = int(self.prefs.printtabwidth)

        #Documentation
        self.prefs.documentationbrowser = self.pnlDocumentation.txtbrowser.GetValue()
        self.prefs.documentationpythonlocation = self.pnlDocumentation.txtpython.GetValue()
        self.prefs.documentationwxwidgetslocation = self.pnlDocumentation.txtwxwidgets.GetValue()
        self.prefs.documentationrehowtolocation = self.pnlDocumentation.txtrehowto.GetValue()
        if self.prefs.defaultidemode:
            importlib.reload(sys)  #this is needed because of wine and linux
            #sys.setdefaultidemode(self.prefs.defaultidemode)
            #wx.SetDefaultPyEncoding(str(self.prefs.defaultidemode))
            #sys.setappdefaultidemode(self.prefs.defaultidemode)

        return self.prefs
