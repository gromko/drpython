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

#Menus

import os.path
import wx
ua_dict= {"Новий" : "New",
"Відкрити" : "Open",
"Відкрити імпортований модуль" : "Open Imported Module",
"Перезавантажити файл" : "Reload File",
"Закрити" : "Close",
"Зберегти" : "Save",
"Зберегти як" : "Save As",
"Зберегти як копію" : "Save A Copy",
"Зберегти вміст консолі до файлу" : "Save Prompt Output To File",
"Налаштування друку" : "Print Setup",
"Закладки":"Bookmarks",
"Друк файлу" : "Print File",
"Друк вмісту консолі" : "Print Prompt",
"Вихід" : "Exit",
"Збільшити відступ" : "Indent",
"Зменшити відступ" : "Dedent",
"У верхній регістр" : "Uppercase",
"У нижній регістр" : "Lowercase",
"Скасувати" : "Undo",
"Повернути" : "Redo",
"Вставити розділювач в код" : "Insert Separator",
"Вставити регулярний вираз" : "Insert Regular Expression",
"Пошук" : "Find",
"Знайти наступне" : "Find Next",
"Знайти попереднє" : "Find Previous",
"Замінити" : "Replace",
"Згорнути/розгорнути" : "Toggle Fold",
"Згорнути все" : "Fold All",
"Розгорнути все" : "Expand All",
"Перейти до початку блоку" : "Go To Block Start",
"Перейти до кінця блоку" : "Go To Block End",
"Перейти до початку визначення класу" : "Go To Class Start",
"Перейти до кінця визначення класу" : "Go To Class End",
"Перейти до початку функції" : "Go To Def Start",
"Перейти до кінця функції" : "Go To Def End",
"Перейти до рядка" : "Go To",
"Збільшити символи" : "Zoom In",
"Зменшити символи" : "Zoom Out",
"Перехід за структурою" : "Source Browser Go To",
"Показати/сховати індикатори пропусків" : "Toggle View Whitespace",
"Встановити аргументи" : "Set Arguments",
"Python" : "Python",
"Налаштування" : "Preferences",
"Налаштувати сполучення клавіш" : "Customize Shortcuts",
"Налаштувати вигулькнe меню" : "Customize Pop Up Menu",
"Налаштувати панель засобів" : "Customize ToolBar",
"Змінити закладки" : "Edit Bookmarks",
"Змінити меню скриптів" : "Edit &Script Menu",
"Help" : "Help",
"Перекляд документації Python" : "View Python Docs",
"Перегляд документації WxWidgets" : "View WxWidgets Docs",
"Посібник по регулярних виразах" : "View Regular Expression Howto",
"Вирізати":"Cut",
"Копіювати":"Copy",
"Вставити":"Paste",
"Видалити":"Delete",
"Обрати все":"Select All",
"Виконати":"Run",
"Зупинити":"End",
"Перевірити синтаксис":"Check Syntax"  
}

class drMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent
        self.bitmapdirectory = os.path.join(self.parent.programdirectory, "bitmaps/16")
    
    def AAppend(self, id, label, LaunchesDialog = False, AmpersandAt = -1, AbsoluteLabel=""):
        #Appends the item, any applicable bitmap, and also any keyboard shortcut.

        item = wx.MenuItem(self, id, self.parent.getmenulabel(label, LaunchesDialog, AmpersandAt, AbsoluteLabel))
        eng_label = ua_dict[label]
        bitmap = os.path.join(self.bitmapdirectory, eng_label + ".png")
       
        if os.path.exists(bitmap):
            item.SetBitmap(wx.Bitmap(wx.Image(bitmap, wx.BITMAP_TYPE_PNG)))

        return self.Append(item)
    
