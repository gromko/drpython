#   Copyright 2003-2010 Daniel Pozmanter
#

#Go To Source Browser

import re
import wx
from drSingleChoiceDialog import drSingleChoiceDialog

respacecount = re.compile(r'\S')

def GetMatches(text, resourcebrowser):
    matches = []
    positions = []

    matcher = resourcebrowser.finditer(text)

    try:
        match = next(matcher)
    except:
        match = None
    while match is not None:
        matches.append(match.group().replace('\t', '    '))
        positions.append(len(text[:match.start()].encode('utf-8')))        
        try:
            match =next(matcher)
        except:
            match = None

    return matches, positions

class drSourceBrowserGoToDialog(drSingleChoiceDialog):

    def __init__(self, parent, Document, matches, positions):
        drSingleChoiceDialog.__init__(self, parent, "Перехід за структурою", matches, False, SetSizer=False)

        self.Document = Document

        self.positions = positions

        self.txtLine = wx.TextCtrl(self, -1, "", (0, 0), (350, -1), style=wx.TE_READONLY)
        self.txtDefinedIn = wx.TextCtrl(self, -1, "", (0, 0), (350, -1), style=wx.TE_READONLY)

        self.lineSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lineSizer.Add(wx.StaticText(self, -1, "  "), 0, wx.SHAPED)
        self.lineSizer.Add(self.txtLine, 1, wx.EXPAND)
        self.lineSizer.Add(wx.StaticText(self, -1, "  "), 0, wx.SHAPED)

        self.defSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.defSizer.Add(wx.StaticText(self, -1, "  "), 0, wx.SHAPED)
        self.defSizer.Add(self.txtDefinedIn, 1, wx.EXPAND)
        self.defSizer.Add(wx.StaticText(self, -1, "  "), 0, wx.SHAPED)

        self.theSizer.Insert(2, wx.StaticText(self, -1, "  "), 0, wx.SHAPED)
        self.theSizer.Insert(3, self.lineSizer, 0, wx.EXPAND)
        self.theSizer.Insert(4, self.defSizer, 0, wx.EXPAND)

        self.SetSizerAndFit(self.theSizer)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected, id=self.ID_CHOICES)

        self.OnSelected(None)
        if parent.PLATFORM_IS_GTK: #does not get initially the focus (bug tracker #1903778, "Open Imported Module: focus problem", 29.02.2008: from Jon White, thanks.
            self.SetFocus()

    def OnSelected(self, event):
        sel = self.listChoices.GetFirstSelected()
        if sel > -1:
            pos = self.listChoices.GetItemData(sel)

            spaces = respacecount.search(self.choices[pos]).start() - 1

            definedin = self.Document.GetFilenameTitle()

            if spaces > 0:
                x = pos
                while x > -1:
                    if (respacecount.search(self.choices[x]).start() - 1) < spaces:
                        definedin = self.choices[x].rstrip()
                        break
                    x -= 1

            linenumber = str(self.Document.LineFromPosition(self.positions[pos]) + 1)

            self.txtLine.SetValue("рядок:      " + linenumber)
            self.txtDefinedIn.SetValue("визначено у:    " + definedin)

def SourceBrowserGoTo(frame, Document):
    compchar = Document.GetIndentationCharacter()
    resourcebrowser = re.compile(r'(^'+compchar+r'*?class\s.*[(:])|(^'+compchar+r'*?def\s.*[(:])|(^'+compchar+r'*?import\s.*$)|(^'+compchar+r'*?from\s.*$)', re.MULTILINE | re.UNICODE)
    text = Document.GetText()

    matches, positions = GetMatches(text, resourcebrowser)

    d = drSourceBrowserGoToDialog(frame, Document, matches, positions)
    answer = d.ShowModal()
    d.Destroy()

    if answer == wx.ID_OK:
        i = d.GetSelection()
        line = Document.LineFromPosition(positions[i])
        Document.EnsureVisible(line)
        Document.ScrollToLine(line)
        Document.GotoLine(line)
        Document.GotoPos(positions[i])

    Document.SetFocus()
    Document.SetSTCFocus(True)
