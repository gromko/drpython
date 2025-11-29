#   Programmer: Daniel Pozmanter (modified by Franz Steinhaeusler)
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2005 Daniel Pozmanter, Franz Steinhaeusler
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

#Plugin
#SearchInFiles
#Original Daniel Pozmanter SearchInFiles 1.0.0
#Modifications by Franz Steinhaeusler for version 1.1.0
#Modifications by Franz Steinhaeusler for version 1.1.1
#Modifications by Franz Steinhaeusler for version 1.1.2
#Modifications by Franz Steinhaeusler for version 1.1.3
#
#Modifications by Franz Steinhaeusler for version 1.1.4, until 02.10.2004
#bug-report (thanks Dan Pozmanter)
#   replace dialog was to small on linux; added SetSizerAndFit
#feature request: (thanks Dan Pozmanter)
#   option: savelastresults and dialog size and position)

#Modifications by Franz Steinhaeusler for version 1.1.5, until 09.10.2004
#thanks Robin Dunn (accelerator keys) and Peter Damoc (listctrl sort bug help)

#Modifications by Franz Steinhaeusler for version 1.1.6, until 10.10.2004
#Modifications by Franz Steinhaeusler for version 1.1.7, until 11.10.2004
#Modifications by Franz Steinhaeusler for version 1.1.8, until 12.10.2004

#Modifications by Franz Steinhaeusler for version 1.1.9, until 12.10.2004
#Modifications by Franz Steinhaeusler for version 1.1.9.1, until 14.10.2004
#Modifications by Franz Steinhaeusler for version 1.1.9.2, until 15.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.0, until 16.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.1, until 17.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.2, until 20.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.3 beta, until 23.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.4 beta, until 24.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.5 beta, until 26.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.6, until 30.10.2004
#Modifications by Franz Steinhaeusler for version 1.2.7, 01.11.2004
#Modifications by Franz Steinhaeusler for version 1.2.8, 13.11.2004
#Modifications by Franz Steinhaeusler for version 1.2.9, 21.01.2005
#Modifications by Franz Steinhaeusler for version 1.3.0, 24.01.2005
#Modifications by Franz Steinhaeusler for version 1.3.1, 15.02.2005
#Modifications by Franz Steinhaeusler for version 1.3.2, 14.07.2005
#patch from Master_Jaf for searching currently open files; thanks.
#Modifications by Franz Steinhaeusler for version 1.3.3, 08.04.2007
#Modifications by Franz Steinhaeusler for version 1.3.4, 19.02.2008

#for Changes please see Changelog.txt

#this is needed for PyChecker
#import sys
#sys.path.append('c:/Eigene Dateien/python/drpython')


import wx
import wx.stc
import os, re, shutil
from drFindReplaceDialog import drFindTextCtrl
import drPrefsFile
import _thread
import time
import stat
from io import BytesIO
import locale
from drRegularExpressionDialog import drRegularExpressionDialog
import drScrolledMessageDialog
import  wx.gizmos   as  gizmos
from functools import reduce


def OnAbout(DrFrame):
    Version = '1.3.6'
    NameAndVersion = "SearchInFiles:\n\nVersion: %s\n" % Version
    AboutString = NameAndVersion + \
    "Original (1.0.0) by Daniel Pozmanter\n\nReleased under the GPL.\n\
Modified (from 1.1.0 - %s) by Franz Steinhaeusler.\n\
Submitted Patch by Master_Jaf for 1.3.2.\n\
    " % Version
    DrFrame.ShowMessage (AboutString, "About")
def OnHelp(DrFrame):
    helpstring = \
"(Dan Pozmanter)\n\
Find/Replace In Files:\n\n\
This is a simple extension for find/replace to\n\
act on all files of a matching pattern ('*.*')\n\
in a given directory.\n\n\
The Replace In Files Dialog has an option to\n\
undo all Replace Operations for the files\n\
altered.  This information is stored in program.\n\n\
If you use the Prompt On replace Option, you can\n\
select which matches to replace in each file.\n\n\n\
(Franz Steinhaeusler)\n\
Added after 1.0.0:\n\n\
You can add several directories separated with ';' characters\n\
and ignore directories with - after the semicolon (example C:/drpython;-/bitmaps)\n\
Also several filepatterns separated with ';' characters; or simply leave out (same as *.*)\n\n\
History for directories, filepattern and search strings are saved.\n\
\n\
It is possible to leave out the searchstring: all files are listed and the find lasts not so long.\n\
\n\
threaded search: you can stop and also edit in the editor, if the search takes longer time.\n\n\
Possibility to save 'Last Results'.\n\n\
Store dialog size and position (manual, automatic).\n\
Set Current Path of active document for the directory path (via menu or alt-a).\n\
Store File search results column sizes (manual, automatic).\n\n\
Sort the results of every column (also with function keys F2, F3 ...\n\n\
Detail view (founded lines and expanded view, where you can navigate with alt-curor down/up or with the buttons).\n\
keys 'v' (view) and 'e' (change betweeen expanded and filtered view).\n\
alt-right, left (next/previous file).\n\n\
With marking a word or if not, the word under cursor can be used to quickly start a new search ('f' key or button 'Find').\n\
right click on SearchResults: Select or Details.\n\n\
Preferences:\n\
Occurances: how often is a string found in search;\n\
this is displayed in the last column (the search takes more time then).\n\
Save Sorting (of column headers).\n\
Sort Case sensitive (this makes more sense in linux as in Windows).\n\n\
You can search all open files with Edit => Currently open files with \n\
a hotkey Alt-O for faster access; idea and patch from Master_Jaf; thanks.\n\n\
There are menu items in Edit for managing \"Favorites\". You can add you current search dir to favorites,\n\
edit the favorites and insert the favorites.\n\
"
    drScrolledMessageDialog.ShowMessage(DrFrame, helpstring, "Help", size = (500, 500))


def OnPreferences(DrFrame):
    d = SearchInFilesPrefsDialog(DrFrame, -1)
    d.ShowModal()
    d.Destroy()


def UnInstall(DrFrame):
    plugindir = DrFrame.pluginsdirectory
    prefsdir = DrFrame.pluginspreferencesdirectory
    userdir = DrFrame.pluginsdatdirectory
    shortcutsdir = DrFrame.pluginsshortcutsdirectory
    if os.path.exists(plugindir + "/bitmaps/16/Find In Files.png"):
        os.remove(plugindir + "/bitmaps/16/Find In Files.png")
    if os.path.exists(plugindir + "/bitmaps/24/Find In Files.png"):
        os.remove(plugindir + "/bitmaps/24/Find In Files.png")
    if os.path.exists(plugindir + "/bitmaps/16/Replace In Files.png"):
        os.remove(plugindir + "/bitmaps/16/Replace In Files.png")
    if os.path.exists(plugindir + "/bitmaps/24/Replace In Files.png"):
        os.remove(plugindir + "/bitmaps/24/Replace In Files.png")
    if os.path.exists(plugindir + "/bitmaps/drpython_searchinfiles.png"):
        os.remove(plugindir + "/bitmaps/drpython_searchinfiles.png")
    if os.path.exists(userdir + "/SearchInFilesHistory.log"):
        os.remove(userdir + "/SearchInFilesHistory.log")
    if os.path.exists(userdir + "/searchinfiles.sizeposcolumn.dat"):
        os.remove(userdir + "/searchinfiles.sizeposcolumn.dat")
    if os.path.exists(prefsdir + "/SearchInFiles.preferences.dat"):
        os.remove(prefsdir + "/SearchInFiles.preferences.dat")
    if os.path.exists(shortcutsdir + "/SearchInFiles.shortcuts.dat"):
        os.remove(shortcutsdir + "/SearchInFiles.shortcuts.dat")
    if os.path.exists(userdir + "/searchinfiles.viewstcsizepos.dat"):
        os.remove(userdir + "/searchinfiles.viewstcsizepos.dat")
    DrFrame.RemovePluginIcon("Find In Files")
    DrFrame.RemovePluginIcon("Replace In Files")

    return True


#**********************************************************************

