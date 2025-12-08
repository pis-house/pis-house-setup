from tkinter import Frame, Label, messagebox, Button, Scrollbar, ttk
from firebase_admin import firestore
from app_data import AppData


class DeviceListPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.set_ui()
        self.init_data()
        
        
    def set_ui(self):
        label = Label(self, text="デバイスリスト", font=("Arial", 20))
        label.pack(pady=10)

        tree_frame = Frame(self)
        tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.device_tree = ttk.Treeview(
            tree_frame, 
            yscrollcommand=tree_scroll.set, 
            columns=("ID", "Name", "IP", "Gateway"), 
            show="headings"
        )
        self.device_tree.pack(fill='both', expand=True)

        tree_scroll.config(command=self.device_tree.yview)

        self.device_tree.heading("ID", text="ID", anchor="w")
        self.device_tree.heading("Name", text="デバイス識別名", anchor="w")
        self.device_tree.heading("IP", text="IPアドレス", anchor="w")
        self.device_tree.heading("Gateway", text="ゲートウェイ", anchor="w")

        self.device_tree.column("ID", width=100, anchor="w")
        self.device_tree.column("Name", width=100, anchor="w")
        self.device_tree.column("IP", width=120, anchor="w")
        self.device_tree.column("Gateway", width=120, anchor="w")
        
        button_frame = Frame(self)
        button_frame.pack(pady=10)
        
        new_button = Button(
            button_frame, 
            text="新規", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.open_create_device_page
        )
        new_button.pack(side="left", padx=10)
        
        edit_button = Button(
            button_frame, 
            text="編集", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.open_edit_device_page
        )
        edit_button.pack(side="left", padx=10)
        
        delete_button = Button(
            button_frame, 
            text="削除", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.delete_device_selected_device
        )
        delete_button.pack(side="left", padx=10)
        
        setup_infrared_button = Button(
            button_frame, 
            text="赤外線登録", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=self.setup_infrared_device_selected_device
        )
        setup_infrared_button.pack(side="left", padx=10)
        
        back_button = Button(
            button_frame, 
            text="終了", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=lambda: self.controller.show_frame("MenuPage")
        )
        back_button.pack(side="left", padx=10)
        

    def init_data(self):
        try:
            devices = firestore.client().collection("setup").document(AppData.APP_UUID).collection("devices").get()
            
            for device in devices:
                data = device.to_dict()
                self.device_tree.insert("", "end", iid=device.id, values=(device.id, data["name"], data["ip"], data["gateway"]))

        except Exception:
            messagebox.showerror("エラー", "デバイスリストの取得中にエラーが発生しました。")


    def open_create_device_page(self):
        self.controller.show_frame("SetupDevicePage")


    def delete_device_selected_device(self):
        selected_item_id = self.device_tree.selection()[0]
        
        if not selected_item_id:
            messagebox.showwarning("警告", "削除するデバイスを選択してください。")
            return

        confirm = messagebox.askyesno(
            "削除の確認",   
            f"デバイス ID: {selected_item_id} を削除してもよろしいですか？\nこの操作は元に戻せません。"
        )
        
        if confirm:
            firestore.client().collection("setup").document(AppData.APP_UUID).collection("devices").document(selected_item_id).delete()
            self.device_tree.delete(selected_item_id)
            
    
    def setup_infrared_device_selected_device(self):
        selected_item_id = self.device_tree.selection()[0]
        
        if not selected_item_id:
            messagebox.showwarning("警告", "編集するデバイスを選択してください。")
            return

        self.controller.show_frame("SetupInfraredPage", args={'id': selected_item_id})


    def open_edit_device_page(self):
        selected_item_id = self.device_tree.selection()[0]
        
        if not selected_item_id:
            messagebox.showwarning("警告", "編集するデバイスを選択してください。")
            return

        self.controller.show_frame("SetupDevicePage", args={'id': selected_item_id})