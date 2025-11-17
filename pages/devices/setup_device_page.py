from tkinter import Frame, Label, Entry, Button
from tkinter import messagebox
import random
from utils.network_config_info import NetworkConfigInfo
from firebase_admin import firestore
from app_data import AppData
from utils.esp32_file_transfer import Esp32FileTransfer
import json

class SetupDevicePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.set_ui()
        
    def set_ui(self):
        label = Label(self, text="デバイスセットアップ", font=("Arial", 20))
        label.pack(pady=10)
        
        prompt_label = Label(
            self, 
            text="デバイス設定を行う前に、ESP32をPCに接続してください", 
            font=("MSゴシック", 14, "bold"),
            fg="red"
        )
        prompt_label.pack(pady=10)

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

        auto_assign_button = Button(
            form_frame,
            text="ネットワーク情報自動割り当て",
            font=("MSゴシック", "20", " "),
            width=20,
            command=self.auto_assign_network_config
        )
        auto_assign_button.grid(row=3, column=1, columnspan=1)
        
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
        form_frame.grid_columnconfigure(1, weight=1)
        
        button_frame = Frame(self)
        button_frame.pack(pady=20)

        setup_button = Button(
            button_frame, 
            text="設定", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.submit
        )
        setup_button.pack(side="left", padx=15)
        
        back_button = Button(
            button_frame, 
            text="終了", 
            font=("MSゴシック", "20", " "),
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
        if not network_config_info.set_config():
            messagebox.showerror("エラー", "ネットワーク情報の取得に失敗しました")
        
        ip_address = self.generate_random_ip(gateway_ip=network_config_info.gateway, subnet_mask=network_config_info.subnet)

        self.entries['ip_address'].delete(0, 'end')
        self.entries['ip_address'].insert(0, ip_address)
        
        self.entries['subnet'].delete(0, 'end')
        self.entries['subnet'].insert(0, network_config_info.subnet)
        
        self.entries['gateway'].delete(0, 'end')
        self.entries['gateway'].insert(0, network_config_info.gateway)
        

    def submit(self):
        setup_data = {key: entry.get() for key, entry in self.entries.items()}
        device_name = setup_data.get("device_name")
        
        validation_fields = {
            "device_name": "デバイス名",
            "ssid": "SSID名",
            "password": "パスワード",
            "ip_address": "IPアドレス",
            "gateway": "ゲートウェイ",
            "subnet": "サブネット",
        }

        for key, display_name in validation_fields.items():
            if not setup_data.get(key) or setup_data.get(key).strip() == "":
                messagebox.showerror("入力エラー", f"「{display_name}」は必須項目です。入力してください。")
                return
        
        firestore_data = {
            "name": device_name,
            "ssid": setup_data["ssid"],
            "password": setup_data["password"],
            "ip": setup_data["ip_address"],
            "gateway": setup_data["gateway"],
            "subnet": setup_data["subnet"],
        }

        try:
            setting_data = {
                "ssid": setup_data["ssid"],
                "password": setup_data["password"],
                "ip": setup_data["ip_address"],
                "gateway": setup_data["gateway"],
                "subnet": setup_data["subnet"],
            }
            
            with open(f"{AppData.DATA_FOLDER}/setting.json", 'w', encoding='utf-8') as f:
                json.dump(setting_data, f)
                
            error_message = Esp32FileTransfer.image_create_and_upload(
                data_folder=AppData.DATA_FOLDER,
                mklittlefs_path=AppData.MKLITTLEFS_PATH,
                output_image=AppData.OUTPUT_IMAGE
            )
            
            if error_message is not None:
                messagebox.showerror("エラー", error_message)
                return
                
            db = firestore.client()
            target_collection_ref = db.collection("setup").document(AppData.APP_UUID).collection("devices")
            
            target_collection_ref.add(firestore_data)
            messagebox.showinfo("成功", "デバイス設定が正常に登録されました。")
            self.controller.show_frame("DeviceListPage")
            
        except Exception as e:
            messagebox.showerror("エラー", f"エラーが発生しました: {e}")