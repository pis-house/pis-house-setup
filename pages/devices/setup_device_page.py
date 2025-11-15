from tkinter import Frame, Label, Entry, Button
from tkinter import messagebox


class SetupDevicePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.set_ui()
        
    def set_ui(self):
        label = Label(self, text="デバイスセットアップ", font=("Arial", 20))
        label.pack(pady=10)

        form_frame = Frame(self)
        form_frame.pack(pady=20, padx=20, fill='x')

        self.entries = {}
        
        fields = [
            ("ip_address", "IPアドレス"),
            ("gateway", "ゲートウェイ"),
            ("subnet", "サブネット"),
            ("ssid", "SSID名"),
            ("password", "パスワード"),
            ("device_name", "デバイス名"),
        ]

        for i, (key, label_text) in enumerate(fields):
            Label(form_frame, text=f"{label_text}:", width=15, anchor='w').grid(row=i, column=0, pady=5, padx=5)
            
            entry = Entry(form_frame, width=40)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key] = entry
            
            if key == "password":
                entry.config(show="*")

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        button_frame = Frame(self)
        button_frame.pack(pady=20)

        setup_button = Button(
            button_frame, 
            text="設定", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.submit_setup_data
        )
        setup_button.pack(side="left", padx=15)
        
        back_button = Button(
            button_frame, 
            text="戻る", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=lambda: self.controller.show_frame("DeviceListPage")
        )
        back_button.pack(side="left", padx=15)
        

    def submit_setup_data(self):
        
        setup_data = {key: entry.get() for key, entry in self.entries.items()}
        
        if not setup_data.get("device_name"):
            messagebox.showerror("エラー", "デバイス名は必須項目です。")
            return
            
        print("--- Firestoreへ送信するデータ (モック) ---")
        for key, value in setup_data.items():
            print(f"{key}: {value}")
        print("---------------------------------------")
        
        try:
            messagebox.showinfo("成功", "デバイス設定が正常に送信されました。")
            
            self.controller.show_frame("MenuPage")
            
        except Exception as e:
            messagebox.showerror("送信エラー", f"設定の送信中にエラーが発生しました: {e}")