#   Programmer: Daniel Pozmanter
#   Copyright 2003-2010 Daniel Pozmanter
#   Distributed under the terms of the GPL (GNU Public License)
#


#The Prompt

import os.path, re
import wx
import wx.stc
from drProperty import *
import drKeywords
import drSTC

import subprocess
import threading
import os
import sys

reserved = [wx.stc.STC_CMD_NEWLINE, wx.stc.STC_CMD_CHARLEFT,
wx.stc.STC_CMD_CHARRIGHT, wx.stc.STC_CMD_LINEUP, wx.stc.STC_CMD_LINEDOWN,
wx.stc.STC_CMD_DELETEBACK, wx.stc.STC_CMD_HOME]


this_errors =\
["ArithmeticError",
"AssertionError",
"AttributeError",
"Exception",
"EOFError",
"FloatingPointError",
"GeneratorExit",
"ImportError",
"IndentationError",
"IndexError",
"KeyError",
"KeyboardInterrupt",
"LookupError",
"MemoryError",
"NameError",
"NotImplementedError",
"OSError",
"OverflowError",
"ReferenceError",
"RuntimeError",
"StopIteration",
"SyntaxError",
"TabError",
"SystemError",
"SystemExit",
"TypeError",
"UnboundLocalError",
"UnicodeError",
"UnicodeEncodeError",
"UnicodeDecodeError",
"UnicodeTranslateError",
"ValueError",
"ZeroDivisionError"]

