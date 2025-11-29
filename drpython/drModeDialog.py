import wx
import drScrolledMessageDialog

LARGESPACER = 30
sample_text = '''
drPython — це легке, зручне та елегантне середовище розробки, спеціально створене для роботи з мовою програмування Python. Мінімалістичний та інтуїтивно зрозумілий інтерфейс drPython вражає своєю простотою, а відсутність зайвих елементів і навантажених меню дозволяє зосередитися на головному — написанні коду. Середовище не вимагає складних налаштувань або установки додаткових компонентів - ви можете почати роботу майже миттєво після встановлення.

Для кого це середовище?
- Для новачків - якщо ви тільки починаєте вивчати Python, drPython стане вашим надійним помічником, який допоможе зрозуміти основи програмування без зайвих складнощів.
- Для викладачів - простий інтерфейс та можливість швидко запускати код роблять drPython ідеальним інструментом для навчання.
- Для професіоналів - якщо вам потрібен швидкий та легкий інструмент для створення простих скриптів або тестування ідей, drPython стане чудовим вибором.
'''   
class drModeDialog(wx.Dialog):
    
    """Creates a new drModeDialog, creates buttons, checkbox, and uses sizers to set
    the layout."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Перший запуск drPython", wx.Point(50,50), wx.Size(800,620), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        
        # Did the user choose the advanced option?
        self.advanced = False
        
        # Button IDs
        self.ID_ADVANCED = 101
        self.ID_BEGINNER = 102
        
        # Does the user not want to be asked at start up?
        self.dontDisplayAtStart = False
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        text0 = wx.StaticText(self)
        text0.SetLabelMarkup("<big><b>Вітаємо у середовищі програмування drPython</b></big>")
        text1 = wx.StaticText(self,label = sample_text)            
        text2 = wx.StaticText(self)
        text2.SetLabelMarkup("<small><i>\ndrPython читається як 'доктор Пайтон'</i></small>")
        text1.Wrap(790)
        self.mainSizer.Add(text0,0, wx.ALIGN_CENTER, border=10)
        self.mainSizer.Add(text1,0, wx.ALIGN_CENTER, border=10)
        
        
        self.cmdSizer = wx.BoxSizer(wx.HORIZONTAL)
       
        # Bitmap buttons
        self.btnAdvanced = wx.BitmapButton(self, self.ID_ADVANCED,wx.Bitmap(wx.Image(parent.bitmapdirectory + "/drAdvanced.png", wx.BITMAP_TYPE_PNG)))
        self.btnBeginner = wx.BitmapButton(self, self.ID_BEGINNER, wx.Bitmap(wx.Image(parent.bitmapdirectory + "/drBeginner.png",wx.BITMAP_TYPE_PNG)))
         
        # The main sizer, spacers are used to make the layout
        # more spread out.
        self.cmdSizer.Add((LARGESPACER, LARGESPACER), 0)
        self.cmdSizer.Add(self.btnBeginner, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.cmdSizer.Add((LARGESPACER + 5, LARGESPACER + 5), 0)
        self.cmdSizer.Add(self.btnAdvanced, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.mainSizer.Add(self.cmdSizer,0, wx.ALIGN_CENTER)
        
        text3 = wx.StaticText(self)
        text3.SetLabelMarkup("<b>Оберіть бажаний тип інтерфейсу середовища</b>") 
        self.mainSizer.Add(text3,0, wx.ALIGN_CENTER)
        self.mainSizer.Add(text2,0, wx.ALIGN_RIGHT)       
        
        
        self.SetAutoLayout(True)
        self.SetSizer(self.mainSizer)
        
        self.Bind(wx.EVT_BUTTON,  self.OnbtnAdvanced, id=self.ID_ADVANCED)
        self.Bind(wx.EVT_BUTTON, self.OnBtnBeginner, id=self.ID_BEGINNER)
                  
    """When the advanced button is clicked,
    save the state of the checkbox, and set the 'advanced' variable to true."""
    def OnbtnAdvanced(self, event):        
        self.advanced = True
        self.EndModal(wx.ID_OK)
        
    """When the beginner button is clicked,
    save the state of the checkbox, and leave the 'advanced' variable as it is,
    because it is false by default."""
    def OnBtnBeginner(self, event):        
        self.EndModal(wx.ID_OK)
    
    """Returns if the advanced mode has been selected"""
    def getChoice(self):
        return self.advanced
    
class drMode():
    def __init__(self, parent):
        dialog = drModeDialog(parent)
        result = dialog.ShowModal()

        if result == wx.ID_OK:            
            parent.idemode = dialog.getChoice()
               

        dialog.Destroy()
