from tkinter import Frame, Tk,messagebox
from pages.devices.device_list_page import DeviceListPage
from pages.menu_page import MenuPage
from pages.devices.setup_device_page import SetupDevicePage
from pages.systems.system_info_page import SystemInfoPage
from pages.devices.setup_infrared_page import SetupInfraredPage
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
import uuid
from pathlib import Path
from app_data import AppData
import inspect
import sys

class Main(Tk):
    UUID_FILE_NAME = "app_uuid.txt"
    
    def __init__(self):
        super().__init__()
        load_dotenv()
        
        AppData.APP_UUID = self.init_setup_uuid()
        AppData.DATA_FOLDER = os.getenv("DATA_FOLDER")
        AppData.MKLITTLEFS_PATH = os.getenv("MKLITTLEFS_PATH")
        AppData.OUTPUT_IMAGE = os.getenv("OUTPUT_IMAGE")
        
        
        self.init_firebase(os.getenv("FIREBASE_ADMIN_SDK_PATH"))
        
        self.page_classes = {
            "MenuPage": MenuPage,
            "DeviceListPage": DeviceListPage,
            "SetupDevicePage": SetupDevicePage,
            "SystemInfoPage": SystemInfoPage,
            "SetupInfraredPage": SetupInfraredPage
        }
        
        self.title("セットアップ")
        self.geometry("1000x500")
        
        self.container = Frame(self)
        self.container.pack(expand=True, fill="both")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        
        self.show_frame("MenuPage")
    
    def show_frame(self, page_name, args=None):
        
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        page_class = self.page_classes.get(page_name)
        
        if page_class is None:
            return
        
        try:
            signature = inspect.signature(page_class.__init__)
            
            accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values())

            if args and accepts_kwargs:
                new_frame = page_class(self.container, self, **args)
            else:
                new_frame = page_class(self.container, self)

        except ValueError:
            new_frame = page_class(self.container, self)
    
        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.tkraise()
        
        self.current_frame = new_frame
            
    def init_firebase(self, firebase_admin_sdk_path):
        try:
            cred = credentials.Certificate(firebase_admin_sdk_path)
            firebase_admin.initialize_app(cred)
        except FileNotFoundError:
            messagebox.showerror("エラー", f"サービスアカウントファイルが見つかりません: {firebase_admin_sdk_path}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("エラー", f"Firebase初期化エラー: {e}")
            self.destroy()
    
    def init_setup_uuid(self):
        uuid_file_path = self.get_executable_dir() / self.UUID_FILE_NAME        
        if uuid_file_path.exists():
            try:
                with open(uuid_file_path, 'r') as f:
                    app_uuid = f.read().strip()
                return app_uuid
            except Exception as e:
                messagebox.showerror("エラー", f"UUIDファイルの書き込みエラー: {e}")

        new_uuid = str(uuid.uuid4())
        
        try:
            with open(uuid_file_path, 'w') as f:
                f.write(new_uuid)
                messagebox.showinfo("重要なお知らせ", f"このIDをスマホアプリに入力してください。\n\n**識別ID:** {new_uuid}\n\n※このIDはアプリと連携するために必要です。後からメニューの「システム情報」でも確認できます。")
        except Exception as e:
            messagebox.showerror("エラー", f"UUIDファイルの書き込みエラー: {e}")
        
        return new_uuid

    def get_executable_dir(self):
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).resolve().parent
        
if __name__ == "__main__":
    app = Main()
    app.mainloop()