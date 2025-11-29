#   Copyright 2003-2010 Daniel Pozmanter
#   Distributed under the terms of the GPL (GNU Public License)


#Regular Expression Dialog

import os
import re
import wx
import drScrolledMessageDialog
import drFileDialog

wildcard = "Text File (*.txt)|*.txt|All files (*)|*"

class drRETextCtrl(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size)

        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnChar(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.GetParent().OnbtnCancel(event)
        elif event.GetKeyCode() == wx.WXK_RETURN:
            self.GetParent().OnbtnOk(event)
        else:
            event.Skip()


class drRegularExpressionDialog(wx.Frame):
    def __init__(self, parent, id, title, prompthasfocus = 0, infiles = 0):

        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        print("tile=",title)
        self.insert = (title == "Вставити регулярний вираз")  #(title == "Insert Regular Expression")

        self.theSizer = wx.FlexGridSizer(0, 1, 5, 10)

        okcancelSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.parent = parent
        self.prompthasfocus = prompthasfocus

        #that part of code is ugly
        if self.insert:
            self.drpyframe = self.parent
        elif not infiles:
            self.drpyframe = self.parent.GetParent()
        else:
            self.drpyframe = self.parent.GetGrandParent()

        self.defaultdirectory = self.drpyframe.prefs.defaultdirectory
        self.enablefeedback = self.drpyframe.prefs.enablefeedback
        self.filedialogparent = self.drpyframe
        self.regdatdirectory = os.path.join(self.drpyframe.datdirectory, "regex")
        if not os.path.exists(self.regdatdirectory):
            os.mkdir(self.regdatdirectory)

        #end of uglpy part of code

        FileMenu = wx.Menu()
        FileMenu.Append(wx.ID_OPEN)
        FileMenu.Append(wx.ID_SAVE)

        TextMenu = wx.Menu()
        mnuNormalText = TextMenu.Append(wx.ID_ANY, "звичайний текст")
        mnuAnyChar = TextMenu.Append(wx.ID_ANY, 'довільний символ  "."')
        mnuAnyDigit = TextMenu.Append(wx.ID_ANY, 'довільна десяткова цифра  "\\d"')
        mnuAnyNonDigit = TextMenu.Append(wx.ID_ANY, 'довільний символ не цифра  "\\D"')
        mnuAnyWS = TextMenu.Append(wx.ID_ANY, 'довільний символ пропуску  "\\s"')
        mnuAnyNonWS = TextMenu.Append(wx.ID_ANY, 'довільний символ не пропуск  "\\S"')
        mnuAnyAlphaNum = TextMenu.Append(wx.ID_ANY, 'довільний алфавітно-цифровий символ  "\\w"')
        mnuAnyNonAlphaNum = TextMenu.Append(wx.ID_ANY, 'довільний не алфавітно-цифровий символ  "\\W"')
        mnuCharSet = TextMenu.Append(wx.ID_ANY, 'набір символів  "[]"')

        RepetitionsMenu = wx.Menu()
        mnuZeroOrMore = RepetitionsMenu.Append(wx.ID_ANY, "0 або більше  \"*\"")
        mnuOneOrMore = RepetitionsMenu.Append(wx.ID_ANY, "1 або більше  \"+\"")
        mnuZeroOrOne = RepetitionsMenu.Append(wx.ID_ANY, "0 або 1  \"?\"")
        mnuRepeat = RepetitionsMenu.Append(wx.ID_ANY, "n  \"{n}\"")

        LimitMenu = wx.Menu()
        mnuStartOfLine = LimitMenu.Append(wx.ID_ANY, 'початок кожного рядка  "^"')
        mnuEndOfLine = LimitMenu.Append(wx.ID_ANY, 'кінець кожного рядка "$"')
        mnuStartOfDoc = LimitMenu.Append(wx.ID_ANY, 'початок документа "\\A"')
        mnuEndOfDoc = LimitMenu.Append(wx.ID_ANY, 'кінець документа  "\\Z"')
        mnuWordBoundary = LimitMenu.Append(wx.ID_ANY, 'початок або кінець слова  "\\b"')
        mnuNonWordBoundary = LimitMenu.Append(wx.ID_ANY, 'Текст, який не знаходиться в кінці слова  "\\B"')

        lookMenu = wx.Menu()
        mnuPositiveLookahead = lookMenu.Append(wx.ID_ANY, "перегляд вперед: позитивний  \"(?=)\"")
        mnuNegativeLookahead = lookMenu.Append(wx.ID_ANY, "перегляд вперед: негативний  \"(?!)\"")
        mnuPositiveLookbehind = lookMenu.Append(wx.ID_ANY, "перегляд назад: позитивний  \"(?<=)\"")
        mnuNegativeLookbehind = lookMenu.Append(wx.ID_ANY, "перегляд назад: негативний  \"(?<!)\"")

        InsertMenu = wx.Menu()
        InsertMenu.Append(wx.ID_ANY, "Символи", TextMenu)
        InsertMenu.Append(wx.ID_ANY, "Квантифікація", RepetitionsMenu)
        InsertMenu.Append(wx.ID_ANY, "Прив'язка", LimitMenu)
        InsertMenu.Append(wx.ID_ANY, "Перегляд", lookMenu)
        mnuOr = InsertMenu.Append(wx.ID_ANY, "Перерахування  \"|\"")
        mnuGroup = InsertMenu.Append(wx.ID_ANY, "Групування  \"( )\"")

        menuBar = wx.MenuBar()
        menuBar.Append(FileMenu, "Файл")
        menuBar.Append(InsertMenu, "Помічник")

        self.SetMenuBar(menuBar)

        self.txtRE = drRETextCtrl(self, -1, "", wx.DefaultPosition, (500, -1))

        self.btnOk = wx.Button(self, wx.ID_OK)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL)

        okcancelSizer.Add(self.btnOk, 1, wx.SHAPED)
        okcancelSizer.Add(self.btnCancel, 1, wx.SHAPED)

        self.theSizer.Add(self.txtRE, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(okcancelSizer, 1, wx.SHAPED | wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.btnOk.SetDefault()
        self.txtRE.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnbtnCancel, self.btnCancel)
        self.Bind(wx.EVT_BUTTON, self.OnbtnOk, self.btnOk)

        self.Bind(wx.EVT_MENU, self.OnLoad, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacter, mnuAnyChar)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterD, mnuAnyDigit)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterND, mnuAnyNonDigit)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterW, mnuAnyWS)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterNW, mnuAnyNonWS)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterA, mnuAnyAlphaNum)
        self.Bind(wx.EVT_MENU, self.OnbtnAnyCharacterNA, mnuAnyNonAlphaNum)
        self.Bind(wx.EVT_MENU, self.OnbtnSetOfCharacters, mnuCharSet)
        self.Bind(wx.EVT_MENU, self.OnbtnStart, mnuStartOfLine)
        self.Bind(wx.EVT_MENU, self.OnbtnEnd, mnuEndOfLine)
        self.Bind(wx.EVT_MENU, self.OnbtnStartD, mnuStartOfDoc)
        self.Bind(wx.EVT_MENU, self.OnbtnEndD, mnuEndOfDoc)
        self.Bind(wx.EVT_MENU, self.OnbtnEdgeW, mnuWordBoundary)
        self.Bind(wx.EVT_MENU, self.OnbtnEdgeNW, mnuNonWordBoundary)
        self.Bind(wx.EVT_MENU, self.OnbtnRepsZeroPlus, mnuZeroOrMore)
        self.Bind(wx.EVT_MENU, self.OnbtnRepsOnePlus, mnuOneOrMore)
        self.Bind(wx.EVT_MENU, self.OnbtnRepsZeroOrOne, mnuZeroOrOne)
        self.Bind(wx.EVT_MENU, self.OnbtnRepsN, mnuRepeat)
        self.Bind(wx.EVT_MENU, self.OnbtnOr, mnuOr)
        self.Bind(wx.EVT_MENU, self.OnbtnGroup, mnuGroup)
        self.Bind(wx.EVT_MENU, self.OnbtnLookPositiveA, mnuPositiveLookahead)
        self.Bind(wx.EVT_MENU, self.OnbtnLookNegativeA, mnuNegativeLookahead)
        self.Bind(wx.EVT_MENU, self.OnbtnLookPositiveB, mnuPositiveLookbehind)
        self.Bind(wx.EVT_MENU, self.OnbtnLookNegativeB, mnuNegativeLookbehind)

        self.Bind(wx.EVT_MENU, self.OnbtnInsertNormalText, mnuNormalText)

        size = (500, 180)

        self.SetSize(size)

    def insertText(self, text):
        pos = self.txtRE.GetInsertionPoint()
        textRE = self.txtRE.GetValue()
        self.txtRE.SetValue(textRE[0:pos] + text + textRE[pos:])
        self.txtRE.SetInsertionPoint(pos + len(text))

    def OnbtnAnyCharacter(self, event):
        self.insertText('.')

    def OnbtnAnyCharacterA(self, event):
        self.insertText('\\w')

    def OnbtnAnyCharacterD(self, event):
        self.insertText('\\d')

    def OnbtnAnyCharacterNA(self, event):
        self.insertText('\\W')

    def OnbtnAnyCharacterND(self, event):
        self.insertText('\\D')

    def OnbtnAnyCharacterNW(self, event):
        self.insertText('\\S')

    def OnbtnAnyCharacterW(self, event):
        self.insertText('\\s')

    def OnbtnCancel(self, event):
        self.txtRE.SetValue("")
        self.Close(1)

    def OnbtnEdgeNW(self, event):
        self.insertText('\\B')

    def OnbtnEdgeW(self, event):
        self.insertText('\\b')

    def OnbtnEnd(self, event):
        self.insertText('$')

    def OnbtnEndD(self, event):
        self.insertText('\\Z')

    def OnbtnGroup(self, event):
        self.insertText('()')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnInsertNormalText(self, event):
        d = wx.TextEntryDialog(self, "Введіть звичайний текст", "Вставити звичайний текст", "")
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            self.insertText(re.escape(v))

    def OnbtnLookNegativeA(self, event):
        self.insertText('(?!)')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnLookPositiveA(self, event):
        self.insertText('(?=)')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnLookNegativeB(self, event):
        self.insertText('(?<!)')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnLookPositiveB(self, event):
        self.insertText('(?<=)')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnOk(self, event):
        self.Show(0)

        result = self.txtRE.GetValue()
        l = len(result)
        if l > 0:
            if self.insert:
                if self.prompthasfocus:
                    pos = self.parent.txtPrompt.GetCurrentPos()
                    self.parent.txtPrompt.InsertText(pos, result)
                    self.parent.txtPrompt.GotoPos(pos + l)
                else:
                    pos = self.parent.txtDocument.GetCurrentPos()
                    self.parent.txtDocument.InsertText(pos, result)
                    self.parent.txtDocument.GotoPos(pos + l)
            else:
                self.parent.txtSearchFor.SetValue(result)

        self.Close(1)

    def OnbtnOr(self, event):
        self.insertText('|')

    def OnbtnRepsN(self, event):
        d = wx.TextEntryDialog(self, "Введіть потрібну кількість повторень:", "Введіть N повторень", "")
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            self.insertText('{' + v + '}')

    def OnbtnRepsOnePlus(self, event):
        self.insertText('+')

    def OnbtnRepsZeroOrOne(self, event):
        self.insertText('?')

    def OnbtnRepsZeroPlus(self, event):
        self.insertText('*')

    def OnbtnSetOfCharacters(self, event):
        self.insertText('[]')
        pos = self.txtRE.GetInsertionPoint()
        self.txtRE.SetInsertionPoint(pos - 1)

    def OnbtnStart(self, event):
        self.insertText('^')

    def OnbtnStartD(self, event):
        self.insertText('\\A')

    def OnLoad(self, event):
        dlg = drFileDialog.FileDialog(self.filedialogparent, "Load Regular Expression From", wildcard)
        if self.regdatdirectory:
            try:
                dlg.SetDirectory(self.regdatdirectory)
            except:
                drScrolledMessageDialog.ShowMessage(self, ("Error Setting Default Directory To: " + self.regdatdirectory), "DrPython Error")
        if dlg.ShowModal() == wx.ID_OK:
            refile = dlg.GetPath().replace('\\', '/')
            try:
                f = open(refile, 'r',encoding="UTF-8")
                text = f.read()
                f.close()
            except:
                drScrolledMessageDialog.ShowMessage(self, ("Error Reading From: " +  refile), "DrPython Error")
                text = ""
            if (text.find('\n') > -1) or (text.find('\r') > -1):
                drScrolledMessageDialog.ShowMessage(self, ("Error Reading From: " +  refile), "DrPython Error")
                text = ""
            self.txtRE.SetValue(text)

        dlg.Destroy()
        self.Raise()

    def OnSave(self, event):
        dlg = drFileDialog.FileDialog(self.filedialogparent, "Save Regular Expression As", wildcard, IsASaveDialog=True)
        if self.regdatdirectory:
            try:
                dlg.SetDirectory(self.regdatdirectory)
            except:
                drScrolledMessageDialog.ShowMessage(self, ("Error Setting Default Directory To: " + self.regdatdirectory), "DrPython Error")
        if dlg.ShowModal() == wx.ID_OK:
            refile = dlg.GetPath().replace('\\', '/')
            if refile.lower()[-4:] != ".txt":
                refile += ".txt"
            try:
                f = open(refile, 'w',encoding="UTF-8")
                f.write(self.txtRE.GetValue())
                f.close()
            except:
                drScrolledMessageDialog.ShowMessage(self, ("Error Writing To: " +  refile), "DrPython Error")
                return
            if self.enablefeedback:
                drScrolledMessageDialog.ShowMessage(self, ("Successfully Saved: " + refile), "Save Success")
            dlg.Destroy()
        self.Raise()