class ErrorDialog(wx.Dialog):
    def __init__(self, error_message, *args, **kwargs):
        super(ErrorDialog, self).__init__(*args, **kwargs)

        self.SetTitle("Помилка в програмі")
        self.SetSize(500, 150)

        # Основний контейнер
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Текстове поле для відображення помилки
        self.text = wx.StaticText(panel)
        self.text.SetLabel(error_message)
        vbox.Add(self.text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Кнопка "Закрити"
        close_button = wx.Button(panel, label="Закрити")
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(close_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)

    def on_close(self, event):
        """Закрити вікно при натисканні кнопки."""
        self.Destroy()


def show_error(error_message):
    """Показати повідомлення про помилку за допомогою wx.MessageDialog."""

    error_info = parse_error(error_message)
    err_msg = translate_error(error_info[2],error_info[1],error_info[3])    
    
    dialog = ErrorDialog(err_msg, parent=None)
    dialog.ShowModal()
   
    
def translate_error(err_type,err_line,err_msg): # переклад повідомлення про помилку українською мовою
    errors_list = {"ArithmeticError":"числові обчислення не виконано",
    "AssertionError":"оператор assert не виконується",
    "AttributeError":"посилання на атрибут або призначення не вдається",
    "Exception":"базовий клас для всіх винятків",
    "EOFError":"метод input() досягає умови 'кінець файлу' (EOF)",
    "FloatingPointError":"обчислення з плаваючою комою не виконано",
    "GeneratorExit":"генератор закрито (за допомогою методу close())",
    "ImportError":"імпортований модуль не існує",
    "IndentationError":"відступ неправильний",
    "IndexError":"індекс послідовності не існує",
    "KeyError":"ключ не існує в словнику",
    "KeyboardInterrupt":"користувач натискає Ctrl+c, Ctrl+z або Delete",
    "LookupError":"не вдається знайти викликані помилки",
    "MemoryError":"програмі не вистачає пам’яті",
    "NameError":"змінна або функція не існує",
    "ModuleNotFoundError":"модуль не знайдено",
    "NotImplementedError":"абстрактний метод вимагає успадкованого класу для заміни методу",
    "OSError":"системна операція викликає помилку",
    "OverflowError":"результат числового обчислення завеликий",
    "ReferenceError":"об’єкт слабкого посилання не існує", 
    "RuntimeError":"помилка, яка не належить до жодного конкретного винятку",
    "StopIteration":"метод next() ітератора не має інших значень",
    "SyntaxError":"cинтаксична помилка",
    "TabError":"відступ складається з табуляції та пропусків",
    "SystemError":"системна помилка",
    "SystemExit":"виклик функції sys.exit().",
    "TypeError":"поєднуються значення з несумісними типами",
    "UnboundLocalError":"призначення посилається на локальну змінну",
    "UnicodeError":"помилка Unicode",
    "UnicodeEncodeError":"помилка кодування Unicode",
    "UnicodeDecodeError":"помилка декодування Unicode",
    "UnicodeTranslateError":"помилка перекладу Unicode",
    "ValueError":"у вказаному типі даних є неправильне значення",
    "ZeroDivisionError":"дільник при діленні дорівнює нулю"}
    
    if err_type in errors_list:   
        translate_err=errors_list[err_type]
        
        ret =  "Виконання програми зупинено у рядку "+err_line+"\nчерез помилку - "+translate_err
    else:
        ret = "Виконання програми зупинено у рядку "+err_line+"\nчерез помилку - "+err_msg
    return ret
    

def parse_error(error_message):
    errs=error_message.split("\n")
    # пошук типу помилки, файлу та рядка
    
    err1_pattern  = r'  File "([^"]+)"(?:, line (\d+))?'
    err2_pattern =  r'(\w+)Error: (.+)'
    err_file=""
    err_line=""
    err_type=""
    err_msg =""
    e1 = False
    e2 = False
    for i in range(len(errs)):
        eline= errs[i]        
        match1 = re.search(err1_pattern, eline)
        if match1 and (not e1):            
            e1 = True
            err_file = match1.group(1)
            err_line = match1.group(2)
           
        match2 =  re.search(err2_pattern, eline)
        if match2 and (not e2):            
            e2 = True
            err_type = match2.group(1)+"Error"
            err_msg = match2.group(2)
                    
    return err_file, err_line, err_type, err_msg    



class DrPrompt(drSTC.DrStyledTextControl):
    STC_STYLE_MESSAGE = 64
    
    def __init__(self, parent, id, grandparent):
        drSTC.DrStyledTextControl.__init__(self, parent, id, grandparent)

        self.MAX_PROMPT_COMMANDS = 25
        self.CommandArray = []
        self.CommandArrayPos = -1

        self.IsAPrompt = True
        self.parent = grandparent
        self.full_output = ""  # для зберігання повного виводу

        self.process = None
        self.output_thread = None
        self.editable_start = 0  # Позиція (в символах), з якої можна редагувати

        # Видаляємо старі зв'язки з python -i
        self.pid = -1
        self.pythoninterpreter = 0
        self.commandinprogress = False

        # Видаляємо margin з номерами рядків (не потрібно для термінала)
        self.SetMarginWidth(1, 0)
        
        #Goto Traceback:
        self.reTFilename = re.compile(r'\".*\"')
        #AB:
        self.reTLinenumber = re.compile(r"line \d+")    
        self.foundvalidline = False

        # Події
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnGotoSelectedLine)
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        self.SetupIndicators()


    def SetupIndicators(self):
        # 🔹 Індикатор 1 — повідомлення ***
        self.INDIC_MESSAGE = 8
        self.IndicatorSetStyle(self.INDIC_MESSAGE, wx.stc.STC_INDIC_TEXTFORE)
        self.IndicatorSetForeground(self.INDIC_MESSAGE, wx.Colour(30, 63, 73))
    
        # 🔹 Індикатор 2 — помилки [error]
        self.INDIC_ERROR = 9
        self.IndicatorSetStyle(self.INDIC_ERROR, wx.stc.STC_INDIC_TEXTFORE)
        self.IndicatorSetForeground(self.INDIC_ERROR, wx.Colour(255, 0, 0))
    
        # 🔹 Індикатор 3 — попередження [warn]
        self.INDIC_WARNING = 10
        self.IndicatorSetStyle(self.INDIC_WARNING, wx.stc.STC_INDIC_BOX)
        self.IndicatorSetForeground(self.INDIC_WARNING, wx.Colour(255, 200, 0))
  
    def HighlightMessages(self):
        text = self.GetText()
    
        # 🔸 Очистити всі старі індикатори
        for indic in (self.INDIC_MESSAGE, self.INDIC_ERROR, self.INDIC_WARNING):
            self.SetIndicatorCurrent(indic)
            self.IndicatorClearRange(0, len(text))
    
        # 🔹 Підсвічуємо рядки з "***"
        self.SetIndicatorCurrent(self.INDIC_MESSAGE)
        for i in range(self.GetLineCount()):
            line_start = self.PositionFromLine(i)
            line = self.GetLine(i)         
            if line.startswith("***"):
                line_end = self.GetLineEndPosition(i)
                self.IndicatorFillRange(line_start, line_end - line_start)
    
        # 🔹 Підсвічуємо фрази "Error:"
        self.SetIndicatorCurrent(self.INDIC_ERROR)
        text = self.GetText()
        start = 0
        
        while True:
            idx = text.find("Error:", start)
            if idx == -1:
                break
        
            # 🔹 Знаходимо номер рядка, де це трапилось
            line_num = self.LineFromPosition(idx)
        
            # 🔹 Визначаємо межі рядка
            line_start = self.PositionFromLine(line_num)
            line_end = self.GetLineEndPosition(line_num)
        
            # 🔹 Підсвічуємо весь рядок
            self.IndicatorFillRange(line_start, line_end - line_start)
        
            # 🔹 Продовжуємо пошук після цього рядка
            start = line_end
    
        # 🔹 Підсвічуємо "[warn]"
        self.SetIndicatorCurrent(self.INDIC_WARNING)
        start = 0
        while True:
            idx = text.find("[warn]", start)
            if idx == -1:
                break
            self.IndicatorFillRange(idx, len("[warn]"))
            start = idx + len("[warn]")  



    def AddMessage(self, text):
        """Додає повідомлення синім кольором."""
        if not text.endswith('\n'):
            text += '\n'

        start_pos = self.GetLength()

        was_readonly = self.GetReadOnly()
        if was_readonly:
            self.SetReadOnly(False)

        self.InsertText(start_pos, text)

        if was_readonly:
            self.SetReadOnly(True)

        end_pos = self.GetLength()
        self.HighlightMessages()

        self.GotoPos(end_pos)
        self.EnsureCaretVisible()

        
    def RunScript(self, script_path):
        """Запускає зовнішній .py-скрипт у терміналі."""
        if not os.path.isfile(script_path):
            self.AddText(f"*** [error] File not found: {script_path}\n")
            
            return

        # 🔴 Зупинити попередній процес (якщо ще працює)
        if self.process and self.process.poll() is None:
            self.TerminateScript()

        # 🔑 Скинути стан термінала
        self.SetReadOnly(False)  # ← дуже важливо!
        self.AddMessage(f"*** exec: {script_path}\n")
        self.editable_start = self.GetLength()
        self.GotoPos(self.editable_start)
        self.EnsureCaretVisible()

        # Вимикаємо буферизацію
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        try:
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env=env
            )
        except Exception as e:
            self.AddMessage(f"*** [error exec: {e}]\n")
            self.SetReadOnly(True)
            return

        # Запуск читання виводу
        self.output_thread = threading.Thread(target=self._read_output, daemon=True)
        self.output_thread.start()

    def TerminateScript(self):
        """
        Завершує поточний процес (якщо він запущений і ще не завершений).
        """
        if self.process is not None and self.process.poll() is None:
            try:
                # Спробувати graceful завершення
                self.process.terminate()
                # Чекаємо 1 секунду на завершення
                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    # Якщо не завершився — примусово
                    self.process.kill()
            except Exception as e:
                # Ігноруємо помилки (процес уже може бути завершений)
                pass
            finally:
                self.process = None
                self.output_thread = None

    def StartInteractive(self):
        """Запускає інтерактивний Python-інтерпретатор (python -i)."""
        # Зупинити попередній процес
        if self.process and self.process.poll() is None:
            self.TerminateScript()

        # Підготувати термінал
        self.SetReadOnly(False)
        self.SetText("*** Python start...\n")
        self.HighlightMessages()
        self.editable_start = self.GetLength()
        self.GotoPos(self.editable_start)
        self.EnsureCaretVisible()

        # Команда: python -i -u
        cmd = [sys.executable, "-i", "-u"]

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env=env
            )
        except Exception as e:
            self.AddText(f"*** [Python start error: {e}]\n")
            self.HighlightMessages()
            self.SetReadOnly(True)
            return

        self.output_thread = threading.Thread(target=self._read_output, daemon=True)
        self.output_thread.start()

    def _read_output(self):
        try:
            while True:
                if self.process.poll() is not None:
                    # Процес завершився — читаємо увесь залишок
                    remainder = self.process.stdout.read()
                    if remainder:
                        wx.CallAfter(self._append_output, remainder)
                    break
    
                char = self.process.stdout.read(1)
                if not char:
                    break
                wx.CallAfter(self._append_output, char)
    
        except Exception as e:
            wx.CallAfter(self._append_output, f"*** [Internal error: {e}]\n")
        finally:
            wx.CallAfter(self._on_process_finished)
            if hasattr(self.grandparent, 'OnScriptFinished'):
                wx.CallAfter(self.grandparent.OnScriptFinished)

    def _on_process_finished(self):
        self._append_output("\n*** [exec completed]\n")
        print("***",self.full_output)
        # 🔍 Перевіряємо, чи була помилка у виводі
        if "Error:" in self.full_output or "Traceback" in self.full_output:
            # Шукаємо останнє повідомлення про помилку (найчастіше — останній рядок з помилкою)
            # Але краще передати весь вивід у show_error
            show_error(self.full_output)
        
        # Очищаємо буфер для наступного запуску
        self.full_output = ""


    def _append_output(self, text):
        """Безпечно додає текст у потік GUI і накопичує вивід."""
        self.full_output += text  # ← зберігаємо весь вивід
        pos = self.GetLength()
        self.AddText(text)
        self.HighlightMessages()
        self.editable_start = self.GetLength()
        self.GotoPos(self.editable_start)
        self.EnsureCaretVisible()

    # --- Обробка вводу ---

    def OnMouseDown(self, event):
        
        event.Skip()

    def OnKeyDown(self, event):
        if not self.process or self.process.poll() is not None:
            event.Skip()
            return

        current_pos = self.GetCurrentPos()
        if current_pos < self.editable_start:
            self.GotoPos(self.editable_start)

        keycode = event.GetKeyCode()

        if keycode == wx.WXK_RETURN:
            # Отримуємо ввід
            user_input = self.GetTextRange(self.editable_start, self.GetLength())
            try:
                self.process.stdin.write(user_input + '\n')
                self.process.stdin.flush()
            except Exception as e:
                self.AddText(f"[input error: {e}]\n")

            # Додаємо новий рядок до історії
            self.AddText('\n')
            self.editable_start = self.GetLength()
            self.GotoPos(self.editable_start)
            self.EnsureCaretVisible()
            return

        elif keycode == wx.WXK_BACK:
            if current_pos <= self.editable_start:
                return  # блокуємо Backspace у історії

        elif keycode in (wx.WXK_LEFT, wx.WXK_HOME):
            if current_pos <= self.editable_start:
                self.GotoPos(self.editable_start)
                return

        # Дозволяємо всі інші клавіші
        event.Skip()
    def OnGotoSelectedLine(self, event):
        
        self.foundvalidline = False

        self.grandparent.PPost(self.grandparent.EVT_DRPY_PROMPT_GOTO)

        line = self.GetLine(self.GetCurrentLine())        
       
        if not self.foundvalidline:
            root, ext = os.path.splitext(self.grandparent.txtDocument.filename)
            if ext == ".lua":
                if line.startswith("lua: "):
                    findpattern = "lua:"
                    pos = line.rfind(findpattern)
                    if pos != -1:
                        pos1 = pos + len(findpattern)
                        pos2 = line[pos1:].find(':')
                        if pos2 != -1:
                            self.gotolinenumber = int (line[pos1 : pos1 + pos2]) - 1
                            self.foundvalidline = True
                            self.gotofilename = self.grandparent.txtDocument.filename
                            #if another file is imported, this could be processed more accurate


        #pattern for traceback?
        if not self.foundvalidline:
          fn = self.reTFilename.search(line)
          ln = self.reTLinenumber.search(line)
          
          if (fn is not None) and (ln is not None):
              self.foundvalidline = True
              self.gotofilename = fn.group().strip('\"')
              try:
                  self.gotolinenumber = int(ln.group().strip("line ")) - 1
              except:
                  self.gotolinenumber = 0

        #pattern for pycheckeroutput?
        if not self.foundvalidline:
            line = line.replace ('\\', '/')
            pos = line.find (': ')
            if pos > -1:
                s = line[:pos]
                split = s.rsplit(':', 1)
                if len (split):
                    self.foundvalidline = True
                    self.gotofilename = split[0]
                    try:
                        self.gotolinenumber = int(split[1]) - 1
                    except:
                        self.gotolinenumber = 0


        if self.foundvalidline:
            if os.path.exists(self.gotofilename):
                self.grandparent.OpenOrSwitchToFile(self.gotofilename, editRecentFiles=False)
  
                top = self.gotolinenumber - self.grandparent.txtDocument.LinesOnScreen()//2
                if top < 0:
                    top = 0
                self.grandparent.txtDocument.ScrollToLine(top)

                self.grandparent.txtDocument.GotoLine(self.gotolinenumber)
                self.grandparent.txtDocument.EnsureCaretVisible()
                self.grandparent.txtDocument.SetFocus()




    # --- Залишок методів (зберігаємо сумісність) ---

    def OnIdle(self, event):
        # Не використовується, бо вивід читається у окремому потоці
        pass

    def OnKeyUp(self, event):
        event.Skip()

    def OnModified(self, event):
        pass

    def RunCheck(self, event):
        pass



    def SetupPrefsPrompt(self, notmdiupdate = 1):
        self.SetEndAtLastLine(not self.grandparent.prefs.promptscrollextrapage)

        if notmdiupdate:
            self.SetViewWhiteSpace(self.grandparent.prefs.promptwhitespaceisvisible)
            self.SetViewEOL(self.grandparent.prefs.promptwhitespaceisvisible and self.grandparent.prefs.vieweol)

        if self.grandparent.prefs.promptwordwrap:
            self.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.SetWrapMode(wx.stc.STC_WRAP_NONE)
        if self.grandparent.prefs.prompteolmode == 1:
            self.SetEOLMode(wx.stc.STC_EOL_CRLF)
        elif self.grandparent.prefs.prompteolmode == 2:
            self.SetEOLMode(wx.stc.STC_EOL_CR)
        else:
            self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetTabWidth(self.grandparent.prefs.prompttabwidth)
        self.SetUseTabs(self.grandparent.prefs.promptusetabs)
        self.SetMarginWidth(1, self.grandparent.prefs.promptmarginwidth)
        
        if self.grandparent.prefs.promptusestyles:

            self.SetKeyWords(0, drKeywords.GetKeyWords(0))

            self.SetLexer(drKeywords.GetLexer(0))

            self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, self.grandparent.prefs.txtPromptStyleDictionary[0])

            self.StyleClearAll()  

            self.StartStyling(0)

            self.SetCaretWidth(self.grandparent.prefs.promptcaretwidth)

            self.SetCaretForeground(self.grandparent.prefs.txtPromptStyleDictionary[15])

            if self.grandparent.prefs.promptusestyles < 2:
                self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, self.grandparent.prefs.txtPromptStyleDictionary[1])
                self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, self.grandparent.prefs.txtPromptStyleDictionary[2])
                self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, self.grandparent.prefs.txtPromptStyleDictionary[3])
                self.StyleSetSpec(wx.stc.STC_P_CHARACTER, self.grandparent.prefs.txtPromptStyleDictionary[4])
                self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, self.grandparent.prefs.txtPromptStyleDictionary[5])
                self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, self.grandparent.prefs.txtPromptStyleDictionary[6])
                self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, self.grandparent.prefs.txtPromptStyleDictionary[7])
                self.StyleSetSpec(wx.stc.STC_P_DEFNAME, self.grandparent.prefs.txtPromptStyleDictionary[8])
                self.StyleSetSpec(wx.stc.STC_P_WORD, self.grandparent.prefs.txtPromptStyleDictionary[9])
                self.StyleSetSpec(wx.stc.STC_P_NUMBER, self.grandparent.prefs.txtPromptStyleDictionary[10])
                self.StyleSetSpec(wx.stc.STC_P_OPERATOR, self.grandparent.prefs.txtPromptStyleDictionary[11])
                self.StyleSetSpec(wx.stc.STC_P_STRING, self.grandparent.prefs.txtPromptStyleDictionary[12])
                self.StyleSetSpec(wx.stc.STC_P_STRINGEOL, self.grandparent.prefs.txtPromptStyleDictionary[13])
                self.StyleSetSpec(wx.stc.STC_P_TRIPLE, self.grandparent.prefs.txtPromptStyleDictionary[14])
                self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, self.grandparent.prefs.txtPromptStyleDictionary[14])

                self.SetSelForeground(1, getStyleProperty("fore", self.grandparent.prefs.txtPromptStyleDictionary[16]))
                self.SetSelBackground(1, getStyleProperty("back", self.grandparent.prefs.txtPromptStyleDictionary[16]))

    
    def SetText(self, text):
        ro = self.GetReadOnly()
        self.SetReadOnly(0)
        wx.stc.StyledTextCtrl.SetText(self, text)
        self.SetReadOnly(ro)

    def SetSelectedText(self, text):
        ro = self.GetReadOnly()
        self.SetReadOnly(0)
        self.SetTargetStart(self.GetSelectionStart())
        self.SetTargetEnd(self.GetSelectionEnd())
        self.ReplaceTarget(text)
        self.SetReadOnly(ro)
