#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2010 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   DrPython is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#FindReplace Dialog

import wx
import wx.stc
import drScrolledMessageDialog
import re

class drFinder:
    #copy old finder limodou 2004/04/19
    def __init__(self, parent, stc, oldfinder=None):
    #end limodou
        self.parent = parent
        self.stc = stc
        self.reset()
        #copy old finder limodou 2004/04/19
        self.Copy(oldfinder)
        #end limodou

    #copy old finder limodou 2004/04/19
    def Copy(self, finder):
        if finder:
            self.findtext = finder.findtext
            self.findflags = finder.findflags
            self.backwards = finder.backwards
            #Franz:  Bug Report with Fix
            self.RE = finder.RE
            #Moved here by Dan.
            #Edited by Dan
            #(Bug Report, Franz.)
            #copy old finder limodou 2004/04/19
            self.docEnd = self.stc.GetTextLength()
            self.SetTargetRange(0, self.docEnd)

            self.replace_findtext = finder.replace_findtext
            self.replace_replacetext = finder.replace_replacetext
            self.replace_flags = finder.replace_flags
            self.replace_prompt = finder.replace_prompt

            #end limodou
    #end limodou

    def DoFind(self, findtext, findflags, backwards=False):
        #self.parent.SetStatusText(findtext, 2)
        self.RE = 0
        self.rectanglefind = 0
        doclength = self.stc.GetLength()

        self.findtext = findtext
        self.findflags = findflags

        prev = self.findpos

        if self.backwards != backwards:
            self.backwards = backwards

        if backwards:
            endpos = self.targetStart
        else:
            endpos = self.targetEnd

        self.findposition = self.stc.FindText(self.findpos, endpos, findtext, findflags)
        self.findpos = self.findposition[0]
        if self.findpos == -1:
            if self.stc.FindText(self.targetStart, self.targetEnd, findtext, findflags) == -1:
                if self.parent.prefs.enablefeedback:
                    drScrolledMessageDialog.ShowMessage(self.parent, "Search string '" + findtext + "' not found.", "Пошук drPython")
                else:
                    self.parent.SetStatusText("NOT FOUND: " + findtext, 2)
                return
            if ((self.findpos >= doclength) or (self.findpos < 0)) and (doclength > 0):
                self.lastposition = -1
                if self.backwards:
                    msg = "Start of document reached: '" + findtext + "'.\nStart again from the end?"
                    fpos =  self.targetEnd
                else:
                    msg = "End of document reached: '" + findtext + "'.\nStart again from the beginning?"
                    fpos =  self.targetStart

                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.YES
                else:
                    answer = wx.MessageBox(msg, "Пошук drPython", wx.YES_NO | wx.ICON_QUESTION)

                if answer == wx.YES:
                    self.findpos = fpos
                    self.stc.GotoPos(self.findpos)
                    if self.backwards:
                        self.DoFindPrevious()
                    else:
                        self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return

        if self.parent.prefs.docfolding:            
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        endpos = self.findpos + len(findtext)

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = self.findpos + len(findtext)

        if backwards:
            self.findpos = self.findpos - 1
        else:
            self.findpos = self.findpos + 1


    def DoREFind(self, findtext, matchcase):
        self.RE = 1
        self.rectanglefind = 0

        self.findtext = findtext
        self.findflags = matchcase

        prev = self.findpos

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Regular Expression Error", "Пошук drPython")
            return

        endpos = self.targetEnd

        nextoffset = self.findpos
        text = self.stc.GetText()
        if findtext[0] == "^":
            self.parent.SetStatusText("find regex with '^' is a little tricky, it has problems with first and last line", 2)
            if self.findpos > 0:
                nextoffset = text[self.findpos:endpos].find("\n") + 1
                if nextoffset != -1:
                    nextoffset += self.findpos
                    if nextoffset >= self.stc.GetTextLength():
                        pass
                    else:
                        while text[nextoffset] == '\n':
                            nextoffset += 1
                            if nextoffset >= self.stc.GetTextLength():
                                break
        matchedtext = regularexpression.search(text[nextoffset:endpos])

        if matchedtext is None:
            testforexist = regularexpression.search(text)
            if testforexist is None:
                drScrolledMessageDialog.ShowMessage(self.parent, "Regular expression '" + findtext + "' not found.", "Пошук drPython")
                return
            self.lastposition = -1
            if prev > self.targetStart:
                self.findpos = self.targetStart

                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.YES
                else:
                    answer = wx.MessageBox("End of document reached: '" + findtext + "'.\nStart again from the beginning?", "Пошук drPython", wx.YES_NO | wx.ICON_QUESTION)

                if answer == wx.YES:
                    self.stc.GotoPos(self.findpos)
                    self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
            return

        self.findpos = nextoffset + matchedtext.start()
        endpos = nextoffset + matchedtext.end()

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = endpos

        self.findpos = endpos

    def DoREFindBackward(self, findtext, matchcase):
        self.RE = 1
        self.rectanglefind = 0

        self.findtext = findtext
        self.findflags = matchcase

        prev = self.findpos

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Regular Expression Error", "Пошук drPython")
            return

        endpos = self.targetEnd

        begpos = min(self.stc.GetSelection())
        matchedtext = regularexpression.finditer(self.stc.GetText()[:begpos])

        match = True
        lastmatch = None
        while match is not None:
            try:
                match = matchedtext.next()
                lastmatch = match
            except StopIteration:
                match = None

        if lastmatch is None:
            #anything found at all?
            testforexist = regularexpression.search(self.stc.GetText())
            if testforexist is None:
                drScrolledMessageDialog.ShowMessage(self.parent, "Regular expression '" + findtext + "' not found backwards.", "Пошук drPython")
                return
            self.lastposition = -1

            if self.parent.prefs.findreplaceautowrap:
                answer = wx.YES
            else:
                answer = wx.MessageBox("Begin of document reached: '" + findtext + "'.\nStart again from the end?", "Пошук drPython", wx.YES_NO | wx.ICON_QUESTION)

            if answer == wx.YES:
                matchedtext = regularexpression.finditer(self.stc.GetText())

                match = True
                lastmatch = None
                while match is not None:
                    try:
                        match = matchedtext.next()
                        lastmatch = match
                    except StopIteration:
                        match = None
            else:
                return

        self.findpos, endpos = lastmatch.span()
        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = self.findpos

    def DoFindNext(self):
        if not self.findtext:
            drScrolledMessageDialog.ShowMessage(self.parent, "No search string", "DrPython Find Next")
            return
        if not self.inselection:
            textlength = self.stc.GetTextLength()
            if textlength != self.docEnd:
                self.docEnd = textlength
                self.SetTargetRange(0, self.docEnd)
        self.findpos = self.stc.GetCurrentPos()
        if not self.RE:
            if self.rectanglefind:
                self.DoRectangleFind(self.findtext, self.findflags)
            else:
                self.DoFind(self.findtext, self.findflags)
        else:
            if self.rectanglefind:
                self.DoRERectangleFind(self.findtext, self.findflags)
            else:
                self.DoREFind(self.findtext, self.findflags)
        self.ScrollFewLinesAbove()

    def DoFindPrevious(self):
        if not self.findtext:
            drScrolledMessageDialog.ShowMessage(self.parent, "No search string", "DrPython Find Previous")
            return
        if not self.inselection:
            textlength = self.stc.GetTextLength()
            if textlength != self.docEnd:
                self.docEnd = textlength
                self.SetTargetRange(0, self.docEnd)
        self.findpos = self.stc.GetCurrentPos()
        if not self.RE:
            if (self.findpos == self.lastposition) and not self.rectanglefind:
                self.findpos = self.findpos - len(self.findtext) - 1
                self.stc.GotoPos(self.findpos)
            elif self.rectanglefind and (self.lastposition == -1) and (not self.backwards):
                self.stc.GotoPos(self.findpos)
            if self.rectanglefind:
                self.DoRectangleFind(self.findtext, self.findflags, True)
            else:
                self.DoFind(self.findtext, self.findflags, True)
            self.ScrollFewLinesBelow()
        else:
            self.DoREFindBackward(self.findtext, self.findflags)

    def ScrollFewLinesAbove(self):
        top = self.parent.txtDocument.GetCurrentLine() - (self.parent.txtDocument.LinesOnScreen() - 5)
        lastline = self.parent.txtDocument.GetFirstVisibleLine() + self.parent.txtDocument.LinesOnScreen()
        if self.parent.txtDocument.GetCurrentLine() > (lastline - 5):
            self.parent.txtDocument.ScrollToLine(top)

    def ScrollFewLinesBelow(self):
        top = self.parent.txtDocument.GetCurrentLine() - 5
        firstline = self.parent.txtDocument.GetFirstVisibleLine()
        if self.parent.txtDocument.GetCurrentLine() < (firstline + 5):
            self.parent.txtDocument.ScrollToLine(top)

    def DoRectangleFind(self, findtext, matchcase, backwards=False):
        self.RE = 0
        self.rectanglefind = 1
        doclength = self.stc.GetLength()
        lenlines = len(self.Lines)

        if matchcase:
            self.findtext = findtext
        else:
            self.findtext = findtext.lower()

        prev = self.findpos

        if self.backwards != backwards:
            self.backwards = backwards
        if self.backwards:
            self.findpos = self.stc.GetCurrentPos()-1

        endpos = self.targetEnd

        lineArrayPosition = self.getArrayPosition(self.findpos)
        if lineArrayPosition == -1:
            self.findpos = self.findpos - 1
            lineArrayPosition = self.getArrayPosition(self.findpos - 1)
            if lineArrayPosition == -1:
                self.findpos = -1
            else:
                relative_findpos = self.positions[lineArrayPosition].index(self.findpos) + 1
        else:
            relative_findpos = self.positions[lineArrayPosition].index(self.findpos)

        if self.findpos > -1:
            self.findpos = self.findInArray(lineArrayPosition, relative_findpos)

        if self.findpos == -1:
            if self.backwards:
                notFound = self.findInArray(0, self.positions[lenlines-1][len(self.positions[lenlines-1])-1]) == -1
            else:
                notFound = self.findInArray(0, 0) == -1
            if notFound:
                drScrolledMessageDialog.ShowMessage(self.parent, "Шукана послідовність '" + findtext + "' не знайдена.", "Пошук drPython")
                return
            if ((self.findpos >= doclength) or (self.findpos < 0)) and (doclength > 0):
                self.lastposition = -1
                if self.backwards:
                    msg = "Досягнуто початок документа при пошуку: '" + findtext + "'.\nПродовжити пошук з кінця?"
                    self.findpos = self.targetEnd + 1
                else:
                    msg = "Досягнуто кінця документу при пошуку: '" + findtext + "'.\nПродовжити пошук з початку?"
                    self.findpos = self.targetStart

                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.YES
                else:
                    answer = wx.MessageBox(msg, "Пошук drPython", wx.YES_NO | wx.ICON_QUESTION)

                if answer == wx.YES:
                    self.stc.GotoPos(self.findpos)
                    if self.backwards:
                        self.DoFindPrevious()
                    else:
                        self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        endpos = self.findpos + len(findtext)

        self.stc.EnsurePositionIsVisible(endpos)
        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = self.findpos + len(findtext)

    def DoRERectangleFind(self, findtext, matchcase):
        self.RE = 1
        self.rectanglefind = 1
        doclength = self.stc.GetLength()

        self.findtext = findtext
        self.findflags = matchcase

        prev = self.findpos

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Помилка у регулярному виразі", "Пошук drPython")
            return

        endpos = self.targetEnd
        if (self.findpos >= doclength) or (self.findpos < 0):
            self.findpos = 0

        lineArrayPosition = self.getArrayPosition(self.findpos)
        if lineArrayPosition == -1:
            self.findpos = self.findpos - 1
            lineArrayPosition = self.getArrayPosition(self.findpos - 1)
            if lineArrayPosition == -1:
                self.findpos = -1
            else:
                relative_findpos = self.positions[lineArrayPosition].index(self.findpos) + 1
        else:
            relative_findpos = self.positions[lineArrayPosition].index(self.findpos)

        if self.findpos > -1:
            matchedtext, newArrayPosition, reloffset = self.searchInArray(regularexpression, lineArrayPosition, relative_findpos)
        else:
            matchedtext = None

        if matchedtext is None:
            testforexist, nap, reloffset = self.searchInArray(regularexpression, 0, 0)
            if testforexist is None:
                drScrolledMessageDialog.ShowMessage(self.parent, "Регулярний вираз '" + findtext + "' не знайдено.", "Пошук drPython")
                return
            self.lastposition = -1
            if prev > self.targetStart:
                self.findpos = self.targetStart

                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.YES
                else:
                    answer = wx.MessageBox("Досягнуто кінця документу під час пошуку: '" + findtext + "'.\nПродовжити пошук з початку?", "Пошук drPython", wx.YES_NO | wx.ICON_QUESTION)

                if answer == wx.YES:
                    self.stc.GotoPos(self.findpos)
                    self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return


        self.findpos = self.positions[newArrayPosition][reloffset + matchedtext.start()]

        endpos = self.findpos + (matchedtext.end() - matchedtext.start())

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = endpos

        self.findpos = endpos

    def findInArray(self, arrayposition, position):
        if self.backwards:
            r = self.Lines[arrayposition][:position].rfind(self.findtext)
            if r == -1:
                arrayposition -= 1
                while arrayposition > -1:
                    r = self.Lines[arrayposition].rfind(self.findtext)
                    if r == -1:
                        arrayposition -= 1
                    else:
                        return self.positions[arrayposition][r]
            else:
                return self.positions[arrayposition][r]
        else:
            l = len(self.Lines)
            r = self.Lines[arrayposition][position:].find(self.findtext)
            if r == -1:
                arrayposition += 1
                while arrayposition < l:
                    r = self.Lines[arrayposition].find(self.findtext)
                    if r == -1:
                        arrayposition += 1
                    else:
                        return self.positions[arrayposition][r]
            else:
                r += position
                return self.positions[arrayposition][r]
        return -1

    def getArrayPosition(self, position):
        x = 0
        for posArray in self.positions:
            if position in posArray:
                return x
            x += 1
        return -1

    def GetFindPos(self):
        return self.findpos

    def GetFindText(self):
        return self.findtext

    def RectangleReplaceAll(self, findtext, replacetext, matchcase):
        targetText = self.stc.GetSelectedText()

        if not matchcase:
            targetText = targetText.lower()
            findtext = findtext.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        lines = targetText.strip().split(eolchar)

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(lines[0])

        x = 0

        for line in lines:
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            p = line.find(findtext)
            if p > -1:
                line = line.replace(findtext, replacetext)
                self.stc.SetTargetStart(position_of_first_character)
                self.stc.SetTargetEnd(position_of_first_character+lenline)
                self.stc.ReplaceTarget(line)
                x = x + 1
            linenumber = linenumber + 1

        return x

    def RectangleREReplaceAll(self, findtext, replacetext, matchcase):
        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Помилка у регулярному виразі", "Заміна drPython")
            return

        targetText = self.stc.GetSelectedText()

        if not matchcase:
            targetText = targetText.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        lines = targetText.strip().split(eolchar)

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(lines[0])

        y = 0

        for line in lines:
            #You need to update the position(do the replace) during the loop.
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            line, x = regularexpression.subn(replacetext, line)
            y = y + x
            self.stc.SetTargetStart(position_of_first_character)
            self.stc.SetTargetEnd(position_of_first_character+lenline)
            self.stc.ReplaceTarget(line)
            linenumber = linenumber + 1

        return y

    def ReplaceAll(self, findtext, replacetext, flags, prompt = 0):
        #store last replace settings
        self.replace_findtext = findtext
        self.replace_replacetext = replacetext
        self.replace_flags = flags
        self.replace_prompt = prompt

        pp = self.stc.FindText(self.findpos, self.targetEnd, findtext, flags)
        p = pp[0]

        if p == -1:
            self.parent.SetStatusText("Заміна: НЕ ЗНАЙДЕНО: " + findtext, 2)
        diff = len(replacetext) - len(findtext)
        x = 0
        notfirst = 0
        favpos = wx.Point(5, 5)

        if not prompt:
            answer = wx.MessageBox("Бажаєте замінити всі входження?", "Замінити все?", wx.YES_NO | wx.ICON_QUESTION)
            #its very annoying, is by accicent or by change everything is replaced, which is not wanted
            if answer != wx.YES:
                p = -1
        
        while p != -1:
            if self.parent.prefs.docfolding:                
                self.stc.EnsureVisible(self.stc.LineFromPosition(p))
            self.stc.GotoPos(p)
            self.stc.EnsureCaretVisible()
            self.stc.SetTargetStart(p)
            self.stc.SetTargetEnd(p + len(findtext))
            if prompt:
                self.stc.SetSelection(p, (p + len(findtext)))
                d = ReplaceDialog(self.parent, "Знайдено '" + findtext + "' у рядку: " \
                                    + str(self.stc.LineFromPosition(p)+1) \
                                    + " позиція: " + str(self.stc.GetColumn(p)) \
                                    + ",\nзамінити на '" + str(replacetext) + "'?" \
                                    + "\n(Натисніть Скасувати, щоб припинити)")
                if notfirst:
                    d.Move(favpos)
                else:
                    notfirst = 1
                answer = d.ShowModal()
                favpos = d.GetPosition()
                d.Destroy()
                if answer == wx.ID_REPLACE:
                    self.stc.ReplaceTarget(replacetext)
                    self.targetEnd = self.targetEnd + diff
                elif answer == wx.ID_IGNORE:
                    x = x - 1
                    p = p + 1
                elif answer == wx.ID_CANCEL:
                    p = -1
                    x = x - 1
                else:
                    oldfindstring = self.findtext #borrow findstring
                    self.findtext = findtext
                    self.stc.Undo()
                    self.DoFindPrevious()
                    p = self.findpos + 1
                    self.stc.GotoPos(p)
                    x = x - 1
                    self.findtext = oldfindstring
                if answer in [wx.ID_REPLACE, wx.ID_IGNORE]:
                    pp = self.stc.FindText(p + len(replacetext), self.targetEnd, findtext, flags)
                    p = pp[0]
            else:
                self.stc.ReplaceTarget(replacetext)
                self.targetEnd = self.targetEnd + diff
                pp = self.stc.FindText((p + len(replacetext)), self.targetEnd, findtext, flags)
                p = pp[0]
            x = x + 1
        return x

    def REReplaceAll(self, findtext, replacetext, matchcase, prompt = 0):

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Помилка у регулярному виразі", "Заміна drPython")
            return

        #important, that in selection, start < begin


        oldtext = self.stc.GetText()
        if not prompt:
            pos = self.stc.GetCurrentPos()
            newtext, x = regularexpression.subn(replacetext, oldtext[self.findpos:self.targetEnd])
            if x == 0:
                drScrolledMessageDialog.ShowMessage(self.parent, "Регулярний вираз: '" + findtext + "' не знайдено - нічого не замінено", "Заміна з регулярними виразами drPython")
            else:
                self.parent.SetStatusText(str(x) + " раз(ів) замінено регулярний вираз", 2)

            self.stc.SetText(oldtext[0:self.findpos] + newtext + oldtext[self.targetEnd:])
            self.stc.SetSelection(pos, pos)
        else:
            matchedtext = regularexpression.search(self.stc.GetText()[self.findpos:self.targetEnd])

            diff = len(replacetext) - len(findtext)

            x = 0
            notfirst = 0

            favpos = wx.Point(5, 5)
            while matchedtext is not None:

                oldpos = self.findpos
                self.findpos = oldpos + matchedtext.start()
                endpos = oldpos + matchedtext.end()

                if self.parent.prefs.docfolding:
                    self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))
                self.stc.GotoPos(self.findpos)
                self.stc.EnsureCaretVisible()
                self.stc.SetSelectionStart(self.findpos)
                self.stc.SetSelectionEnd(endpos)
                self.stc.SetTargetStart(self.findpos)
                self.stc.SetTargetEnd(endpos)

                d = wx.SingleChoiceDialog(self.parent, ("Знайдено \"" + findtext + "\" у рядку: " \
                + str(self.stc.LineFromPosition(self.findpos)+1) + \
                " позиція: " + str(self.stc.GetColumn(self.findpos)) + \
                "\n(Hit Cancel to Stop)"), "Replace", ["Replace", "Skip"], wx.CHOICEDLG_STYLE)

                if notfirst:
                    d.Move(favpos)
                else:
                    notfirst = 1
                answer = d.ShowModal()
                favpos = d.GetPosition()
                d.Destroy()
                if answer == wx.ID_OK:
                    if d.GetStringSelection() == "Replace":
                        self.stc.ReplaceTarget(replacetext)
                        self.findpos = self.findpos + len(replacetext)
                        self.targetEnd = self.targetEnd + diff
                    else:
                        self.findpos = endpos
                        x = x - 1
                    x = x + 1

                    matchedtext = regularexpression.search(self.stc.GetText()[self.findpos:self.targetEnd])
                else:
                    matchedtext = None

        return x

    def reset(self):
        self.inselection = 0
        self.findflags = 0
        self.findpos = 0
        self.lastposition = 0
        self.backwards = 0
        self.findtext = ""
        self.targetStart = 0
        self.targetEnd = 0
        self.docEnd = 0
        self.RE = 0
        self.rectanglefind = 0
        self.replace_findtext = ""
        self.replace_replacetext = ""
        self.replace_flags = 0
        self.replace_prompt = 0

    def searchInArray(self, regularexpression, arrayposition, position):
        l = len(self.Lines)
        reloffset = position
        match = regularexpression.search(self.Lines[arrayposition][position:])
        if match is None:
            reloffset = 0
            arrayposition += 1
            while arrayposition < l:
                match = regularexpression.search(self.Lines[arrayposition])
                if match is None:
                    arrayposition += 1
                else:
                    return match, arrayposition, reloffset
        return match, arrayposition, reloffset

    def SetFindPos(self, findpos):
        self.findpos = findpos

    def SetFindText(self, findtext):
        self.findtext = findtext

    def SetTargetPositions(self, matchcase):
        self.targetText = self.stc.GetSelectedText()

        self.findflags = matchcase

        if not matchcase:
            self.targetText = self.targetText.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        self.Lines = self.targetText.strip().split(eolchar)

        self.targetText = self.targetText.replace(eolchar, "")

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(self.Lines[0])

        self.positions = []

        for line in self.Lines:
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            self.positions.append(range(position_of_first_character, position_of_first_character+lenline))
            linenumber = linenumber + 1

    def SetTargetRange(self, start, end, backwards = 0):
        self.docEnd = self.stc.GetTextLength()
        self.inselection = (start > 0) | (end < self.docEnd)

        self.findpos = start
        if backwards:
            self.findpos = end
        self.targetStart = start
        self.targetEnd = end

