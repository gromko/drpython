import wx
import ast
import traceback
import builtins
# Список синтаксичних помилок з перекладом
errors_list = \
{"invalid syntax":"інтерпретатор зустрів неправильний синтаксис.",
"unexpected EOF while parsing":"код незавершений (наприклад, відсутня закриваюча дужка, лапка або двокрапка).",
"unmatched ')'":"є зайва закриваюча дужка.",
"'(' was never closed":"є незакрита дужка",
"EOL while scanning string literal":"рядок не закрито лапками.",
"Missing parentheses in call to 'print'. Did you mean print(...)?":"відсутні дужки у виклику 'print'.",
"closing parenthesis ')' does not match opening parenthesis '['":"є незакрита дужка '['",
"closing parenthesis ']' does not match opening parenthesis '('":"є зайва закриваюча дужка ']'",
"invalid character in identifier":"в ідентифікаторі (назві змінної, функції тощо) використовується заборонений символ (наприклад, '@', '$').",
"unexpected indent":"відступи в коді неправильні (наприклад, зайвий пропуск або табуляція).",
"unexpected character after line continuation character":"неочікуваний символ після символу продовження рядка.",
"unindent does not match any outer indentation level":"відступи в коді не узгоджуються між собою.",
"expected ':'":"після умови 'if', 'else', 'elif', 'for', 'while', 'def', 'class' тощо пропущено двокрапку.",
"invalid decimal literal":"число записано неправильно (наприклад, '123abc').",
"leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers":"число починається з нуля (наприклад, '0123').",
"can't assign to keyword":"ви намагаєтеся присвоїти значення ключовому слову (наприклад, 'if = 5').",
"invalid syntax (possibly missing a comma?)":"пропущено кому в списку, кортежі чи словнику.",
"'return' outside function":"'return' використовується поза функцією.",
"'break' outside loop":"'break' використовується поза циклом.",
"'continue' not properly in loop":"'continue' використовується поза циклом.",
"'yield' outside function":"'yield' використовується поза функцією.",
"non-default argument follows default argument":"в оголошенні функції аргумент без значення за замовчуванням йде після аргументу зі значенням за замовчуванням.",
"invalid syntax in import statement":"синтаксис імпорту неправильний (наприклад, 'import os,').",
"future feature is not defined":"використовується '__future__' імпорт з неіснуючою функцією.",
"unterminated string literal":"рядок не закрито лапками.",
"f-string: unmatched '['":"в f-рядку є незакрита квадратна дужка.",
"f-string: expecting '}'":"в f-рядку є незакрита фігурна дужка.",
"f-string: invalid syntax":"синтаксис f-рядка неправильний.",
"'await' outside async function":"'await' використовується поза асинхронною функцією.",
"'async for' outside async function":"'async for' використовується поза асинхронною функцією.",
"'async with' outside async function":"'async with' використовується поза асинхронною функцією.",
"'yield' outside function":"'yield' використовується поза функцією.",
"'yield from' outside function":"'yield from' використовується поза функцією.",
"invalid syntax in dictionary literal":"синтаксис словника неправильний (наприклад, пропущено кому).",
"invalid syntax in list literal":"синтаксис списку неправильний.",
"invalid syntax in tuple literal":"синтаксис кортежу неправильний.",
"invalid escape sequence":"використовується неправильна escape-послідовність (наприклад, '\\x' без шістнадцяткового числа).",
"invalid syntax in decorator":"синтаксис декоратора неправильний.",
"cannot assign to literal":"ви намагаєтеся присвоїти значення літералу (наприклад, '5 = x').",
"cannot assign to operator":"ви намагаєтеся присвоїти значення оператору (наприклад, 'x + 1 = 5').",
"invalid syntax in if statement":"синтаксис умовного оператора 'if' неправильний.",
"invalid syntax in for loop":"синтаксис циклу 'for' неправильний.",
"invalid syntax in while loop":"синтаксис циклу 'while' неправильний."}
class drSyntaxChecker(wx.Frame):
    def __init__(self, filepath, parent=None, id=-1, title=""):
        wx.Frame.__init__(self, parent, id, title)
        print("filepatch=",filepath)
        self.isError = False
        self.errLine = 0
        self.filepath = filepath
        self.InitUI()
        self.OnCheck(self.filepath)

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.txt = wx.StaticText(panel, label ="  drPython здійснює перевірку правильності коду")
        self.cb = wx.CheckBox(panel, -1, 'Перевірити невизначені функції та змінні', (-1, -1))
        self.cb.SetValue(False)
        self.stxt = wx.StaticText(panel, -1, '* функції та змінні, які визначені у зовнішніх модулях,\n   можуть визначатись неправильно', (-1,-1))
        font = wx.Font(8,  wx.FONTFAMILY_MODERN, wx.ITALIC, wx.NORMAL)
        self.stxt.SetFont(font)
        self.btn1 = wx.Button(panel, -1, label ="Перевірити", pos = wx.DefaultPosition, size =(-1, -1)) 
        self.Bind(wx.EVT_BUTTON, self.ClickCheck, self.btn1)
        
        self.resultText = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.btn = wx.Button(panel, -1, label ="Закрити", pos = wx.DefaultPosition, size =(-1, -1))  
        self.Bind(wx.EVT_BUTTON, self.onclick, self.btn) 
        
        vbox.Add(self.txt, 0, wx.ALL, border=10)
        vbox.Add(self.cb, 0, wx.ALL, border=10)
        vbox.Add(self.stxt, 0, wx.ALL, border=10)
        vbox.Add(self.btn1, 0, wx.ALL | wx.ALIGN_CENTER)
        vbox.Add(self.resultText, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(self.btn, 0, wx.ALL | wx.ALIGN_CENTER)
        panel.SetSizer(vbox)

        self.SetSize((600, 400))
        self.SetTitle("Синтаксична перевірка Python коду")
        self.Centre()
        self.Show()

    def onclick(self, e): 
        # Close 
        self.Destroy()
        
    def ClickCheck(self, event):
        self.OnCheck(self.filepath)
        
    def OnCheck(self, filepath):
        #filepath = self.filePicker.GetPath()
        if not filepath:
            wx.MessageBox("Будь ласка, виберіть файл для перевірки.", "Помилка", wx.OK | wx.ICON_ERROR)
            return

        self.resultText.Clear()
        self.resultText.AppendText(f"Перевірка файлу: {filepath}\n\n")

        try:
            with open(filepath, 'r',encoding="UTF-8") as f:
                source = f.read()

            # Синтаксична перевірка за допомогою ast
            tree = ast.parse(source, filename=filepath)
            self.resultText.AppendText("Перевірка синтаксису - помилок не виявлено.\n\n")

            # Перевірка на невизначені змінні та функції
            self.check_undefined_names(tree, filepath)

        except SyntaxError as err:            
            error_msg = self.get_error_message(err, filepath)
            self.resultText.AppendText(f"Перевірка синтаксису - виявлено помилку:\n{error_msg}\n")
            self.resultText.AppendText("Перевірка невизначених змінних та функцій не виконана через синтаксичну помилку.\n")
        
        except IndentationError as err:
            self.resultText.AppendText(f"Неправильний відступ: {str(err)}\n")
            
        except Exception as err:
            self.resultText.AppendText(f"Помилка: {str(err)}\n")

    def get_error_message(self, err, filepath):
        error_details = traceback.format_exception_only(SyntaxError, err)
        error_line = err.lineno
        self.errLine = error_line
        self.isError = True
        error_text = err.text.strip() if err.text else "Невідомий рядок"
        print(">>> ",error_details)
        
        if len(error_details)==3:
            if "Error:" in error_details[2]:
                error_msg = error_details[2].strip()
        if len(error_details)==4:
            if "Error:" in error_details[3]:
                error_msg = error_details[3].strip()
        
            
        s_err="SyntaxError: "
        emsg_err = error_msg
        if s_err in error_msg:
            msg_err=error_msg[len(s_err):]
            try:
                emsg_err = errors_list[msg_err]
            except:
                emsg_err = msg_err    
        
        
        if emsg_err=="IndentationError: unexpected indent":
            emsg_err = "відступ в коді неправильний (наприклад, зайвий пропуск або його не вистачає)"
        print("error_msg=",emsg_err)
        return f"\nУ рядку {error_line} {emsg_err}\nРядок з помилкою: {error_text}\n"

    def check_undefined_names(self, tree, filepath):
        class UndefinedNamesChecker(ast.NodeVisitor):
            def __init__(self):
                self.undefined_names = []
                self.defined_names = set()
                self.imported_names = set()
                self.function_calls = set()  # Множина для зберігання імен функцій, які викликаються
                self.builtin_names = set(dir(builtins))  # Вбудовані імена Python

            def visit_Import(self, node):
                # Обробка звичайного імпорту (наприклад, `import os`)
                for alias in node.names:
                    self.imported_names.add(alias.name)
                super().generic_visit(node)

            def visit_ImportFrom(self, node):
                # Обробка імпорту з модуля (наприклад, `from os import path`)
                module_name = node.module if node.module else ""
                for alias in node.names:
                    self.imported_names.add(f"{module_name}.{alias.name}" if module_name else alias.name)
                super().generic_visit(node)

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    # Перевірка, чи змінна визначена, імпортована або є вбудованою
                    if (node.id not in self.defined_names and 
                        node.id not in self.imported_names and 
                        node.id not in self.function_calls and 
                        node.id not in self.builtin_names):  # Ігнорувати вбудовані імена
                        self.undefined_names.append((node.lineno, node.id, "змінна"))
                super().generic_visit(node)

            def visit_Call(self, node):
                # Перевірка, чи функція визначена, імпортована або є вбудованою
                if isinstance(node.func, ast.Name):
                    if (node.func.id not in self.defined_names and 
                        node.func.id not in self.imported_names and 
                        node.func.id not in self.builtin_names):  # Ігнорувати вбудовані функції
                        self.undefined_names.append((node.lineno, node.func.id, "функція"))
                        self.function_calls.add(node.func.id)  # Додати ім'я функції до множини викликів
                super().generic_visit(node)

            def visit_FunctionDef(self, node):
                # Додаємо ім'я функції до визначених імен
                self.defined_names.add(node.name)
                super().generic_visit(node)

            def visit_Assign(self, node):
                # Додаємо імена змінних до визначених імен
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.defined_names.add(target.id)
                super().generic_visit(node)
        
        if self.cb.GetValue()==False:
            return
        
        checker = UndefinedNamesChecker()
        checker.visit(tree)

        if checker.undefined_names:
            self.resultText.AppendText("Перевірка невизначених змінних та функцій - виявлено помилки:\n")
            for lineno, name, type_ in checker.undefined_names:
                self.resultText.AppendText(f"Рядок {lineno} - невизначена {type_}: {name}\n")
                
        else:
            self.resultText.AppendText("Перевірка невизначених змінних та функцій - помилок не виявлено.\n")
    
    def getResult(self):
        return self.isError,self.errLine
        

