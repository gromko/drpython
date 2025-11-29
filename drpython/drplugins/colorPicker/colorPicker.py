def OnAbout(DrFrame):
    DrFrame.ShowMessage("Color Picker\nVersion 1.0\n\nBy DrPython User", "About")

def Plugin(DrFrame):
    import wx

    class ColorPickerDialog(wx.Dialog):
        def __init__(self, parent):
            super(ColorPickerDialog, self).__init__(
                parent,
                title="Вибір кольору",
                size=(400, 600)
            )
            self.gradient_bitmap = None
            self.InitUI()
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            self.alive = True


        def InitUI(self):
            panel = wx.Panel(self)
            main_sizer = wx.BoxSizer(wx.VERTICAL)

            # Панель для вибору кольору мишею
            self.color_picker_panel = wx.Panel(panel, size=(200, 200))
            self.color_picker_panel.Bind(wx.EVT_PAINT, self.on_paint)
            self.color_picker_panel.Bind(wx.EVT_LEFT_DOWN, self.on_pick_color)
            self.color_picker_panel.Bind(wx.EVT_SIZE, self.on_gradient_size)  # ← ДОДАНО
            main_sizer.Add(self.color_picker_panel, flag=wx.EXPAND | wx.ALL, border=10)

            # Повзунок для регулювання синього компонента (яскравості)
            self.brightness_slider = wx.Slider(panel, value=128, minValue=0, maxValue=255, style=wx.SL_HORIZONTAL)
            self.brightness_slider.Bind(wx.EVT_SLIDER, self.on_brightness_change)
            main_sizer.Add(self.brightness_slider, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

            # Поле для відображення вибраного кольору
            self.color_display_panel = wx.Panel(panel, size=(200, 50))
            self.color_display_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
            main_sizer.Add(self.color_display_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

            # Слайдери для R, G, B
            self.sliders = {}
            for color in ['R', 'G', 'B']:
                hbox = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(panel, label=f"{color}:")
                hbox.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)

                slider = wx.Slider(panel, value=255, minValue=0, maxValue=255, style=wx.SL_HORIZONTAL)
                slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
                hbox.Add(slider, proportion=1, flag=wx.EXPAND)

                value_label = wx.StaticText(panel, label="255 (0xFF)")
                hbox.Add(value_label, flag=wx.LEFT, border=10)

                self.sliders[color] = {'slider': slider, 'label': value_label}
                main_sizer.Add(hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

            # HEX та копіювання
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            self.hex_label = wx.StaticText(panel, label="HEX: #FFFFFF")
            hbox.Add(self.hex_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)

            copy_icon = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_BUTTON, (16, 16))
            self.copy_button = wx.BitmapButton(panel, bitmap=copy_icon, size=(24, 24))
            self.copy_button.Bind(wx.EVT_BUTTON, self.on_copy_hex)
            hbox.Add(self.copy_button, flag=wx.ALIGN_CENTER_VERTICAL)

            main_sizer.Add(hbox, flag=wx.LEFT | wx.BOTTOM, border=10)

            # Стандартні кольори
            self.standard_colors_panel = wx.Panel(panel)
            self.standard_colors_sizer = wx.GridSizer(rows=2, cols=8, vgap=5, hgap=5)
            self.standard_colors_panel.SetSizer(self.standard_colors_sizer)

            self.standard_colors = [
                wx.Colour(255, 0, 0), wx.Colour(0, 255, 0), wx.Colour(0, 0, 255), wx.Colour(255, 255, 0),
                wx.Colour(255, 0, 255), wx.Colour(0, 255, 255), wx.Colour(128, 0, 0), wx.Colour(0, 128, 0),
                wx.Colour(0, 0, 128), wx.Colour(128, 128, 0), wx.Colour(128, 0, 128), wx.Colour(0, 128, 128),
                wx.Colour(192, 192, 192), wx.Colour(128, 128, 128), wx.Colour(64, 64, 64), wx.Colour(0, 0, 0)
            ]

            for color in self.standard_colors:
                color_button = wx.Button(self.standard_colors_panel, size=(30, 30))
                color_button.SetBackgroundColour(color)
                color_button.Bind(wx.EVT_BUTTON, self.on_standard_color_select)
                self.standard_colors_sizer.Add(color_button, flag=wx.EXPAND)

            main_sizer.Add(self.standard_colors_panel, flag=wx.EXPAND | wx.ALL, border=10)

            panel.SetSizer(main_sizer)

            dialog_sizer = wx.BoxSizer(wx.VERTICAL)
            dialog_sizer.Add(panel, proportion=1, flag=wx.EXPAND)
            self.SetSizer(dialog_sizer)
            self.Centre()

        def on_gradient_size(self, event):
            """Викликається, коли панель отримує реальний розмір"""
            if not hasattr(self, '_gradient_initialized'):
                wx.CallAfter(self.generate_gradient)
                self._gradient_initialized = True
            event.Skip()

        def on_copy_hex(self, event):
            if not self.SafeUpdate():
                return
            full_text = self.hex_label.GetLabel()
            if ": " in full_text:
                hex_value = full_text.split(": ", 1)[1]
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(hex_value))
                    wx.TheClipboard.Close()
                    wx.Bell()  # ✅ Сповіщення без вікна
            

        def OnClose(self, event):
            self.alive = False
            self.Destroy()

        def SafeUpdate(self):
            return getattr(self, 'alive', False)

        def on_paint(self, event):
            if not self.SafeUpdate():
                return
            dc = wx.PaintDC(self.color_picker_panel)
            if self.gradient_bitmap:
                dc.DrawBitmap(self.gradient_bitmap, 0, 0)

        def generate_gradient(self):
            if not self.SafeUpdate():
                return
            width, height = self.color_picker_panel.GetSize()
            if width <= 0 or height <= 0:
                return

            b = self.brightness_slider.GetValue()
            image = wx.Image(width, height)
            data = bytearray(width * height * 3)

            for y in range(height):
                g_val = int((y / height) * 255)
                for x in range(width):
                    r_val = int((x / width) * 255)
                    idx = (y * width + x) * 3
                    data[idx] = r_val     # R
                    data[idx + 1] = g_val # G
                    data[idx + 2] = b     # B

            image.SetData(bytes(data))
            self.gradient_bitmap = image.ConvertToBitmap()
            self.color_picker_panel.Refresh()


        def on_brightness_change(self, event):
            if not self.SafeUpdate():
                return
            self.generate_gradient()  # Оновлюємо градієнт
            # Оновлюємо мітки, щоб відобразити нове значення B
            self.update_slider_labels()
            r = self.sliders['R']['slider'].GetValue()
            g = self.sliders['G']['slider'].GetValue()
            b = self.brightness_slider.GetValue()
            color = wx.Colour(r, g, b)
            self.update_color_display(color)

        def update_slider_labels(self):
            r = self.sliders['R']['slider'].GetValue()
            g = self.sliders['G']['slider'].GetValue()
            b = self.sliders['B']['slider'].GetValue()
            self.sliders['R']['label'].SetLabel(f"{r} (0x{r:02X})")
            self.sliders['G']['label'].SetLabel(f"{g} (0x{g:02X})")
            self.sliders['B']['label'].SetLabel(f"{b} (0x{b:02X})")

        def on_slider_change(self, event):
            if not self.SafeUpdate():
                return
            self.update_slider_labels()
            r = self.sliders['R']['slider'].GetValue()
            g = self.sliders['G']['slider'].GetValue()
            b = self.brightness_slider.GetValue()
            color = wx.Colour(r, g, b)
            self.update_color_display(color)

        def on_pick_color(self, event):
            if not self.SafeUpdate():
                return
            x, y = event.GetPosition()
            width, height = self.color_picker_panel.GetSize()
            if width == 0 or height == 0:
                return
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = self.brightness_slider.GetValue()

            self.sliders['R']['slider'].SetValue(r)
            self.sliders['G']['slider'].SetValue(g)
            self.sliders['B']['slider'].SetValue(b)
            self.update_slider_labels()

            color = wx.Colour(r, g, b)
            self.update_color_display(color)

        def on_standard_color_select(self, event):
            if not self.SafeUpdate():
                return
            button = event.GetEventObject()
            color = button.GetBackgroundColour()

            self.sliders['R']['slider'].SetValue(color.Red())
            self.sliders['G']['slider'].SetValue(color.Green())
            self.sliders['B']['slider'].SetValue(color.Blue())
            self.update_slider_labels()

            self.update_color_display(color)



        def on_copy_hex(self, event):
            if not self.SafeUpdate():
                return
            full_text = self.hex_label.GetLabel()
            if ": " in full_text:
                hex_value = full_text.split(": ", 1)[1]
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(hex_value))
                    wx.TheClipboard.Close()
                    wx.MessageBox(f"Скопійовано: {hex_value}", "Буфер обміну", wx.OK | wx.ICON_INFORMATION)

        def update_color_display(self, color):
            if not self.SafeUpdate():
                return
            self.color_display_panel.SetBackgroundColour(color)
            self.color_display_panel.Refresh()

            r, g, b = color.Red(), color.Green(), color.Blue()
            hex_value = f"#{r:02X}{g:02X}{b:02X}"
            self.hex_label.SetLabel(f"HEX: {hex_value}")

    # --- Реєстрація пункту меню ---
    ID_COLOR = DrFrame.GetNewId()
    
    if hasattr(DrFrame, "programmenu"):
        menu = DrFrame.programmenu
    else:
        menu = DrFrame.optionsmenu

    menu.AppendSeparator()
    menu.Append(ID_COLOR, "Color Picker")

    def ShowColorPicker(event):
        dlg = ColorPickerDialog(DrFrame)
        dlg.ShowModal()
        dlg.Destroy()

    DrFrame.Bind(wx.EVT_MENU, ShowColorPicker, id=ID_COLOR)