class SearchInFilesPrefsDialog(wx.Dialog):

    def __init__(self, parent, id):

        wx.Dialog.__init__(self, parent, id, "Search In Files Preferences", wx.Point(50, 50), \
                        (282, 540), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

        self.parent = parent

        self.chkregularexpression = wx.CheckBox(self, -1, "")
        self.chkmatchcase = wx.CheckBox(self, -1, "")
        self.chksubdirectories = wx.CheckBox(self, -1, "")
        self.chkpromptonreplace = wx.CheckBox(self, -1, "")
        self.chkbackupbeforereplace = wx.CheckBox(self, -1, "")
        self.chkwordundercursor = wx.CheckBox(self, -1, "")
        self.chkusefindhistory = wx.CheckBox(self, -1, "")
        self.chkputsearchtohistoryforfind = wx.CheckBox(self, -1, "")
        self.chkSaveSizePosition = wx.RadioBox(self, -1, "Size/Position/Columnwidths", \
                                            choices = ["Do not save", "Save manually", "Save automatically"],\
                                            style = wx.RA_SPECIFY_ROWS)
        self.chkColumnWidths= wx.RadioBox(self, -1, "Columnwidths", \
                                            choices = ["No save", "Save Absolut", "Save Percentage"],\
                                            style = wx.RA_SPECIFY_ROWS)
        self.chkappenddironbrowse = wx.CheckBox(self, -1, "")
        self.chkSaveLastResults = wx.CheckBox(self, -1, "")
        self.chkSearchInThread = wx.CheckBox(self, -1, "")
        self.chkSortCaseSensitive = wx.CheckBox(self, -1, "") #especially in windows, one don't care about case in filenames
        self.chkSaveSorting = wx.CheckBox(self, -1, "")
        self.chkOccurances = wx.CheckBox(self, -1, "")

        self.chkregularexpression.SetValue(self.parent.SEARCHINFILESPREFSregularexpression)
        self.chkmatchcase.SetValue(self.parent.SEARCHINFILESPREFSmatchcase)
        self.chksubdirectories.SetValue(self.parent.SEARCHINFILESPREFSsubdirectories)
        self.chkpromptonreplace.SetValue(self.parent.SEARCHINFILESPREFSpromptonreplace)
        self.chkbackupbeforereplace.SetValue(self.parent.SEARCHINFILESPREFSbackupbeforereplace)
        self.chkwordundercursor.SetValue(self.parent.SEARCHINFILESPREFSwordundersursor)
        self.chkusefindhistory.SetValue(self.parent.SEARCHINFILESPREFSusefindhistory)
        self.chkputsearchtohistoryforfind.SetValue(self.parent.SEARCHINFILESPREFSputsearchtohistoryforfind)

        self.chkSaveSizePosition.SetSelection(self.parent.SEARCHINFILESPREFSsavesizeposition)
        self.chkappenddironbrowse.SetValue(self.parent.SEARCHINFILESPREFSappenddironbrowse)
        self.chkSaveLastResults.SetValue(self.parent.SEARCHINFILESPREFSsavelastresults)
        self.chkColumnWidths.SetSelection(self.parent.SEARCHINFILESPREFScolumnwidths)
        self.chkSearchInThread.SetValue(self.parent.SEARCHINFILESPREFSsearchinthread)
        self.chkSortCaseSensitive.SetValue(self.parent.SEARCHINFILESPREFSsortcasesensitive)
        self.chkSaveSorting.SetValue(self.parent.SEARCHINFILESPREFSsavesorting)
        self.chkOccurances.SetValue(self.parent.SEARCHINFILESPREFSoccurances)

        self.theSizer = wx.FlexGridSizer(0, 3, 3, 5)

        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Regular Expression:"),1,wx.GROW)
        self.theSizer.Add(self.chkregularexpression, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Match Case:"),1,wx.GROW)
        self.theSizer.Add(self.chkmatchcase, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Subdirectories:"),1,wx.GROW)
        self.theSizer.Add(self.chksubdirectories, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Word under Cursor:"),1,wx.GROW)
        self.theSizer.Add(self.chkwordundercursor, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Use Find History:"),1,wx.GROW)
        self.theSizer.Add(self.chkusefindhistory, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Put Search to history for Find:"),1,wx.GROW)
        self.theSizer.Add(self.chkputsearchtohistoryforfind, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Prompt O&n Replace:"),1,wx.GROW)
        self.theSizer.Add(self.chkpromptonreplace, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Backup Before Replace:"),1,wx.GROW)
        self.theSizer.Add(self.chkbackupbeforereplace, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

        self.theSizer.Add(self.chkSaveSizePosition, 1, wx.GROW)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkColumnWidths, 1, wx.GROW)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Append Dir on Browse:"),1,wx.GROW)
        self.theSizer.Add(self.chkappenddironbrowse, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Save LastResults:"),1,wx.GROW)
        self.theSizer.Add(self.chkSaveLastResults, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Search In Thread:"),1,wx.GROW)
        self.theSizer.Add(self.chkSearchInThread, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Sort Case Sensitive:"),1,wx.GROW)
        self.theSizer.Add(self.chkSortCaseSensitive, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Save Sorting:"),1,wx.GROW)
        self.theSizer.Add(self.chkSaveSorting, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Occurances:"),1,wx.GROW)
        self.theSizer.Add(self.chkOccurances, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 1, wx.SHAPED)


        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "&Close")
        self.btnSave = wx.Button(self, wx.ID_OK, "&Save And Update")
        self.btnSave.SetDefault()

        self.buttonSizer.Add(self.btnCancel, 1, wx.SHAPED)
        self.buttonSizer.Add(self.btnSave, 1, wx.GROW)

        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.buttonSizer, 0, wx.SHAPED | wx.ALIGN_CENTER)
        #print self.theSizer.GetCols(), self.theSizer.GetRows()

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        if parent.PLATFORM_IS_WIN:
            self.SetSizerAndFit(self.theSizer)

        self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnSave, id = wx.ID_OK)
        self.Bind(wx.EVT_RADIOBOX,  self.OnSizePos, id = -1)

    def OnSizePos (self, event):
        if event.GetSelection() == 0:
            if os.path.exists (DrFrame.pluginsdatdirectory + 'searchinfiles.sizeposcolumn.dat'):
                answer = wx.MessageBox("Delete sizeandposition entries?", "Warning", wx.YES_NO | wx.ICON_QUESTION)
                if answer == wx.YES:
                    os.remove(DrFrame.pluginsdatdirectory + 'searchinfiles.sizeposcolumn.dat')


    def OnbtnClose(self, event):
        self.EndModal(0)

    def OnbtnSave(self, event):
        self.parent.SEARCHINFILESPREFSregularexpression = int(self.chkregularexpression.GetValue())
        self.parent.SEARCHINFILESPREFSmatchcase = int(self.chkmatchcase.GetValue())
        self.parent.SEARCHINFILESPREFSpromptonreplace = int(self.chkpromptonreplace.GetValue())
        self.parent.SEARCHINFILESPREFSsubdirectories = int(self.chksubdirectories.GetValue())
        self.parent.SEARCHINFILESPREFSbackupbeforereplace = int(self.chkbackupbeforereplace.GetValue())
        self.parent.SEARCHINFILESPREFSwordundersursor = int(self.chkwordundercursor.GetValue())
        self.parent.SEARCHINFILESPREFSusefindhistory = int(self.chkusefindhistory.GetValue())
        self.parent.SEARCHINFILESPREFSputsearchtohistoryforfind = int(self.chkputsearchtohistoryforfind.GetValue())
        self.parent.SEARCHINFILESPREFSsavesizeposition = int(self.chkSaveSizePosition.GetSelection())
        self.parent.SEARCHINFILESPREFScolumnwidths = int(self.chkColumnWidths.GetSelection())
        self.parent.SEARCHINFILESPREFSappenddironbrowse = int (self.chkappenddironbrowse.GetValue())
        self.parent.SEARCHINFILESPREFSsavelastresults = int(self.chkSaveLastResults.GetValue())
        self.parent.SEARCHINFILESPREFSsearchinthread = int(self.chkSearchInThread.GetValue())
        self.parent.SEARCHINFILESPREFSsortcasesensitive = int(self.chkSortCaseSensitive.GetValue())
        self.parent.SEARCHINFILESPREFSsavesorting = int(self.chkSaveSorting.GetValue())
        #Occurrances need restart

        preffile = self.parent.pluginspreferencesdirectory + "/SearchInFiles.preferences.dat"
        f = open(preffile, 'w',encoding="UTF-8")

        f.write("<search.in.files.regularexpression>" + str(self.parent.SEARCHINFILESPREFSregularexpression) + "</search.in.files.regularexpression>\n")
        f.write("<search.in.files.match.case>" + str(self.parent.SEARCHINFILESPREFSmatchcase) + "</search.in.files.match.case>\n")
        f.write("<search.in.files.prompt.on.replace>" + str(self.parent.SEARCHINFILESPREFSpromptonreplace) + "</search.in.files.prompt.on.replace>\n")
        f.write("<search.in.files.subdirectories>" + str(self.parent.SEARCHINFILESPREFSsubdirectories) + "</search.in.files.subdirectories>\n")
        f.write("<search.in.files.backup.before.replace>" + str(self.parent.SEARCHINFILESPREFSbackupbeforereplace) + "</search.in.files.backup.before.replace>\n")
        f.write("<search.in.files.wordundercursor>" + str(self.parent.SEARCHINFILESPREFSwordundersursor) + "</search.in.files.wordundercursor>\n")
        f.write("<search.in.files.usefindhistory>" + str(self.parent.SEARCHINFILESPREFSusefindhistory) + "</search.in.files.usefindhistory>\n")
        f.write("<search.in.files.putsearchtohistoryforfind>" + str(self.parent.SEARCHINFILESPREFSputsearchtohistoryforfind) + "</search.in.files.putsearchtohistoryforfind>\n")
        f.write("<search.in.files.savesizeposition>" + str(self.parent.SEARCHINFILESPREFSsavesizeposition) + "</search.in.files.savesizeposition>\n")
        f.write("<search.in.files.columnwidths>" + str(self.parent.SEARCHINFILESPREFScolumnwidths) + "</search.in.files.columnwidths>\n")
        f.write("<search.in.files.appenddironbrowse>" + str(self.parent.SEARCHINFILESPREFSappenddironbrowse) + "</search.in.files.appenddironbrowse>\n")
        f.write("<search.in.files.savelastresults>" + str(self.parent.SEARCHINFILESPREFSsavelastresults) + "</search.in.files.savelastresults>\n")
        f.write("<search.in.files.searchinthread>" + str(self.parent.SEARCHINFILESPREFSsearchinthread) + "</search.in.files.searchinthread>\n")
        f.write("<search.in.files.sortcasesensitive>" + str(self.parent.SEARCHINFILESPREFSsortcasesensitive) + "</search.in.files.sortcasesensitive>\n")
        f.write("<search.in.files.savesorting>" + str(self.parent.SEARCHINFILESPREFSsavesorting) + "</search.in.files.savesorting>\n")
        f.write("<search.in.files.occurances>" + str(int(self.chkOccurances.GetValue())) + "</search.in.files.occurances>\n")

        if int(self.chkOccurances.GetValue()) != self.parent.SEARCHINFILESPREFSoccurances:
            self.parent.ShowMessage("Occurances changed:\n You need to restart SearchInFiles!", "Changed Occurances")

        f.close()
        if self.GetParent().prefs.enablefeedback:
            self.parent.ShowMessage("Succesfully wrote to:\n" + preffile + "\nand updated the current instance of DrPython.", "Saved Preferences")

#**********************************************************************

class drMyRegularExpressionDialog(drRegularExpressionDialog):
    def __init__(self, parent, id, title, prompthasfocus = 0, infiles = 0):
        drRegularExpressionDialog.__init__(self, parent, id, title, prompthasfocus, infiles)

    def OnbtnOk(self, event):
        self.Show(0)

        result = self.txtRE.GetValue()
        l = len(result)
        if l > 0:
            self.parent.panel.cBoxSearchFor.SetValue(result)

        self.Close(1)

class drMultipleItemQuestionDialog(wx.Dialog):

    def __init__(self, parent, title, results, iteritems):
        wx.Dialog.__init__(self, parent, -1, title, wx.Point(50, 50), (790, 400), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        #proportional font would be better?
        #font f = wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL)
        #f.SetFaceName ("Courier")
        #self.SetFont(f)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.boxItems = wx.ListBox(self, 405)
        self.boxItems.AppendItems(results)

        self.iteritems = iteritems

        self.theSizer.Add(self.boxItems, 1, wx.EXPAND)

        self.btnClose = wx.Button(self, 401, "&Skip File")
        self.btnOk = wx.Button(self, 402, "&Ok")
        self.btnQuit = wx.Button(self, 403, "&Quit")

        self.commandSizer.Add(self.btnClose, 0, wx.ALIGN_LEFT | wx.SHAPED)
        self.commandSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnOk, 0, wx.SHAPED)
        self.commandSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnQuit, 0, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.theSizer.Add(self.commandSizer, 0, wx.ALIGN_CENTER | wx.SHAPED)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.answer = 0

        self.Bind(wx.EVT_LISTBOX_DCLICK,  self.OnRemoveItem, id = 405)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id = 401)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnOk, id = 402)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnQuit, id = 403)
        
        
    def GetAnswer(self):
        return self.answer

    def GetResults(self):
        return self.iteritems

    def OnbtnQuit(self, event):
        self.answer = 2
        self.EndModal(0)

    def OnbtnClose(self, event):
        self.answer = 0
        self.EndModal(0)

    def OnbtnOk(self, event):
        self.answer = 1
        self.EndModal(0)

    def OnRemoveItem(self, event):
        answer = wx.MessageBox("Remove Match (" + self.boxItems.GetStringSelection() + ")?", "Remove", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            i = self.boxItems.GetSelection()
            self.iteritems.pop(i)
            self.boxItems.Delete(i)

class FilesListCtrl (wx.ListCtrl):
    def __init__(self, parent, id, pos, size):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style = wx.LC_REPORT|wx.SUNKEN_BORDER )
        self.SetBackgroundColour(wx.Colour(231, 239, 239))
        self.parent = parent
        self.drframe = parent.parent.parent

        self.columndwithsabsdefault = [50, 250, 160, 70, 70, 120, 70]
        self.columndwithsabs = self.columndwithsabsdefault[:]
        sumall = reduce(lambda x, y: x + y, self.columndwithsabs)
        self.columndwithspercent = map(lambda x: x * 1000/ sumall, self.columndwithsabs)
        if self.drframe.SEARCHINFILESPREFScolumnwidths:
            self.parent.LoadDialogColumnwidths(self, 'searchinfiles.sizeposcolumn.dat')

        self.InsertColumn(0, "L",     wx.LIST_FORMAT_LEFT,  self.columndwithsabs[0])
        self.InsertColumn(1, "Path",  wx.LIST_FORMAT_LEFT,  self.columndwithsabs[1])
        self.InsertColumn(2, "Name",  wx.LIST_FORMAT_LEFT,  self.columndwithsabs[2])
        self.InsertColumn(3, "Ext",   wx.LIST_FORMAT_LEFT,  self.columndwithsabs[3])
        self.InsertColumn(4, "Size",  wx.LIST_FORMAT_RIGHT, self.columndwithsabs[4])
        self.InsertColumn(5, "Date",  wx.LIST_FORMAT_LEFT,  self.columndwithsabs[5])
        if self.drframe.PLATFORM_IS_WIN:
            self.InsertColumn(6, "R/O",  wx.LIST_FORMAT_LEFT, self.columndwithsabs[6])
        else:
            self.InsertColumn(6, "Permissions",  wx.LIST_FORMAT_LEFT, self.columndwithsabs[6])
        if self.drframe.SEARCHINFILESPREFSoccurances:
            self.InsertColumn(7, "O",  wx.LIST_FORMAT_LEFT,  self.columndwithsabs[5])

        self.Bind(wx.EVT_KILL_FOCUS,  self.OnKillListFocus)
        self.Bind(wx.EVT_SET_FOCUS,  self.OnSetListFocus)
        self.Bind(wx.EVT_CHAR,  self.OnChar)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.OnListItemSelected)

    def OnListItemSelected(self, event):
        index = event.GetIndex()
        item = self.GetItem(index, 1)
        path = item.GetText()
        item = self.GetItem(index, 2)
        name = item.GetText()
        fname = os.path.join (path, name)
        fname = fname.replace("\\", "/")
        self.parent.statusBar.SetStatusText (fname, 1)
        event.Skip()

    def UnSelectListCtrlItems(self):
        d = -1
        for i in range (self.GetItemCount()):
            d = self.GetNextItem(d, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if d == -1:
                break
            self.SetItemState(d, 0, wx.LIST_STATE_SELECTED)

    def OnChar (self, event, force = False):
        if self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) != -1:
            if force or ((event.GetKeyCode() == wx.WXK_LEFT or event.GetKeyCode() == wx.WXK_RIGHT) and event.AltDown())\
                or event.GetKeyCode() == ord ('v') or event.GetKeyCode() == ord ('e'):
                self.parent.parent.OnView(None)
                index = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                while self.parent.jump_again:
                    self.UnSelectListCtrlItems()
                    if index == -1:
                        index = 0
                    cnt = self.GetItemCount ()
                    if self.parent.jump_again == 1:
                        index += 1
                        if index >= cnt:
                            index = 0
                    else:
                        index -= 1
                        if index < 0:
                            index = cnt - 1
                    self.SetItemState(index, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED , wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                    self.parent.parent.OnView(None, index)
                self.UnSelectListCtrlItems()
                self.SetItemState(index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED , wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)


            else:
                if event.GetKeyCode() == wx.WXK_ESCAPE:
                    self.parent.OnbtnCancel(event)
                else:
                    event.Skip()
        else:
            event.Skip()

    def OnKillListFocus (self, event):
        self.parent.btnFind.SetDefault()
        event.Skip()

    def OnSetListFocus (self, event):
        self.parent.btnSelect.SetDefault()
        event.Skip()


class ComboBoxEditDialog(wx.Dialog):

    """ComboBoxEntryDialog."""
    def __init__(self, parent, title='Edit Favorites', choices=[]):
        """Create the ComboBoxEntryDialog."""
        wx.Dialog.__init__(self, parent, -1, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER)
        elb = gizmos.EditableListBox(self, -1, "Edit List of Favorites", (50,50), (250, 250))
        elb.SetStrings(choices)
        #print self.GetParent().parent.SearchInFiles_favoritenames

        self.elb = elb
        btnCancel = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        btnOk = wx.Button(self, wx.ID_OK, "&Ok")

        self.Bind(wx.EVT_BUTTON, self.OnbtnClose, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnbtnOk, id=wx.ID_OK)

        v_sizer = wx.BoxSizer (wx.VERTICAL)
        v_sizer.Add (elb, wx.ID_ANY, wx.GROW|wx.ALL, 5)

        line = wx.StaticLine (self, wx.ID_ANY,
          size=(20, -1), style=wx.LI_HORIZONTAL)

        v_sizer.Add (line, 0, wx.GROW|wx.ALL, 5)

        btn_sizer = wx.StdDialogButtonSizer()

        btn_sizer.AddButton(btnCancel)
        btn_sizer.AddButton(btnOk)
        btn_sizer.Realize()

        v_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

        self.SetSizer(v_sizer)
        #v_sizer.Fit(self)
        self.SetSize((350, 250))
        self.SetMinSize((350, 250))

        self.elb.GetListCtrl().SetFocus()
        #wx.CallAfter (self.elb.GetListCtrl().Select, 2)
        btnOk.SetDefault()

    def rewrite_list(self):
        #rewrite
        self.GetParent().parent.SearchInFiles_favoritenames = self.elb.GetStrings()
        #print self.GetParent().parent.SearchInFiles_favoritenames

    def OnbtnClose(self, event):
        """Close the dialog."""
        self.rewrite_list()
        self.EndModal(wx.ID_CANCEL)

    def OnbtnOk (self, event):
        """Close the dialog."""
        self.rewrite_list()
        #wx.MessageBox("Directory Field is empty", "Add to Favorits", wx.OK | wx.ICON_EXCLAMATION)
        self.EndModal(wx.ID_OK)


class MyCheckBox (wx.CheckBox):
    def __init__(self, parent, id, label):
        self.parent = parent
        wx.CheckBox.__init__(self, parent, id, label)
        self.Bind (wx.EVT_CHECKBOX, self.OnCheckBox)

    def OnCheckBox (self, event):
        self.parent.btnFind.SetFocus()
        #bug 1.2.5 fix (create button wasn't enabled)
        event.Skip()

class ViewStc(wx.stc.StyledTextCtrl):
    def __init__(self, panel, parent, id, filename):
        wx.stc.StyledTextCtrl.__init__(self, parent, id)
        self.filtered = True
        self.panel = panel
        self.parent = parent
        self.filename = filename
        if self.panel.parent.parent.PLATFORM_IS_WIN:
            self.face = 'Courier New'
            self.pb = 10
        else:
            self.face = 'Courier'
            self.pb = 10

        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "size:%d,face:%s" % (self.pb, self.face))

        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        self.SetMarginWidth(1, 40)
        self.SetTabWidth (self.panel.parent.parent.txtDocument.tabwidth)
        self.findstr = panel.cBoxSearchFor.GetValue()
        panel.jump_again = 0
        self.filteredlinenr = 1
        self.expandedlinenr = 1

        self.case = panel.chkMatchCase.GetValue()
        if panel.chkRegularExpression.GetValue():
            if self.case:
                x = 0
            else:
                x = re.IGNORECASE
            #problem endless loup
            #x = x | re.MULTILINE
            self.finder = re.compile(panel.cBoxSearchFor.GetValue(), x)
        self.GetLines()


        #collect all lines collecting containing the search string
        self.SetSize ((400, 200))
        self.SetReadOnly (1)

        self.StyleSetSpec(2, "fore:#FF0000")
        self.StyleSetSpec(3, "fore:#0000FF")
        self.findcount = 0
        self.ShowFoundLines()


        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnActivate)

    def GetLines (self):
        f = open(self.filename, 'r',encoding="UTF-8")
        text = ""
        self.linecount = 0
        index = 0
        for i in f.readlines():
            index += 1
            if self.filtered:
                found = 0
                if self.panel.chkRegularExpression.GetValue():
                    y = self.finder.search(i)
                    if y is not None:
                        if y.group():
                            found = 1
                else:
                    if self.case:
                        if i.find (self.findstr) > -1:
                            found = 1
                    else:
                        if i.lower().find (self.findstr.lower()) > -1:
                            found = 1

                if found:
                    text += "%6d: %s" % (index, i)
                    self.linecount += 1
            else:
                text += i

        if text:
            if text [-1] == '\n':
                text = text[:-1]
        f.close()
        highlightlinestyle = "#FFFFC0"
        if self.filtered:
            highlightlinestyle = "#C0C0FF"
        self.SetCaretLineVisible(1)
        self.SetCaretLineBackground(highlightlinestyle)
        linenrcolor = "#99A9C2"
        if self.filtered:
            linenrcolor = "#9DBBB5"
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "size:%d,face:%s,back:%s" % (self.pb, self.face, linenrcolor))

        self.SetReadOnly (0)
        self.SetText (text)
        self.SetReadOnly (1)



    def ShowFoundLines(self):
        self.expandmatchlines = []
        if not self.panel.chkRegularExpression.GetValue():
            fflag = 0
            founded = 0
            curpos = 0
            if self.case:
                fflag = wx.stc.STC_FIND_MATCHCASE
            while founded != -1:
                #fetch flags (case sensitive, regex)
                founded = self.FindText(curpos, self.GetTextLength(), self.findstr, fflag)
                founded =founded[0]
                if founded != -1:
                    if not self.filtered:
                        startline = self.LineFromPosition(founded)
                        self.expandmatchlines.append (startline)
                        self.GotoLine(startline)
                        start = self.GetCurrentPos()
                        self.StartStyling(start) #, 0xff)
                        self.SetStyling(len(self.GetLine(startline)), 3)
                    self.StartStyling(founded) #, 0xff)
                    self.SetStyling(len(self.findstr), 2)
                    curpos = founded + 1
                    self.findcount += 1
        else:
            #either check findall and run throught the list, or use (as here) iter
            z = self.finder.finditer(self.GetText())
            occ = 0
            while True:
                try:
                    s = next(z)
                    fstr = s.group () #found string
                    beg = s.start () #start pos
                    if not self.filtered:
                        startline = self.LineFromPosition(beg)
                        self.expandmatchlines.append (startline)
                        self.GotoLine(startline)
                        start = self.GetCurrentPos()
                        self.StartStyling(start) #, 0xff)
                        self.SetStyling(len(self.GetLine(startline)), 3)
                    self.StartStyling(beg) #, 0xff)
                    self.SetStyling(len(fstr), 2)
                    occ += 1
                    self.findcount += 1
                except:
                    break
        if not self.filtered:
            self.GotoLine (self.expandedlinenr - 1)
            self.UpdateExpandedStatusText (self.expandedlinenr - 1)


        else:
            #eventuell weiterbewegt: look for fitting linenr
            for i in range(self.GetLineCount()):
                line = self.GetLine (i)

                try:
                    linenr = int (line[0:line.find (':')])
                except:
                    linenr = 0
                if self.expandedlinenr < linenr:
                    self.filteredlinenr = i
                    break
            else:
                self.filteredlinenr = self.GetLineCount()
            self.GotoLine (self.filteredlinenr - 1)

    def JumpToNextFoundLine (self, down):
        line = self.GetCurrentLine()
        if down:
            if line >= self.expandmatchlines[-1]:
                l = self.expandmatchlines[0]
            else:
                for l in self.expandmatchlines:
                    if line < l:
                        break
        else:
            if line <= self.expandmatchlines[0]:
                l = self.expandmatchlines[-1]
            else:
                for i in range (len(self.expandmatchlines)):
                    if self.expandmatchlines [i] >= line:
                        l = self.expandmatchlines [i - 1]
                        break
                else:
                    #bug fix, 27.10.2004:
                    l = self.expandmatchlines [len(self.expandmatchlines) - 1]

        self.GotoLine (l)
        self.UpdateExpandedStatusText(l)

    def UpdateExpandedStatusText (self, line):
        i = -1
        for i in range(len(self.expandmatchlines)):
            if line <= self.expandmatchlines[i]:
                break
        if i != -1:
            self.parent.status.SetStatusText ("Line: %d/%d" % (i + 1, len(self.expandmatchlines)), 1)


    def UpdateStatus (self):
        self.parent.status.SetStatusText ("%d lines found" % self.linecount, 2)
        self.parent.status.SetStatusText ("%d occurances found" % self.findcount, 3)

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE or event.GetKeyCode() == ord ('V')\
            or (event.GetKeyCode() == ord ('D') and event.AltDown()):
            self.parent.Destroy()
        else:
            if ((event.GetKeyCode() == wx.WXK_LEFT) or (event.GetKeyCode() == wx.WXK_RIGHT)) and event.AltDown():
                if event.GetKeyCode() == wx.WXK_RIGHT:
                    self.panel.jump_again = 1
                else:
                    self.panel.jump_again = 2
                self.parent.Destroy()
            else:
                if event.GetKeyCode() == wx.WXK_RETURN:
                    self.OnActivate(None)
                else:
                    if event.GetKeyCode() == ord ("E"):

                        if self.filtered:
                            self.filtered = False
                            #get linenumber und verwandle das in (wie activate) expand
                            self.oldstatustext = self.parent.status.GetStatusText (1)

                            self.expandedlinenr = self.GetLineNr()
                            self.parent.SetTitle ("Quick View Expanded : " + self.filename)
                        else:
                            self.filtered = True
                            self.expandedlinenr = self.GetCurrentLine()+1
                            self.parent.status.SetStatusText (self.oldstatustext, 1)
                            self.parent.SetTitle ("Quick View Filtered : " + self.filename)
                            #finde <= expanded (on move) self.filteredlinenr = 1 set

                        self.GetLines ()
                        self.ShowFoundLines()
                        self.parent.btnNextOccurance.Enable(not self.filtered)
                        self.parent.btnPreviousOccurance.Enable(not self.filtered)

                        self.parent.btnExpanded.SetValue (not self.filtered)
                    else:
                        if (event.GetKeyCode() == wx.WXK_DOWN or event.GetKeyCode() == wx.WXK_UP) and event.AltDown():
                            if not self.filtered:
                                self.JumpToNextFoundLine (event.GetKeyCode() == wx.WXK_DOWN)
                            else:
                                event.Skip()
                        else:
                            if event.GetKeyCode() == ord ('F'):
                                #only in selection or wordendpos, else skip
                                self.panel.NewFindString = self.GetSelectedText()
                                if self.panel.NewFindString == "":
                                    gcp = self.GetCurrentPos()
                                    st = self.WordStartPosition(gcp, 1)
                                    end = self.WordEndPosition(gcp, 1)
                                    self.panel.NewFindString = self.GetTextRange (st, end)

                                if self.panel.NewFindString != "":
                                    self.parent.Destroy()
                            else:
                                event.Skip()

    def OnActivate(self, event):
        if self.filtered:
            line = self.GetLineNr() -1
        else:
            line = self.GetCurrentLine()
        self.parent.Destroy()
        self.panel.JumpToFileAndLine = line

    def GetLineNr(self):
        line =  self.GetCurLine()[0]
        if line.find (':') == -1:
            return 0
        line = int (line[0:line.find (':')])
        return line

class OnViewDlg(wx.Dialog):
    def __init__(self, parent, id, title, size, style, fname, index):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, size, style)
        self.parent = parent
        self.btnClose = wx.Button (self, wx.ID_CANCEL, "&Close")
        self.btnNext = wx.Button (self, 5001, "&Next")
        self.btnPrevious = wx.Button (self, 5002, "&Previous")
        self.btnExpanded = wx.ToggleButton (self, 5003, "&Expanded")
        self.btnSaveSize = wx.Button (self, 5004, "&SaveSize")
        self.btnSaveSize.Enable (self.parent.parent.SEARCHINFILESPREFSsavesizeposition == 1)
        self.btnFindAgain = wx.Button (self, 5007, "&Find again")
        self.btnNextOccurance = wx.Button (self, 5005, "N&ext Find")
        self.btnPreviousOccurance = wx.Button (self, 5006, "P&rev. Find")
        self.btnNextOccurance.Disable()
        self.btnPreviousOccurance.Disable()

        self.status = wx.StatusBar (self)
        self.status.SetFieldsCount (4)
        self.status.SetStatusWidths ([-45, -15, -20, -20])
        self.status.SetStatusText (fname, 0)
        self.status.SetStatusText ("Item: %d/%d" % (index + 1, self.parent.panel.listctrlresults.GetItemCount()), 1)

        self.stc = ViewStc(self.parent.panel, self, -1, fname)
        self.stc.UpdateStatus()

        commandSizer = wx.BoxSizer(wx.VERTICAL)
        commandSizer.Add((0, 10), 0, wx.ALL, 0)
        commandSizer.Add(self.btnClose, 0, wx.ALL, 0)
        commandSizer.Add((0, 25), 0, wx.ALL, 0)
        commandSizer.Add(self.btnNext, 0, wx.ALL, 0)
        commandSizer.Add((0, 10), 0, wx.ALL, 0)
        commandSizer.Add(self.btnPrevious, 0, wx.ALL, 0)
        commandSizer.Add((0, 25), 0, wx.ALL, 0)
        commandSizer.Add(self.btnExpanded, 0, wx.ALL, 0)
        commandSizer.Add((0, 25), 0, wx.ALL, 0)
        commandSizer.Add(self.btnSaveSize, 0, wx.ALL, 0)
        commandSizer.Add((0, 25), 0, wx.ALL, 0)
        commandSizer.Add(self.btnFindAgain, 0, wx.ALL, 0)
        commandSizer.Add((0, 25), 0, wx.ALL, 0)
        commandSizer.Add(self.btnNextOccurance, 0, wx.ALL, 0)
        commandSizer.Add((0, 10), 0, wx.ALL, 0)
        commandSizer.Add(self.btnPreviousOccurance, 0, wx.ALL, 0)

        leftSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftSizer.Add(self.stc, 1, wx.EXPAND | wx.ALL, 5)
        leftSizer.Add(commandSizer, 0, wx.EXPAND | wx.ALL, 5)

        topSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer.Add(leftSizer, 1, wx.EXPAND | wx.ALL, 0)
        topSizer.Add(self.status, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(topSizer)
        self.SetSizeHints(400, 250)
        if self.parent.parent.SEARCHINFILESPREFSsavesizeposition:
            self.parent.LoadDialogSizeAndPosition(self, 'searchinfiles.viewstcsizepos.dat')
            self.Bind(wx.EVT_CLOSE, self.OnCloseViewStc)

        self.Bind(wx.EVT_BUTTON, self.OnNext, id = 5001)
        self.Bind(wx.EVT_BUTTON, self.OnPrevious, id = 5002)
        self.Bind(wx.EVT_BUTTON, self.OnSaveSize, id = 5004)
        self.Bind(wx.EVT_BUTTON, self.OnFindAgain, id = 5007)

        self.Bind(wx.EVT_BUTTON, self.OnCloseViewStc, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnbtnNextOccurance, id = 5005)
        self.Bind(wx.EVT_BUTTON, self.OnbtnPreviousOccurance, id = 5006)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle, id = 5003)
        self.stc.SetFocus()

    def OnCloseViewStc (self, event):
        if self.parent.parent.SEARCHINFILESPREFSsavesizeposition:
            self.parent.parent.SaveDialogSizeAndPosition(self.parent.onviewdlg, 'searchinfiles.viewstcsizepos.dat',
                                                         self.parent.parent.pluginsdatdirectory)
        event.Skip()

    def OnSaveSize (self, event):
        self.parent.parent.SaveDialogSizeAndPosition(self.parent.onviewdlg, 'searchinfiles.viewstcsizepos.dat',
                                                     self.parent.parent.pluginsdatdirectory)
        event.Skip()


    def OnNext (self, event):
        evt = wx.KeyEvent()
        evt.m_altDown = True
        evt.m_keyCode = wx.WXK_RIGHT
        self.stc.OnKeyDown(evt)
        event.Skip()


    def OnPrevious (self, event):
        evt = wx.KeyEvent()
        evt.m_altDown = True
        evt.m_keyCode = wx.WXK_LEFT
        self.stc.OnKeyDown(evt)
        event.Skip()

    def OnFindAgain (self, event):
        evt = wx.KeyEvent()
        evt.m_keyCode = ord ('F')
        self.stc.OnKeyDown(evt)
        event.Skip()


    def OnbtnNextOccurance(self, event):
        evt = wx.KeyEvent()
        evt.m_keyCode = wx.WXK_DOWN
        evt.m_altDown = True
        self.stc.OnKeyDown(evt)
        self.stc.SetFocus()
        event.Skip()

    def OnbtnPreviousOccurance(self, event):
        evt = wx.KeyEvent()
        evt.m_keyCode = wx.WXK_UP
        evt.m_altDown = True
        self.stc.OnKeyDown(evt)
        self.stc.SetFocus()


    def OnToggle (self, event):
        evt = wx.KeyEvent()
        evt.m_keyCode =  ord('E')
        self.stc.OnKeyDown(evt)
        self.stc.SetFocus()
        event.Skip()


class drFindReplaceInFilesPanel(wx.Panel):

    def __init__(self, parent, id, grandparent, IsReplace = 0):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.grandparent = grandparent
        self.fromthread = False

        self.ID_BROWSE = 1001
        self.ID_SELECT = 1002
        self.ID_CHK_REGEX = 1010
        self.ID_CREATERE = 1011
        self.ID_DETAIL = 1012
        self.ID_POPUP_FIND = 1020
        self.ID_RESULTS = 1030
        self.ID_CBOXSEARCHFOR = 1040
        self.ID_CBOXREPLACEWITH = 1041
        self.ID_CBOXPATTERN = 1042
        self.ID_CBOXDIRECTORY = 1043

        self.ID_CBOXSEARCHFOR_FOCUS = 1050
        self.ID_CBOXREPLACEWITH_FOCUS = 1051
        self.ID_CBOXPATTERN_FOCUS = 1052
        self.ID_CBOXDIRECTORY_FOCUS = 1053
        self.ID_FILES_LIST_FOCUS = 1054
        self.ID_CURRENT_DOCPATH = 1055

        self.IsReplace = IsReplace
        self.in_searchthread = False
        self.oldsortcolumn = -1
        self.sort_asc = True
        self.nCol = 1

        self.JumpToFileAndLine = None
        self.NewFindString = ""

        self.jump_again = 0
        self.filelist = []


        c = locale.getdefaultlocale()[0]
        self.timeformat = '%m/%d/%Y %H:%M:%S'
        #german format?
        if len(c) >= 2:
            if "de" == c[:2]:
                self.timeformat = '%d.%m.%Y %H:%M:%S'

        self.cBoxSearchFor = drFindTextCtrl(self, self.ID_CBOXSEARCHFOR, "", wx.DefaultPosition, (350, -1), None, True)
        self.cBoxSearchFor.SetBackgroundColour(wx.Colour(231, 239, 239))


        if IsReplace:
            self.ID_POPUP_REPLACE = 1021
            self.ID_UNDO_REPLACE = 1031
            self.cBoxReplaceWith = drFindTextCtrl(self, self.ID_CBOXREPLACEWITH, "", wx.DefaultPosition, (350, -1), None, True)
            self.cBoxReplaceWith.SetBackgroundColour(wx.Colour(231, 239, 239))
            self.replacetrail = []
            self.filetrail = []
            self.replacetext = ""

        self.cBoxPattern = drFindTextCtrl(self, self.ID_CBOXPATTERN, "", wx.DefaultPosition, wx.DefaultSize, None, True)
        self.cBoxPattern.SetBackgroundColour(wx.Colour(231, 239, 239))
        self.cBoxDirectory = drFindTextCtrl(self, self.ID_CBOXDIRECTORY, "", wx.DefaultPosition, (350, -1), None, True)
        self.cBoxDirectory.SetBackgroundColour(wx.Colour(231, 239, 239))

        self.listctrlresults = FilesListCtrl(self, self.ID_RESULTS, wx.DefaultPosition, (200, -1))
        self.clearedimage = [True] * self.listctrlresults.GetColumnCount()

        self.il = wx.ImageList(16, 16)

        try:
            self.sm_up = self.il.Add(self.getSmallUpArrowBitmap())
        except:
            self.sm_up = -1
        try:
            self.sm_dn = self.il.Add(self.getSmallDnArrowBitmap())
        except:
            self.sm_dn = -1
        try:
            self.loaded = self.il.Add(self.getFileLoadedBitmap())
        except:
            self.loaded = -1
        try:
            self.modified = self.il.Add(self.getFileModifiedBitmap())
        except:
            self.modified = -1


        self.listctrlresults.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.btnPopUpFind = wx.Button(self, self.ID_POPUP_FIND, "&Edit", size = (90, -1))
        if IsReplace:
            self.btnPopUpReplace = wx.Button(self, self.ID_POPUP_REPLACE, "E&dit", size = (90, -1))
        self.btnBrowse = wx.Button(self, self.ID_BROWSE, "&Browse", size = (90, -1))
        self.btnFind = wx.Button(self, wx.ID_OK, "&Search", size = (90, -1))
        self.btnCreateRE = wx.Button(self, self.ID_CREATERE, "Cre&ate", size = (90, -1))
        self.chkRegularExpression = MyCheckBox(self, self.ID_CHK_REGEX, "&Regular Expression")
        self.chkMatchCase = MyCheckBox(self, -1, "&Match Case")
        self.chkSubDirectories = MyCheckBox(self, -1, "S&ubdirectories")
        if IsReplace:
            self.chkPromptOnReplace  = MyCheckBox(self, -1, "Prompt on Replace")
            self.chkPromptOnReplace.SetValue(grandparent.SEARCHINFILESPREFSpromptonreplace)
        self.btnDetail = wx.Button(self, self.ID_DETAIL, "&Detail", size = (90, -1))
        self.btnSelect = wx.Button(self, self.ID_SELECT, "Selec&t", size = (90, -1))
        if IsReplace:
            self.btnUndo = wx.Button(self, self.ID_UNDO_REPLACE, "U&ndo Replace", size = (90, -1))
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "&Close", size = (90, -1))

        #Prefs
        if IsReplace:
            #self.chkRegularExpression.SetValue(1)
            #self.chkRegularExpression.Enable(0)
            #self.btnCreateRE.Enable(1)

            self.chkRegularExpression.SetValue(grandparent.SEARCHINFILESPREFSregularexpression)
            self.btnCreateRE.Enable(grandparent.SEARCHINFILESPREFSregularexpression)
        else:
            self.chkRegularExpression.SetValue(grandparent.SEARCHINFILESPREFSregularexpression)
            self.btnCreateRE.Enable(grandparent.SEARCHINFILESPREFSregularexpression)
        self.chkMatchCase.SetValue(grandparent.SEARCHINFILESPREFSmatchcase)
        if IsReplace:
            self.chkMatchCase.SetValue(True)
        self.chkSubDirectories.SetValue(grandparent.SEARCHINFILESPREFSsubdirectories)

        self.statusBar = wx.StatusBar(self, -1)
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths ([-3, -12, -3])

        self.grandparent.SearchInFiles_historypathnames = []
        self.grandparent.SearchInFiles_historyextnames = []
        self.grandparent.SearchInFiles_historysearchnames = []
        self.grandparent.SearchInFiles_historyreplacenames = []
        self.grandparent.SearchInFiles_favoritenames = []
        focusonlistctrlresults = False

        if os.path.exists(self.grandparent.SearchInFiles_searchhistfile):
            f = open(self.grandparent.SearchInFiles_searchhistfile, 'r',encoding="UTF-8")
            text = f.read()
            f.close()
            self.grandparent.SearchInFiles_historypathnames = drPrefsFile.ExtractPreferenceFromText(text, "Path").rstrip().split('\n')
            self.grandparent.SearchInFiles_historyextnames = drPrefsFile.ExtractPreferenceFromText(text, "Ext").rstrip().split('\n')
            if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                self.grandparent.SearchInFiles_historysearchnames = drPrefsFile.ExtractPreferenceFromText(text, "Search").rstrip().split('\n')
                self.grandparent.SearchInFiles_historyreplacenames = drPrefsFile.ExtractPreferenceFromText(text, "Replace").rstrip().split('\n')
            if len(self.grandparent.SearchInFiles_historypathnames) > 1:
                #first value is empty: bug?
                self.grandparent.SearchInFiles_historypathnames.pop (0)
            self.grandparent.SearchInFiles_favoritenames = drPrefsFile.ExtractPreferenceFromText(text, "Favorites").rstrip().split('\n')
            #print self.grandparent.SearchInFiles_favoritenames
            if len(self.grandparent.SearchInFiles_favoritenames) > 1:
                #first value is empty: bug?
                self.grandparent.SearchInFiles_favoritenames.pop (0)
            #print self.grandparent.SearchInFiles_favoritenames
            self.cBoxDirectory.SetValue(self.grandparent.SearchInFiles_historypathnames[-1])
            self.SetHistory(self.cBoxDirectory, self.grandparent.SearchInFiles_historypathnames)

            if len(self.grandparent.SearchInFiles_historyextnames) > 1:
                self.grandparent.SearchInFiles_historyextnames.pop (0)
            #SetHistory
            exttext = self.grandparent.SearchInFiles_historyextnames[-1]
            self.cBoxPattern.SetValue(exttext)
            self.SetHistory(self.cBoxPattern, self.grandparent.SearchInFiles_historyextnames)


            if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                if len(self.grandparent.SearchInFiles_historysearchnames) > 1:
                    self.grandparent.SearchInFiles_historysearchnames.pop (0)
                self.SetHistory(self.cBoxSearchFor, self.grandparent.SearchInFiles_historysearchnames)

            if IsReplace:
                if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                    if len(self.grandparent.SearchInFiles_historyreplacenames) > 1:
                        self.grandparent.SearchInFiles_historyreplacenames.pop (0)
                    self.SetHistory(self.cBoxReplaceWith, self.grandparent.SearchInFiles_historyreplacenames)
                    replacetext = self.grandparent.SearchInFiles_historyreplacenames[-1]
                    self.cBoxReplaceWith.SetValue(replacetext)

            if self.grandparent.SEARCHINFILESPREFSsavesorting:
                try:
                    sortdata = drPrefsFile.ExtractPreferenceFromText(text, "Sorting").rstrip().split('\n')
                    self.nCol = int (sortdata [1])
                    self.sort_asc = eval (sortdata [2])
                    self.SortHeader (True)
                except:
                    pass

            if not IsReplace and self.grandparent.SEARCHINFILESPREFSsavelastresults:
                self.grandparent.SearchInFiles_lastresults = drPrefsFile.ExtractPreferenceFromText(text, "Last Results").rstrip().split('\n')
                if self.grandparent.SearchInFiles_lastresults:
                    self.grandparent.SearchInFiles_lastresults.pop(0)
                    if self.grandparent.SearchInFiles_lastresults:
                        try:
                            self.cBoxSearchFor.SetValue(self.grandparent.SearchInFiles_lastresults.pop(0))
                            self.cBoxPattern.SetValue(self.grandparent.SearchInFiles_lastresults.pop(0))
                            self.cBoxDirectory.SetValue(self.grandparent.SearchInFiles_lastresults.pop(0))
                            self.chkRegularExpression.SetValue(eval(self.grandparent.SearchInFiles_lastresults.pop(0)))
                            self.chkMatchCase.SetValue(eval(self.grandparent.SearchInFiles_lastresults.pop(0)))
                            self.chkSubDirectories.SetValue(eval(self.grandparent.SearchInFiles_lastresults.pop(0)))
                            if self.grandparent.SEARCHINFILESPREFSoccurances:
                                for i in self.grandparent.SearchInFiles_lastresults:
                                    i = i.split(";")
                                    try:
                                        n = int(i[1])
                                    except:
                                        n = 0
                                    self.filelist.append ([i[0], n])

                            else:
                                self.filelist = self.grandparent.SearchInFiles_lastresults[:]
                            self.PrepaireData (self.filelist)
                            self.Set ()
                            if self.listctrlresults.GetItemCount() > 0:
                                self.SortHeader (True)
                                self.listctrlresults.SetItemState(0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED , wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                                self.listctrlresults.SetFocus()
                                focusonlistctrlresults = True
                                self.OnSize (None)

                        except:
                            pass


        if self.grandparent.SEARCHINFILESPREFSwordundersursor:
            #this save last results should have priority over SEARCHINFILESPREFSwordundersursor
            if not self.grandparent.SEARCHINFILESPREFSsavelastresults or IsReplace:
                self.FindAndSetDefaultSearchString()

        commandSizer = wx.BoxSizer(wx.VERTICAL)
        commandSizer.Add((0, 5), 0, wx.ALL, 0)
        commandSizer.Add(self.btnPopUpFind, 0, wx.ALL, 0)
        if IsReplace:
            commandSizer.Add((0, 3), 0, wx.ALL, 0)
            commandSizer.Add(self.btnPopUpReplace, 0, wx.ALL, 0)
        commandSizer.Add((0, 29), 0, wx.ALL, 0)
        commandSizer.Add(self.btnBrowse, 0, wx.ALL, 0)
        commandSizer.Add((0, 10), 0, wx.ALL, 0)
        commandSizer.Add(self.btnFind, 0, wx.ALL, 0)

        commandSizer.Add((0, 12), 0, wx.ALL, 0)
        commandSizer.Add(self.btnCreateRE, 0, wx.ALL, 0)
        commandSizer.Add((0, 5), 0, wx.ALL, 0)

        commandSizer.Add(self.chkRegularExpression, 0, wx.ALL, 0)
        commandSizer.Add((0, 15), 0, wx.ALL, 0)
        commandSizer.Add(self.chkMatchCase, 0, wx.ALL, 0)
        commandSizer.Add((0, 5), 0, wx.ALL, 0)
        commandSizer.Add(self.chkSubDirectories, 0, wx.ALL, 0)
        if IsReplace:
            commandSizer.Add((0, 5), 0, wx.ALL, 0)
            commandSizer.Add(self.chkPromptOnReplace, 0, wx.ALL, 0)
        commandSizer.Add((0, 15), 0, wx.ALL, 0)
        commandSizer.Add(self.btnDetail, 0, wx.ALL, 0)
        commandSizer.Add((0, 15), 0, wx.ALL, 0)
        commandSizer.Add(self.btnSelect, 0, wx.ALL, 0)
        if IsReplace:
            commandSizer.Add((0, 15), 0, wx.ALL, 0)
            commandSizer.Add(self.btnUndo, 0, wx.SHAPED)
        commandSizer.Add((0, 15), 0, wx.ALL, 0)
        commandSizer.Add(self.btnCancel, 0, wx.ALL, 0)

        topSizer = wx.FlexGridSizer(0, 2, 5, 5)
        topSizer.AddGrowableCol(1)
        if self.grandparent.PLATFORM_IS_GTK:
            topSizer.Add(wx.StaticText(self, -1, "search For: "), 0)
        else:
            topSizer.Add(wx.StaticText(self, -1, "Search &For: "), 0)
        topSizer.Add(self.cBoxSearchFor, 1, wx.GROW)
        if IsReplace:
            if self.grandparent.PLATFORM_IS_GTK:
                topSizer.Add(wx.StaticText(self, -1, "replace With: "), 0)
            else:
                topSizer.Add(wx.StaticText(self, -1, "Replace &With: "), 0)
            topSizer.Add(self.cBoxReplaceWith, 1, wx.GROW)
        if self.grandparent.PLATFORM_IS_GTK:
            topSizer.Add(wx.StaticText(self, -1, "file Pattern:"), 0)
        else:
            topSizer.Add(wx.StaticText(self, -1, "File &Pattern:"), 0)
        topSizer.Add(self.cBoxPattern, 1, wx.GROW)
        if self.grandparent.PLATFORM_IS_GTK:
            topSizer.Add(wx.StaticText(self, -1, "directorY:"), 0)
        else:
            topSizer.Add(wx.StaticText(self, -1, "Director&y:"), 0)
        topSizer.Add(self.cBoxDirectory, 1, wx.GROW)


        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(topSizer, 0, wx.EXPAND | wx.ALL, 5)
        leftSizer.Add(self.listctrlresults, 1, wx.EXPAND | wx.ALL, 5)

        newSizer = wx.BoxSizer(wx.HORIZONTAL)
        newSizer.Add(leftSizer,1, wx.EXPAND | wx.ALL, 10)
        newSizer.Add(commandSizer,0, wx.ALIGN_TOP | wx.ALL, 10)
        lastSizer = wx.BoxSizer(wx.VERTICAL)
        lastSizer.Add(newSizer,1, wx.EXPAND | wx.ALL, 0)
        lastSizer.Add(self.statusBar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(lastSizer)

        self.btnFind.SetDefault()
        if not focusonlistctrlresults:
            self.cBoxSearchFor.SetFocus()
        else:
            #wxpython workaround
            wx.CallAfter(self.cBoxSearchFor.SetMark, 0, 0)
            self.btnSelect.SetDefault()

        self.Bind(wx.EVT_BUTTON,  self.OnbtnBrowse, id = self.ID_BROWSE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnCancel, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnFind, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnCreateRE, id = self.ID_CREATERE)
        self.Bind(wx.EVT_BUTTON,  self.OnActivateItem, id = self.ID_SELECT)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnDetail, id = self.ID_DETAIL)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,  self.OnActivateItem, id=self.ID_RESULTS)

        self.Bind(wx.EVT_CHECKBOX,  self.OnCheckRegularExpression, id=self.ID_CHK_REGEX)

        self.Bind(wx.EVT_BUTTON,  self.OnbtnPopUpFind, id=self.ID_POPUP_FIND)
        self.Bind(wx.EVT_IDLE,  self.OnIdle)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyDown, id = -1)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnHeaderClick, id = self.ID_RESULTS)

        if IsReplace:
            self.Bind(wx.EVT_BUTTON,  self.OnbtnPopUpReplace, id=self.ID_POPUP_REPLACE)
            self.Bind(wx.EVT_BUTTON,  self.OnbtnUndoReplace, id=self.ID_UNDO_REPLACE)

        self.listctrlresults.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        # for wxMSW
        self.listctrlresults.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        # for wxGTK
        self.listctrlresults.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        self.Bind(wx.EVT_MENU,  self.OnCBoxSearchForSetFocus, id = self.ID_CBOXSEARCHFOR_FOCUS)
        self.Bind(wx.EVT_MENU,  self.OnCBoxReplaceWithSetFocus, id = self.ID_CBOXREPLACEWITH_FOCUS)
        self.Bind(wx.EVT_MENU,  self.OnCBoxPatternSetFocus, id = self.ID_CBOXPATTERN_FOCUS)
        self.Bind(wx.EVT_MENU,  self.OnCBoxDirectorySetFocus, id = self.ID_CBOXDIRECTORY_FOCUS)
        self.Bind(wx.EVT_MENU,  self.OnFileListCtrlFileListSetFocus, id = self.ID_FILES_LIST_FOCUS)
        self.Bind(wx.EVT_MENU,  self.OnCBoxDirectoryCurrentDocPath, id = self.ID_CURRENT_DOCPATH)

        self.Bind(wx.EVT_SIZE,  self.OnSize, id = -1)

        tbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord('F'), self.ID_CBOXSEARCHFOR_FOCUS)
                                ,(wx.ACCEL_ALT, ord('W'), self.ID_CBOXREPLACEWITH_FOCUS)
                                ,(wx.ACCEL_ALT, ord('P'), self.ID_CBOXPATTERN_FOCUS)
                                ,(wx.ACCEL_ALT, ord('Y'), self.ID_CBOXDIRECTORY_FOCUS)
                                ,(wx.ACCEL_ALT, ord('L'), self.ID_FILES_LIST_FOCUS)
                                ,(wx.ACCEL_ALT, ord('A'), self.ID_CURRENT_DOCPATH)
                                ])

        self.SetAcceleratorTable(tbl)

        wx.CallAfter(self.cBoxPattern.SetMark, 0, 0)
        wx.CallAfter(self.cBoxDirectory.SetMark, 0, 0)
        if IsReplace:
            wx.CallAfter(self.cBoxReplaceWith.SetMark, 0, 0)


    def OnSize (self, event):
        #check size entries
        if self.grandparent.SEARCHINFILESPREFScolumnwidths == 2:
            all = reduce(lambda x, y: x + y, self.listctrlresults.columndwithspercent)
            if all > 1000:
                sumall = reduce(lambda x, y: x + y, self.listctrlresults.columndwithsabsdefault)

                for i in range (self.listctrlresults.GetColumnCount()):
                    self.listctrlresults.columndwithspercent[i] = (self.listctrlresults.columndwithsabsdefault[i] * 1000) / sumall

            listcontrolwidth =  self.listctrlresults.GetClientSize()[0]
            #code from listcontrol mixins
            if self.grandparent.PLATFORM_IS_WIN:
                if self.listctrlresults.GetItemCount() > self.listctrlresults.GetCountPerPage():
                    scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                    listcontrolwidth -= scrollWidth

            entirewidth = 0
            #last subtract (rounding error) to always a align last column to the right
            for i in range (self.listctrlresults.GetColumnCount() - 1):
                curwidth = (self.listctrlresults.columndwithspercent[i] * listcontrolwidth)  / 1000
                self.listctrlresults.SetColumnWidth(i, curwidth)
                entirewidth += curwidth

            #sometimes, the horizontal scrollbar is visible (wxpython bug?)
            self.listctrlresults.SetColumnWidth(self.listctrlresults.GetColumnCount() - 1, listcontrolwidth - entirewidth)
        if event is not None:
            event.Skip()

    #from wxPython Demo
    def LoadDialogSizeAndPosition(self, dialog, dialogfile):
        dlgsizefile = os.path.join(self.grandparent.pluginsdatdirectory, dialogfile)
        if os.path.exists(dlgsizefile):
            f = open(dlgsizefile, 'r',encoding="UTF-8")
            text = f.read()
            f.close()
            t = ''
            t = drPrefsFile.GetPrefFromText(t, text, "search.in.files.SizePos").rstrip()
            try:
                u = t.split()
                x = int (u[0])
                y = int (u[1])
                px = int (u[2])
                py = int (u[3])
                dialog.SetSize((x, y))
                dialog.Move(wx.Point(px, py))
            except:
                pass
        dialog.Bind(wx.EVT_CLOSE, dialog.OnCloseW)

    def LoadDialogColumnwidths(self, dialog, dialogfile):
        columnwithsfile = os.path.join(self.grandparent.pluginsdatdirectory, dialogfile)
        if os.path.exists(columnwithsfile):
            f = open(columnwithsfile, 'r',encoding="UTF-8")
            text = f.read()
            f.close()
            t = ''
            try:
                t = drPrefsFile.GetPrefFromText(t, text, "search.in.files.ColumnwidthsAbs").rstrip()
                u = t.split()
                dialog.columndwithsabs = []
                for i in u:
                    dialog.columndwithsabs.append (int (i))
            except:
                pass
            try:
                t = drPrefsFile.GetPrefFromText(t, text, "search.in.files.ColumnwidthsPercent").rstrip()
                u = t.split()
                dialog.columndwithspercent = []
                for i in u:
                    dialog.columndwithspercent.append (int (i))
            except:
                pass
        dialog.Bind(wx.EVT_CLOSE, dialog.parent.parent.OnCloseW)

    def SaveDialogSizePosColumn(self, dialog, dialogfile):
        try:
            f = open(os.path.join (self.grandparent.pluginsdatdirectory, dialogfile), 'w',encoding="UTF-8")
            x, y = dialog.GetSizeTuple()
            px, py = dialog.GetPositionTuple()

            f.write("<search.in.files.SizePos>\n")
            f.write(str(x) + '\n' + str(y) + '\n' + str(px) + '\n' + str(py) + '\n')
            f.write("</search.in.files.SizePos>\n")
            f.write("<search.in.files.ColumnwidthsAbs>\n")
            for i in range (self.listctrlresults.GetColumnCount()):
                f.write(str(self.listctrlresults.GetColumnWidth(i)) + '\n')
            f.write("</search.in.files.ColumnwidthsAbs>\n")
            f.write("<search.in.files.ColumnwidthsPercent>\n")

            sumall = self.listctrlresults.GetClientSize()[0]
            #code from listcontrol mixins
            if self.grandparent.PLATFORM_IS_WIN:
                if self.listctrlresults.GetItemCount() > self.listctrlresults.GetCountPerPage():
                    scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                    sumall -= scrollWidth
            newsum = 0
            for i in range (self.listctrlresults.GetColumnCount() - 1):
                self.listctrlresults.columndwithspercent[i] = self.listctrlresults.GetColumnWidth(i) * 1000 / sumall
                newsum += self.listctrlresults.GetColumnWidth(i)
                f.write(str(self.listctrlresults.columndwithspercent[i]) + '\n')
            #lastpercent
            if (sumall - newsum) > 0:
                lastpercent = (sumall - newsum) * 1000 / sumall
            else:
                lastpercent = 0

            f.write(str(lastpercent) + '\n')
            f.write("</search.in.files.ColumnwidthsPercent>\n")

            f.close()
        except:
            self.grandparent.ShowMessage(dialog, "Error Saving Dialog Size", 'Error')


    def OnRightClick(self, event):
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupSelect, id = self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupDetail, id = self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupCopyCurrentFilename, id = self.popupID3)

        menu = wx.Menu()
        menu.Append(self.popupID1, "Select")
        menu.Append(self.popupID2, "Detail")
        menu.Append(self.popupID3, "Copy Current Filename")
        #changed 1.32
        lx, ly = self.listctrlresults.GetPosition()
        lx += self.x
        ly += self.y

        self.PopupMenu(menu, (lx, ly))
        menu.Destroy()

    def OnPopupSelect(self, event):
        self.OnActivateItem(None)

    def OnDetail(self, event = None):
        self.listctrlresults.OnChar (None, True)

    def OnPopupDetail(self, event):
        self.OnDetail()

    def OnCopyCurrentFilename (self):
        if self.listctrlresults.GetItemCount() == 0:
            return
        index = self.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index == -1:
            self.grandparent.ShowMessage ('No File selected', "Info")
            return
        #index = self.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        fname = self.GetFilenameFromIndex(index)

        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(fname))
        wx.TheClipboard.Close()
        self.grandparent.SetStatusText("Copied current filename to Clipboard: '%s'" % fname, 2)
        #else (come from popupmenu or select button or doubleclick) => take all marked files


    def OnPopupCopyCurrentFilename (self, event):
        self.OnCopyCurrentFilename ()

    #from wxPython Demo
    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()
        #bug fixed 1.32 (no need to add these values)
        #lx, ly = self.listctrlresults.GetPosition()
        #self.y += ly
        #self.x += lx
        item, flags = self.listctrlresults.HitTest((self.x, self.y))
        if flags & wx.LIST_HITTEST_ONITEM:
            #helper function instead of SetItemState(idx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.listctrlresults.Select(item)
        event.Skip()

    def OnCBoxSearchForSetFocus(self, event):
        self.cBoxSearchFor.SetFocus()

    def OnCBoxReplaceWithSetFocus(self, event):
        if self.IsReplace:
            self.cBoxReplaceWith.SetFocus()

    def OnCBoxPatternSetFocus(self, event):
        self.cBoxPattern.SetFocus()

    def OnCBoxDirectorySetFocus(self, event):
        self.cBoxDirectory.SetFocus()

    def OnFileListCtrlFileListSetFocus(self, event):
        self.listctrlresults.SetFocus()

    def OnCBoxDirectoryCurrentDocPath(self, event):
        self.parent.OnCurrentPath(None)

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            self.OnbtnCancel(event)
        else:
            sort_column = -1
            if keycode == wx.WXK_F1:
                sort_column = 0
            elif keycode == wx.WXK_F2:
                sort_column = 1
            elif keycode == wx.WXK_F3:
                sort_column = 2
            elif keycode == wx.WXK_F4:
                sort_column = 3
            elif keycode == wx.WXK_F5:
                sort_column = 4
            elif keycode == wx.WXK_F6:
                sort_column = 5
            elif keycode == wx.WXK_F7:
                sort_column = 6
            if sort_column != -1:
                self.nCol = sort_column
                self.SortHeader()

    def OnHeaderClick(self, event):
        self.nCol = event.GetColumn()
        self.SortHeader()

    def SortHeader(self, no_change_sort = False):
        #wxPython Bug(?) workaround
        #a column image must not cleared two times (unhandled exception)

        if not no_change_sort:
            if self.oldsortcolumn != -1:
                if not self.clearedimage [self.oldsortcolumn]:
                    self.listctrlresults.ClearColumnImage(self.oldsortcolumn)
                    self.clearedimage [self.oldsortcolumn] = True
            if self.oldsortcolumn != self.nCol:
                self.sort_asc = True
                self.oldsortcolumn = self.nCol
            else:
                self.sort_asc = not self.sort_asc

            if self.sort_asc:
                idx = self.sm_up
            else:
                idx = self.sm_dn

            self.listctrlresults.SetColumnImage(self.nCol, idx)
            self.clearedimage [self.nCol] = False
        else:
            if self.oldsortcolumn == -1:
                if self.grandparent.SEARCHINFILESPREFSsavesorting:
                    if self.sort_asc:
                        idx = self.sm_up
                    else:
                        idx = self.sm_dn

                    self.listctrlresults.SetColumnImage(self.nCol, idx)
                    self.clearedimage [self.nCol] = False
                    self.oldsortcolumn = self.nCol
                else:
                    return

        self.listctrlresults.SortItems(self.columnSorter)

        nItem = self.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if nItem != -1:
            self.listctrlresults.EnsureVisible(nItem)


    def getColumnText(self, index, col):
        return self.listctrldata[index][col]

    def columnSorter(self, key1, key2):
        if not self.sort_asc:
            key1, key2 = key2, key1
        item1 = self.getColumnText (key1, self.nCol)
        item2 = self.getColumnText (key2, self.nCol)
        if not self.grandparent.SEARCHINFILESPREFSsortcasesensitive:
            item1 = item1.lower()
            item2 = item2.lower()
        if self.nCol == 4:
            item1 = int (item1.replace ('.', ''))
            item2 = int (item2.replace ('.', ''))
        if self.nCol == 5:
            #code from Dan Pozmanter in drFileDialog
            item1 = time.strptime(item1, self.timeformat)
            item2 = time.strptime(item2, self.timeformat)
            i2 = item1[0]
            i1 = item2[0]
            x = 1
            while (i1 == i2) and (x < 6):
                i2 = item1[x]
                i1 = item2[x]
                x = x + 1
        if self.nCol == 7:
            item1 = int (item1)
            item2 = int (item2)
        if item1 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            # loaded or extension or name: also path
            if self.nCol == 0 or self.nCol == 2 or self.nCol == 3 or self.nCol == 7:
                item1 = self.getColumnText (key1, 1)
                item2 = self.getColumnText (key2, 1)
                if not self.grandparent.SEARCHINFILESPREFSsortcasesensitive:
                    item1 = item1.lower()
                    item2 = item2.lower()
                if item1 < item2:
                    return -1
                elif item1 > item2:
                    return 1
                else:
                    # loaded or extension: also name
                    if self.nCol == 0 or self.nCol == 3 or self.nCol == 7:
                        item1 = self.getColumnText (key1, 2)
                        item2 = self.getColumnText (key2, 2)
                        if not self.grandparent.SEARCHINFILESPREFSsortcasesensitive:
                            item1 = item1.lower()
                            item2 = item2.lower()
                        if item1 < item2:
                            return -1
                        elif item1 > item2:
                            return 1
                        else:
                            return 0
                    else:
                        return 0
            #path: also name
            elif self.nCol == 1:
                item1 = self.getColumnText (key1, 2)
                item2 = self.getColumnText (key2, 2)
                if not self.grandparent.SEARCHINFILESPREFSsortcasesensitive:
                    item1 = item1.lower()
                    item2 = item2.lower()
                if item1 < item2:
                    return -1
                elif item1 > item2:
                    return 1
                else:
                    return 0
            else:
                return 0


    #workaround: searching with thread, listctrlresults doesn't work as expected
    def OnIdle(self, event):
        if self.in_searchthread:
            self.fromthread = True
        else:
            if self.fromthread:
                self.fromthread = False
                self.listctrlresults.SetFocus()
        event.Skip()

    def FindAndSetDefaultSearchString (self):
        word = ''
        x, y = self.grandparent.txtDocument.GetSelection()
        #nothing selected
        if x == y:
            gcp = self.grandparent.txtDocument.GetCurrentPos()
            st = self.grandparent.txtDocument.WordStartPosition(gcp, 1)
            end = self.grandparent.txtDocument.WordEndPosition(gcp, 1)
            if st != end:
                self.grandparent.txtDocument.SetSelection(st, end)
                word = self.grandparent.txtDocument.GetSelectedText()
        else:
            word = self.grandparent.txtDocument.GetSelectedText()

        if word == '':
            if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                try:
                    word = self.grandparent.SearchInFiles_historysearchnames[-1]
                except:
                    pass
        self.cBoxSearchFor.SetValue(word)

    def GetFilenameFromIndex(self, index):
        item = self.listctrlresults.GetItem(index, 1)
        path = item.GetText()
        item = self.listctrlresults.GetItem(index, 2)
        name = item.GetText()
        fname = os.path.join (path, name)
        fname = fname.replace("\\", "/")
        return fname

    def OnActivateItem(self, event, jump_to_line = -1, fname = ""):
        if self.listctrlresults.GetItemCount() == 0:
            return
        filelist = []
        if fname == "":

            index = -1
            for i in range (self.listctrlresults.GetItemCount()):
                index = self.listctrlresults.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if index == -1:
                    break
                else:
                    fname = self.GetFilenameFromIndex(index)
                    #index = self.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                    filelist.append(fname)
        else:
            filelist = [fname]
        #else (come from popupmenu or select button or doubleclick) => take all marked files

        if fname == '':
            #Apparantly nothing selected in listbox
            return

        farray = map(lambda x: x.filename, self.grandparent.txtDocumentArray)

        for fname in filelist:
            if fname in farray:
                i = farray.index(fname)
                self.grandparent.setDocumentTo(i)
            else:
                old = self.grandparent.txtDocument.filename
                filename = fname
                self.grandparent.OpenOrSwitchToFile(filename, editRecentFiles=False)

