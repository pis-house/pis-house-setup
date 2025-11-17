from tkinter import Frame, Label, ttk, messagebox, Button
from app_data import AppData

class SystemInfoPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.set_ui()
        
    def set_ui(self):
        title_frame = Frame(self)
        title_frame.pack(fill='x', pady=10)

        title_label = Label(title_frame, text="システム情報", font=("Yu Gothic UI", 16, "bold"))
        title_label.pack(side="left", padx=20)

        info_frame = Frame(self, padx=20, pady=10)
        info_frame.pack(fill='both', expand=True)

        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=2)

        self._add_info_row(info_frame, 0, "アプリケーションバージョン:", AppData.APP_VERSION)

        ttk.Separator(info_frame, orient='horizontal').grid(row=2, columnspan=2, sticky="ew", pady=(10, 5))

        self._add_uuid_row(info_frame, 3, "スマホアプリ連携ID:", AppData.APP_UUID)

        ttk.Separator(info_frame, orient='horizontal').grid(row=4, columnspan=2, sticky="ew", pady=(5, 10))
        
        button_frame = Frame(self)
        button_frame.pack(pady=20)
        
        back_button = Button(
            button_frame, 
            text="終了", 
            font=("MSゴシック", "20", " "),
            width=10,
            command=lambda: self.controller.show_frame("MenuPage")
        )
        back_button.pack(side="left", padx=15)


    def _add_info_row(self, parent_frame, row_index, label_text, value_text):
        label = Label(parent_frame, text=label_text, anchor="w", font=("Yu Gothic UI", 10))
        label.grid(row=row_index, column=0, sticky="ew", padx=5, pady=5)
        
        value = Label(parent_frame, text=value_text, anchor="w", font=("Yu Gothic UI", 10, "bold"), wraplength=400)
        value.grid(row=row_index, column=1, sticky="ew", padx=5, pady=5)

    def _add_uuid_row(self, parent_frame, row_index, label_text, uuid_value):
        self._add_info_row(parent_frame, row_index, label_text, uuid_value)
        
        copy_button = Button(
            parent_frame,
            text="IDをコピー",
            command=lambda: self._copy_uuid(uuid_value),
            font=("MSゴシック", "20", " "),
            width=12
        )
        copy_button.grid(row=row_index, column=2, sticky="w", padx=(5, 0))
        parent_frame.columnconfigure(2, weight=0)

    def _copy_uuid(self, uuid_value):
        try:
            self.controller.clipboard_clear()
            self.controller.clipboard_append(uuid_value)
            self.controller.update() 
            messagebox.showinfo("コピー完了", "識別IDがクリップボードにコピーされました。")
        except Exception as e:
            messagebox.showerror("エラー", f"UUIDのコピー中にエラーが発生しました: {e}")