from tkinter import Frame, Label, font, Button

class MenuPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.set_ui()
        
    def set_ui(self):
        title = Label(self, text="メインメニュー", font=font.Font(family="Arial", size=24, weight="bold"))
        title.pack(pady=30)
        
        menu_frame = Frame(self)
        menu_frame.pack()
        
        menus = {
            "デバイス一覧": lambda: self.controller.show_frame("DeviceListPage"),
            "デバイス情報": lambda: None
        }
        
        for menu_name, command_func in menus.items():
            button = Button(menu_frame, text=menu_name, font=("MSゴシック", "20", " "), width=30, command=command_func)
            button.pack(pady=10)