#                if (len(old) > 0) or self.grandparent.txtDocument.GetModify():
#                    self.grandparent.OpenFile(filename, True)
#                else:
#                    self.grandparent.OpenFile(filename, False)

            if not self.cBoxSearchFor.GetValue() == '':
                self.grandparent.txtDocument.Finder.reset()

                if self.chkMatchCase.GetValue():
                    self.grandparent.txtDocument.Finder.findflags = wx.stc.STC_FIND_MATCHCASE
                self.grandparent.txtDocument.Finder.findtext = self.cBoxSearchFor.GetValue()
                self.grandparent.txtDocument.Finder.targetEnd = self.grandparent.txtDocument.GetLength()
                self.grandparent.txtDocument.SetSelection (0, 0)
                self.grandparent.txtDocument.Finder.RE = self.chkRegularExpression.GetValue()


                if self.IsReplace:
                    if self.replacetrail:
                        self.grandparent.txtDocument.Finder.findtext = self.replacetext

                if jump_to_line > -1:
                    self.grandparent.txtDocument.GotoLine(jump_to_line)
                else:
                    #self.grandparent.txtDocument.ScrollToLine(1)
                    #self.grandparent.ScrollToColumn(1)
                    wx.CallAfter (self.grandparent.OnMenuFindNext,event) #otherwise on gtk, sometimes it is scrolling to right
                    #self.grandparent.txtDocument.Finder.ScrollFewLinesAbove()
                    #self.grandparent.CenterCurrentLine (self.grandparent.txtDocument.GetCurrentLine())

                    if self.grandparent.SEARCHINFILESPREFSputsearchtohistoryforfind:
                        try:
                            i = self.grandparent.FindHistory.index(self.grandparent.txtDocument.Finder.findtext)
                            self.grandparent.FindHistory.pop(i)
                        except:
                            pass
                        self.grandparent.FindHistory.append(self.grandparent.txtDocument.Finder.findtext)


        self.grandparent.Raise()
        self.grandparent.SetFocus()
        self.grandparent.txtDocument.SetFocus()

    def OnbtnBrowse(self, event):
        path = self.cBoxDirectory.GetValue()
        lastdir = path.split(';')[0]#[-1]#changed 09.03.2005
        if not os.path.exists(lastdir):
            path = ""
        d = wx.DirDialog(self, "Add Directory:", lastdir, style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON|wx.MAXIMIZE_BOX)
        if d.ShowModal() == wx.ID_OK:
            if path:
                path += ';'
            newpath = d.GetPath()
            newpath = newpath.replace ('\\', "/")
            if self.grandparent.SEARCHINFILESPREFSappenddironbrowse:
                path += newpath
            else:
                path = newpath

            self.cBoxDirectory.SetValue(path)
            wx.CallAfter(self.cBoxDirectory.SetMark, len (path), len (path))
            self.cBoxDirectory.SetFocus()
            d.Destroy()

    def OnbtnCancel(self, event):
        if self.closing == 1:
            event.Skip()
            return
        self.closing = 1
        self.parent.Close(1)

    def OnbtnPopUpFind(self, event):
        s = self.cBoxSearchFor.GetPosition()[0]
        x = self.btnPopUpFind.GetPosition()[0]
        self.cBoxSearchFor.PopUp((x-s, 0))

    def OnbtnPopUpReplace(self, event):
        s = self.cBoxReplaceWith.GetPosition()[0]
        x = self.btnPopUpReplace.GetPosition()[0]
        self.cBoxReplaceWith.PopUp((x-s, 0))

    def OnbtnCreateRE(self, event):
        d = drMyRegularExpressionDialog(self.parent, -1, "Create Regular Expression", 0, 0)
        d.Show()

    def OnbtnDetail (self, event):
        if self.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) != -1:
            self.OnDetail()
            #self.parent.OnView(None)

    def OnbtnSelect (self, event):
        self.OnActivateItem (self, wx.ListEvent ()) # dummy event

    def CheckBeforeSearchAndReplace(self):

        self.q = self.createRE(self.cBoxPattern.GetValue())

        self.subdir = self.chkSubDirectories.GetValue()

        directoriesvalue = self.cBoxDirectory.GetValue().split (';')

        self.ignoredirectories = []
        self.directories = []
        for i in directoriesvalue:
            if i[0] == '-':
                self.ignoredirectories.append (i[1:])
            else:
                self.directories.append (i)
        for i in self.directories:
            if os.path.exists(i):
                break
        else:
            self.grandparent.ShowMessage ('Directory "' + self.cBoxDirectory.GetValue() + '" does not exist', "Error")
            self.statusBar.SetStatusText("Done.")
            return False

        self.should_append_history = True
        return True

    def ReplaceFiles (self):

        answer = wx.MessageBox("This will Replace \"" + self.cBoxSearchFor.GetValue() \
        + "\" with \"" +  self.cBoxReplaceWith.GetValue() + "\" in files of type: \""\
        + self.cBoxPattern.GetValue() + "\" in the directory: \"" + self.cBoxDirectory.GetValue() + "\"."\
        + "\nAre you sure you want to do this?", "Replace in Files", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.NO:
            return
        
        self.filelist = []
        case = self.chkMatchCase.GetValue()
        #if self.chkRegularExpression.GetValue():
        if case:
            x = 0
        else:
            x = re.IGNORECASE

        findstring = self.cBoxSearchFor.GetValue()
        
        if not self.chkRegularExpression.GetValue():
            findstring = re.escape(findstring)

        try:
            finder = re.compile(findstring, x)
        except:
            self.grandparent.ShowMessage ('Problem compiling Regular Expression.', "Error")
            return

        if self.chkPromptOnReplace.GetValue():
            frame = self.parent
        else:
            frame = None
        self.replacetrail = []

        for i in self.directories:
            if os.path.exists(i):
                self.replace_abort = False
                fl, rt = self.runDirReplaceRE(finder, self.cBoxReplaceWith.GetValue(), i, os.listdir(i), self.q,
                            self.subdir, frame, self.grandparent.SEARCHINFILESPREFSbackupbeforereplace)
                self.filelist += fl
                self.replacetrail += rt
            else:
                self.grandparent.ShowMessage ('Directory %s does not exist.' % i, "Note")
                self.should_append_history = False

        self.filetrail = self.filelist
        self.replacetext = self.cBoxReplaceWith.GetValue()


    def DoReplace (self):
        if not self.CheckBeforeSearchAndReplace():
            return
        self.ReplaceFiles ()
        self.SetSearchResultandHistory ()

    def DoSearch (self):

        self.filelist = []
        if not self.CheckBeforeSearchAndReplace():
            return
        self.SearchInFiles_count = 0
        self.SearchInFiles_findcount = 0
        case = self.chkMatchCase.GetValue()
        if self.chkRegularExpression.GetValue():
            if case:
                x = 0
            else:
                x = re.IGNORECASE
            x = x | re.MULTILINE
            try:
                finder = re.compile(self.cBoxSearchFor.GetValue(), x)
            except:
                self.grandparent.ShowMessage ('Problem compiling Regular Expression.', "Error")
                return

            for i in self.directories:
                if os.path.exists(i):
                    self.filelist += self.runDirRE(finder, i, os.listdir(i), self.q, self.subdir, self.cBoxSearchFor.GetValue())
                else:
                    self.grandparent.ShowMessage ('Directory %s does not exist.' % i, "Note")
                    self.should_append_history = False

            self.statusBar.SetStatusText("%d Files total"  % self.SearchInFiles_count, 2)
            self.statusBar.SetStatusText("", 1)
        else:
            if case:
                findtext = self.cBoxSearchFor.GetValue()
            else:
                findtext = self.cBoxSearchFor.GetValue().lower()
            for i in self.directories:
                if os.path.exists(i):
                    self.filelist += self.runDir(findtext, i, os.listdir(i), self.q, self.subdir, case)
                else:
                    self.grandparent.ShowMessage ('Directory %s does not exist.' % i, "Note")
                    self.should_append_history = False

                if not self.search_thread_run:
                    break

            self.statusBar.SetStatusText("%d Files total"  % self.SearchInFiles_count, 2)
            self.statusBar.SetStatusText("", 1)
        self.SetSearchResultandHistory ()



    def thousand_separate(self, strValue, cDelimiter = '.'):
        nLen = len(strValue)
        nCommas = int((nLen-1)/3)
        nPos = nLen - nCommas * 3
        
        strResult = strValue [:nPos]
        for i in range(nCommas):
            strResult += cDelimiter
            strResult += strValue [nPos: nPos + 3]
            nPos += 3
        return strResult


    def PrepaireData(self, items):
        self.listctrldata = []
        print("Items=", items)
    
        for i in items:
            self.listctrldata.append([])
    
            # i — це рядок (повний шлях до файлу)
            j = i
            if not self.grandparent.SEARCHINFILESPREFSoccurances:
                j = j.split(';')[0]
    
            print("jfname=", i)
            fname = j.replace("\\", "/")
            print("fname=", fname)
    
            loaded = ' '
            farray = [x.filename for x in self.grandparent.txtDocumentArray]
            if fname in farray:
                loaded = 'Y'
                index = farray.index(fname)
                if self.grandparent.txtDocumentArray[index].GetModify():
                    loaded = 'M'
    
            name = os.path.split(fname)[1]
            path = os.path.split(fname)[0]
            ext = os.path.splitext(fname)[1][1:]
            if os.path.exists(fname):
                st = os.stat(fname)
                size = str(st.st_size)
                size = self.thousand_separate(size)
                mtime = time.strftime(self.timeformat, time.localtime(st.st_mtime))
    
                mmode = ''
                if self.grandparent.PLATFORM_IS_WIN:
                    if not st[stat.ST_MODE] & stat.S_IWOTH:
                        mmode = 'Y'
                else:
                    mmode = str(oct(stat.S_IMODE(st.st_mode)))
    
                self.listctrldata[-1].extend([loaded, path, name, ext, size, mtime, mmode])
    
                if self.grandparent.SEARCHINFILESPREFSoccurances:
                    # Якщо колись items буде списком типу [fname, count]
                    # — цей блок не зламається:
                    if isinstance(i, (list, tuple)) and len(i) > 1:
                        self.listctrldata[-1].append(str(i[1]))
    

    def Set(self):

        self.listctrlresults.DeleteAllItems()

        if self.listctrldata:
            index = 0
            for data in self.listctrldata:
                idx = -1
                if data:
                    if data[0]=='Y':
                        idx = self.loaded
                    elif data[0]=='M':
                        idx = self.modified

                    self.listctrlresults.InsertItem(index, "", idx)
                    self.listctrlresults.SetItem(index, 1, data[1])
                    self.listctrlresults.SetItem(index, 2, data[2])
                    self.listctrlresults.SetItem(index, 3, data[3])
                    self.listctrlresults.SetItem(index, 4, data[4])
                    self.listctrlresults.SetItem(index, 5, data[5])
                    self.listctrlresults.SetItem(index, 6, data[6])
                    if self.grandparent.SEARCHINFILESPREFSoccurances:
                        self.listctrlresults.SetItem(index, 7, data[7])

                    self.listctrlresults.SetItemData(index, index)

                    index += 1

    def SetSearchResultandHistory (self):
        self.filelist.sort()
        self.PrepaireData (self.filelist)
        self.Set()
        self.SortHeader(True)
        self.OnSize (None)

        if self.listctrlresults.GetItemCount() > 0:
            self.listctrlresults.SetItemState(0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED , wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)

            self.listctrlresults.SetFocus()
        else:
            self.cBoxSearchFor.SetFocus()
            wx.CallAfter (self.cBoxSearchFor.SetInsertionPointEnd)
        self.statusBar.SetStatusText(str(len(self.filelist)) + " Files Found")
        if self.should_append_history:
            if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                self.cBoxSearchFor.AppendToHistory(self.grandparent.SearchInFiles_historysearchnames)
            if self.IsReplace and self.grandparent.SEARCHINFILESPREFSusefindhistory:
                self.cBoxReplaceWith.AppendToHistory(self.grandparent.SearchInFiles_historyreplacenames)
            self.cBoxDirectory.AppendToHistory(self.grandparent.SearchInFiles_historypathnames)
            self.cBoxPattern.AppendToHistory(self.grandparent.SearchInFiles_historyextnames)

            if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                self.SetHistory(self.cBoxSearchFor, self.grandparent.SearchInFiles_historysearchnames)
            if self.IsReplace:
                if self.grandparent.SEARCHINFILESPREFSusefindhistory:
                    self.SetHistory(self.cBoxReplaceWith, self.grandparent.SearchInFiles_historyreplacenames)
            self.SetHistory(self.cBoxDirectory, self.grandparent.SearchInFiles_historypathnames)
            self.SetHistory(self.cBoxPattern, self.grandparent.SearchInFiles_historyextnames)
        self.SaveHistory()

    def SearchFiles (self):
        self.in_searchthread = True

        self.statusBar.SetStatusText("Searching...")
        self.DoSearch()

        if not self.grandparent.SEARCHINFILESPREFSsearchinthread:
#           wx.Yield() #don't know, if needed. let it here.
            wx.SafeYield() #don't know, if needed. let it here.

        self.btnFind.SetLabel ("&Search")
        self.in_searchthread = False


    def OnbtnFind(self, event):
        self.listctrlresults.DeleteAllItems()
        if self.cBoxDirectory.GetValue().find ('\\') != -1:
            self.cBoxDirectory.SetValue(self.cBoxDirectory.GetValue().replace ('\\', '/'))
        if self.IsReplace:
            self.DoReplace ()
        else:
            if not self.grandparent.SEARCHINFILESPREFSsearchinthread:
                self.search_thread_run = True #little irritating, but this variable is needed
                self.SearchFiles()
            else:
                if not self.in_searchthread:
                    self.search_thread_run = True
                    self.btnFind.SetLabel ("&Stop")
                    _thread.start_new_thread(self.SearchFiles, ())
                else:
                    self.search_thread_run = False
                    self.btnFind.SetLabel ("&Search")
        self.listctrlresults.SetFocus()

    def OnbtnUndoReplace(self, event):
        if self.replacetrail:
            answer = wx.MessageBox("This will Undo the Last Replace In Files Operation.\nAre you sure you want to do this?", "Undo Replace in Files", wx.YES_NO | wx.ICON_QUESTION)
            if answer == wx.YES:
                lenreplace = len(self.replacetext)
                try:
                    x = 0
                    l = len(self.filetrail)
                    while x < l:
                        f = open(self.filetrail[x], 'r',encoding="UTF-8")
                        text = f.read()
                        f.close()
                        for item in self.replacetrail[x]:
                            text = text[:item.start()] + item.group() + text[item.start()+lenreplace:]
                        f = open(self.filetrail[x], 'w',encoding="UTF-8")
                        f.write(text)
                        f.close()
                        x = x + 1

                    self.replacetrail = []
                    self.filetrail = []
                except:
                    pass

    def OnCheckRegularExpression(self, event):
        usingRegularExpressions = self.chkRegularExpression.GetValue()
        self.btnCreateRE.Enable(usingRegularExpressions)

    #**********************************************************************
    #Dan: Taken from the findf script I wrote to use in bash:

    def createRE(self, query):
        #no pattern: take all files (* the same aus *.*)
        if query == '':
            query = "*"
        query_amount = query.split (';')
        first = True
        xall = ""
        for i in query_amount:
            x = self.createREString(i)
            x =  x + '$'
            x = '(' + x + ')'
            if not first:
                x = '|' + x
            xall += x
            first = False
        #$ = only snarf the end.
        return re.compile(xall, re.IGNORECASE)

    def createREString(self, query):
        returnstr = ""
        query = query.replace('.', "\\.")
        if query.find("*") == -1:
            if query:
                return query
            else:
                return ""
        l = query.find("*")
        while l > -1:
            if l > 0:
                temp = query[0:l]
                returnstr = returnstr + temp + ".*"
                query = query[(l + 1):]
            else:
                returnstr = returnstr + ".*"
                query = query[1:]
            l = query.find("*")
        if query:
            returnstr = returnstr + query
        return returnstr

    def testIgnoreDirectories (self, cdir):
        for i in self.ignoredirectories:
            if cdir.lower().find(i.lower()) != -1:
                return True
        return False

    def runDir(self, findtext, cdir, dir_data, query, subdir, case):
        l = len(dir_data)
        x = 0

        matches = []

        if self.testIgnoreDirectories(cdir):
            return matches

        splitexts = self.cBoxPattern.GetValue().split(";")

        lookfornoext = False
        if "*." in splitexts:
            lookfornoext = True


        while (x < l) and self.search_thread_run:
            filename = os.path.normpath(cdir + "/" + dir_data[x])
            filename = filename.replace ('\\', '/')
            if not os.path.isdir(filename):
                v = query.match(dir_data[x])
                foundpattern = False
                if v is not None:
                    if v.group():
                        foundpattern = True
                if not foundpattern:
                    if lookfornoext:
                        if filename[:-1] == '.' or filename.find('.') == -1:
                            foundpattern = True

                if foundpattern:
                    self.SearchInFiles_count += 1

                    try:
                        if findtext != "":
                            f = open(filename, 'r',encoding="UTF-8")
                            text = f.read()
                            if not case:
                                text = text.lower()
                            f.close()
                        if self.grandparent.SEARCHINFILESPREFSoccurances:
                            occ = 0
                            if findtext != "":
                                occ = text.count(findtext)
                            if findtext == "" or occ > 0:
                                matches.append([filename, occ])
                                self.SearchInFiles_findcount += 1
                        else:
                            if findtext == "" or text.find(findtext) > -1 :
                                matches.append(filename)
                                self.SearchInFiles_findcount += 1
                    except:
                        pass
                    self.statusBar.SetStatusText("Current File: %s"  % filename, 1)
                    self.statusBar.SetStatusText("%d/%d"  % (self.SearchInFiles_findcount, self.SearchInFiles_count), 2)
            if subdir:
                if not os.path.islink(filename):
                    if os.path.isdir(filename):
                        try:
                            matches.extend(self.runDir(findtext, filename, os.listdir(filename), query, subdir, case))
                        except:
                            #Skip it.
                            pass
            x = x + 1

        return matches

    def runDirRE(self, finder, cdir, dir_data, query, subdir, findtext):
        l = len(dir_data)
        x = 0

        matches = []

        #For each entry in the directory, see if it matches.
        if self.testIgnoreDirectories(cdir):
            return matches

        lookfornoext = False

        splitexts = self.cBoxPattern.GetValue().split(";")
        if "*." in splitexts:
            lookfornoext = True

        while x < l:
            filename = os.path.normpath(cdir + "/" + dir_data[x])
            filename = filename.replace ('\\', '/')
            if not os.path.isdir(filename):
                v = query.match(dir_data[x])
                foundpattern = False
                if v is not None:
                    if v.group():
                        foundpattern = True
                if not foundpattern:
                    if lookfornoext:
                        if filename[:-1] == '.' or filename.find('.') == -1:
                            foundpattern = True

                if foundpattern:

                    self.SearchInFiles_count += 1
                    try:
                        f = open(filename, 'r',encoding="UTF-8")
                        text = f.read()
                        f.close()

                        if self.grandparent.SEARCHINFILESPREFSoccurances:
                            if findtext != "":
                                y = finder.findall(text)
                                if y:
                                    matches.append([filename, len(y)])
                                    self.SearchInFiles_findcount += 1
                            else:
                                matches.append([filename, 0])
                                self.SearchInFiles_findcount += 1
                        else:
                            if findtext != "":
                                y = finder.search(text)
                                if y is not None:
                                    if y.group():
                                        matches.append(filename)
                                        self.SearchInFiles_findcount += 1
                            else:
                                matches.append(filename)
                                self.SearchInFiles_findcount += 1

                    except:
                        pass
                    self.statusBar.SetStatusText("Current File:%s"  % filename, 1)
                    self.statusBar.SetStatusText("%d/%d"  % (self.SearchInFiles_findcount, self.SearchInFiles_count), 2)
            if subdir:
                if not os.path.islink(filename):
                    if os.path.isdir(filename):
                        try:
                            matches.extend(self.runDirRE(finder, filename, os.listdir(filename), query, subdir, findtext))
                        except:
                            #Skip it.
                            pass
            x = x + 1

        return matches

    def GetLineAndLineNumber(self, text, startpos):
        finder = re.compile("^.*$", re.MULTILINE)
        find_iter = finder.finditer(text)
        linenr = 0
        start = 0
        end = 0
        match = 1 #pseudo value; only to init this
        while match is not None:
            linenr += 1
            try:
                match = next(find_iter)
                start = match.start()
                end = match.end()
            except:
                match = None

            if match:
                if start <= startpos and end >= startpos:
                    return linenr, text [start:end].strip()
            else:
                return linenr, text [start:end].strip()
        return 0, ""

    def runDirReplaceRE(self, finder, replacetext, cdir, dir_data, query, subdir, frameprompt, backupfiles):

        curflen = len(dir_data)
        curfptr = 0
        
        if not self.chkRegularExpression.GetValue():
            #replacetext = re.escape(replacetext)
            replacetext = replacetext.replace("\\", "\\\\")

        targets = []
        matches = []
        #For each entry in the directory, see if it matches.

        if self.testIgnoreDirectories(cdir):
            return matches, targets
        while curfptr < curflen:
            if self.replace_abort:
                break

            filename = os.path.normpath(cdir + "/" + dir_data[curfptr])
            filename = filename.replace ('\\', '/')

            v = query.match(dir_data[curfptr])
            if v is not None:
                if v.group():
                    try:
                        f = open(filename, 'r',encoding="UTF-8")
                        text = f.read()
                        
                        f.close()
                        y = finder.search(text)
                        
                        if y is not None: # якщо y не None, тобто рядок знайдено
                            
                            if y.group(): # повертає шукане
                                
                                t = re.finditer(finder, text) # ітератор
                                
                                if frameprompt is not None:
                                    
                                    try:
                                        item = next(t)
                                    except:
                                        item = None
                                        
                                    results = []
                                    items = []
                                    while item is not None:
                                        if item.group():
                                            
                                            linenr, line = self.GetLineAndLineNumber(text, item.start())
                                            
                                            if linenr:
                                                results.append(str(linenr) + ": " + "*"+ item.group() + "*"  + " - " + line)
                                            items.append(item)
                                        try:
                                            item = next(t)
                                        except:
                                            item = None
                                    
                                    d = drMultipleItemQuestionDialog(self, "Replace In " + filename +\
                                        ' "'+ self.cBoxSearchFor.GetValue() + '" ' + 'with' + ' "' + replacetext + '" ' , results, items)
                                    d.ShowModal()
                                    answer = d.GetAnswer()
                                    if answer == 2:
                                        self.replace_abort = True
                                    results = d.GetResults()
                                    d.Destroy()
                                else:
                                    try:
                                        item = next(t)
                                    except:
                                        item = None
                                    results = []
                                    items = []
                                    while item is not None:
                                        if item.group():
                                            results.append(str(item.start()) + ": " + item.group())
                                            items.append(item)
                                        try:
                                            item = next(t)
                                        except:
                                            item = None
                                    results = items
                                if (frameprompt is None) or answer == 1:
                                    if frameprompt is None:
                                        text, pos = finder.subn(replacetext, text)
                                        #todo append x and filename to list, to display at the end
                                    else: # prompt with answer yes
                                        starter = 0
                                        for result in results:
                                            #### orig
                                            #text = text[:result.start()+starter] + replacetext + text[result.end()+starter:]
                                            #starter = starter + len(replacetext) - (result.end() - result.start())
                                            #### orig end
                                            start = result.start()+starter
                                            end = result.end()+starter
                                            textbefore = text[:start]
                                            textafter = text[end:]
                                            origtext = text [start:end]
                                            #newtext = re.sub(("ab", "de", origtext
                                            newtext = finder.sub(replacetext, origtext)
                                            diff = len(newtext) - len(origtext)
                                            text = textbefore + newtext + textafter

                                            starter = starter + diff

                                    if backupfiles:
                                        shutil.copyfile(filename, filename+".bak")
                                    f = open(filename, 'w',encoding="UTF-8")
                                    f.write(text)
                                    f.close()
                                    targets.append(results)
                                    matches.append([filename, len(results)])


                    except:
                        pass
            if subdir:
                if not os.path.islink(filename):
                    if os.path.isdir(filename):
                        try:
                            if self.replace_abort:
                                return matches, targets
                            matchlist, targetlist = self.runDirReplaceRE(finder, replacetext, filename, os.listdir(filename), query, subdir, frameprompt, backupfiles)
                            matches.extend(matchlist)
                            targets.extend(targetlist)
                        except:
                            #Skip it.
                            pass
            curfptr = curfptr + 1

        return matches, targets



    def SetHistory(self, cbox, history):
        val = cbox.GetValue()
        if cbox.GetCount() > 0:
            cbox.Clear()
        l = len(history)
        x = l - 1
        while x > -1:
            cbox.Append(history[x])
            x = x - 1
        cbox.SetValue (val)


    def SaveHistory (self):
        f = open(self.grandparent.SearchInFiles_searchhistfile, 'w',encoding="UTF-8")
        f.write("<Path>\n")
        #later from preferences
        length = 20
        try:
            to_save = self.grandparent.SearchInFiles_historypathnames[-length:]
            for path in to_save:
                if path:
                    f.write(path + '\n')
        except:
            pass
        f.write("</Path>\n")
        f.write("<Ext>\n")
        try:
            to_save = self.grandparent.SearchInFiles_historyextnames[-length:]
            for ext in to_save:
                if ext:
                    f.write(ext + '\n')
        except:
            pass
        f.write("</Ext>\n")

        if self.grandparent.SEARCHINFILESPREFSusefindhistory:
            f.write("<Search>\n")
            try:
                to_save = self.grandparent.SearchInFiles_historysearchnames[-length:]
                for search in to_save:
                    if search:
                        f.write(search + '\n')
            except:
                pass
            f.write("</Search>\n")

            f.write("<Replace>\n")
            try:
                to_save = self.grandparent.SearchInFiles_historyreplacenames[-length:]
                for search in to_save:
                    if search:
                        f.write(search + '\n')
            except:
                pass
            f.write("</Replace>\n")

        if self.grandparent.SEARCHINFILESPREFSsavelastresults:
            if not self.IsReplace: #anyway, otherwise, it doesn't make much sense
                f.write("<Last Results>\n")

                f.write(self.cBoxSearchFor.GetValue() + '\n')
                f.write(self.cBoxPattern.GetValue() + '\n')
                f.write(self.cBoxDirectory.GetValue() + '\n')
                f.write(str (self.chkRegularExpression.GetValue()) + '\n')
                f.write(str (self.chkMatchCase.GetValue()) + '\n')
                f.write(str (self.chkSubDirectories.GetValue()) + '\n')

                for i in self.filelist:
                    if self.grandparent.SEARCHINFILESPREFSoccurances:
                        f.write(i[0] + ";" + str(i[1]) + '\n')
                    else:
                        f.write(i + '\n')
                f.write("</Last Results>\n")
        if self.grandparent.SEARCHINFILESPREFSsavesorting:
            f.write("<Sorting>\n")
            f.write (str (self.nCol) + '\n')
            #oldsortcolumn
            f.write (str (self.sort_asc) + '\n')
            f.write("</Sorting>\n")

        f.write("<Favorites>\n")
        for s in self.grandparent.SearchInFiles_favoritenames:
            if s:
                f.write(s + '\n')
        f.write("</Favorites>\n")


        f.close()

    def getSmallUpArrowBitmap(self):
        return wx.Bitmap(self.getSmallUpArrowImage())

    def getSmallUpArrowImage(self):
        stream = BytesIO(self.getSmallUpArrowData())
        return wx.Image(stream)

    def getSmallDnArrowBitmap(self):
        return wx.Bitmap(self.getSmallDnArrowImage())

    def getSmallDnArrowImage(self):
        stream = BytesIO(self.getSmallDnArrowData())
        return wx.Image(stream)

    def getFileLoadedBitmap(self):
        return wx.Bitmap(self.getFileLoadedImage())

    def getFileLoadedImage(self):
        stream = BytesIO(self.getFileLoadedData())
        return wx.Image(stream)

    def getFileModifiedBitmap(self):
        return wx.Bitmap(self.getFileModifiedImage())

    def getFileModifiedImage(self):
        stream = BytesIO(self.getFileModifiedData())
        return wx.Image(stream)

#----------------------------------------------------------------------

    def getSmallUpArrowData(self):
        return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00<IDATx\x9ccddbf\xa0\x040Q\xa4{h\x18\xf0\xff\xdf\xdf\xffd\x1b\x00\xd3\
\x8c\xcf\x10\x9c\x06\xa0k\xc2e\x08m\xc2\x00\x97m\xd8\xc41\x0c \x14h\xe8\xf2\
\x8c\xa3)q\x10\x18\x00\x00R\xd8#\xec\x95{\xc4\x11\x00\x00\x00\x00IEND\xaeB`\
\x82'

    def getSmallDnArrowData(self):
        return \
b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00HIDATx\x9ccddbf\xa0\x040Q\xa4{\xd4\x00\x06\x06\x06\x06\x06\x16t\x81\
\xff\xff\xfe\xfe'\xa4\x89\x91\x89\x99\x11\xa7\x0b\x90%\ti\xc6j\x00>C\xb0\x89\
\xd3.\x10\xd1m\xc3\xe5*\xbc.\x80i\xc2\x17.\x8c\xa3y\x81\x01\x00\xa1\x0e\x04e\
\x1d\xc4;\xb7\x00\x00\x00\x00IEND\xaeB`\x82"

    def getFileLoadedData(self):
        return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\xddIDATx\x9c\xa5\x92?kTQ\x10\xc5\x7f\xf7\xde]\xf7\x8f\xa0Ub\xc0\x80\
\x84,v"\xd6\xa2\x8d\xb5\x08\xe2w\xb0\xb3\xf03\xf8q\xc4*\x95\x8d\xc8\xa2h\x08\
\x82\x85h\xa3\xc1$l\x88\x86\xc5,f\xf3\xde\x9b;3\x16\xbb\xfbvMP\x0b\x0f\x1c\
\xe62\xf7\xce\x993\xdc\t\xee\xee\xfc\x07\x1a\x00W\xee?\xe3\xee\x9d\x1e7\xd6\
\x8fp\xc0\\Q\xcbS*\xea\x19s\x83i\xaf\xad\xed5\xfaov\x19<\xbd7\x11XZ\xba\xc0\
\xad\x9b=z\xab\x1f\xc9V!f\x88\x1ab\x99\xec\x19\x98\x99\x0c\x00\xbc|\xb5\xc9\
\xf2\xe5u\x063\x07\x93\xab\xc0J\\A=#.x4B\x8a\xc4\x18\x891Lc$\xa5\xc4\xa5k\
\xc7\xec\x7f\x1e\xcfG\x98\x89\xb7\xacE\xd6D+\xb6\xeb\xc7\xa7cJ\x89\x18\xc6\
\x98\xfa\\\xc0\xddQ\x9b$\x16;\xfd)fsdQ@\r$;1FB\x08\x7f-\x06\xc8\xea\x88\xda\
\\\xc0\xdc\xa9t.0\x83\x99af\xa8j\x9ds\xf7\xb3\x02j\xce\xf6\x8f\xc0\x93~\xa2\
\x10\xa3\x10\xa5\x14\xa5\xccF)V\x9f+1\xaal\x949\x91\x17G0sJ1\xfa\x9f\x0e\xe9\
\xa5\x1d\x9a\xcd&\t\xe8N\t\xb0w\xa4\xbc\xde\xeb\xb2\xb6|\x9es\x8dx\xd6A!FV\
\xe7\xd1\xed6\xef\xbf5\xb8\xbe\xdaau\xf9bm}\xe3\xdd>/\x06\x115\xa7\xcaV;\x88\
\x00\xeaN)\x8a\x9a1\x1a\x8dx\xb8\x01[\xdb#NNNjjV\x9a\xcd&\xea\x01\xc9F\xb6S#\
\x14\xa2\x93\xef\x11\x01@D\x18\x8f\xc7\xb5\x03U\xa5\xddnc\x9e15\xf2o#8\x94\
\xd9PuRJ<\x7f0\xa4\xd5j\x9d\x11\xe8v\xbbx\xf9\x13\xd1\xf9\xde4\x00\x8a\xe3\
\x82\xc1\xd7\xef\xe4\xa3\x82\x0f;B\xa7\xd3\x01d\xca\t\xbe\x1cdtxHU\x8c\xa9D\
\xa8\x0e\x0e&\x0b\xec\xee\x1eB\x80\xab\x8f\xc1\xe6\x05\xff\xc4\xf0-\x0c7\xf9\
\x05\xc2\xc6H\xf5\xa6\xe7\x172\x00\x00\x00\x00IEND\xaeB`\x82'

    def getFileModifiedData(self):
        return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\xe3IDATx\x9c\xa5\x93\xbdjTA\x14\x80\xbf\x99\xc9\xee\xb2\x12c\x14Q0D\
\x14\x1ba\xed\xd2\x08b\x91\xd6\xd6\xc2\'\xb0\xf3\x01\xc4\xda\x17\xb0\xf3%D+\
\x11\r"H@\xd0BC\x10d%\x85,"A\xa3\xac\xe1\xde;?\xe7\x1c\x8b\xdd\xec\xde\x08\
\xda\xe4\xc0p\xa6\x98\xf9\xce\xc793\xce\xcc\x8c#\xc4\x02\xc0\xab\xa5S\xac\
\xde\xbc\xc5\xee\xd5u\x9c9\x8a*E\xa1\x14Cd\xb2W5\x0ej\r^?\xe3\xdb\xcb\xa7\\\
\xab\xf7&\x80\xc53\xe7\xb8\xb8~\x83t\xf9:1))\x1a\x12\x05\xa2\xa1\xd9p@hU\xdd\
\xdcx\xc2\x95\xb3\x97\xe6\x06\x00\x1e\xe3\xe4\x8a\x91\xb3RJA\xc4\xe1=x\x1fp.\
\xe0\xbd\xc7{O\x08\x01\xf7h\x85\xbc\xb3{\x18\x00\x9e\x85\x9e@(t\x9d\x9b\x1d\
\xfe;\x87\x10\xf8\xe9\x1c\xaaq\x0e03Ld\x82iU\xfaW6QHy\x0ep"X\x8ex\xefq\xce\
\xfd\xf72\x80\xe5\x8c\xe5\xd6\x14L\x14\x9a4\x03\x1c\x84\xaa\xa2\xaa\xc8\xd4\
\xee\xc0\x96"hJm\x80\xe0wF,\xdf}\x00U\x83V5\x12#\x163\xda4h\x93\xb0\x98\xd04\
\xc9\xfd:R\x17i5Q\x05\x9a\xc8xc\x93\xe1\xe0<\x9dN\x07z@\xaf\x03K\x9dI\xe9/_\
\xc9[\x9f\xb8\xb0x\x02\xdf\xed\xa2\xed\x1e\x98\x08T\r\x14\xa1\xdc\xbbM\xf7\
\xddG:k\x03\x8e\xaf\xae\xcc\xd4\x7f<~\xc1\xc2\xdbmL\xa6\xfa\xa5Lg7\xed\x816\
\x11-\x85\xf1xL\xbas\x9f\xea\xcd{\xea\xba\x9e-\x91\xcc1<\xbe\x08\xa4L\xc2\
\xe6\x06\xaa\x82\xd45&B\xce\x13\xb5\x9c3UU\xcd\x0cD\x84e\x02N\x14Q=\x0c\xf0\
\xc5a1C\x11B\x08\xec=\x7fH\xaf\xd7\xc3Z\x00\'\xc2i\x02\xbf\xcd\xa80\n\xad16\
\xcd>\xdfG\x9f\xc9\xa5\xc2>l\xd1\xed\xf71 \xce\x9f)n8d\x97\x9a_&\xecc\x8c\
\xd8g\rpG\xfd\xce\x7f\x00\x84\xd8)\x90\xe6\x1ct\xb0\x00\x00\x00\x00IEND\xaeB\
`\x82'

class drFindReplaceInFilesFrame(wx.Frame):

    def __init__(self, parent, id, title, IsReplace = 0, name =''):

        height = 420
        if not parent.PLATFORM_IS_WIN:
            height = 480 #suggestion from Dan (thanks) for GTK or Linux

        if IsReplace:
            height = 570
            if not parent.PLATFORM_IS_WIN:
                height = 640 #hope, this is sufficient for linux

        wx.Frame.__init__(self, parent, id, title, wx.Point(50, 50), (740, height), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.MINIMIZE_BOX, name)
        #(as option) call with parameter wx.FRAME_FLOAT_ON_PARENT (non modal frame)
        try:
            if os.path.exists (parent.pluginsdirectory + "/bitmaps/drpython_searchinfiles.png"):
                icon = wx.EmptyIcon()
                icon.CopyFromBitmap(wx.BitmapFromImage(wx.Image(parent.pluginsdirectory + "/bitmaps/drpython_searchinfiles.png", wx.BITMAP_TYPE_PNG)))
                self.SetIcon(icon)
        except:
            pass
        self.parent = parent

        self.ID_SAVESIZEPOS = wx.NewId()
        self.ID_CLOSE = wx.NewId()
        self.ID_PREFERENCES = wx.NewId()
        self.ID_VIEW = wx.NewId()
        self.ID_COPYCURRENTFILENAME = wx.NewId()
        self.ID_EDIT = wx.NewId()
        self.ID_CURRENTFILES = wx.NewId()

        self.ID_ADDTOFAVORIT = wx.NewId()
        self.ID_INSERTFAVORIT = wx.NewId()
        self.ID_EDITFAVORITS = wx.NewId()

        self.ID_ABOUT = wx.NewId()
        self.ID_HELP = wx.NewId()

        self.panel = drFindReplaceInFilesPanel(self, id, parent, IsReplace)
        self.panel.closing = 0
        self.SetSizeHints(355, height)
        if self.parent.SEARCHINFILESPREFSsavesizeposition:
            self.panel.LoadDialogSizeAndPosition(self, 'searchinfiles.sizeposcolumn.dat')

        self.menuBar = wx.MenuBar()

        self.filemenu = wx.Menu()
        self.filemenu.Append(self.ID_CLOSE, "&Exit")
        self.menuBar.Append(self.filemenu,"F&ile")

        self.editmenu = wx.Menu()
        self.editmenu.Append(self.ID_EDIT, "&Current DocPath\tAlt-A")
        self.editmenu.Append(self.ID_CURRENTFILES, "Current Open &Files\tAlt-O")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_INSERTFAVORIT, "Insert Favorit\tCtrl-I")
        self.editmenu.Append(self.ID_ADDTOFAVORIT, "Add to Favorits\tCtrl-A")
        self.editmenu.Append(self.ID_EDITFAVORITS, "Edit Favorits\tCtrl-E")
        self.menuBar.Append(self.editmenu,"&Edit")

        self.viewmenu = wx.Menu()
        self.viewmenu.Append(self.ID_VIEW, "&Details")
        self.viewmenu.Append(self.ID_COPYCURRENTFILENAME, "&Copy Currrent Filename")
        self.menuBar.Append(self.viewmenu,"&View")

        self.prefmenu = wx.Menu()
        self.prefmenu.Append(self.ID_PREFERENCES, "&Preferences")
        self.prefmenu.Append(self.ID_SAVESIZEPOS, "&Save Size/Pos/Columns Now")
        self.prefmenu.Enable(self.ID_SAVESIZEPOS, self.parent.SEARCHINFILESPREFSsavesizeposition)
        self.menuBar.Append(self.prefmenu,"&Options")

        self.helpmenu = wx.Menu()
        self.helpmenu.Append(self.ID_ABOUT, "&About")
        self.helpmenu.Append(self.ID_HELP, "&Help")
        self.menuBar.Append(self.helpmenu,"&Help")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU,  self.OnClose, id = self.ID_CLOSE)
        self.Bind(wx.EVT_MENU,  self.OnPreferences, id = self.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU,  self.OnSaveSizePosNow, id = self.ID_SAVESIZEPOS)
        self.Bind(wx.EVT_MENU,  self.OnAbout, id = self.ID_ABOUT)
        self.Bind(wx.EVT_MENU,  self.OnHelp, id = self.ID_HELP)
        self.Bind(wx.EVT_MENU,  self.OnCurrentPath, id = self.ID_EDIT)
        self.Bind(wx.EVT_MENU,  self.OnCurrentOpenFiles, id = self.ID_CURRENTFILES)
        self.Bind(wx.EVT_MENU,  self.OnInsertFavorit, id = self.ID_INSERTFAVORIT)
        self.Bind(wx.EVT_MENU,  self.OnAddtoFavorit, id = self.ID_ADDTOFAVORIT)
        self.Bind(wx.EVT_MENU,  self.OnEditFavorits, id = self.ID_EDITFAVORITS)

        self.Bind(wx.EVT_MENU,  self.OnView, id = self.ID_VIEW)
        self.Bind(wx.EVT_MENU,  self.OnCopyCurrentFilename, id = self.ID_COPYCURRENTFILENAME)

        #wxpython bug? workaround: on the first onsize, the client data width is not correct
        #so call it here to get the data and set the columns
        self.panel.OnSize (None)
        #bug on GTK(?): bug-report (thanks Dan Pozmanter)
        #problem: StatusBar isn't displayed immediatly
        if not parent.PLATFORM_IS_WIN:
            evtsize = wx.SizeEvent (self.GetSize())
            wx.CallAfter (self.OnSize, evtsize)

    #this should force the statusbar to be displayed (?)
    def OnSize (self, event):
        event.Skip()

    def OnCurrentPath(self, event):
        self.panel.cBoxDirectory.SetValue (os.path.split(self.parent.txtDocument.filename)[0])

    #patch from Master_Jaf, for 1.3.2, 14.07.2005
    def OnCurrentOpenFiles(self, event):
        # If you're searching in currently opened files, you have to save them
        # before starting find/replace.
        dl = []
        fl = []
        for f in self.parent.GetAlreadyOpen():
            if f:
                h,t = os.path.split(f)
                if not (h in dl):
                    dl.append(h)
                if not (t in fl):
                    fl.append(t)
        self.panel.cBoxPattern.SetValue (";".join([f for f in fl]))
        self.panel.cBoxDirectory.SetValue (";".join([d for d in dl]))
        self.panel.chkSubDirectories.SetValue(False)

    def OnAddtoFavorit(self, event):
        s = self.panel.cBoxDirectory.GetValue()
        if not s:
            wx.MessageBox("Directory Field is empty", "Add to Favorits", wx.OK | wx.ICON_EXCLAMATION)
            return
        if s in self.parent.SearchInFiles_favoritenames:
            wx.MessageBox("Not added: Already in List: %s" % s, "Add to Favorites",  wx.OK | wx.ICON_EXCLAMATION)
            return
        self.parent.SearchInFiles_favoritenames.append(s)
        wx.MessageBox(self.panel.cBoxDirectory.GetValue(), "Added to Favorites:", wx.OK | wx.ICON_EXCLAMATION)

    def OnEditFavorits(self, event):
        #print self.parent.SearchInFiles_favoritenames
        dlg = ComboBoxEditDialog(self, choices = self.parent.SearchInFiles_favoritenames)
        if dlg.ShowModal() == wx.ID_OK:
            l = dlg.elb.GetListCtrl()
            self.panel.cBoxDirectory.SetValue(l.GetItemText(l.GetFirstSelected()))

    def OnInsertFavorit(self, event):
        d = wx.SingleChoiceDialog(self, "Select Favorit:", "Insert Favorit", self.parent.SearchInFiles_favoritenames, wx.CHOICEDLG_STYLE)
        d.SetSize((250, 250))
        answer = d.ShowModal()
        d.Destroy()
        if answer == wx.ID_OK:
            self.panel.cBoxDirectory.SetValue (d.GetStringSelection())

    def OnSaveColumnwidthsNow (self, event):
        self.parent.Save(self, 'searchinfiles.sizeposcolumn.dat')

    def OnPreferences(self, event):
        OnPreferences (self.parent)
        self.prefmenu.Enable(self.ID_SAVESIZEPOS, self.parent.SEARCHINFILESPREFSsavesizeposition)

    def OnAbout(self, event):
        OnAbout (self.parent)

    def OnHelp(self, event):
        OnHelp (self.parent)

    def OnView(self, event, index = -2):
        #put this in extra class?
        if index == -2:
            index = self.panel.listctrlresults.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index != -1:
            fname = self.panel.GetFilenameFromIndex(index)
            self.onviewdlg = OnViewDlg (self, -1, "Quick View Filtered : " + fname, (800, 600)
                ,wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER, fname, index)
            self.onviewdlg.ShowModal()
            if self.panel.JumpToFileAndLine is not None:
                self.panel.OnActivateItem(None, self.panel.JumpToFileAndLine, fname)
                self.panel.JumpToFileAndLine = None
            if self.panel.NewFindString != "":
                self.panel.cBoxSearchFor.SetValue(self.panel.NewFindString)
                self.panel.OnbtnFind(None)
                self.panel.NewFindString = ""
        #else:
        #no item selected

    def OnCopyCurrentFilename(self, event):
        self.panel.OnCopyCurrentFilename()

    def LoadDialogSizeAndPosition(self, dialog, dialogfile):
        try:
            dlgsizepostfile = os.path.join(self.parent.pluginsdatdirectory, dialogfile)
            if os.path.exists(dlgsizepostfile):
                f = open(dlgsizepostfile, 'r',encoding="UTF-8")
                text = f.read()
                x, y, px, py = map(int, text.split('\n'))
                f.close()
                dialog.SetSize((x, y))
                dialog.Move(wx.Point(px, py))
        except:
            self.parent.ShowMessage("Error Loading Dialog Size", 'Error')


    def SaveDialogSizePosColumn(self):
        self.panel.SaveDialogSizePosColumn (self, 'searchinfiles.sizeposcolumn.dat')

    def OnSaveSizePosNow(self, event):
        if self.parent.SEARCHINFILESPREFSsavesizeposition:
            self.SaveDialogSizePosColumn()

    def OnClose(self, event):
        if self.parent.SEARCHINFILESPREFSsavesizeposition == 2:
            self.SaveDialogSizePosColumn()
        self.Close()

    def OnCloseW(self, event):
        if self.parent.SEARCHINFILESPREFSsavesizeposition == 2:
            self.SaveDialogSizePosColumn()
        self.panel.SaveHistory()
        self.parent.Raise()
        self.parent.SetFocus()
        self.parent.txtDocument.SetFocus()

        event.Skip()


