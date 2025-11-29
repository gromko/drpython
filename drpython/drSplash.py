import wx

"""
     Створюємо та показуємо splash screen
"""
class drSplashScreen(wx.Frame):
    def __init__(self, imagepath, parent=None, id=-1, title=""):
        wx.Frame.__init__(self, parent, id, title, style=wx.BORDER_NONE | wx.STAY_ON_TOP)

        try:
            image = wx.Image(imagepath, wx.BITMAP_TYPE_PNG)
            if not image.IsOk():
                raise Exception("Зображення не завантажено або пошкоджено.")
            self.bitmap = wx.Bitmap(image)
            w, h = self.bitmap.GetSize()
        except Exception as e:
            print(f"Помилка завантаження зображення: {e}")
            w, h = 500, 450

        # Встановлюємо точний розмір
        self.SetClientSize((w, h))
        self.CenterOnScreen()

        # Створюємо панель і зображення
        self.panel = wx.Panel(self, size=(w, h))
        self.image_ctrl = wx.StaticBitmap(self.panel, bitmap=self.bitmap)    


        # Створення індикатора поступу
        self.progress = wx.Gauge(self.panel, -1, range=100, size=(250, 4), pos=(125, 50))
        self.Show()
        # Таймер для оновлення індикатора поступу
        self.progress_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress, self.progress_timer)
        self.progress_timer.Start(20)  # Оновлення кожні 20 мс

        # Таймер для закриття заставки через 2 секунди
        self.close_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.close_splash, self.close_timer)
        self.close_timer.Start(3000)  # 2000 мс = 2 секунди

    def update_progress(self, event):
        # Оновлення індикатора поступу
        value = self.progress.GetValue()
        if value < 100:
            self.progress.SetValue(value + 1)
        else:
            self.progress_timer.Stop()  # Зупинити таймер після завершення

    def close_splash(self, event):
        self.Destroy()  # Закриття заставки
        
