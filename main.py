from tkinter import Frame, Tk
from pages.devices.device_list_page import DeviceListPage
from pages.menu_page import MenuPage
from pages.devices.setup_device_page import SetupDevicePage


class MainPage(Tk):
    def __init__(self):
        super().__init__()
        self.title("セットアップ")
        self.geometry("1000x500")
        
        self.page_classes = {
            "MenuPage": MenuPage,
            "DeviceListPage": DeviceListPage,
            "SetupDevicePage": SetupDevicePage
        }
        
        self.container = Frame(self)
        self.container.pack(expand=True, fill="both")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        
        self.show_frame("MenuPage")
    
    def show_frame(self, page_name):
        
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        page_class = self.page_classes.get(page_name)
        
        if page_class is None:
            print(f"Error: Page class '{page_name}' not found.")
            return

        new_frame = page_class(self.container, self)
        
        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.tkraise()
        
        self.current_frame = new_frame
        
        
if __name__ == "__main__":
    app = MainPage()
    app.mainloop()