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

# Bookmarks Dialog

import wx
import os
from drScrolledMessageDialog import ShowMessage
from drFileDialog import FileDialog
from drTreeDialog import drTreeDialog

import wx

def BuildTreeFromString(dialog, branch, thestring):
    line = " "
    roots = [branch]
    rootindex = 0
    lastCount = 1
    i = 0
    lastI = 0

    # Skip the First Line
    i = thestring.find('\n')
    if i > -1:
        line = thestring[0:(i + 1)]
        lastI = i + 1
    thestring = thestring[lastI:]

    # Get On With It!
    while line:
        i = thestring.find('\n')
        if i > -1:
            line = thestring[0:(i + 1)]
            lastI = i + 1
            thestring = thestring[lastI:]
            c = line.count('\t')
            line = line[c:].rstrip()
            while lastCount > c:
                roots.pop()
                rootindex -= 1
                lastCount -= 1
            currentItem = dialog.datatree.AppendItem(roots[rootindex], line)

            # Встановлення значків для елементів дерева
            if line[0] == '>':
                dialog.datatree.SetItemImage(currentItem, 0, wx.TreeItemIcon_Normal)  # Закритий стан
                dialog.datatree.SetItemImage(currentItem, 1, wx.TreeItemIcon_Expanded)  # Розкритий стан
                roots.append(currentItem)
                rootindex += 1
                lastCount = c + 1
            else:
                dialog.datatree.SetItemImage(currentItem, 2, wx.TreeItemIcon_Normal)  # Звичайний елемент
                dialog.datatree.SetItemImage(currentItem, 2, wx.TreeItemIcon_Selected)  # Вибраний елемент
        else:
            line = ""


def WriteBranch(tree, branch, filehandle, tablevel):
    t = tree.GetItemText(branch)
    isfolder = (t[0] == '>')
    y = '\t' * tablevel + t + "\n"
    filehandle.write(y)
    if isfolder:
        ccount = tree.GetChildrenCount(branch, 0)
        if ccount > 0:
            b, cookie = tree.GetFirstChild(branch)
            WriteBranch(tree, b, filehandle, (tablevel + 1))
            for _ in range(1, ccount):
                b, cookie = tree.GetNextChild(branch, cookie)
                WriteBranch(tree, b, filehandle, (tablevel + 1))

class drBookmarksDialog(drTreeDialog):

    def __init__(self, parent, bookmarksfile):
        drTreeDialog.__init__(self, parent, "Edit Bookmarks", "Bookmarks", bookmarksfile, parent.prefs.bookmarksstyle,
                             "bookmarksdialog.sizeandposition.dat", os.path.join(parent.bitmapdirectory, "16/bookmark.png"), BuildTreeFromString, WriteBranch)

        # Створення ImageList для значків
        self.image_list = wx.ImageList(16, 16)  # Розмір значків 16x16 пікселів

        # Завантаження значків (замініть шляхи на ваші)
        self.folder_closed_icon = wx.Bitmap(os.path.join(parent.bitmapdirectory,"16/folder.png"), wx.BITMAP_TYPE_PNG)
        self.folder_open_icon = wx.Bitmap(os.path.join(parent.bitmapdirectory,"16/folder open.png"), wx.BITMAP_TYPE_PNG)
        self.file_icon = wx.Bitmap(os.path.join(parent.bitmapdirectory,"16/bookmark.png"), wx.BITMAP_TYPE_PNG)

        # Додавання значків до ImageList
        self.folder_closed_idx = self.image_list.Add(self.folder_closed_icon)
        self.folder_open_idx = self.image_list.Add(self.folder_open_icon)
        self.file_idx = self.image_list.Add(self.file_icon)

        # Призначення ImageList до TreeCtrl
        self.datatree.AssignImageList(self.image_list)

        self.ID_ADD = wx.NewIdRef()
        self.btnAdd = wx.Button(self, self.ID_ADD, "Додати")
        self.cmdSizer.Prepend(self.btnAdd, 0, wx.SHAPED)
        self.SetupSizer()
        self.Bind(wx.EVT_BUTTON, self.OnbtnAdd, id=self.ID_ADD)

        if parent.PLATFORM_IS_GTK:
            self.SetFocus()

    def OnbtnAdd(self, event):
        sel = self.datatree.GetSelection()
        if not sel.IsOk():
            if self.datatree.GetCount() < 2:
                sel = self.datatree.GetRootItem()
            else:
                return
        if self.datatree.GetItemText(sel)[0] == '>':
            d = wx.SingleChoiceDialog(self, "Додати до Закладок:", "Додати закладку", ["обрати теку", "обрати файл", "за іменем", "поточний файл"], wx.OK | wx.CANCEL)
            d.SetSize((250, 200))
            answer = d.ShowModal()
            d.Destroy()
            if answer == wx.ID_OK:
                s = d.GetStringSelection()
                addentry = str()
                if s == "замітка":
                    d = wx.TextEntryDialog(self, "Введіть текст:", "Додати за іменем", "")
                    if d.ShowModal() == wx.ID_OK:
                        addentry = d.GetValue().replace('\\', '/')
                    d.Destroy()
                elif s == "обрати теку":
                    d = wx.DirDialog(self, "Оберіть теку:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON | wx.MAXIMIZE_BOX)
                    if self.parent.ddirectory:
                        try:
                            d.SetPath(self.parent.ddirectory)
                        except:
                            ShowMessage(self.parent, ("Помилка встановлення поточної теки: " + self.parent.ddirectory), "Помилка drPython")
                    if d.ShowModal() == wx.ID_OK:
                        addentry = d.GetPath().replace('\\', '/')
                    d.Destroy()
                elif s == "обрати файл":
                    dlg = FileDialog(self.parent, "Оберіть файл", self.wildcard)
                    if self.parent.ddirectory:
                        try:
                            dlg.SetDirectory(self.parent.ddirectory)
                        except:
                            drScrolledMessageDialog.ShowMessage(self.parent, ("Помилка встановлення поточної теки: " + self.parent.ddirectory), "Помилка drPython")
                    if dlg.ShowModal() == wx.ID_OK:
                        
                        addentry = dlg.GetPaths()[0].replace('\\', '/')
                    dlg.Destroy()
                else: # Select current file
                    if self.parent.txtDocument.filename:
                        addentry = self.parent.txtDocument.filename
                    else:
                        drScrolledMessageDialog.ShowMessage(self.parent, "Не можу додати до Закладок (не ымёя файлу)\nПопередньо збережіть файл", "Помилка drPython")

                if addentry:
                    #check for duplicates
                    add = True
                    self.GetCurrentItems()
                    if addentry in self.curentries:
                        answer = wx.MessageBox("Це вже було: '" + addentry + "'\nДодати знову до Закладок?", "Повідомлення", wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT)
                        if answer != wx.YES:
                            add = False
                    if add:
                        currentItem = self.datatree.AppendItem(sel, addentry)
                        self.datatree.SetItemImage(currentItem, 2, wx.TreeItemIcon_Normal)
                        self.datatree.SetItemImage(currentItem, 2, wx.TreeItemIcon_Selected)
                        self.datatree.SetModified()
        else:
            drScrolledMessageDialog.ShowMessage(self, "You can only add a bookmark to a folder.\nSelect either \"Bookmarks\", or a folder.", "Bad Bookmark Folder")
