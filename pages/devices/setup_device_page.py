from tkinter import Frame, Label, Entry, Button
from tkinter import messagebox
import random
from utils.network_config_info import NetworkConfigInfo

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
            ("device_name", "デバイス名"),
            ("ssid", "SSID名"),
            ("password", "パスワード"),
            ("ip_address", "IPアドレス"),
            ("gateway", "ゲートウェイ"),
            ("subnet", "サブネット"),
        ]

        # 修正箇所: fontサイズを調整し、pady/stickyを追加して視認性を確保
        auto_assign_button = Button(
            form_frame,
            text="自動割り当て",
            font=("MSゴシック", "14", " "), # ボタンを狭くするためフォントサイズを調整
            width=10, # 幅を固定
            command=self.auto_assign_network_config
        )
        # gridで配置。padyを追加し、sticky='e'で右寄せにすることで、見えなくなるのを防ぐ
        auto_assign_button.grid(row=3, column=1, columnspan=1, pady=(5, 10), padx=5, sticky='e') 
        
        for i, (key, label_text) in enumerate(fields):
            row_index = i
            if key in ["ip_address", "gateway", "subnet"]:
                row_index += 1 

            Label(form_frame, text=f"{label_text}:", width=15, anchor='w').grid(row=row_index, column=0, pady=5, padx=5)
            
            entry = Entry(form_frame, width=40)
            entry.grid(row=row_index, column=1, pady=5, padx=5)
            self.entries[key] = entry
            
            if key == "password":
                entry.config(show="*")

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1) # このweight=1がボタンを見えなくする原因ではないことを確認

        # ボタンのフォントサイズも修正し、横幅を短くする
        button_font = ("MSゴシック", "14", " ")
        
        button_frame = Frame(self)
        button_frame.pack(pady=20)

        setup_button = Button(
            button_frame, 
            text="設定", 
            font=button_font, # 修正
            width=10,
            command=self.submit_setup_data
        )
        setup_button.pack(side="left", padx=15)
        
        back_button = Button(
            button_frame, 
            text="戻る", 
            font=button_font, # 修正
            width=10,
            command=lambda: self.controller.show_frame("DeviceListPage")
        )
        back_button.pack(side="left", padx=15)
        
    def generate_random_ip(self, gateway_ip, subnet_mask):
        if subnet_mask != "255.255.255.0":
            return None
        gateway_parts = gateway_ip.split('.')
        
        if len(gateway_parts) != 4:
            return None

        network_prefix = ".".join(gateway_parts[:3])
        random_host_part = random.randint(2, 254) 
        return f"{network_prefix}.{random_host_part}"
        
    def auto_assign_network_config(self):
        network_config_info = NetworkConfigInfo()
        
        # set_config()が成功した場合のみ先に進む
        if not network_config_info.set_config():
            messagebox.showerror("エラー", "ネットワーク情報の取得に失敗しました。")
            return
        
        # ゲートウェイとサブネットが取得できたかチェック
        if not network_config_info.gateway or not network_config_info.subnet:
            messagebox.showerror("エラー", "ゲートウェイまたはサブネット情報が取得できませんでした。")
            return

        ip_address = self.generate_random_ip(
            gateway_ip=network_config_info.gateway, 
            subnet_mask=network_config_info.subnet
        )

        if ip_address is None:
             messagebox.showerror("エラー", "IPアドレスの生成に失敗しました。\n(現在はサブネット255.255.255.0のみ対応しています。)")
             return

        self.entries['ip_address'].delete(0, 'end')
        self.entries['ip_address'].insert(0, ip_address)
        
        self.entries['subnet'].delete(0, 'end')
        self.entries['subnet'].insert(0, network_config_info.subnet)
        
        self.entries['gateway'].delete(0, 'end')
        self.entries['gateway'].insert(0, network_config_info.gateway)
        
        messagebox.showinfo("完了", "ネットワーク設定を自動割り当てしました。")

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