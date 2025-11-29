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

# drStyleDialog

import string, os.path
import logging
import warnings
import wx
import wx.stc
from drProperty import *
import drScrolledMessageDialog
from drPrefsFile import ExtractPreferenceFromText

LOG = logging.getLogger(__name__)

class drColorPanel(wx.Panel):

    def __init__(self, parent, id, point, size, fg):
        wx.Panel.__init__(self, parent, id, point, size)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.txtColor = wx.TextCtrl(self, wx.ID_ANY, "", wx.Point(0, 10), (100, -1))

        self.isForeground = fg

        self.red = wx.Slider(self, wx.ID_ANY, 0, 0, 255, wx.Point(0, 40), (100, 45), wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.green = wx.Slider(self, wx.ID_ANY, 0, 0, 255, wx.Point(0, 80), (100, 45), wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.blue = wx.Slider(self, wx.ID_ANY, 0, 0, 255, wx.Point(0, 120), (100, 45), wx.SL_HORIZONTAL | wx.SL_LABELS)

        self.theSizer.Add(self.txtColor, 0, wx.SHAPED)
        self.theSizer.Add(self.red, 0, wx.SHAPED)
        self.theSizer.Add(self.green, 0, wx.SHAPED)
        self.theSizer.Add(self.blue, 0, wx.SHAPED)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.Bind(wx.EVT_SCROLL, self.OnScroll)
        self.red.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.green.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.blue.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.txtColor)

    def GetValue(self):
        return self.txtColor.GetValue()

    def OnLeftUp(self, event):
        self.txtColor.SetEditable(True)
        event.Skip()

    def OnScroll(self, event):
        #self.txtColor.SetEditable(False) # unnecessary and makes problems
        widget = event.GetEventObject()
        if widget is self.red:
            r = self.red.GetValue()
            sr = ''
            if r < 16:
                sr = '0'
            sr = sr + hex(r)[2:]
            sr = sr.upper()
            text = self.txtColor.GetValue()
            if len(text) != 7:
                drScrolledMessageDialog.ShowMessage(self, "Текстове поле має містити дані на кшталт:\n#0033AA,\nПочатковий символ має бути #, потім 6 символів 0-9 або a-f.\nDrPython ігнорує будь-які зміни кольору, що не відповідають цим правилам.", "Помилка")
                return
            self.txtColor.SetValue(text[0:1] + sr + text[3:])
        elif widget is self.green:
            g = self.green.GetValue()
            sr = ''
            if g < 16:
                sr = '0'
            sr = sr + hex(g)[2:]
            sr = sr.upper()
            text = self.txtColor.GetValue()
            if len(text) != 7:
                drScrolledMessageDialog.ShowMessage(self, "Текстове поле має містити дані на кшталт:\n#0033AA,\nПочатковий символ має бути #, потім 6 символів 0-9 або a-f.\nDrPython ігнорує будь-які зміни кольору, що не відповідають цим правилам.", "Помилка")
                return
            self.txtColor.SetValue(text[0:3] + sr + text[5:])
        elif widget is self.blue:
            b = self.blue.GetValue()
            sr = ''
            if b < 16:
                sr = '0'
            sr = sr + hex(b)[2:]
            sr = sr.upper()
            text = self.txtColor.GetValue()
            if len(text) != 7:
                drScrolledMessageDialog.ShowMessage(self, "Текстове поле має містити дані на кшталт:\n#0033AA,\nПочатковий символ має бути #, потім 6 символів 0-9 або a-f.\nDrPython ігнорує будь-які зміни кольору, що не відповідають цим правилам.", "Помилка")
                return
            self.txtColor.SetValue(text[0:5] + sr + text[7:])
        event.Skip()

    def OnTextChange(self, event):
        v = self.txtColor.GetValue()
        if self.txtColor.IsEditable():
            if not v:
                self.red.Enable(False)
                self.green.Enable(False)
                self.blue.Enable(False)
                return
            if (v[0] == "#") and (len(v) == 7):
                #Update Sliders
                self.red.Enable(True)
                self.green.Enable(True)
                self.blue.Enable(True)
                try:
                    self.red.SetValue(int(v[1:3], 16))
                    self.green.SetValue(int(v[3:5], 16))
                    self.blue.SetValue(int(v[5:7], 16))
                except:
                    drScrolledMessageDialog.ShowMessage(self, ("Помилкові дані кольору.  Має бути записано на кшталт #00A3F4\nВикористовуйте тільки цифри 0-9 і символи A-F"), "Помилка")
            else:
                self.red.Enable(False)
                self.green.Enable(False)
                self.blue.Enable(False)
        if len(v) == 7:
            if v[0] == "#":
                #Update Parent
                if self.isForeground:
                    self.GetParent().foreground = v
                else:
                    self.GetParent().background = v
                self.GetParent().SetColor()
        event.Skip()

    def SetValue(self, colorstring):
        self.txtColor.SetValue(colorstring)
        r = int(colorstring[1:3], 16)
        g = int(colorstring[3:5], 16)
        b = int(colorstring[5:7], 16)
        self.red.SetValue(r)
        self.green.SetValue(g)
        self.blue.SetValue(b)

#*****************************************

class drSeparatorDialog(wx.Dialog):

    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, (500, 300))

        self.parent = parent
       
        self.favorites = {
            0: ('#000000', '#CAFFFF'),
            1: ('#000000', '#FFFFC6'),
            2: ('#000000', '#BEFFC6'),
            3: ('#000000', '#FFA400'),
            4: ('#000000', '#A0A0A0')
        }

        self.favoritefile = os.path.join(self.parent.datdirectory, "separator.favorite.colours.dat")

        self.txtLabel = wx.TextCtrl(self, -1, "текст розділювача", size=(400, 32), style=wx.TE_PROCESS_ENTER | wx.TE_RICH2)
        self.txtLabel.SetSelection(0, 1)

        self.btn0 = wx.Button(self, 0, '&0', style=wx.BU_EXACTFIT)
        self.btn1 = wx.Button(self, 1, '&1', style=wx.BU_EXACTFIT)
        self.btn2 = wx.Button(self, 2, '&2', style=wx.BU_EXACTFIT)
        self.btn3 = wx.Button(self, 3, '&3', style=wx.BU_EXACTFIT)
        self.btn4 = wx.Button(self, 4, '&4', style=wx.BU_EXACTFIT)

        self.btnSave = wx.Button(self, wx.ID_SAVE, "Зберегти обране")

        self.bgPanel = drColorPanel(self, -1, (-1, -1), (300, 200), False)
        self.bgPanel.SetValue('#FFFFFF')

        self.btnCancel = wx.Button(self, wx.ID_CANCEL)
        self.btnOk = wx.Button(self, wx.ID_OK)

        self.LoadFavorites()

        # Sizer:
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.textSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.favoritesSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Додавання елементів до текстових та кнопкових сізерів        

        self.favoritesSizer.Add(self.btn0, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.favoritesSizer.Add(self.btn1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.favoritesSizer.Add(self.btn2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.favoritesSizer.Add(self.btn3, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.favoritesSizer.Add(self.btn4, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.favoritesSizer.Add(self.btnSave, 0, wx.ALL | wx.ALIGN_CENTER, 5)
       
        self.panelSizer.Add(self.bgPanel, 1, wx.EXPAND | wx.ALL, 10)

        self.buttonSizer.Add(self.btnCancel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.buttonSizer.Add(self.btnOk, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Додавання всіх сізерів до головного сізера
        self.theSizer.Add(self.txtLabel,0,wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, "Обрані кольори:"), 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.theSizer.Add(self.favoritesSizer, 0, wx.ALIGN_CENTER)
        self.theSizer.Add(self.panelSizer, 1, wx.EXPAND) 
        self.theSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.OnFavorite, id=0)
        self.Bind(wx.EVT_BUTTON, self.OnFavorite, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnFavorite, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnFavorite, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnFavorite, id=4)
        self.Bind(wx.EVT_BUTTON, self.OnbtnSave, self.btnSave)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.txtLabel.Bind(wx.EVT_CHAR, self.OnChar)
        if parent.PLATFORM_IS_GTK: #does not get initially the focus (bug tracker #1903778, "Open Imported Module: focus problem", 29.02.2008: from Jon White, thanks.
            self.SetFocus()

    def GetLabel(self):
        c = self.bgPanel.GetValue()
        if c=="#000000":
            c="#101010"    
        return self.txtLabel.GetValue(),c

    def LoadFavorites(self):
        if os.path.exists(self.favoritefile):
            try:
                f = open(self.favoritefile, 'r',encoding="UTF-8")
                text = f.read()
                f.close()

                for fL in range(5):
                    result = ExtractPreferenceFromText(text, str(fL))
                    if result:
                        results = result.split(',')
                        if len(results) == 2:
                            self.favorites[fL] = results
            except:
                self.parent.ShowMessage("Помилка завантаження обраних кольорів", "Помилка")

    def OnbtnSave(self, event):
        d = wx.SingleChoiceDialog(self, "Зберегти обраний колір до набору?", "Збереження обраного", ['0', '1', '2', '3', '4'], wx.OK|wx.CANCEL)
        answer = d.ShowModal()
        i = d.GetSelection()
        d.Destroy()
        if answer == wx.ID_OK:
            try:
                self.favorites[i] = ("#000000", self.bgPanel.GetValue())
                f = open(self.favoritefile, 'w',encoding="UTF-8")
                x = 0
                l = len(self.favorites)
                while x < l:
                    f.write('<' + str(x) + '>' + self.favorites[x][0] + ',' + self.favorites[x][1] + '</' + str(x) + '>')
                    x += 1
                f.close()
            except:
                self.parent.ShowMessage("Помилка при збереженні обраних кольорів", "Помилка")

    def OnChar(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

    def OnFavorite(self, event):
        i = event.GetId()

        #self.fgPanel.SetValue(self.favorites[i][0])
        self.bgPanel.SetValue(self.favorites[i][1])

    def SetColor(self):
        #self.txtLabel.SetForegroundColour(wx.Colour(self.fgPanel.red.GetValue(), self.fgPanel.green.GetValue(), self.fgPanel.blue.GetValue()))
        self.txtLabel.SetBackgroundColour(wx.Colour(self.bgPanel.red.GetValue(), self.bgPanel.green.GetValue(), self.bgPanel.blue.GetValue()))

#*****************************************

class drSimpleStyleDialog(wx.Dialog):

    def __init__(self, parent, id, title, stylestring, defaultstylestring, ChangeSpec = 0):

        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (-1, -1))

        LOG.debug('init')
        self.Enum = wx.FontEnumerator()
        self.Enum.EnumerateFacenames()
        self.FontList = self.Enum.GetFacenames()
        self.FontList.sort()

        self.OK = False

        self.font = getStyleProperty("face", stylestring)
        if not self.font:
            self.font = getStyleProperty("face", defaultstylestring)
        self.size = getStyleProperty("size", stylestring)
        if not self.size:
            self.size = getStyleProperty("size", defaultstylestring)
        self.foreground = getStyleProperty("fore", stylestring)
        if not self.foreground:
            self.foreground = getStyleProperty("fore", defaultstylestring)
        self.background = getStyleProperty("back", stylestring)
        if not self.background:
            self.background = getStyleProperty("back", defaultstylestring)
        self.bold = getStyleProperty("bold", stylestring)
        self.italic = getStyleProperty("italic", stylestring)
        self.underline = getStyleProperty("underline", stylestring)
        self.txtPreview = wx.stc.StyledTextCtrl(self, wx.ID_ANY, wx.Point(225, 15), (225, 150))

        if ChangeSpec > 0:
            self.font = getStyleProperty("face", defaultstylestring)
            self.size = getStyleProperty("size", defaultstylestring)
            if ChangeSpec == 1:
                self.background = getStyleProperty("back", defaultstylestring)
            elif ChangeSpec == 3:
                self.foreground = getStyleProperty("fore", defaultstylestring)

        if self.font not in self.FontList:
            old = self.font
            self.size = '12'
            options = ["Courier","Courier 10 Pitch","Monospace","Sans",""]
            for font in options:
                if font in self.FontList:
                    self.font = font
                    break
            drScrolledMessageDialog.ShowMessage(self, ("Шрифт за замовчуванням [%s] не знайдено! \nНатомість застосовано [%s]." %(old,self.font)), "Помилка")

        self.txtPreview.SetText("print('Hello world')\n()[]{}\n0123")
        self.txtPreview.SetUseHorizontalScrollBar(0)

        self.txtPreview.SetReadOnly(1)
        self.txtPreview.SetMarginWidth(0, 0)
        self.txtPreview.SetMarginWidth(1, 0)
        self.txtPreview.SetMarginWidth(2, 0)

        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))

        self.txtPreview.StyleClearAll()

        self.txtPreview.StartStyling(0)

        self.boxFonts = wx.ListBox(self, wx.ID_ANY, wx.Point(10, 10), (250, 250), self.FontList)

        try:
            i = self.boxFonts.FindString(self.font)
            if i < 0:
                i = 0
            self.boxFonts.Select(i)
            self.boxFonts.SetFirstItem(i)
        except:
            drScrolledMessageDialog.ShowMessage(self, ("Сталося щось незрозуміле під час спроби \nвстановити шрифт за замовчуванням."), "Помилка")
            self.boxFonts.SetSelection(0)

        self.boxSize = wx.ComboBox(self, wx.ID_ANY, self.size, wx.Point(10, 175), (150, 50), list(map(str, range(8, 31))))

        self.fgPanel = drColorPanel(self, wx.ID_ANY, wx.Point(10, 200), (400, 225), True)
        self.fgPanel.SetValue(self.foreground)
        self.bgPanel = drColorPanel(self, wx.ID_ANY, wx.Point(220, 200), (400, 225), False)
        self.bgPanel.SetValue(self.background)

        self.chkBold = wx.CheckBox(self, wx.ID_BOLD, "Жирний", wx.Point(10, 345))
        if self.bold:
            self.chkBold.SetValue(1)
        self.chkItalic = wx.CheckBox(self, wx.ID_ITALIC, "Курсив", wx.Point(110, 345))
        if self.italic:
            self.chkItalic.SetValue(1)
        self.chkUnderline = wx.CheckBox(self, wx.ID_UNDERLINE, "Підкреслено", wx.Point(210, 345))
        if self.underline:
            self.chkUnderline.SetValue(1)

        if ChangeSpec > 0:
            self.boxFonts.Enable(False)
            self.boxSize.Enable(False)
            self.chkBold.Enable(False)
            self.chkItalic.Enable(False)
            self.chkUnderline.Enable(False)
            if ChangeSpec == 1:
                self.bgPanel.Enable(False)
            elif ChangeSpec == 3:
                self.fgPanel.Enable(False)

        self.btnCancel = wx.Button(self, wx.ID_CANCEL)
        self.btnOk = wx.Button(self, wx.ID_OK)

        #Sizer:

        self.theSizer = wx.FlexGridSizer(0, 2, 5, 1)
        self.styleSizerLeft = wx.BoxSizer(wx.VERTICAL)
        self.styleSizerRight = wx.BoxSizer(wx.VERTICAL)

        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "Шрифт:"), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(self.boxFonts, 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "Розмір:"), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(self.boxSize, 0, wx.ALL|wx.SHAPED, 4)

        self.styleSizerLeft.Add(self.chkBold, 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(self.chkItalic, 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerLeft.Add(self.chkUnderline, 0, wx.ALL|wx.SHAPED, 4)

        self.styleSizerRight.Add(self.txtPreview, 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerRight.Add(wx.StaticText(self, wx.ID_ANY, "Колір символів:"), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerRight.Add(self.fgPanel, 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerRight.Add(wx.StaticText(self, wx.ID_ANY, "Колір тла:"), 0, wx.ALL|wx.SHAPED, 4)
        self.styleSizerRight.Add(self.bgPanel, 1, wx.ALL|wx.SHAPED, 4)

        self.theSizer.Add(self.styleSizerLeft, 0, wx.ALL|wx.SHAPED, 4)
        self.theSizer.Add(self.styleSizerRight, 0, wx.ALL|wx.SHAPED, 4)
        self.theSizer.Add(self.btnCancel, 0, wx.ALL|wx.SHAPED|wx.ALIGN_RIGHT, 4)
        self.theSizer.Add(self.btnOk, 0, wx.ALL | wx.SHAPED|wx.ALIGN_LEFT, 4)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        self.btnCancel.SetDefault()

        #End Sizer

        self.Bind(wx.EVT_LISTBOX, self.OnFontSelect, self.boxFonts)
        self.Bind(wx.EVT_COMBOBOX, self.OnSizeSelect, self.boxSize)
        self.Bind(wx.EVT_TEXT, self.OnChangeSize, self.boxSize)
        self.Bind(wx.EVT_CHECKBOX, self.OnBold, self.chkBold)
        self.Bind(wx.EVT_CHECKBOX, self.OnItalic, self.chkItalic)
        self.Bind(wx.EVT_CHECKBOX, self.OnUnderline, self.chkUnderline)
        self.Bind(wx.EVT_BUTTON, self.OnbtnOk, self.btnOk)

    def OnChangeSize(self, event):
        self.size = self.boxSize.GetValue()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnFontSelect(self, event):
        self.font = self.boxFonts.GetStringSelection()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnSizeSelect(self, event):
        self.size = self.boxSize.GetStringSelection()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def SetColor(self):
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnBold(self, event):
        if self.chkBold.IsChecked():
            self.bold = "bold"
        else:
            self.bold = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnItalic(self, event):
        if self.chkItalic.IsChecked():
            self.italic = "italic"
        else:
            self.italic = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnUnderline(self, event):
        if self.chkUnderline.IsChecked():
            self.underline = "underline"
        else:
            self.underline = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0, 0xff)

    def OnbtnOk(self, event):
        """
        :todo: Remove this method when `ClickedOk()` is gone.
        """
        self.OK = True
        self.EndModal(wx.ID_OK)

    def ClickedOk(self):
        warnings.warn("`ClickedOk` is deprecated."
                      " Use the return value of `ShowModal()` instead",
                      DeprecationWarning, 2)
        return self.OK

    def GetBackground(self):
        return self.background

    def GetColorString(self):
        return ("fore:" + self.foreground + ",back:" + self.background)

    def GetForeground(self):
        return self.foreground

    def GetStyleString(self):
        return ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline)

class drStyleDialog(wx.Dialog):

    def __init__(self, parent, id, title, isPrompt = False):

        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (640, 700))
        
        self.ancestor = parent.grandparent.parent
        self.last = 0

        if isPrompt:
            self.txtPromptStyleDictionary = self.ancestor.prefs.txtPromptStyleDictionary.copy()
        else:
            self.PythonStyleDictionary = self.ancestor.prefs.PythonStyleDictionary.copy()
            self.CPPStyleDictionary = self.ancestor.prefs.CPPStyleDictionary.copy()
            self.HTMLStyleDictionary = self.ancestor.prefs.HTMLStyleDictionary.copy()

        self.targetArray = []

        self.ChangeSpec = 0

        self.Enum = wx.FontEnumerator()
        self.Enum.EnumerateFacenames()
        self.FontList = self.Enum.GetFacenames()
        self.FontList.sort()

        self.txtPreview = wx.stc.StyledTextCtrl(self, wx.ID_ANY, wx.Point(225, 15), (225, 125))

        self.Ok = False

        self.isPrompt = isPrompt

        i = self.ancestor.txtDocument.filetype
        if i > 2:
            i = 0
        self.boxLanguage = wx.Choice(self, wx.ID_ANY, wx.Point(150, 135), (-1, -1), ["Python", "C/C++", "HTML"])
        self.boxLanguage.SetSelection(i)

        if isPrompt:
            self.boxLanguage.Enable(False)

        self.txtPreview.SetText('print("Hello, world!")\n()[]{}\n0123')
        self.txtPreview.SetUseHorizontalScrollBar(0)

        self.txtPreview.SetMarginWidth(0, 0)
        self.txtPreview.SetMarginWidth(1, 0)
        self.txtPreview.SetMarginWidth(2, 0)

        self.txtPreview.SetReadOnly(1)

        self.boxFonts = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (200, 250), self.FontList)

        self.boxSize = wx.ComboBox(self, wx.ID_ANY, "10", wx.DefaultPosition, (150, 50), list(map(str, range(8, 31))))

        self.fgPanel = drColorPanel(self, wx.ID_ANY, wx.DefaultPosition, (100, 200), True)
        self.bgPanel = drColorPanel(self, wx.ID_ANY, wx.DefaultPosition, (100, 200), False)

        self.chkBold = wx.CheckBox(self, wx.ID_BOLD, "Жирний")
        self.chkItalic = wx.CheckBox(self, wx.ID_ITALIC, "Курсив")
        self.chkUnderline = wx.CheckBox(self, wx.ID_UNDERLINE, "Підкреслено")

        self.btnCancel = wx.Button(self, wx.ID_CANCEL)
        self.btnCancel.SetDefault()
        self.btnOk = wx.Button(self, wx.ID_OK)

        self.boxStyle = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (150, 350), [""])

        #Sizer:

        self.theSizer = wx.FlexGridSizer(4, 3, 1, 1)
        self.selectSizer = wx.FlexGridSizer(4, 3, 1, 10)
        self.listSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.styleSizerLeft = wx.BoxSizer(wx.VERTICAL)
        self.styleSizerRight = wx.BoxSizer(wx.VERTICAL)
        
        self.styleSizerRight.Add(wx.StaticText(self, wx.ID_ANY, "Перегляд:"), 0, wx.SHAPED)
        self.styleSizerRight.Add(self.txtPreview, 0, wx.SHAPED)
        
        self.styleSizerRight.Add(wx.StaticText(self, wx.ID_ANY, "Коліт символів:"), 0, wx.SHAPED)
        self.styleSizerRight.Add(self.fgPanel, 0, wx.SHAPED)
        
        self.styleSizerRight.Add(wx.StaticText(self, wx.ID_ANY, "Колір тла:"), 0, wx.SHAPED)
        self.styleSizerRight.Add(self.bgPanel, 0, wx.SHAPED)
        
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "Шрифт:"), 0, wx.SHAPED)
        self.styleSizerLeft.Add(self.boxFonts, 0, wx.SHAPED)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "Розмір:"), 0, wx.SHAPED)
        self.styleSizerLeft.Add(self.boxSize, 0, wx.SHAPED)

        self.styleSizerLeft.Add(self.chkBold, 0, wx.SHAPED)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.SHAPED)
        self.styleSizerLeft.Add(self.chkItalic, 0, wx.SHAPED)
        self.styleSizerLeft.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.SHAPED)
        self.styleSizerLeft.Add(self.chkUnderline, 0, wx.SHAPED)




        self.listSizer.Add(wx.StaticText(self, wx.ID_ANY, "Мова: "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.listSizer.Add(self.boxLanguage, 0, wx.ALIGN_CENTER | wx.SHAPED)

        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0, wx.ALIGN_LEFT | wx.SHAPED)
        self.selectSizer.Add(self.listSizer, 0, wx.ALIGN_LEFT | wx.SHAPED)
        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.ALIGN_LEFT | wx.SHAPED)

        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0, wx.ALIGN_LEFT | wx.SHAPED)
        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, "Тип тексту:"), 0, wx.ALIGN_LEFT | wx.SHAPED)
        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, "   "), 0, wx.ALIGN_LEFT | wx.SHAPED)

        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.selectSizer.Add(self.boxStyle, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.selectSizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0,  wx.SHAPED | wx.ALIGN_CENTER)

        self.theSizer.Add(self.selectSizer, 0, wx.SHAPED)
        self.theSizer.Add(self.styleSizerLeft, 0, wx.SHAPED)
        self.theSizer.Add(self.styleSizerRight, 0, wx.SHAPED)
        self.theSizer.Add(self.btnCancel, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0, wx.SHAPED)
        self.theSizer.Add(self.btnOk, 1, wx.SHAPED | wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        #End Sizer

        self.OnSelectLanguage(None)

        self.Bind(wx.EVT_LISTBOX, self.OnFontSelect, self.boxFonts)
        self.Bind(wx.EVT_LISTBOX, self.OnSelectStyle, self.boxStyle)
        self.Bind(wx.EVT_CHOICE, self.OnSelectLanguage, self.boxLanguage)
        self.Bind(wx.EVT_COMBOBOX, self.OnSizeSelect, self.boxSize)
        self.Bind(wx.EVT_TEXT, self.OnChangeSize, self.boxSize)
        self.Bind(wx.EVT_CHECKBOX, self.OnBold, self.chkBold)
        self.Bind(wx.EVT_CHECKBOX, self.OnItalic, self.chkItalic)
        self.Bind(wx.EVT_CHECKBOX, self.OnUnderline, self.chkUnderline)
        self.Bind(wx.EVT_BUTTON, self.OnbtnOk, self.btnOk)

    def OnChangeSize(self, event):
        self.size = self.boxSize.GetValue()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnFontSelect(self, event):
        self.font = self.boxFonts.GetStringSelection()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnSizeSelect(self, event):
        self.size = self.boxSize.GetStringSelection()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def SetColor(self):
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnBold(self, event):
        if self.chkBold.IsChecked():
            self.bold = "bold"
        else:
            self.bold = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnItalic(self, event):
        if self.chkItalic.IsChecked():
            self.italic = "italic"
        else:
            self.italic = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnUnderline(self, event):
        if self.chkUnderline.IsChecked():
            self.underline = "underline"
        else:
            self.underline = ""
        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

    def OnbtnOk(self, event):

        if self.ChangeSpec == 0:
            self.targetArray[self.last] = self.GetStyleString()
        elif self.ChangeSpec == 1:
            self.targetArray[self.last] = self.GetForeground()
        elif self.ChangeSpec == 2:
            self.targetArray[self.last] = self.GetColorString()
        elif self.ChangeSpec == 3:
            self.targetArray[self.last] = self.GetBackground()

        self.Ok = True
        self.EndModal(wx.ID_OK)

    def ClickedOk(self):
        return self.Ok

    def GetArrays(self):
        if self.isPrompt:
            return self.txtPromptStyleDictionary
        return self.PythonStyleDictionary, self.CPPStyleDictionary, self.HTMLStyleDictionary

    def GetBackground(self):
        return self.background

    def GetColorString(self):
        return ("fore:" + self.foreground + ",back:" + self.background)

    def GetForeground(self):
        return self.foreground

    def GetStyleString(self):
        return ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline)

    def OnSelectLanguage(self, event):
        sel = self.boxLanguage.GetSelection()

        try:
            if self.ChangeSpec == 0:
                self.targetArray[self.last] = self.GetStyleString()
            elif self.ChangeSpec == 1:
                self.targetArray[self.last] = self.GetForeground()
            elif self.ChangeSpec == 2:
                self.targetArray[self.last] = self.GetColorString()
            elif self.ChangeSpec == 3:
                self.targetArray[self.last] = self.GetBackground()
        except:
            #This will happen the first time this function is called.
            pass

        if self.isPrompt:
            self.targetArray = self.txtPromptStyleDictionary
            array = ["Normal", "Line Number (Margin)", "Brace-Selected (Match)", "Brace-Selected (No Match)", "Character (Single Quoted String)", "Class Name", "Comment", "Comment Block", "Function Name", "Keyword", "Number", "Operator", "String", "String EOL", "Triple Quoted String", "Caret Foreground", "Selection"]
        else:
            if sel == 1:
                self.targetArray = self.CPPStyleDictionary
                array = ["Normal", "Line Number (Margin)", "Brace-Selected (Match)", "Brace-Selected (No Match)", "Character", "Preprocessor", "Comment", "Verbatim", "Keyword", "C Identifier", "Number", "Operator", "String", "String EOL", "Global Class", "Regex", "UUID", "Caret Foreground", "Selection", "Folding", "Long Line Indicator", "Current Line Highlight"]
            elif sel == 2:
                self.targetArray = self.HTMLStyleDictionary
                array = ["Normal", "Line Number (Margin)", "Brace-Selected (Match)", "Brace-Selected (No Match)", "Tag", "Unkown Tag", "Atrribute", "Unkown Attribute", "Number", "String", "Character (Single Quoted String)", "Comment", "Entity", "Tag End", "XML Start", "XML End", "Script", "Value", "Caret Foreground", "Selection", "Folding", "Long Line Indicator", "Current Line Highlight"]
            else:
                self.targetArray = self.PythonStyleDictionary
                array = ["Normal", "Line Number (Margin)", "Brace-Selected (Match)", "Brace-Selected (No Match)", "Character (Single Quoted String)", "Class Name", "Comment", "Comment Block", "Function Name", "Keyword", "Number", "Operator", "String", "String EOL", "Triple Quoted String", "Caret Foreground", "Selection", "Folding", "Long Line Indicator", "Current Line Highlight", "Indentation Guide"]

        self.last = -1

        self.boxStyle.Set(array)
        self.boxStyle.SetSelection(0)
        self.OnSelectStyle(event)

    def OnSelectStyle(self, event):
        current = self.boxStyle.GetSelection()
        #strange, in gtk after the above lines (when select langauge, the current selection seems to be -1, should be 0)
        #so simply ignore that event, if the selection is out of the borders
        if current == -1:
            return
        seltext = self.boxStyle.GetStringSelection()

        if self.last > -1:
            if self.ChangeSpec == 0:
                self.targetArray[self.last] = self.GetStyleString()
            elif self.ChangeSpec == 1:
                self.targetArray[self.last] = self.GetForeground()
            elif self.ChangeSpec == 2:
                self.targetArray[self.last] = self.GetColorString()
            elif self.ChangeSpec == 3:
                self.targetArray[self.last] = self.GetBackground()

        self.ChangeSpec = 0

        stylestring = self.targetArray[current]
        if (seltext == "Caret Foreground") or (seltext == "Long Line Indicator") or (seltext == "Indentation Guide"):
            self.ChangeSpec = 1
            stylestring = "fore:" + stylestring
        elif (seltext == "Selection") or (seltext == "Folding"):
            self.ChangeSpec = 2
        elif seltext == "Current Line Highlight":
            self.ChangeSpec = 3
            stylestring = "back:" + stylestring

        self.font = getStyleProperty("face", stylestring)
        if not self.font:
            self.font = getStyleProperty("face", self.targetArray[0])
        self.size = getStyleProperty("size", stylestring)
        if not self.size:
            self.size = getStyleProperty("size", self.targetArray[0])
        self.foreground = getStyleProperty("fore", stylestring)
        if not self.foreground:
            self.foreground = getStyleProperty("fore", self.targetArray[0])
        self.background = getStyleProperty("back", stylestring)
        if not self.background:
            self.background = getStyleProperty("back", self.targetArray[0])
        self.bold = getStyleProperty("bold", stylestring)
        self.italic = getStyleProperty("italic", stylestring)
        self.underline = getStyleProperty("underline", stylestring)

        if self.ChangeSpec > 0:
            self.font = getStyleProperty("face", self.targetArray[0])
            self.size = getStyleProperty("size", self.targetArray[0])
            if self.ChangeSpec == 1:
                self.background = getStyleProperty("back", self.targetArray[0])
            elif self.ChangeSpec == 3:
                self.foreground = getStyleProperty("fore", self.targetArray[0])

        if self.font not in self.FontList:
            f1 = string.capwords(self.font)
            f2 = string.lower(self.font)
            if f1 in self.FontList:
                self.font = f1
            elif f2 in self.FontList:
                self.font = f2

        if self.font not in self.FontList:
            old = self.font
            self.size = '12'
            options = ["Courier","Courier 10 Pitch","Monospace","Sans",""]
            for font in options:
                if font in self.FontList:
                    self.font = font
                    break
            #I don't know why this a traceback: no foreground !!!
            #drScrolledMessageDialog.ShowMessage(self, ("Default font [%s] not found! \nChoosed [%s] instead." %(old,self.font)), "Error")
            print("Шрифт за замовчуванням [%s] не знайдено! \nНатомість обрано [%s]." %(old,self.font))

        self.txtPreview.StyleResetDefault()
        self.txtPreview.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, ("fore:" + self.foreground + ",back:" + self.background + ",size:" + self.size + ",face:" + self.font + "," + self.bold + "," + self.italic + "," + self.underline))
        self.txtPreview.StyleClearAll()
        self.txtPreview.StartStyling(0)

        try:
            #self.boxFonts.SetStringSelection(self.font)
            i = self.boxFonts.FindString(self.font)
            if i < 0:
                i = 0
            self.boxFonts.Select(i)
            #self.boxFonts.EnsureVisible(i) # Bug: Doesn't work
            self.boxFonts.SetFirstItem(i)
        except:
            drScrolledMessageDialog.ShowMessage(self, ("Сталося щось незрозуміле під час спроби \nвстановити шрифт за замовчуванням."), "Помилка")
            self.boxFonts.SetSelection(0)

        try:
            tsizearray = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
            if not self.size in tsizearray:
                self.boxSize.SetValue(self.size)
            else:
                i = tsizearray.index(self.size)
                self.boxSize.SetSelection(i)
        except:
            drScrolledMessageDialog.ShowMessage(self, ("Сталося щось незрозуміле під час спроби \nвстановити шрифт за замовчуванням."), "Помилка")
            self.boxSize.SetSelection(0)

        self.OnSizeSelect(event)

        self.fgPanel.SetValue(self.foreground)
        self.bgPanel.SetValue(self.background)

        self.chkBold.SetValue((len(self.bold) > 0))
        self.chkItalic.SetValue((len(self.italic) > 0))
        self.chkUnderline.SetValue((len(self.underline) > 0))

        self.boxFonts.Enable(self.ChangeSpec == 0)
        self.boxSize.Enable(self.ChangeSpec == 0)
        self.chkBold.Enable(self.ChangeSpec == 0)
        self.chkItalic.Enable(self.ChangeSpec == 0)
        self.chkUnderline.Enable(self.ChangeSpec == 0)
        if self.ChangeSpec == 1:
            self.fgPanel.Enable(True)
            self.bgPanel.Enable(False)
        elif self.ChangeSpec == 3:
            self.fgPanel.Enable(False)
            self.bgPanel.Enable(True)
        else:
            self.fgPanel.Enable(True)
            self.bgPanel.Enable(True)

        self.last = current
