from tkinter import Frame, Label, Entry, Button, messagebox
from firebase_admin import firestore
from app_data import AppData
from tkinter.ttk import Combobox

class SetupInfraredPage(Frame):
    def __init__(self, parent, controller, **args):
        super().__init__(parent)
        self.controller = controller
        self.device_id = args.get('id')
        self.device_doc_ref = firestore.client().collection("setup").document(AppData.APP_UUID).collection("devices").document(self.device_id)
        setup_device = self.device_doc_ref.get().to_dict()
        self.device_type_var = setup_device["device_type"]
        self.rows = []
        self.set_ui()
        self.load_device_info()

    def set_ui(self):
        Label(self, text="赤外線登録", font=("Arial", 20)).pack(pady=8)
        self.form_frame = Frame(self)
        self.form_frame.pack(padx=16, pady=8)

        headers = ["赤外線名", "アドレス", "コマンド", "プロトコル", "独自処理識別名"]
        for i, h in enumerate(headers):
            Label(self.form_frame, text=h, font=("MSゴシック", 10, "bold")).grid(row=1, column=i, padx=6, pady=6)

        self.rows_start_row = 2

        button_frame = Frame(self)
        button_frame.pack(pady=12)

        save_btn = Button(button_frame, text="保存", font=("MSゴシック", "20", ""), width=10, command=self.on_save)
        save_btn.pack(side='left', padx=8)

        back_btn = Button(button_frame, text="戻る", font=("MSゴシック", "20", ""), width=10, command=lambda: self.controller.show_frame("DeviceListPage"))
        back_btn.pack(side='left', padx=8)

    def load_device_info(self):
        proc_list = [
            "NEC",
            "SONY",
            "RC5",
            "RC6",
            "JVC",
            "SAMSUNG",
            "PANASONIC"
        ]
        aircon_patterns = {
            "aircon_stop": "エアコン停止",
            "aircon_heat": "暖房",
            "aircon_dry": "除湿",
            "aircon_cool": "冷房",
            "aircon_temp_up": "温度を上げる",
            "aircon_temp_down": "温度を下げる"
        }
        
        light_patterns = {
            "light_on": "照明オン",
            "light_off": "照明オフ",
            "light_bright_up": "明るさを上げる",
            "light_bright_down": "明るさを下げる"
        }

        patterns = aircon_patterns if self.device_type_var == 'aircon' else light_patterns

        for widget in self.form_frame.winfo_children():
             if int(widget.grid_info()['row']) >= self.rows_start_row:
                 widget.destroy()
        self.rows = [] 
        infrared_docs = self.device_doc_ref.collection("infrared").stream()
        existing_data = {doc.id: doc.to_dict() for doc in infrared_docs}

        for idx, (pattern_key, pattern_name) in enumerate(patterns.items()):
            row_index = self.rows_start_row + idx
            
            name_label = Label(self.form_frame, text=pattern_name, font=("MSゴシック", 12))
            name_label.grid(row=row_index, column=0, padx=4, pady=4, sticky='w')
            
            addr_entry = Entry(self.form_frame, width=18)
            addr_entry.grid(row=row_index, column=1, padx=4, pady=4, sticky='w')

            cmd_entry = Entry(self.form_frame, width=24)
            cmd_entry.grid(row=row_index, column=2, padx=4, pady=4, sticky='w')
            
            proc_combobox = Combobox(
                self.form_frame, 
                values=[
                    "NEC",
                    "SONY",
                    "RC5",
                    "RC6",
                    "JVC",
                    "SAMSUNG",
                    "PANASONIC"
                ],
                width=16, 
                state='readonly'
            )
            proc_combobox.grid(row=row_index, column=3, padx=4, pady=4, sticky='w')
            
            custom_process_entry = Entry(self.form_frame, width=24)
            custom_process_entry.grid(row=row_index, column=2, padx=4, pady=4, sticky='w')
            
            
            if pattern_key in existing_data:
                data = existing_data[pattern_key]
                
                cmd = data.get("command", "")
                cmd_entry.insert(0, cmd)

                addr = data.get("address", "")
                addr_entry.insert(0, addr)
                
                proc = data.get("protocol", "")
                if proc in proc_list:
                    proc_combobox.set(proc)

                custom_process = data.get("custom_process", "")
                custom_process_entry.insert(0, custom_process)
                


            self.rows.append({
                "pattern_key": pattern_key,
                "pattern_name": pattern_name,
                "address_entry": addr_entry,
                "command_entry": cmd_entry,
                "protocol_combobox": proc_combobox,
                "custom_process_entry": custom_process
            })

    def on_save(self):
        db = firestore.client()
        batch = db.batch()

        for r in self.rows:
            addr = r["address_entry"].get().strip()
            cmd = r["command_entry"].get().strip()
            proc = r["protocol_combobox"].get().strip()
            custom_process = r["custom_process"].get().strip()
            
            pattern_key = r["pattern_key"] 
            
            infrared_document_ref = self.device_doc_ref.collection("infrared").document(pattern_key)
            
            if cmd == "" and addr == "":
                batch.delete(infrared_document_ref)
            else:
                batch.set(infrared_document_ref, {
                    "address": addr,
                    "command": cmd,
                    "protocol": proc,
                    "custom_process": custom_process
                })
        
        try:
            # バッチ処理を実行
            batch.commit()
            messagebox.showinfo("成功", "赤外線登録が正常に完了しました。")
            self.controller.show_frame("DeviceListPage")
        except Exception as e:
            messagebox.showerror("エラー", f"データの保存中にエラーが発生しました: {e}")