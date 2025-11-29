def OnAbout(DrFrame):
    DrFrame.ShowMessage("Clipboard Editor\nVersion 1.0\n\nBy DrPython User", "About")

def Plugin(DrFrame):
    import wx

    class ClipboardEditorDialog(wx.Dialog):
        def __init__(self, parent):
            super(ClipboardEditorDialog, self).__init__(
                parent,
                title="Редактор буфера обміну",
                size=(500, 300)
            )
            self.text_value = ""
            self.InitUI()
            self.Centre()

        def InitUI(self):
            panel = wx.Panel(self)
            vbox = wx.BoxSizer(wx.VERTICAL)

            self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
            vbox.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

            hbox = wx.BoxSizer(wx.HORIZONTAL)
            ok_btn = wx.Button(panel, wx.ID_OK, "OK")
            ok_btn.SetDefault()
            cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")

            hbox.Add(ok_btn, flag=wx.RIGHT, border=5)
            hbox.Add(cancel_btn)

            vbox.Add(hbox, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)
            panel.SetSizer(vbox)

            self.LoadFromClipboard()

        def LoadFromClipboard(self):
            try:
                if wx.TheClipboard.Open():
                    data = wx.TextDataObject()
                    if wx.TheClipboard.GetData(data):
                        text = data.GetText()
                        self.text_ctrl.SetValue(text)
                        self.text_value = text
                    wx.TheClipboard.Close()
            except Exception:
                self.text_ctrl.SetValue("")
                self.text_value = ""

        def GetEditedText(self):
            return self.text_ctrl.GetValue()

    # --- Реєстрація меню ---
    ID_CLIP_EDITOR = DrFrame.GetNewId()

    if hasattr(DrFrame, "programmenu"):
        menu = DrFrame.programmenu
    else:
        menu = DrFrame.optionsmenu

    menu.AppendSeparator()
    menu.Append(ID_CLIP_EDITOR, "Clipboard Editor")

    def ShowClipEditor(event):
        dlg = ClipboardEditorDialog(DrFrame)
        if dlg.ShowModal() == wx.ID_OK:
            # 🔥 Саме тут записуємо у буфер обміну!
            edited_text = dlg.GetEditedText()
            try:
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(edited_text))
                    wx.TheClipboard.Close()
            except Exception:
                pass
        dlg.Destroy()

    DrFrame.Bind(wx.EVT_MENU, ShowClipEditor, id=ID_CLIP_EDITOR)
