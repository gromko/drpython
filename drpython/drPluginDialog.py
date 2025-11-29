
#Plugins Dialog
# Plugins Dialog (локальна версія)
import os, shutil, zipfile, tempfile, sys
import wx, wx.adv, wx.lib.dialogs, wx.html, wx.lib.newevent
import drScrolledMessageDialog
import drFileDialog
from drPrefsFile import ExtractPreferenceFromText
import _thread

#*******************************************************************************
# Install Wizard (локальна версія)
class drPluginInstallLocationPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Встановлення доповнень")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        msg = wx.StaticText(self, -1, label="Помічник допоможе встановити доповнення drPython з ZIP-пакетів.\n"
                                           "Пакет має містити файл з кодом доповнення у форматі .py\n"
                                           "та, за потреби, індексний файл (.idx).\n"
                                           "Для продовження натисніть Next.")
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(msg, -1, wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

class drPluginInstallSelectPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Оберіть доповнення для встановлення:")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.btnAdd = wx.Button(self, wx.ID_ADD)
        self.btnRemove = wx.Button(self, wx.ID_REMOVE)
        self.lstPlugins = wx.ListBox(self, wx.ID_ANY, size=(300, 300))
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.bSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bSizer.Add(self.btnAdd, 0, wx.SHAPED | wx.ALIGN_LEFT)
        self.bSizer.Add(self.btnRemove, 0, wx.SHAPED)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.bSizer, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.lstPlugins, 0, wx.SHAPED)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btnAdd)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.btnRemove)

    def OnAdd(self, event):
        dlg = drFileDialog.FileDialog(self.parent.ancestor, "Оберіть ZIP-файли доповнень", self.parent.wildcard, MultipleSelection=True)
        if self.parent.ancestor.pluginsdirectory:
            dlg.SetDirectory(self.parent.ancestor.pluginsdirectory)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            filenames = [x.replace('\\', '/') for x in filenames]
            self.parent.pluginstoinstall.extend(filenames)
            labels = [os.path.splitext(os.path.split(x)[1])[0] for x in filenames]
            self.parent.pluginlabels.extend(labels)
            self.parent.pluginsinstallmethod.extend([0] * len(labels))
            self.lstPlugins.Set(self.parent.pluginlabels)
        dlg.Destroy()

    def OnRemove(self, event):
        i = self.lstPlugins.GetSelection()
        if i < 0:
            return
        answer = wx.MessageBox(f"Видалити '{self.parent.pluginlabels[i]}'?", "Видалити зі списку", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            self.parent.pluginlabels.pop(i)
            self.parent.pluginstoinstall.pop(i)
            self.lstPlugins.Set(self.parent.pluginlabels)

    def Run(self):
        pass  # Немає потреби в оновленні списку плагінів онлайн

(UpdateDownloadPage, EVT_UPDATE_DOWNLOADPAGE) = wx.lib.newevent.NewEvent()

class drPluginInstallDownloadPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        self.errors = []
        title = wx.StaticText(self, -1, "Розпакування обраних доповнень:")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.stxtUnPacking = wx.StaticText(self, -1, "Розпакування...")
        self.stxtDone = wx.StaticText(self, -1, "Готово")
        self.stxtUnPacking.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtDone.SetForegroundColour(self.GetBackgroundColour())
        self.gUnPack = wx.Gauge(self, -1, 0, size=(250, -1))
        
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtUnPacking, 0, wx.SHAPED)
        self.theSizer.Add(self.gUnPack, 0, wx.SHAPED)
       
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtDone, 0, wx.SHAPED)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(EVT_UPDATE_DOWNLOADPAGE, self.UpdateUI)

    def CreateDirectories(self, targetdir, zippedfilename):
        zippedfilename = zippedfilename.replace('\\', '/')
        d = zippedfilename.find('/')
        while d > -1:
            dir = zippedfilename[:d]
            targetdir = os.path.join(targetdir, dir)
            if not os.path.exists(targetdir):
                os.mkdir(targetdir)
            zippedfilename = zippedfilename[d+1:]
            d = zippedfilename.find('/')

    def Run(self):
        _thread.start_new_thread(self.RunInThread, ())

    def RunInThread(self):
        
        l = len(self.parent.pluginstoinstall)
        if l == 0:
            wx.PostEvent(self, UpdateDownloadPage(step=1, range=0, value=0, done=True, status="No plugins to install."))
            return
    
        wx.PostEvent(self, UpdateDownloadPage(step=1, range=l, value=0, done=False, status=""))
        x = 0
        while x < l:
            self.UnPack(self.parent.pluginstoinstall[x], self.parent.pluginlabels[x])
            x += 1
            wx.PostEvent(self, UpdateDownloadPage(step=1, range=l, value=x, done=False, status=""))
        wx.PostEvent(self, UpdateDownloadPage(step=1, range=l, value=x, done=True, status=""))

    def UnPack(self, filename, label):
        try:
            zf = zipfile.ZipFile(filename, 'r')
            dir = os.path.join(self.parent.tempdir, label)
            if not os.path.exists(dir):
                os.mkdir(dir)
            zippedfiles = zf.namelist()
            self.parent.UnZippedFilesArray.append(zippedfiles)
            for zippedfile in zippedfiles:
                if zippedfile.endswith('/') or zippedfile.endswith('\\'):
                    self.CreateDirectories(dir, zippedfile)
                else:
                    self.CreateDirectories(dir, zippedfile)
                    data = zf.read(zippedfile)
                    with open(os.path.join(dir, zippedfile), 'wb') as f:
                        f.write(data)
            zf.close()
        except Exception as e:
            self.errors.append([filename, str(e)])

    def UpdateUI(self, event):
        if event.step == 1:
            if not event.done:
                self.stxtUnPacking.SetForegroundColour(self.GetForegroundColour())
            else:
                self.stxtUnPacking.SetForegroundColour(wx.Colour(175, 175, 175))
                self.stxtDone.SetForegroundColour(self.GetForegroundColour())
            if event.range != self.gUnPack.GetRange():
                self.gUnPack.SetRange(event.range)
            self.gUnPack.SetValue(event.value)
            self.Refresh()
            if self.errors:
                error = self.errors.pop(0)
                drScrolledMessageDialog.ShowMessage(self.parent,
                    f"Помилка розпакування '{error[0]}':\n{error[1]}", "Помилка")

class drPluginInstallIndexPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Спосіб завантаження:")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.chklLoadByDefault = wx.CheckListBox(self, wx.ID_ANY, choices=self.parent.pluginlabels)
        self.chklLoadFromIndex = wx.CheckListBox(self, wx.ID_ANY, choices=[])
        self.theSizer = wx.FlexGridSizer(0, 1, 5, 5)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.EXPAND)
        self.theSizer.Add(wx.StaticText(self, -1, "Завантажувати за замовчуванням:"), 0, wx.EXPAND)
        self.theSizer.Add(self.chklLoadByDefault, 0, wx.EXPAND)
        self.theSizer.Add(wx.StaticText(self, -1, "Завантажувати через індекс:"), 0, wx.EXPAND)
        self.theSizer.Add(self.chklLoadFromIndex, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnLoadByDefault, self.chklLoadByDefault)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnLoadFromIndex, self.chklLoadFromIndex)

    def GetDefSel(self, idx_sel):
        txt = self.chklLoadFromIndex.GetString(idx_sel)
        return self.chklLoadByDefault.FindString(txt)

    def GetIdxSel(self, def_sel):
        txt = self.chklLoadByDefault.GetString(def_sel)
        return self.chklLoadFromIndex.FindString(txt)

    def OnLoadByDefault(self, event):
        sel = event.GetSelection()
        i = self.GetIdxSel(sel)
        if sel > -1:
            if self.chklLoadByDefault.IsChecked(sel) and i > -1:
                self.parent.pluginsinstallmethod[sel] = 0
                self.chklLoadFromIndex.Check(i, False)
            elif i > -1 and not self.chklLoadFromIndex.IsChecked(i):
                self.parent.pluginsinstallmethod[sel] = -1

    def OnLoadFromIndex(self, event):
        sel = event.GetSelection()
        i = self.GetDefSel(sel)
        if sel > -1 and i > -1:
            if self.chklLoadFromIndex.IsChecked(sel):
                self.parent.pluginsinstallmethod[i] = 1
                self.chklLoadByDefault.Check(i, False)
            elif not self.chklLoadByDefault.IsChecked(i):
                self.parent.pluginsinstallmethod[i] = -1

    def Run(self):
        if not self.parent.pluginstoinstall:
            return
        self.chklLoadByDefault.Set(self.parent.pluginlabels)
        indexlabels = []
        for x, label in enumerate(self.parent.pluginlabels):
            pluginname = label.split('-')[0].split('.')[0]
            for fn in self.parent.UnZippedFilesArray[x]:
                if fn.endswith(pluginname + ".idx"):
                    indexlabels.append(label)
                    break
        self.chklLoadFromIndex.Set(indexlabels)
        for i in range(len(self.parent.pluginlabels)):
            self.chklLoadByDefault.Check(i, True)

class drPluginInstallInstallPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Встановлення доповнень:")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.stxtInstalling = wx.StaticText(self, -1, "Встановлення...")
        self.stxtIndexing = wx.StaticText(self, -1, "Індексація...")
        self.stxtDone = wx.StaticText(self, -1, "Виконано")
        self.stxtInstalling.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtIndexing.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtDone.SetForegroundColour(self.GetBackgroundColour())
        self.gInstall = wx.Gauge(self, -1, 0, size=(200, -1))
        self.gIndex = wx.Gauge(self, -1, 0, size=(200, -1))
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtInstalling, 0, wx.SHAPED)
        self.theSizer.Add(self.gInstall, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtIndexing, 0, wx.SHAPED)
        self.theSizer.Add(self.gIndex, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtDone, 0, wx.SHAPED)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

    def RemoveTempDir(self, tempdir):
        entries = os.listdir(tempdir)
        for entry in entries:
            fname = os.path.join(tempdir, entry)
            if os.path.isdir(fname):
                self.RemoveTempDir(fname)
            else:
                os.remove(fname)
        os.rmdir(tempdir)

    def Index(self, label, unzippedfiles, installmethod):
        pluginname = label.split('-')[0].split('.')[0]
        if installmethod == 0:
            indexfile = os.path.join(self.parent.GetParent().preferencesdirectory, "default.idx")
            if not os.path.exists(indexfile):
                open(indexfile, 'w', encoding='UTF-8').close()
            try:
                with open(indexfile, 'r', encoding='UTF-8') as f:
                    plugins = [x.strip() for x in f if x.strip()]
                plugins = [p for p in plugins if p != pluginname]
                plugins.append(pluginname)
                with open(indexfile, 'w', encoding='UTF-8') as f:
                    f.write('\n'.join(plugins) + '\n')
            except Exception as e:
                drScrolledMessageDialog.ShowMessage(self.parent,
                    f"Помилка додавання '{pluginname}' до default.idx:\n{e}", "Помилка")
        elif installmethod == 1:
            target = pluginname + ".idx"
            indexfile = None
            for fname in unzippedfiles:
                if os.path.basename(fname) == target:
                    indexfile = os.path.join(self.parent.tempdir, label, fname)
                    break
            if not indexfile or not os.path.exists(indexfile):
                drScrolledMessageDialog.ShowMessage(self.parent, f"Не знайдено .idx файл для '{label}'", "Помилка індексації")
                return
            shutil.copyfile(indexfile, os.path.join(self.parent.pluginsdirectory, target))

    def Install(self, filename, label, unzippedfiles):
        pluginname = label.split('-')[0].split('.')[0]
        dir = os.path.join(self.parent.tempdir, label)
        target = pluginname + ".py"
        pluginfile = None
        for fname in unzippedfiles:
            if os.path.basename(fname) == target:
                pluginfile = os.path.join(dir, fname)
                break
        if not pluginfile:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Не знайдено .py файл для '{label}'", "Помилка встановлення")
            return

        pluginrfile = os.path.join(self.parent.pluginsdirectory, target)
        plugininstallfile = pluginfile + ".install"
        continueinstallation = True

        if os.path.exists(plugininstallfile):
            try:
                with open(plugininstallfile, 'r', encoding='UTF-8') as f:
                    scripttext = f.read()
                code = compile(scripttext + '\n', plugininstallfile, "exec")
                cwd = os.getcwd()
                os.chdir(os.path.join(dir, os.path.commonprefix(unzippedfiles) or '.'))
                exec(code)
                continueinstallation = Install(self.parent.ancestor)
                os.chdir(cwd)
            except Exception as e:
                drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка виконання install-скрипта:\n{e}", "Помилка")
                return

        if continueinstallation:
            try:
                copyf = True
                if os.path.exists(pluginrfile):
                    answer = wx.MessageBox(f"Перезаписати '{pluginrfile}'?", "DrPython", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                    if answer != wx.YES:
                        copyf = False
                if copyf:
                    shutil.copyfile(pluginfile, pluginrfile)
                    # Копіюємо .idx, якщо є
                    idx_src = os.path.splitext(pluginfile)[0] + ".idx"
                    if os.path.exists(idx_src):
                        idx_dst = os.path.splitext(pluginrfile)[0] + ".idx"
                        shutil.copyfile(idx_src, idx_dst)
            except Exception as e:
                drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка копіювання '{pluginfile}':\n{e}", "Помилка")

    def Run(self):
        l = len(self.parent.pluginstoinstall)
        if l < 1:
            self.stxtDone.SetForegroundColour(self.GetForegroundColour())
            return

        self.stxtInstalling.SetForegroundColour(self.GetForegroundColour())
        self.gInstall.SetRange(l)
        for x in range(l):
            self.Install(self.parent.pluginstoinstall[x], self.parent.pluginlabels[x], self.parent.UnZippedFilesArray[x])
            self.gInstall.SetValue(x + 1)
        self.stxtInstalling.SetForegroundColour(wx.Colour(175, 175, 175))

        self.stxtIndexing.SetForegroundColour(self.GetForegroundColour())
        self.gIndex.SetRange(l)
        for x in range(l):
            self.Index(self.parent.pluginlabels[x], self.parent.UnZippedFilesArray[x], self.parent.pluginsinstallmethod[x])
            self.gIndex.SetValue(x + 1)
        self.stxtIndexing.SetForegroundColour(wx.Colour(175, 175, 175))

        # Очищення тимчасових файлів
        for label in self.parent.pluginlabels:
            dir = os.path.join(self.parent.tempdir, label)
            try:
                self.RemoveTempDir(dir)
            except:
                pass

        self.stxtDone.SetForegroundColour(self.GetForegroundColour())

class drPluginInstallWizard(wx.adv.Wizard):
    def __init__(self, parent, title, bitmap):
        wx.adv.Wizard.__init__(self, parent, wx.ID_ANY, title, bitmap)
        self.ancestor = parent
        self.pluginsdirectory = parent.pluginsdirectory
        self.wildcard = "DrPython Plugin Archive (*.zip)|*.zip"
        self.pluginstoinstall = []
        self.pluginsinstallmethod = []
        self.pluginlabels = []
        self.UnZippedFilesArray = []
        try:
            self.tempdir = os.path.split(tempfile.mktemp())[0].replace('\\', '/')
        except:
            drScrolledMessageDialog.ShowMessage(parent, "Помилка отримання тимчасової теки.", "Помилка")
            return

        self.LocationPage = drPluginInstallLocationPage(self)
        self.SelectPage = drPluginInstallSelectPage(self)
        self.DownloadPage = drPluginInstallDownloadPage(self)
        self.IndexPage = drPluginInstallIndexPage(self)
        self.InstallPage = drPluginInstallInstallPage(self)

        wx.adv.WizardPageSimple.Chain(self.LocationPage, self.SelectPage)
        wx.adv.WizardPageSimple.Chain(self.SelectPage, self.DownloadPage)
        wx.adv.WizardPageSimple.Chain(self.DownloadPage, self.IndexPage)
        wx.adv.WizardPageSimple.Chain(self.IndexPage, self.InstallPage)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        cp = self.GetCurrentPage()
        if cp == self.SelectPage:
            self.SelectPage.Run()
        elif cp == self.DownloadPage:
            self.DownloadPage.Run()
        elif cp == self.IndexPage:
            self.IndexPage.Run()
        elif cp == self.InstallPage:
            self.InstallPage.Run()

    def Run(self):
        self.RunWizard(self.LocationPage)

#*******************************************************************************
# UnInstall Wizard (без змін)
class drPluginUnInstallSelectPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Оберіть доповнення\n для видалення:")
        self.btnAdd = wx.Button(self, wx.ID_ADD)
        self.btnRemove = wx.Button(self, wx.ID_REMOVE)
        self.lstPlugins = wx.ListBox(self, wx.ID_ANY, size=(300, 300))
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.bSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bSizer.Add(self.btnAdd, 0, wx.SHAPED | wx.ALIGN_LEFT)
        self.bSizer.Add(self.btnRemove, 0, wx.SHAPED)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.bSizer, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.lstPlugins, 0, wx.SHAPED)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btnAdd)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.btnRemove)

    def OnAdd(self, event):
        plist = os.listdir(self.parent.GetParent().pluginsdirectory)
        PluginList = [p[:-3] for p in plist if p.endswith(".py")]
        PluginList.sort()
        d = wx.lib.dialogs.MultipleChoiceDialog(self, "Оберіть доповнення\n для видалення:", "Додати доповнення до списку", PluginList)
        if d.ShowModal() == wx.ID_OK:
            selections = d.GetValueString()
            self.parent.pluginstoremove.extend(selections)
            self.lstPlugins.Set(self.parent.pluginstoremove)
        d.Destroy()

    def OnRemove(self, event):
        i = self.lstPlugins.GetSelection()
        if i < 0:
            return
        answer = wx.MessageBox("Видалити '%s'?" % self.parent.pluginstoremove[i], "Видалити доповнення зі списку", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            self.parent.pluginstoremove.pop(i)
            self.lstPlugins.Set(self.parent.pluginstoremove)

class drPluginUnInstallDataPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Видалити налаштування\n та сполучення клавіш?:")
        self.chklData = wx.CheckListBox(self, wx.ID_ANY, choices=self.parent.pluginstoremove)
        self.theSizer = wx.FlexGridSizer(0, 1, 5, 5)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.EXPAND)
        self.theSizer.Add(self.chklData, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnData, self.chklData)

    def OnData(self, event):
        sel = event.GetSelection()
        if sel > -1:
            self.parent.removealldataforpluginArray[sel] = self.chklData.IsChecked(sel)

    def Run(self):
        if not self.parent.pluginstoremove:
            return
        self.chklData.Set(self.parent.pluginstoremove)
        self.parent.removealldataforpluginArray = [True] * len(self.parent.pluginstoremove)
        for i in range(len(self.parent.pluginstoremove)):
            self.chklData.Check(i, True)

