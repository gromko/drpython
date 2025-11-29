import wx

def OnAbout(DrFrame):
    DrFrame.ShowMessage("PIP GUI\nVersion 0.0.3", "About")

def Plugin(DrFrame):
    class PipManager(wx.Dialog):
        def __init__(self, parent):
            self.alive = True  
            super().__init__(parent, title='Розпорядник пакетів PIP', size=(800, 600))
            self.InitUI()
            self.Bind(wx.EVT_CLOSE, self.OnClose)
       
        
        def InitUI(self):
            panel = wx.Panel(self)
            main_sizer = wx.BoxSizer(wx.VERTICAL)
        
            # Заголовок
            title = wx.StaticText(panel, label="Розпорядник пакетів PIP")
            title.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            main_sizer.Add(title, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        
            # Горизонтальний сізер для списку (ліворуч) і логу (праворуч)
            content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
            self.packages_list = wx.ListBox(panel, style=wx.LB_SINGLE)
            content_sizer.Add(self.packages_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
            self.log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
            content_sizer.Add(self.log, proportion=3, flag=wx.EXPAND | wx.ALL, border=5)
        
            main_sizer.Add(content_sizer, proportion=1, flag=wx.EXPAND)
        
            # Кнопки внизу
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for lbl, func in (("Оновити", self.LoadPackages),
                              ("Інформація", self.OnInfo),
                              ("Встановити", self.OnInstall),
                              ("Видалити", self.OnRemove)):
                b = wx.Button(panel, label=lbl)
                b.Bind(wx.EVT_BUTTON, func)
                button_sizer.Add(b, proportion=1, flag=wx.ALL, border=5)
        
            main_sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        
            # 🔑 Головне: сізер призначається PANEL, а не self!
            panel.SetSizer(main_sizer)
        
            # Діалог просто містить panel
            dialog_sizer = wx.BoxSizer(wx.VERTICAL)
            dialog_sizer.Add(panel, proportion=1, flag=wx.EXPAND)
            self.SetSizer(dialog_sizer)
        
            self.Centre()
            self.LoadPackages()

        def OnClose(self, event):
            self.alive = False
            self.Destroy()

        def SafeAppend(self, text):
            if self.alive and self.log:
                self.log.AppendText(text)
                self.log.SetInsertionPointEnd()

        def LoadPackages(self, event=None):
            try:
                import pkg_resources
                pkgs = [p.key for p in pkg_resources.working_set]
                self.packages_list.Clear()
                self.packages_list.AppendItems(pkgs)
                self.SafeAppend(f"Завантажено {len(pkgs)} пакетів.\n")
            except Exception as e:
                self.SafeAppend(f"Помилка: {e}\n")

        def OnInfo(self, event):
            import threading
            sel = self.packages_list.GetSelection()
            if sel == wx.NOT_FOUND: return
            pkg = self.packages_list.GetString(sel)
            self.SafeAppend(f"Інформація про {pkg}...\n")
            t = threading.Thread(target=self._pip_show, args=(pkg,), daemon=True)
            t.start()

        def _pip_show(self, pkg):
            import subprocess, sys
            try:
                out = subprocess.check_output([sys.executable, '-m', 'pip', 'show', pkg],
                                              stderr=subprocess.STDOUT)
                wx.CallAfter(self.SafeAppend, out.decode(errors='replace'))
            except subprocess.CalledProcessError as e:
                wx.CallAfter(self.SafeAppend, e.output.decode(errors='replace'))

        def OnInstall(self, event):
            import wx, threading
            dlg = wx.TextEntryDialog(self, 'Назва пакету:', 'Встановлення пакету')
            if dlg.ShowModal() == wx.ID_OK:
                pkg = dlg.GetValue()
                self.SafeAppend(f"Встановлення {pkg}...\n")
                t = threading.Thread(target=self._pip_cmd, args=(["install", pkg],), daemon=True)
                t.start()
            dlg.Destroy()

        def OnRemove(self, event):
            import wx, threading
            sel = self.packages_list.GetSelection()
            if sel == wx.NOT_FOUND: return
            pkg = self.packages_list.GetString(sel)
            dlg = wx.MessageDialog(self, f"Видалити {pkg}?", "Підтвердження", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.SafeAppend(f"Видалення {pkg}...\n")
                t = threading.Thread(target=self._pip_cmd, args=(["uninstall", "-y", pkg],), daemon=True)
                t.start()
            dlg.Destroy()

        def _pip_cmd(self, args):
            import subprocess, sys
            try:
                out = subprocess.check_output([sys.executable, '-m', 'pip'] + args,
                                              stderr=subprocess.STDOUT)
                wx.CallAfter(self.SafeAppend, out.decode(errors='replace'))
                wx.CallAfter(self.LoadPackages)
            except subprocess.CalledProcessError as e:
                wx.CallAfter(self.SafeAppend, e.output.decode(errors='replace'))

    # --- Додаємо пункт меню ---
    ID = DrFrame.GetNewId()
    menu = DrFrame.optionsmenu
    menu.Append(ID, "Розпорядник пакетів PIP")

    def PipShow(evt):
        dlg = PipManager(DrFrame)
        dlg.ShowModal()
        dlg.Destroy()

    DrFrame.Bind(wx.EVT_MENU, PipShow, id=ID)