def Plugin(DrFrame):

    DrFrame.FindInFilesHistory = []
    DrFrame.ReplaceInFilesHistory = []

    #Preferences
    DrFrame.SEARCHINFILESPREFSregularexpression = 0
    DrFrame.SEARCHINFILESPREFSmatchcase = 1
    DrFrame.SEARCHINFILESPREFSpromptonreplace = 1
    DrFrame.SEARCHINFILESPREFSsubdirectories = 0
    DrFrame.SEARCHINFILESPREFSbackupbeforereplace = 1
    DrFrame.SEARCHINFILESPREFSwordundersursor = 1
    DrFrame.SEARCHINFILESPREFSsavesizeposition = 0
    DrFrame.SEARCHINFILESPREFScolumnwidths = 0
    DrFrame.SEARCHINFILESPREFSsavelastresults = 0
    DrFrame.SEARCHINFILESPREFSsearchinthread = 0
    DrFrame.SEARCHINFILESPREFSsortcasesensitive = 0
    DrFrame.SEARCHINFILESPREFSsavesorting = 0
    DrFrame.SEARCHINFILESPREFSoccurances = 0
    DrFrame.SEARCHINFILESPREFSappenddironbrowse = 0
    DrFrame.SEARCHINFILESPREFSusefindhistory = 0
    DrFrame.SEARCHINFILESPREFSputsearchtohistoryforfind = 1


    if os.path.exists(DrFrame.pluginspreferencesdirectory+ "/SearchInFiles.preferences.dat"):
        f = open(DrFrame.pluginspreferencesdirectory + "/SearchInFiles.preferences.dat", 'r',encoding="UTF-8")
        text = f.read()
        f.close()
        DrFrame.SEARCHINFILESPREFSregularexpression = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSregularexpression, text, "search.in.files.regularexpression", True)
        DrFrame.SEARCHINFILESPREFSmatchcase = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSmatchcase, text, "search.in.files.match.case", True)
        DrFrame.SEARCHINFILESPREFSpromptonreplace = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSpromptonreplace, text, "search.in.files.prompt.on.replace", True)
        DrFrame.SEARCHINFILESPREFSsubdirectories = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsubdirectories, text, "search.in.files.subdirectories", True)
        DrFrame.SEARCHINFILESPREFSbackupbeforereplace = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSbackupbeforereplace, text, "search.in.files.backup.before.replace", True)
        DrFrame.SEARCHINFILESPREFSwordundersursor = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSwordundersursor, text, "search.in.files.wordundercursor", True)
        DrFrame.SEARCHINFILESPREFSusefindhistory = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSusefindhistory, text, "search.in.files.usefindhistory", True)
        DrFrame.SEARCHINFILESPREFSputsearchtohistoryforfind = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSputsearchtohistoryforfind, text, "search.in.files.putsearchtohistoryforfind", True)
        DrFrame.SEARCHINFILESPREFSsavesizeposition = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsavesizeposition, text, "search.in.files.savesizeposition", True)
        DrFrame.SEARCHINFILESPREFScolumnwidths = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFScolumnwidths, text, "search.in.files.columnwidths", True)
        DrFrame.SEARCHINFILESPREFSsavelastresults = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsavelastresults, text, "search.in.files.savelastresults", True)
        DrFrame.SEARCHINFILESPREFSappenddironbrowse = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSappenddironbrowse, text, "search.in.files.appenddironbrowse", True)
        DrFrame.SEARCHINFILESPREFSsearchinthread = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsearchinthread, text, "search.in.files.searinthread", True)
        DrFrame.SEARCHINFILESPREFSsortcasesensitive = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsortcasesensitive, text, "search.in.files.sortcasesensitive", True)
        DrFrame.SEARCHINFILESPREFSsavesorting = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSsavesorting, text, "search.in.files.savesorting", True)
        DrFrame.SEARCHINFILESPREFSoccurances = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSoccurances , text, "search.in.files.occurances", True)

    #End Preferences

    def ReloadOccurances():
        if os.path.exists(DrFrame.pluginspreferencesdirectory + "/SearchInFiles.preferences.dat"):
            f = open(DrFrame.pluginspreferencesdirectory + "/SearchInFiles.preferences.dat", 'r',encoding="UTF-8")
            text = f.read()
            f.close()
            DrFrame.SEARCHINFILESPREFSoccurances = drPrefsFile.GetPrefFromText(DrFrame.SEARCHINFILESPREFSoccurances , text, "search.in.files.occurances", True)

    def OnFindInFiles(event):
        window = DrFrame.FindWindowByName("Search In Files")
        if window is None:
            ReloadOccurances()
            drFindReplaceInFilesFrame(DrFrame, -1, "Search In Files", name="Search In Files").Show(True)
        else:
            window.SetFocus()
            #window.panel.listctrlresults.SetFocus()
            if DrFrame.SEARCHINFILESPREFSwordundersursor:
                #oldtext = window.panel.cBoxSearchFor.GetValue()
                window.panel.FindAndSetDefaultSearchString()
                #if window.panel.cBoxSearchFor.GetValue() != oldtext:
                #   window.panel.cBoxSearchFor.SetFocus()
            window.panel.cBoxSearchFor.SetFocus()
            if not DrFrame.PLATFORM_IS_WIN:
                window.Raise()

    def OnReplaceInFiles(event):
        window = DrFrame.FindWindowByName("Replace In Files")
        if window is None:
            ReloadOccurances()
            drFindReplaceInFilesFrame(DrFrame, -1, "Replace In Files", True, "Replace In Files").Show(True)
        else:
            window.SetFocus()
            window.panel.listctrlresults.SetFocus()
            if DrFrame.SEARCHINFILESPREFSwordundersursor:
                window.panel.FindAndSetDefaultSearchString()
            window.panel.cBoxSearchFor.SetFocus()
            if not DrFrame.PLATFORM_IS_WIN:
                window.Raise()

    ID_FIND_IN_FILES = DrFrame.GetNewId()
    ID_REPLACE_IN_FILES = DrFrame.GetNewId()


    DrFrame.Bind(wx.EVT_MENU, OnFindInFiles, id=ID_FIND_IN_FILES)
    DrFrame.Bind(wx.EVT_MENU, OnReplaceInFiles, id=ID_REPLACE_IN_FILES)

    DrFrame.AddPluginFunction("SearchInFiles", "Find In Files", OnFindInFiles)
    DrFrame.AddPluginFunction("SearchInFiles", "Replace In Files", OnReplaceInFiles)
    DrFrame.SearchInFiles_searchhistfile = DrFrame.pluginsdatdirectory + "/SearchInFilesHistory.log"

    DrFrame.LoadPluginShortcuts('SearchInFiles')
    DrFrame.searchmenu.AppendSeparator()
    DrFrame.searchmenu.Append(ID_FIND_IN_FILES, DrFrame.GetPluginMenuLabel('SearchInFiles', 'Find In Files', 'Find In Files'))
    DrFrame.searchmenu.Append(ID_REPLACE_IN_FILES, DrFrame.GetPluginMenuLabel('SearchInFiles', 'Replace In Files', 'Replace In Files'))