class drFindTextCtrl(wx.ComboBox):
    def __init__(self, parent, id, value, pos, size, returnfunction = None, InFiles = False):
        wx.ComboBox.__init__(self, parent, id, value, pos, size)

        #This is a workaround for a bug in how wx.TextCtrl handles
        #carriage returns on windows.
        self.parent = parent
        if InFiles:
            self.ancestor = parent.parent.parent
        else:
            self.ancestor = parent.parent
        if self.ancestor.PLATFORM_IS_WIN:
            self.doReplace = True
            self.cr = chr(5)
        else:
            self.doReplace = False
            self.cr = '\r'

        self.ID_CHAR_BASE = 20

        self.ID_MENU_BASE = 50

        self.ID_HISTORY_BASE = 420

        self.returnfunc = returnfunction
        if self.returnfunc is None:
            self.returnfunc = self.parent.OnbtnFind

        self.Bind(wx.EVT_CHAR, self.OnChar)

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopUp)

        #wxPython Bug Work-Around
        if self.ancestor.PLATFORM_IS_WIN:
            self.insertionpoint = -1
            self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
            #franz07/19: catch kill focus
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            #endfranz07/19

    def AppendToHistory(self, targetList):
        text = self.GetText()
        try:
            i = targetList.index(text)
            targetList.pop(i)
        except:
            pass

        targetList.append(text)

    def GetText(self):
        text = self.GetValue()
        if self.doReplace:
            return text.replace(chr(5), '\r')
        else:
            return text

    def OnChar(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.parent.OnbtnCancel(event)
        elif event.GetKeyCode() == wx.WXK_RETURN:
            self.returnfunc(event)
        else:
            event.Skip()

    def OnFocus(self, event):
        self.insertionpoint = -1
        event.Skip()

    #franz07/19: do not steal focus
    #drpython: removed "pass", replaced with function code below.
    def OnKillFocus(self, event):
        self.insertionpoint = self.GetInsertionPoint()
        event.Skip()

    #franz07/19

    def OnPopUp(self, event):
        self.PopUp(event.GetPosition())

    def OnPopUpMenu(self, event):
        eid = event.GetId()

        pos = self.GetInsertionPoint()
        #wxPython Bug Work-Around
        if self.ancestor.PLATFORM_IS_WIN:
            if self.insertionpoint > -1:
                pos = self.insertionpoint
        text = self.GetValue()

        if eid == self.ID_CHAR_BASE:
            self.SetValue(text[:pos] + '\t' + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_CHAR_BASE+1:
            self.SetValue(text[:pos] + '\n' + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_CHAR_BASE+2:
            self.SetValue(text[:pos] + self.cr + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_MENU_BASE+1:
            self.Cut()
        elif eid == self.ID_MENU_BASE+2:
            self.Copy()
        elif eid == self.ID_MENU_BASE+3:
            self.Paste()
        elif eid == self.ID_MENU_BASE+4:
            f, to = self.GetSelection()
            self.Remove(f, to)
        elif eid == self.ID_MENU_BASE+5:
            self.SetValue("")

        self.SetFocus()

    def PopUp(self, pos):
        self.PopUpMenu = wx.Menu()

        self.CharMenu = wx.Menu()

        self.CharMenu.Append(self.ID_CHAR_BASE, "Tab (\\t)")
        self.CharMenu.Append(self.ID_CHAR_BASE+1, "Newline (\\n)")
        self.CharMenu.Append(self.ID_CHAR_BASE+2, "Carraige Return (\\r)")

        self.PopUpMenu.Append(self.ID_MENU_BASE+5, "Очистити пошук")

        self.PopUpMenu.AppendSeparator()

        self.PopUpMenu.Append(self.ID_MENU_BASE, "Вставити спецсимвол", self.CharMenu)

        self.PopUpMenu.AppendSeparator()

        self.PopUpMenu.Append(self.ID_MENU_BASE+1, "Вирізати")
        self.PopUpMenu.Append(self.ID_MENU_BASE+2, "Копіювати")
        self.PopUpMenu.Append(self.ID_MENU_BASE+3, "Вставити")
        self.PopUpMenu.Append(self.ID_MENU_BASE+4, "Видалити")

        x = 0
        y = 0
        while x < 6:
            if y < 3:
                self.Bind(wx.EVT_MENU, self.OnPopUpMenu, id=self.ID_CHAR_BASE+y)
                y = y + 1
            self.Bind(wx.EVT_MENU, self.OnPopUpMenu, id=self.ID_MENU_BASE+x)
            x = x + 1

        self.PopupMenu(self.PopUpMenu, pos)

        self.PopUpMenu.Destroy()

    def SetHistory(self, history):
        if self.GetCount() > 0:
            self.Clear()
        l = len(history)
        x = l - 1
        while x > -1:
            self.Append(history[x])
            x = x - 1
        if l > 0:
            self.SetTextSelection(0, len(history[l-1]))

class ReplaceDialog(wx.Dialog):
    def __init__(self, parent, text=""):
        wx.Dialog.__init__(self, parent, -1, title="Заміна",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER)

        statictext = wx.StaticText(self, -1, text)

        btnCancel = wx.Button(self, wx.ID_CANCEL, "Скасувати")
        btnBack = wx.Button(self, wx.ID_BACKWARD, "Назад")
        btnSkip = wx.Button(self, wx.ID_IGNORE, "Пропустити")
        btnReplace = wx.Button(self, wx.ID_REPLACE, "Замінити")

        v_sizer = wx.BoxSizer (wx.VERTICAL)

        v_sizer.Add (statictext, wx.ID_ANY, wx.GROW|wx.ALL, 5)

        line = wx.StaticLine (self, wx.ID_ANY,
          size = (20, -1), style = wx.LI_HORIZONTAL)

        v_sizer.Add (line, 0, wx.GROW|wx.ALL, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn_sizer.Add(btnCancel, wx.GROW|wx.ALL, 5)
        btn_sizer.Add(btnBack, wx.GROW|wx.ALL, 5)
        btn_sizer.Add(btnSkip, wx.GROW|wx.ALL, 5)
        btn_sizer.Add(btnReplace, wx.GROW|wx.ALL, 5)

        v_sizer.Add (btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

        self.SetSizer (v_sizer)
        #v_sizer.Fit (self)

        self.Bind(wx.EVT_BUTTON,  self.OnbtnCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnBack, id=wx.ID_BACKWARD)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnSkip, id=wx.ID_IGNORE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnReplace, id=wx.ID_REPLACE)

        tbl = wx.AcceleratorTable(
            [(wx.ACCEL_NORMAL, ord('c'), wx.ID_CANCEL),
            (wx.ACCEL_NORMAL, ord('b'), wx.ID_BACKWARD),
            (wx.ACCEL_NORMAL, ord('s'), wx.ID_IGNORE),
            (wx.ACCEL_NORMAL, ord('r'), wx.ID_REPLACE),
             ])

        self.SetAcceleratorTable(tbl)
        self.SetFocus() #needed for gtk, else it has no default focus (user must first click onto the dialog) and the esc key is not working
        btnReplace.SetDefault()
        btnReplace.SetFocus()

    def OnbtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnbtnBack(self, event):
        self.EndModal(wx.ID_BACKWARD)

    def OnbtnSkip(self, event):
        self.EndModal(wx.ID_IGNORE)

    def OnbtnReplace(self, event):
        self.EndModal(wx.ID_REPLACE)

class drFindReplaceDialog(wx.Dialog):

    ID_BTNSF = None
    ID_BTNRW = None

    def __init__(self, parent, id, title, stc, IsReplace = 0):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (-1, -1), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

        # TODO: This hack can be removed when all literal IDs are eliminated.
        get_new_id = wx.GetApp().GetTopWindow().GetNewId
        if drFindReplaceDialog.ID_BTNSF is None:
            drFindReplaceDialog.ID_BTNSF = get_new_id()
            drFindReplaceDialog.ID_BTNRW = get_new_id()

        self.parent = parent

        self.stc = stc

        self.theSizer = wx.FlexGridSizer(0, 3, 5, 10)

        self.IsReplace = IsReplace

        #Size Buffer
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Шукати: "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.txtSearchFor = drFindTextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, (250, -1))
        self.btnPopUpSearchFor = wx.Button(self, self.ID_BTNSF, " Меню ")
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.txtSearchFor, 1, wx.SHAPED)
        self.theSizer.Add(self.btnPopUpSearchFor, 1, wx.SHAPED)

        self.txtSearchFor.SetHistory(parent.FindHistory)

        if IsReplace:
            #self.SetSize((400, 345))
            self.txtReplaceWith = drFindTextCtrl(self, -1, "", wx.DefaultPosition, (250, -1))
            self.btnPopUpReplaceWith = wx.Button(self, self.ID_BTNRW, " Меню ")
            self.txtReplaceWith.SetHistory(parent.ReplaceHistory)

        self.chkRegularExpression = wx.CheckBox(self, wx.ID_ANY, "Регулярний вираз")
        self.btnCreateRE = wx.Button(self, wx.ID_ANY, "Створити")
        self.chkMatchCase = wx.CheckBox(self, -1, "Враховувати регістр")
        self.chkFindBackwards = wx.CheckBox(self, -1, "Пошук назад")
        self.chkWholeWord = wx.CheckBox(self, -1, "Слово цілком")
        self.chkInSelection = wx.CheckBox(self, wx.ID_ANY, "У виділеному")
        self.chkFromCursor = wx.CheckBox(self, -1, "Від курсору")

        #Prefs
        self.chkRegularExpression.SetValue(parent.prefs.findreplaceregularexpression)
        self.btnCreateRE.Enable(parent.prefs.findreplaceregularexpression)
        self.chkMatchCase.SetValue(parent.prefs.findreplacematchcase)
        self.chkFindBackwards.SetValue(parent.prefs.findreplacefindbackwards)
        self.chkWholeWord.SetValue(parent.prefs.findreplacewholeword)
        self.chkInSelection.SetValue(parent.prefs.findreplaceinselection)
        self.chkFromCursor.SetValue(parent.prefs.findreplacefromcursor)

        currentselection = len(parent.txtDocument.GetSelectedText()) > 0
        if not currentselection:
            self.chkInSelection.SetValue(0)
        self.chkInSelection.Enable(currentselection)

        if IsReplace:
            self.chkPromptOnReplace  = wx.CheckBox(self, -1, "Заміна за запитом")
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, "Замінити на: "), 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
            self.theSizer.Add(self.txtReplaceWith, 1, wx.SHAPED)
            self.theSizer.Add(self.btnPopUpReplaceWith, 1, wx.SHAPED)

            #self.chkFromCursor.Disable()
            self.chkFindBackwards.Disable()

            #Prefs
            self.chkPromptOnReplace.SetValue(parent.prefs.findreplacepromptonreplace)

            self.Bind(wx.EVT_BUTTON,  self.OnbtnPopUp, id=self.ID_BTNRW)

        #Size Buffer
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkRegularExpression, 1, wx.SHAPED)
        self.theSizer.Add(self.btnCreateRE, 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkMatchCase, 1, wx.SHAPED)
        self.theSizer.Add(self.chkFindBackwards, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkWholeWord, 1, wx.SHAPED)
        self.theSizer.Add(self.chkInSelection, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkFromCursor, 1, wx.SHAPED)
        if IsReplace:
            self.theSizer.Add(self.chkPromptOnReplace, 1, wx.SHAPED)
        else:
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.btnCancel = wx.Button(self, wx.ID_CANCEL)
        self.btnFind = wx.Button(self, wx.ID_FIND)
        self.btnFind.Enable(False)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.btnCancel, 1, wx.SHAPED)
        self.theSizer.Add(self.btnFind, 1, wx.SHAPED)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        self.btnFind.SetDefault()
        self.txtSearchFor.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnbtnFind, self.btnFind)
        self.Bind(wx.EVT_BUTTON, self.OnbtnCreateRE, self.btnCreateRE)
        self.Bind(wx.EVT_BUTTON, self.OnbtnPopUp, id=self.ID_BTNSF)

        self.Bind(wx.EVT_CHECKBOX,  self.OnCheckRegularExpression, self.chkRegularExpression)
        self.Bind(wx.EVT_CHECKBOX,  self.OnCheckInSelection, self.chkInSelection)

        self.Bind(wx.EVT_TEXT, self.OnTextChanged, self.txtSearchFor)

        self.parent.LoadDialogSizeAndPosition(self, "findreplacedialog.sizeandposition.dat")

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, "findreplacedialog.sizeandposition.dat")
        if event is not None:
            event.Skip()

    def GetOptions(self):
        rarray = [self.chkRegularExpression.GetValue(), self.chkMatchCase.GetValue(), \
        self.chkFindBackwards.GetValue(), self.chkWholeWord.GetValue(), \
        self.chkInSelection.GetValue(), self.chkFromCursor.GetValue()]

        if self.IsReplace:
            rarray.append(self.chkPromptOnReplace.GetValue())

        return rarray

    def OnbtnCreateRE(self, event):
        from drRegularExpressionDialog import drRegularExpressionDialog
        d = drRegularExpressionDialog(self, -1, "Створення регулярного виразу")
        d.Show()

    def OnbtnFind(self, event):
        if not self.btnFind.IsEnabled():
            return
        self.Show(0)
        findflags = 0
        findbackwards = self.chkFindBackwards.GetValue()

        isRegularExpression = self.chkRegularExpression.GetValue()
        isMatchCase = self.chkMatchCase.GetValue()

        self.txtSearchFor.AppendToHistory(self.parent.FindHistory)
        if self.IsReplace:
            self.txtReplaceWith.AppendToHistory(self.parent.ReplaceHistory)

        #Set Target Range
        if self.chkInSelection.GetValue():
            selstart = self.stc.GetSelectionStart()
            selend = self.stc.GetSelectionEnd()
            if (selend - selstart) < 1:
                selstart = 0
                selend = self.stc.GetTextLength()
            if self.IsReplace:
                if selstart > selend:
                    selstart, selend = selend, selstart
            self.stc.Finder.SetTargetRange(selstart, selend, findbackwards)
            #Do the Search if it's a rectangle:
            if self.stc.SelectionIsRectangle():
                if self.IsReplace:
                    if isRegularExpression:
                        x = self.stc.Finder.RectangleREReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase)
                        if self.parent.prefs.enablefeedback:
                            drScrolledMessageDialog.ShowMessage(self, (str(x) + " входження \"" + self.txtSearchFor.GetText() + "\" замінено на \"" + self.txtReplaceWith.GetText() + "\""), "Заміна")
                    else:
                        x = self.stc.Finder.RectangleReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase)
                        if self.parent.prefs.enablefeedback:
                            drScrolledMessageDialog.ShowMessage(self, (str(x) + " входження \"" + self.txtSearchFor.GetText() + "\" замінено на \"" + self.txtReplaceWith.GetText() + "\""), "Заміна")
                else:
                    self.stc.Finder.SetTargetPositions(isMatchCase)
                    if isRegularExpression:
                        self.stc.Finder.DoRERectangleFind(self.txtSearchFor.GetText(), isMatchCase)
                    else:
                        self.stc.Finder.DoRectangleFind(self.txtSearchFor.GetText(), isMatchCase, findbackwards)
                self.Close(1)
                return
        else:
            self.stc.Finder.SetTargetRange(0, self.stc.GetTextLength(), findbackwards)


        if self.chkFromCursor.GetValue(): #) and (not self.IsReplace):
            self.stc.Finder.SetFindPos(self.stc.GetCurrentPos())

        if self.chkInSelection.GetValue():
            self.stc.Finder.SetFindPos(selstart)


        statustext = "Пошук: '" + self.txtSearchFor.GetText() + "'"
        if self.IsReplace:
            statustext += ", заміна на: '" + self.txtReplaceWith.GetText()  + "'"
        self.parent.SetStatusText(statustext, 2)

        #Do Search
        if isRegularExpression:
            if self.IsReplace:
                x = self.stc.Finder.REReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase, self.chkPromptOnReplace.GetValue())
                if x == 0:
                    if self.parent.prefs.enablefeedback:
                        drScrolledMessageDialog.ShowMessage(self, "Рядок пошуку: '" + self.txtSearchFor.GetText() + "' не знайдено.", 'Заміна drPython')
                    else:
                        self.parent.SetStatusText("'" + self.txtSearchFor.GetText() + "' НЕ ЗНАЙДЕНО", 2)
                else:
                    if self.parent.prefs.enablefeedback:
                        drScrolledMessageDialog.ShowMessage(self, (str(x) + " входження \"" + self.txtSearchFor.GetText() + "\" замінено на \"" + self.txtReplaceWith.GetText() + "\""), "Заміна")
                    else:
                        self.parent.SetStatusText(str(x) + " входження '" + self.txtSearchFor.GetText() + "' замінено на '" + self.txtReplaceWith.GetText() + "'", 2)
            else:
                if findbackwards:
                    self.stc.Finder.DoREFindBackward(self.txtSearchFor.GetText(), isMatchCase)
                else:
                    self.stc.Finder.DoREFind(self.txtSearchFor.GetText(), isMatchCase)
        else:
            #Set Flags
            if self.chkWholeWord.GetValue():
                findflags = findflags | wx.stc.STC_FIND_WHOLEWORD
            if isMatchCase:
                findflags = findflags | wx.stc.STC_FIND_MATCHCASE

            if self.IsReplace:
                x = self.stc.Finder.ReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), findflags, self.chkPromptOnReplace.GetValue())
                if x == 0:
                    if self.parent.prefs.enablefeedback:
                        drScrolledMessageDialog.ShowMessage(self, "Рядок пошуку: '" + self.txtSearchFor.GetText() + "' не знайдено.", "Заміна DrPython")
                    else:
                        self.parent.SetStatusText("'" + self.txtSearchFor.GetText() + "' НЕ ЗНАЙДЕНО", 2)
                else:
                    if self.parent.prefs.enablefeedback:
                        drScrolledMessageDialog.ShowMessage(self, (str(x) + " входження \"" + self.txtSearchFor.GetText() + "\" замінено на \"" + self.txtReplaceWith.GetText() + "\""), "Заміна")
                    else:
                        self.parent.SetStatusText(str(x) + " входження '" + self.txtSearchFor.GetText() + "' замінено на '" + self.txtReplaceWith.GetText() + "'", 2)
            else:
                self.stc.Finder.DoFind(self.txtSearchFor.GetText(), findflags, findbackwards)

        self.Close(1)

        if self.IsReplace:
            self.parent.ReplaceOptions = self.GetOptions()
        else:
            self.parent.FindOptions = self.GetOptions()
        if findbackwards:
            self.stc.Finder.ScrollFewLinesBelow()
        else:
            self.stc.Finder.ScrollFewLinesAbove()
