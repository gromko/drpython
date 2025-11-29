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
#Full Screen Support

#Version 0.0.1 08.04.2007

import wx

def OnAbout(DrFrame):
    AboutString = """FullScreen:

Version: 0.0.1

By Daniel Pozmanter

Released under the GPL."""
    DrFrame.ShowMessage(AboutString, "About")

def Plugin(DrFrame):

    def OnToggleFullScreen(event):
        DrFrame.ShowFullScreen(not DrFrame.IsFullScreen(), \
wx.FULLSCREEN_NOTOOLBAR | wx.FULLSCREEN_NOBORDER | wx.FULLSCREEN_NOCAPTION)

    ID_TOGGLE_FULLSCREEN = DrFrame.GetNewId()

    DrFrame.LoadPluginShortcuts('FullScreen')
    DrFrame.viewmenu.AppendSeparator()
    DrFrame.viewmenu.Append(ID_TOGGLE_FULLSCREEN, "Toggle FullScreen Mode")

    DrFrame.Bind(wx.EVT_MENU, OnToggleFullScreen, id=ID_TOGGLE_FULLSCREEN)

    DrFrame.AddPluginFunction("FullScreen", "Toggle FullScreen Mode", OnToggleFullScreen)
