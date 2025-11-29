#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2004 Daniel Pozmanter
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
#Shell Menu

#Version: 1.0.1, 08.04.2007.

import wx
import wx.lib.dialogs

def OnAbout(DrFrame):
    Version = "Shell Menu: Version: 1.0.1\n"
    AboutString = Version + "By Daniel Pozmanter\n\nReleased under the GPL."
    d = wx.lib.dialogs.ScrolledMessageDialog(DrFrame, AboutString, "About")
    d.ShowModal()
    d.Destroy()

def Plugin(DrFrame):
    def OnRunInPrompt(event):
        d = wx.TextEntryDialog(DrFrame, "Enter Shell Command:", "Run Shell Command In Prompt", DrFrame.InPromptCommand)
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            DrFrame.Execute(v)

    def OnRunWithShell(event):
        d = wx.TextEntryDialog(DrFrame, "Enter Shell Command:", "Run Shell Command In wx.Shell", DrFrame.ShellCommand)
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            DrFrame.ShellCommand = v
            wx.Shell(v)

    ID_IN_PROMPT = DrFrame.GetNewId()
    ID_WX_SHELL = DrFrame.GetNewId()

    DrFrame.InPromptCommand = ""
    DrFrame.ShellCommand = ""

    DrFrame.LoadPluginShortcuts('ShellMenu')

    shellmenu = wx.Menu()
    shellmenu.Append(ID_IN_PROMPT, "Run In Prompt")
    shellmenu.Append(ID_WX_SHELL, "wx.Shell")

    DrFrame.programmenu.AppendSeparator()
    DrFrame.programmenu.AppendMenu(DrFrame.GetNewId(), "Shell Command", shellmenu)

    DrFrame.Bind(wx.EVT_MENU, OnRunInPrompt, id=ID_IN_PROMPT)
    DrFrame.Bind(wx.EVT_MENU, OnRunWithShell, id=ID_WX_SHELL)

    DrFrame.AddPluginShortcutFunction("ShellMenu", "OnRunInPrompt", OnRunInPrompt)
    DrFrame.AddPluginShortcutFunction("ShellMenu", "OnRunWithShell", OnRunWithShell)
