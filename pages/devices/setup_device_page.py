from tkinter import Frame, Label, Entry, Button, Radiobutton, StringVar
from tkinter import messagebox
import random
from utils.network_config_info import NetworkConfigInfo
from firebase_admin import firestore
from app_data import AppData
from utils.esp32_file_transfer import Esp32FileTransfer
import json
import ulid

class SetupDevicePage(Frame):
    def __init__(self, parent, controller, **args):
        super().__init__(parent)
        self.controller = controller
        self.device_id = args.get('id')
        self.device_type_var = StringVar(self, value='light') 
        self.set_ui()
        self.get_edit_data()
        
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
        
        current_row = 0

        Label(form_frame, text="デバイス名:", width=15, anchor='w').grid(row=current_row, column=0, pady=5, padx=5)
        entry = Entry(form_frame, width=40)
        entry.grid(row=current_row, column=1, pady=5, padx=5)
        self.entries['device_name'] = entry
        current_row += 1

        Label(form_frame, text="デバイス種別:", width=15, anchor='w').grid(row=current_row, column=0, pady=5, padx=5)
        
        radio_frame = Frame(form_frame)
        radio_frame.grid(row=current_row, column=1, pady=5, padx=100, sticky='w')
        
        light_radio = Radiobutton(
            radio_frame, 
            text="照明", 
            variable=self.device_type_var, 
            value='light'
        )
        
        light_radio.pack(side='left', padx=10)
        
        if self.device_id:
            light_radio.config(state="disabled")
        
        aricon_radio = Radiobutton(
            radio_frame, 
            text="エアコン", 
            variable=self.device_type_var, 
            value='aircon'
        )
        
        aricon_radio.pack(side='left', padx=10)
        
        if self.device_id:
            aricon_radio.config(state="disabled")
        
        current_row += 1

        Label(form_frame, text="SSID名:", width=15, anchor='w').grid(row=current_row, column=0, pady=5, padx=5)
        entry = Entry(form_frame, width=40)
        entry.grid(row=current_row, column=1, pady=5, padx=5)
        self.entries['ssid'] = entry
        current_row += 1
        
        Label(form_frame, text="パスワード:", width=15, anchor='w').grid(row=current_row, column=0, pady=5, padx=5)
        entry = Entry(form_frame, width=40)
        entry.grid(row=current_row, column=1, pady=5, padx=5)
        self.entries['password'] = entry
        current_row += 1

        auto_assign_button = Button(
            form_frame,
            text="ネットワーク情報自動割り当て",
            font=("MSゴシック", "13", " "),
            width=20,
            command=self.auto_assign_network_config
        )
        auto_assign_button.grid(row=current_row, column=1, columnspan=1, pady=5)
        current_row += 1

        network_fields = [
            ("ip_address", "IPアドレス"),
            ("self_ip_address", "ラズパイIPアドレス"),
            ("gateway", "ゲートウェイ"),
            ("subnet", "サブネット"),
        ]

        for key, label_text in network_fields:
            Label(form_frame, text=f"{label_text}:", width=15, anchor='w').grid(row=current_row, column=0, pady=5, padx=5)
            
            entry = Entry(form_frame, width=40)
            entry.grid(row=current_row, column=1, pady=5, padx=5)
            self.entries[key] = entry
            current_row += 1

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
            return
        
        ip_address = self.generate_random_ip(gateway_ip=network_config_info.gateway, subnet_mask=network_config_info.subnet)
        
        if ip_address is None:
            messagebox.showerror("エラー", "自動割り当てはサブネットマスクが255.255.255.0の場合のみサポートされています。")
            return

        self.entries['ip_address'].delete(0, 'end')
        self.entries['ip_address'].insert(0, ip_address)
        
        self.entries['self_ip_address'].delete(0, 'end')
        self.entries['self_ip_address'].insert(0, network_config_info.ip)
        
        self.entries['subnet'].delete(0, 'end')
        self.entries['subnet'].insert(0, network_config_info.subnet)
        
        self.entries['gateway'].delete(0, 'end')
        self.entries['gateway'].insert(0, network_config_info.gateway)
        

    def submit(self):
        setup_data = {key: entry.get() for key, entry in self.entries.items()}
        setup_data['device_type'] = self.device_type_var.get()
        device_name = setup_data.get("device_name")
        
        validation_fields = {
            "device_name": "デバイス名",
            "ssid": "SSID名",
            "password": "パスワード",
            "ip_address": "IPアドレス",
            "self_ip_address": "ラズパイIPアドレス",
            "gateway": "ゲートウェイ",
            "subnet": "サブネット",
        }

        for key, display_name in validation_fields.items():
            if not setup_data.get(key) or setup_data.get(key).strip() == "":
                messagebox.showerror("入力エラー", f"「{display_name}」は必須項目です。入力してください。")
                return
        
        
        firestore_data = {
            "id": self.device_id,
            "name": device_name,
            "device_type": setup_data['device_type'],
            "ssid": setup_data["ssid"],
            "password": setup_data["password"],
            "ip": setup_data["ip_address"],
            "self_ip": setup_data['self_ip_address'],
            "gateway": setup_data["gateway"],
            "subnet": setup_data["subnet"],
        }
        
        if self.device_id is None:
            setup_device_id = str(ulid.new())
            firestore_data["id"] = setup_device_id
            firestore_data["is_active"] = False
            firestore_data["aircon_temperature"] = 0
            firestore_data["light_brightness_percent"] = 0

        try:
            setting_data = {
                "ssid": setup_data["ssid"],
                "password": setup_data["password"],
                "ip": setup_data["ip_address"],
                "remote_ip": setup_data['self_ip_address'],
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
            
            collection_ref = firestore.client().collection("setup").document(AppData.APP_UUID).collection("devices")
            if self.device_id is None:
                collection_ref.document(setup_device_id).set(firestore_data)
            else:
                collection_ref.document(self.device_id).update(firestore_data)
                
            messagebox.showinfo("成功", "デバイス設定が正常に完了しました。")
            self.controller.show_frame("DeviceListPage")
            
        except Exception as e:
            messagebox.showerror("エラー", f"エラーが発生しました: {e}")
    
    def get_edit_data(self):
        if not self.device_id:
            return
        try:
            
            doc = firestore.client().collection("setup").document(AppData.APP_UUID).collection("devices").document(self.device_id).get()
            if doc.exists:
                firestore_data = doc.to_dict()
                initial_data = {
                    "device_name": firestore_data.get("name", ""),
                    "ssid": firestore_data.get("ssid", ""),
                    "password": firestore_data.get("password", ""),
                    "ip_address": firestore_data.get("ip", ""),
                    "self_ip_address": firestore_data.get("self_ip",""),
                    "gateway": firestore_data.get("gateway", ""),
                    "subnet": firestore_data.get("subnet", ""),
                }
                
                device_type = firestore_data.get("device_type", 'light')
                self.device_type_var.set(device_type)

                for key, value in initial_data.items():
                    if value is None:
                            value = ""
                    if key in self.entries:
                        self.entries[key].delete(0, 'end')
                        self.entries[key].insert(0, value)
            else:
                messagebox.showwarning("警告", "指定されたデバイスIDのデータが見つかりませんでした。新規作成モードで開きます。")
                self.device_id = None
                
        except Exception as e:
            messagebox.showerror("エラー", f"デバイスデータの取得中にエラーが発生しました: {e}")
            self.device_id = None