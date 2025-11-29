def OnAbout(DrFrame):
    DrFrame.ShowMessage("Calculator\nVersion 1.0\n\nBy DrPython User", "About")

def Plugin(DrFrame):
    import wx
    import wx.grid

    class CalculatorDialog(wx.Dialog):
        def __init__(self, parent):
            super(CalculatorDialog, self).__init__(
                parent,
                title="Calculator",
                size=(360, 340)  # трохи збільшено висоту
            )
            self.InitUI()
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            self.alive = True

        def InitUI(self):
            panel = wx.Panel(self)
            vbox = wx.BoxSizer(wx.VERTICAL)

            self.display = wx.TextCtrl(panel, style=wx.TE_RIGHT)
            vbox.Add(self.display, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=4)

            gs = wx.GridBagSizer(5, 5)

            # Макет кнопок — останній стовпець у рядках 6-7 залишаємо порожнім для "="
            buttons_layout = [
                ['7',   '8',   '9',   '/'],
                ['4',   '5',   '6',   '*'],
                ['1',   '2',   '3',   '-'],
                ['0',   '.',   'CLEAR',   '+'],
                ['HEX', 'OCT', 'BIN', 'DEC'],
                ['ORD', 'CHR', 'ASCII','AND'],
                ['OR',  'XOR', 'NOT', ''],   # (6,3) — порожньо
                ['<<',  '>>',  '+/-', '']    # (7,3) — порожньо
            ]

            # Додаємо всі кнопки з макету
            for row in range(len(buttons_layout)):
                for col in range(4):
                    label = buttons_layout[row][col]
                    if label == '':
                        continue
                    btn = wx.Button(panel, label=label)
                    btn.Bind(wx.EVT_BUTTON, self.OnButton)
                    gs.Add(btn, pos=(row, col), flag=wx.EXPAND)

            # Додаємо "=" у вільну колонку (3) рядків 6 і 7
            equals_btn = wx.Button(panel, label='=')
            equals_btn.Bind(wx.EVT_BUTTON, self.OnButton)
            gs.Add(equals_btn, pos=(6, 3), span=(2, 1), flag=wx.EXPAND)

            # Робимо стовпці та рядки розтяжними
            for i in range(4):
                gs.AddGrowableCol(i)
            for i in range(8):
                gs.AddGrowableRow(i)

            vbox.Add(gs, proportion=1, flag=wx.EXPAND)
            panel.SetSizer(vbox)

            dialog_sizer = wx.BoxSizer(wx.VERTICAL)
            dialog_sizer.Add(panel, proportion=1, flag=wx.EXPAND)
            self.SetSizer(dialog_sizer)

        def OnClose(self, event):
            self.alive = False
            self.Destroy()

        def SafeDisplay(self, text):
            if getattr(self, 'alive', False) and hasattr(self, 'display') and self.display:
                self.display.SetValue(text)

        def OnButton(self, event):
            label = event.GetEventObject().GetLabel()
            current_value = self.display.GetValue()

            if label == 'CLEAR':
                self.SafeDisplay("")
            elif label == '=':
                try:
                    # Замінюємо текстові операції на Python-оператори
                    expr = current_value.replace('AND', '&').replace('OR', '|') \
                                        .replace('XOR', '^').replace('NOT', '~') \
                                        .replace('<<', '<<').replace('>>', '>>')
                    result = eval(expr)
                    self.SafeDisplay(str(result))
                except Exception as e:
                    self.SafeDisplay("Error")
            elif label == 'HEX':
                try:
                    num = self._convert_to_decimal(current_value)
                    self.SafeDisplay(hex(num))
                except:
                    self.SafeDisplay("Error")
            elif label == 'OCT':
                try:
                    num = self._convert_to_decimal(current_value)
                    self.SafeDisplay(oct(num))
                except:
                    self.SafeDisplay("Error")
            elif label == 'BIN':
                try:
                    num = self._convert_to_decimal(current_value)
                    self.SafeDisplay(bin(num))
                except:
                    self.SafeDisplay("Error")
            elif label == 'DEC':
                try:
                    num = self._convert_to_decimal(current_value)
                    self.SafeDisplay(str(num))
                except:
                    self.SafeDisplay("Error")
            elif label == 'ORD':
                if len(current_value) == 1:
                    self.SafeDisplay(str(ord(current_value)))
                else:
                    self.SafeDisplay("Error")
            elif label == 'CHR':
                try:
                    code = int(current_value)
                    self.SafeDisplay(chr(code))
                except:
                    self.SafeDisplay("Error")                
            elif label == 'ASCII':
                self.show_ascii_table()
            elif label == '+/-':
                try:
                    num = self._convert_to_decimal(current_value)
                    self.SafeDisplay(str(-num))
                except:
                    self.SafeDisplay("Error")
            elif label == 'NOT':
                if current_value.strip():
                    self.SafeDisplay('NOT ' + current_value)
                else:
                    self.SafeDisplay('NOT ')
            elif label in ('AND', 'OR', 'XOR', '<<', '>>', '+', '-', '*', '/'):
                self.SafeDisplay(current_value + ' ' + label + ' ')
            else:
                # Усе інше: цифри, '.' — без пробілів
                self.SafeDisplay(current_value + label)                

        def _convert_to_decimal(self, value):
            if not value:
                raise ValueError("Empty input")
            value = value.strip()
            if value.startswith('0x') or value.startswith('-0x'):
                return int(value, 16)
            elif value.startswith('0o') or value.startswith('-0o'):
                return int(value, 8)
            elif value.startswith('0b') or value.startswith('-0b'):
                return int(value, 2)
            else:
                return int(value)

        def show_ascii_table(self):
            ascii_window = wx.Frame(None, title="ASCII Table", size=(660, 320))
            panel = wx.Panel(ascii_window)
            grid = wx.grid.Grid(panel)
            grid.CreateGrid(8, 16)

            for col in range(16):
                grid.SetColLabelValue(col, f"{col:X}")
            for row in range(8):
                grid.SetRowLabelValue(row, f"{row * 16}")

            ascii_names = [
                "NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
                "BS", "HT", "LF", "VT", "FF", "CR", "SO", "SI",
                "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
                "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US"
            ]

            for code in range(128):
                row = code // 16
                col = code % 16
                if code < 32:
                    grid.SetCellValue(row, col, ascii_names[code])
                elif code == 127:
                    grid.SetCellValue(row, col, "DEL")
                else:
                    grid.SetCellValue(row, col, chr(code))
                grid.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

            grid.AutoSizeColumns()
            grid.SetRowLabelSize(50)
            grid.SetColLabelSize(30)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(grid, 1, wx.EXPAND)
            panel.SetSizer(sizer)

            ascii_window.SetMinSize((660, 320))
            ascii_window.SetMaxSize((660, 320))
            ascii_window.Layout()
            ascii_window.Show()

    # --- Реєстрація пункту меню ---
    ID_CALC = DrFrame.GetNewId()

    # Визначаємо, яке меню використовувати
    if hasattr(DrFrame, "programmenu"):
        menu = DrFrame.programmenu
    else:
        menu = DrFrame.optionsmenu

    menu.AppendSeparator()
    menu.Append(ID_CALC, "Calculator")

    def ShowCalculator(event):
        dlg = CalculatorDialog(DrFrame)
        dlg.ShowModal()
        dlg.Destroy()

    DrFrame.Bind(wx.EVT_MENU, ShowCalculator, id=ID_CALC)