#        top = self.parent.txtDocument.GetCurrentLine() - self.parent.txtDocument.LinesOnScreen()/2
#        if top < 0:
#            top = 0
#        self.parent.txtDocument.ScrollToLine(top)

    def OnbtnPopUp(self, event):
        eid = event.GetId()
        if eid == self.ID_BTNSF:
            s = self.txtSearchFor.GetPosition()[0]
            x = self.btnPopUpSearchFor.GetPosition()[0]
            self.txtSearchFor.PopUp((x-s, 0))
        elif eid == self.ID_BTNRW:
            s = self.txtReplaceWith.GetPosition()[0]
            x = self.btnPopUpReplaceWith.GetPosition()[0]
            self.txtReplaceWith.PopUp((x-s, 0))

    def OnCheckRegularExpression(self, event):
        usingRegularExpressions = self.chkRegularExpression.GetValue()
        self.btnCreateRE.Enable(usingRegularExpressions)
        self.chkWholeWord.Enable(not usingRegularExpressions)
        self.OnCheckBackwards(None)

    def OnCheckInSelection(self, event):
        self.chkFromCursor.Enable(not self.chkInSelection.GetValue())
        self.OnCheckBackwards(None)

    def OnCheckBackwards(self, event):
        enableFindBackwards = True
        if self.IsReplace:
            enableFindBackwards = False
        if self.chkRegularExpression.GetValue() and self.chkInSelection.GetValue():
            enableFindBackwards = False
        self.chkFindBackwards.Enable(enableFindBackwards)

    def OnTextChanged(self, event):
        self.btnFind.Enable(len(self.txtSearchFor.GetText()) > 0)

    def SetFindString(self, findstring):
        self.txtSearchFor.SetValue(findstring)
        self.txtSearchFor.SetTextSelection(0, len(findstring))
        self.OnTextChanged(None)

    def SetOptions(self, OptionsArray):
        if OptionsArray:
            self.chkRegularExpression.SetValue(OptionsArray[0])
            self.btnCreateRE.Enable(OptionsArray[0])
            self.chkMatchCase.SetValue(OptionsArray[1])
            self.chkFindBackwards.SetValue(OptionsArray[2])
            self.chkWholeWord.SetValue(OptionsArray[3])
            self.chkInSelection.SetValue(OptionsArray[4])
            currentselection = len(self.parent.txtDocument.GetSelectedText()) > 0
            if not currentselection:
                self.chkInSelection.SetValue(0)
            self.chkInSelection.Enable(currentselection)

            self.chkFromCursor.SetValue(OptionsArray[5])

            if self.IsReplace:
                self.chkPromptOnReplace.SetValue(OptionsArray[6])

        self.OnCheckRegularExpression(None)
        self.OnCheckInSelection(None)
        self.OnCheckBackwards(None)