class drPluginUnInstallUnInstallPage(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        wx.adv.WizardPageSimple.__init__(self, parent)
        self.parent = parent
        title = wx.StaticText(self, -1, "Видалення обраних доповнень:")
        title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.stxtUnInstalling = wx.StaticText(self, -1, "Видалення...")
        self.stxtUnIndexing = wx.StaticText(self, -1, "Видалення з файлів індексу...")
        self.stxtDone = wx.StaticText(self, -1, "Виконано")
        self.stxtUnInstalling.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtUnIndexing.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtDone.SetForegroundColour(self.GetBackgroundColour())
        self.gUnInstall = wx.Gauge(self, -1, 0, size=(200, -1))
        self.gUnIndex = wx.Gauge(self, -1, 0, size=(200, -1))
        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.theSizer.Add(title, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtUnInstalling, 0, wx.SHAPED)
        self.theSizer.Add(self.gUnInstall, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtUnIndexing, 0, wx.SHAPED)
        self.theSizer.Add(self.gUnIndex, 0, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.theSizer.Add(self.stxtDone, 0, wx.SHAPED)
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

    def RemoveDatFiles(self, plugin):
        pluginpreferencesfilebase = os.path.join(self.parent.GetParent().pluginsdirectory, plugin)
        pluginshortcutsfilebase = os.path.join(self.parent.GetParent().pluginsshortcutsdirectory, plugin)
        try:
            if os.path.exists(pluginpreferencesfilebase + ".preferences.dat"):
                os.remove(pluginpreferencesfilebase + ".preferences.dat")
            if os.path.exists(pluginshortcutsfilebase + ".shortcuts.dat"):
                os.remove(pluginshortcutsfilebase + ".shortcuts.dat")
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, "Помилка при видаленні файлів налаштувань доповнення", "Помилка видалення")



    def RemoveFromIndex(self, idx):
        print("Remove idx =", idx)
    
        # Обробляємо файл, чия назва передана (наприклад, progCalc.idx)
        if idx == "default.idx":
            idxfile = os.path.join(self.parent.GetParent().preferencesdirectory, idx)
        else:
            idxfile = os.path.join(self.parent.GetParent().pluginsdirectory, idx)
    
        if not os.path.exists(idxfile):
            return
    
        try:
            with open(idxfile, 'r', encoding='UTF-8') as f:
                plugins = [line.strip() for line in f if line.strip()]
        except Exception as e:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка читання індексу '{idx}':\n{e}", "Помилка")
            return
    
        pluginstowrite = [p for p in plugins if p not in self.parent.pluginstoremove]
    
        try:
            if not pluginstowrite:
                if idx == "default.idx":
                    with open(idxfile, 'w', encoding='UTF-8') as f:
                        pass  # залишаємо порожнім
                else:
                    os.remove(idxfile)
            else:
                with open(idxfile, 'w', encoding='UTF-8') as f:
                    for p in pluginstowrite:
                        f.write(p + '\n')
        except Exception as e:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка запису індексу '{idx}':\n{e}", "Помилка")
    
        # 🔥 Додатково: видаляємо плагіни з default.idx, якщо це не він сам
        if idx != "default.idx":
            # Витягуємо назву плагіна з імені .idx-файлу
            plugin_name = os.path.splitext(idx)[0]
            if plugin_name in self.parent.pluginstoremove:
                self._remove_from_default_index(plugin_name)


    def _remove_from_default_index(self, plugin_name):
        default_idx = os.path.join(self.parent.GetParent().preferencesdirectory, "default.idx")
        if not os.path.exists(default_idx):
            return
    
        try:
            with open(default_idx, 'r', encoding='UTF-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка читання default.idx:\n{e}", "Помилка")
            return
    
        updated = [line for line in lines if line != plugin_name]
    
        try:
            with open(default_idx, 'w', encoding='UTF-8') as f:
                for line in updated:
                    f.write(line + '\n')
        except Exception as e:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка оновлення default.idx:\n{e}", "Помилка")
    
    
    def Run(self):
        self.stxtUnInstalling.SetForegroundColour(self.GetForegroundColour())
        self.gUnInstall.SetRange(len(self.parent.pluginstoremove))
        for i, plugin in enumerate(self.parent.pluginstoremove):
            self.UnInstall(plugin)
            if self.parent.removealldataforpluginArray[i]:
                self.RemoveDatFiles(plugin)
            self.gUnInstall.SetValue(i + 1)
        self.stxtUnInstalling.SetForegroundColour(wx.Colour(175, 175, 175))

        self.stxtUnIndexing.SetForegroundColour(self.GetForegroundColour())
        plist = os.listdir(self.parent.GetParent().pluginsdirectory)
        IndexList = [p for p in plist if p.endswith(".idx")]
        self.gUnIndex.SetRange(len(IndexList))
        print("IndexList:",IndexList)
        for i, idx in enumerate(IndexList):
            try:
                self.RemoveFromIndex(idx)
            except:
                drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка видалення з індексу: '{idx}'", "Помилка")
            self.gUnIndex.SetValue(i + 1)
        self.stxtUnIndexing.SetForegroundColour(wx.Colour(175, 175, 175))
        self.stxtDone.SetForegroundColour(self.GetForegroundColour())

    def UnInstall(self, plugin):
        pluginfile = os.path.join(self.parent.GetParent().pluginsdirectory, plugin + ".py")
        try:
            continueuninstall = True
            try:
                exec(compile("import " + plugin, plugin, "exec"))
                exec(compile("continueuninstall = " + plugin + ".UnInstall(self.parent.ancestor)", plugin, "exec"))
            except:
                pass
            if continueuninstall:
                for ext in ["", "c", ".bak"]:
                    fpath = pluginfile + ext
                    if os.path.exists(fpath):
                        os.remove(fpath)
        except Exception as e:
            drScrolledMessageDialog.ShowMessage(self.parent, f"Помилка видалення файлу: {pluginfile}\n{e}", "Помилка")

class drPluginUnInstallWizard(wx.adv.Wizard):
    def __init__(self, parent, title, bitmap):
        wx.adv.Wizard.__init__(self, parent, wx.ID_ANY, title, bitmap)
        self.ancestor = parent
        self.pluginstoremove = []
        self.removealldataforpluginArray = []
        self.SelectPage = drPluginUnInstallSelectPage(self)
        self.DataPage = drPluginUnInstallDataPage(self)
        self.UnInstallPage = drPluginUnInstallUnInstallPage(self)
        wx.adv.WizardPageSimple.Chain(self.SelectPage, self.DataPage)
        wx.adv.WizardPageSimple.Chain(self.DataPage, self.UnInstallPage)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        cp = self.GetCurrentPage()
        if cp == self.DataPage:
            self.DataPage.Run()
        elif cp == self.UnInstallPage:
            self.UnInstallPage.Run()

    def Run(self):
        self.RunWizard(self.SelectPage)


#*******************************************************************************
#Edit Indexes Dialog

class drEditIndexDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Редагування індексів", wx.DefaultPosition, (-1, -1), wx.DEFAULT_DIALOG_STYLE)
       
        wx.Yield()  # TODO: Why!?

        plist = os.listdir(parent.pluginsdirectory)

        self.PluginList = []

        self.IndexList = []

        self.indexname = ""
        self.indexplugins = []
        self.dirtyflag = False

        for p in plist:
            i = p.find(".py")
            l = len(p)
            if i > -1 and (i + 3 == l):
                self.PluginList.append(p[:i])

        pidxlist = os.listdir(parent.pluginsdirectory)
        for p in pidxlist:
            i = p.find(".idx")
            if i > -1:
                self.IndexList.append(p)
        ##AB:
        #if len(self.IndexList)==0:
            #self.IndexList.append("default.idx")

        ##FS: 25.03.2007: added again
        self.IndexList.append("default.idx")

        self.PluginList.sort()
        self.IndexList.sort()

        self.boxNotInIndex = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (200, 200), self.PluginList)

        self.boxInIndex = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (200, 200))

        self.btnAdd = wx.Button(self, wx.ID_ADD)
        self.btnRemove = wx.Button(self, wx.ID_REMOVE)

        self.btnUp = wx.Button(self, wx.ID_UP)
        self.btnDown = wx.Button(self, wx.ID_DOWN)

        self.cboIndex = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, (250, -1), self.IndexList)

        self.cboIndex.SetStringSelection("default.idx")

        self.btnClose = wx.Button(self, wx.ID_CANCEL, "Закрити діалог")
        self.btnDelete = wx.Button(self, wx.ID_DELETE)
        self.btnNew = wx.Button(self, wx.ID_NEW)
        self.btnSave = wx.Button(self, wx.ID_SAVE)
        self.btnSaveAs = wx.Button(self, wx.ID_SAVEAS)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)
        self.indexSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topmenuSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer = wx.FlexGridSizer(0, 4, 5, 10)
        self.menubuttonSizer = wx.BoxSizer(wx.VERTICAL)

        self.indexSizer.Add(wx.StaticText(self, -1, "   Поточний індекс:   "), 0, wx.SHAPED)
        self.indexSizer.Add(self.cboIndex, 0, wx.SHAPED)
        self.indexSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.SHAPED)
        self.indexSizer.Add(self.btnClose, 0, wx.SHAPED)

        self.topmenuSizer.Add(self.btnDelete, 1, wx.SHAPED)
        self.topmenuSizer.Add(self.btnNew, 1, wx.SHAPED)
        self.topmenuSizer.Add(self.btnSave, 1, wx.SHAPED)
        self.topmenuSizer.Add(self.btnSaveAs, 1, wx.SHAPED)

        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(self.btnAdd, 0, wx.SHAPED)
        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(self.btnUp, 0, wx.SHAPED)
        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(self.btnDown, 0, wx.SHAPED)
        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.menubuttonSizer.Add(self.btnRemove, 0, wx.SHAPED)

        self.mainSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "Не в індексі:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, "Додатки в індексі:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.mainSizer.Add(self.boxNotInIndex, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.mainSizer.Add(self.menubuttonSizer, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.mainSizer.Add(self.boxInIndex, 0,  wx.SHAPED | wx.ALIGN_CENTER)

        self.theSizer.Add(wx.StaticText(self, -1, ""), 1, wx.SHAPED)
        self.theSizer.Add(self.indexSizer, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, ""), 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.topmenuSizer, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.mainSizer, 9, wx.EXPAND)
        self.theSizer.Add(wx.StaticText(self, -1, ""), 1, wx.SHAPED)

        self.parent = parent

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        self.Bind(wx.EVT_BUTTON, self.OnbtnUp, self.btnUp)
        self.Bind(wx.EVT_BUTTON, self.OnbtnDown, self.btnDown)

        self.Bind(wx.EVT_BUTTON, self.OnbtnAdd, self.btnAdd)
        self.Bind(wx.EVT_BUTTON, self.OnbtnRemove, self.btnRemove)
        self.Bind(wx.EVT_BUTTON, self.OnbtnSave, self.btnSave)
        self.Bind(wx.EVT_BUTTON, self.OnbtnDelete, self.btnDelete)
        self.Bind(wx.EVT_BUTTON, self.OnbtnSaveAs, self.btnSaveAs)
        self.Bind(wx.EVT_BUTTON, self.OnbtnNew, self.btnNew)
        self.Bind(wx.EVT_BUTTON, self.OnCloseW, self.btnClose)

        self.Bind(wx.EVT_CHOICE, self.OnOpen, self.cboIndex)

        self.parent.LoadDialogSizeAndPosition(self, "editindexdialog.sizeandposition.dat")

        self.OnOpen(None)

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, "plugindialog.sizeandposition.dat")
        if self.dirtyflag:
            answer = wx.MessageBox("Ви не зберегли файл індексу\nЗберегти негайно?", "Редагувати індекси?", wx.YES_NO | wx.ICON_QUESTION)
            if answer == wx.YES:
                self.OnbtnSave(None)
        wx.MessageBox("Для оновлення завантажених доповнень, будь-ласка, перезавантажте drPython", "Редагування індексів", wx.ICON_EXCLAMATION)
        self.EndModal(0)

    def OnbtnAdd(self, event):
        self.dirtyflag = True
        tselection = self.boxNotInIndex.GetStringSelection()
        try:
            self.indexplugins.index(tselection)
            drScrolledMessageDialog.ShowMessage(self, "Доповнення '" + tselection + "' вже додано.", "Доповнення вже додано")
        except:
            tsel = self.boxNotInIndex.GetSelection()
            if tsel == -1:
                drScrolledMessageDialog.ShowMessage(self, "Нічого не обрано, щоб додати", "Помилка")
                return
            sel = self.boxInIndex.GetSelection()
            if sel == -1:
                sel = 0
            self.boxInIndex.Append(tselection)
            self.boxInIndex.SetSelection(sel)
            self.indexplugins.append(tselection)
            self.SetNotInIndex()

    def OnbtnDelete(self, event):
        self.dirtyflag = True
        indexname = self.cboIndex.GetStringSelection()
        if indexname == "default.idx":
            drScrolledMessageDialog.ShowMessage(self, "Ви не можете видалити індекс по замовчуванню", "Помилка")
            return
        answer = wx.MessageBox("Видалити '%s'?" % indexname, "drPython", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            indexfile = os.path.join(self.parent.pluginsbasepreferencesdir, indexname)
            if not os.path.exists(indexfile):
                drScrolledMessageDialog.ShowMessage(self, "'%s' не існує." % indexfile, "Помилка")
                return
            try:
                os.remove(indexfile)
            except:
                drScrolledMessageDialog.ShowMessage(self, "Помилка видалення '%s'." % indexfile, "Помилка")
            if indexname in self.IndexList:
                i = self.IndexList.index(indexname)
                self.IndexList.pop(i)
                self.cboIndex.Delete(i)
            self.cboIndex.SetStringSelection("default.idx")
            self.OnOpen(None)
            if self.parent.prefs.enablefeedback:
                drScrolledMessageDialog.ShowMessage(self, "Успішно видалено '%s'." % indexfile, "Індекс видалено")

    def OnbtnDown(self, event):
        self.dirtyflag = True
        sel = self.boxInIndex.GetSelection()
        if sel < self.boxInIndex.GetCount() - 1 and sel > -1:
            txt = self.boxInIndex.GetString(sel)
            self.boxInIndex.Delete(sel)
            self.boxInIndex.InsertItems([txt], sel+1)
            self.boxInIndex.SetSelection(sel+1)
            #franz:swap elements
            self.indexplugins.insert(sel+1, self.indexplugins.pop(sel))

    def OnbtnNew(self, event):
        d = wx.TextEntryDialog(self, "Введіть назву нового індексу (без .idx):", "Новий індекс", "")
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            indexname = v + ".idx"
            indexfile = os.path.join(self.parent.pluginsbasepreferencesdir, indexname)
            self.IndexList.append(indexname)
            self.cboIndex.Append(indexname)
            self.cboIndex.SetStringSelection(indexname)
            try:
                f = open(indexfile, 'w', encoding='UTF-8')
                f.write('\n')
                f.close()
            except:
                drScrolledMessageDialog.ShowMessage(self, "Помилка створення '%s'." % indexfile, "Помилка")
                return

            self.OnOpen(None)

    def OnbtnRemove(self, event):
        self.dirtyflag = True
        sel = self.boxInIndex.GetSelection()
        if sel == -1:
            drScrolledMessageDialog.ShowMessage(self, "Нічого не обрано для видалення", "Помилка")
            return

        self.indexplugins.pop(sel)
        self.boxInIndex.Delete(sel)
        self.boxInIndex.SetSelection(sel-1)
        self.SetNotInIndex()

    def OnbtnSave(self, event):
        self.dirtyflag = False
        f = open(self.indexname, 'w', encoding='UTF-8')
        for plugin in self.indexplugins:
            f.write(plugin + "\n")
        f.close()
        if self.parent.prefs.enablefeedback:
            drScrolledMessageDialog.ShowMessage(self, ("Успішно збережено до:\n"  + self.indexname), "Зміни збережено до індексного файлу")

    def OnbtnSaveAs(self, event):
        idx = self.cboIndex.GetStringSelection()
        d = wx.TextEntryDialog(self, "Save '%s' As(No .idx):" % idx, "Save Index As", "")
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            indexname = v + ".idx"
            indexfile = os.path.join(self.parent.pluginsbasepreferencesdir, indexname)
            self.IndexList.append(indexname)
            self.cboIndex.Append(indexname)
            self.cboIndex.SetStringSelection(indexname)
            try:
                f = open(indexfile, 'w', encoding='UTF-8')
                for plugin in self.indexplugins:
                    f.write(plugin + "\n")
                f.close()
                if self.parent.prefs.enablefeedback:
                    drScrolledMessageDialog.ShowMessage(self, ("Успішно збережено до:\n"  + indexfile), "Зміни збережено до індексного файлу")
            except:
                drScrolledMessageDialog.ShowMessage(self, "Помилка запису '%s' у '%s'." % (idx, indexname), "Помилка")
                return

    def OnbtnUp(self, event):
        sel = self.boxInIndex.GetSelection()
        if sel > 0:
            txt = self.boxInIndex.GetString(sel)
            self.boxInIndex.Delete(sel)
            self.boxInIndex.InsertItems([txt], sel-1)
            self.boxInIndex.SetSelection(sel-1)
            #franz:swap elements
            self.indexplugins.insert(sel-1, self.indexplugins.pop(sel))

    def OnOpen(self, event):
        fname = self.cboIndex.GetStringSelection()
        self.indexname = os.path.join(self.parent.preferencesdirectory, fname)
        if not os.path.exists(self.indexname):
            return
        try:
            f = open(self.indexname, 'r', encoding='UTF-8')
            self.indexplugins = f.read().rstrip().split('\n')
            f.close()

            x = 0
            l = len(self.indexplugins)
            while x < l:
                if not self.indexplugins[x]:
                    self.indexplugins.pop(x)
                    x = x - 1
                    l = l - 1
                x = x + 1

            self.boxInIndex.Set(self.indexplugins)
            self.SetNotInIndex()
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, ("Помилка зчитування файлу індексу: " + self.indexname), "Помилка вікривання файлу")

    def SetNotInIndex(self):
        #Written By Franz
        #AB: Modified to keep old selection
        sel = self.boxNotInIndex.GetSelection()
        nlist = []
        for i in self.PluginList:
            if i not in self.indexplugins:
                nlist.append (i)
        self.boxNotInIndex.Set (nlist)
        if sel < 0:
            sel = 0
        if sel >= len(nlist):
            sel = len(nlist) - 1
        self.boxNotInIndex.SetSelection(sel)
