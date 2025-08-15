# editor.py

import csv
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox
import webbrowser
from one import FlashcardApp as capp
import tool
from tkinter import filedialog

class CsvRowEditorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("CSV 한 행 집중 수정기")
        self.geometry("500x350")
        self.data = []
        self.fieldnames = []
        self.cur_idx = 0
        self.entries = []
        self.csv_file_path = None

        # 파일 열기 버튼 (초기 화면)
        self.open_btn = ctk.CTkButton(self, text="CSV 파일 열기", command=tool.open_csv(self=self))
        self.open_btn.pack(pady=32)

        # 나머지 위젯(Entry 등)은 일단 None으로
        self.idx_label = None
        self.form_frame = None
        self.btn_frame = None
        self.prev_btn = None
        self.save_btn = None
        self.next_btn = None
        self.save_all_btn = None


    def show_editor(self):
        # 행 번호 표시
        self.idx_label = ctk.CTkLabel(self, text="")
        self.idx_label.pack(pady=6)

        # Entry 영역
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=16)

        for i, field in enumerate(self.fieldnames):
            row = ctk.CTkFrame(self.form_frame)
            row.pack(fill="x", pady=3)
            label = ctk.CTkLabel(row, text=field, width=120, anchor="w")
            label.pack(side="left")
            entry = ctk.CTkEntry(row, width=260)
            entry.pack(side="left")
            self.entries.append(entry)

        # 이동 및 저장 버튼
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)
        self.prev_btn = ctk.CTkButton(self.btn_frame, text="이전", width=80, command=self.go_prev)
        self.prev_btn.pack(side="left", padx=6)
        self.save_btn = ctk.CTkButton(self.btn_frame, text="저장", width=90, fg_color="#008800", command=self.update_row)
        self.save_btn.pack(side="left", padx=6)
        self.next_btn = ctk.CTkButton(self.btn_frame, text="다음", width=80, command=self.go_next)
        self.next_btn.pack(side="left", padx=6)

        # 전체 저장 버튼
        self.save_all_btn = ctk.CTkButton(self, text="CSV 전체 저장", fg_color="#333399", command=self.save_csv)
        self.save_all_btn.pack(pady=6)

        self.show_row()

        # 키 바인딩
        self.bind('<Key>', self.key_event)
        self.bind('<Return>', self.enter_event)
        self.bind("1", lambda event: capp.search(self=self, target=1))
        self.bind("2", lambda event: capp.search(self=self, target=2))
        self.bind("3", lambda event: capp.search(self=self, target=3, event=event))
        self.bind("4", lambda event: capp.search(self=self, target=4))
        self.bind("q", lambda event: capp.search(self=self, target=11)); self.bind("Q", lambda event: capp.search(self=self, target=11))
        self.bind("e", lambda event: capp.search(self=self, target=12)); self.bind("E", lambda event: capp.search(self=self, target=12))
        self.bind(";", lambda event: capp.search(self=self, target=13))
        self.focus_set()

    def enter_event(self, event):
        self.update_row()
        self.go_next()

    def key_event(self, event):
        if event.char == '1':
            t_value = self.data[self.cur_idx].get('T', None)
            url = f"https://ja.dict.naver.com/#/search?query={t_value}"
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(tool.get_chrome_path()))
            webbrowser.get('chrome').open(url)

    def show_row(self):
        for i, field in enumerate(self.fieldnames):
            value = self.data[self.cur_idx][field]
            self.entries[i].delete(0, tk.END)
            self.entries[i].insert(0, value if value is not None else "")
        self.idx_label.configure(text=f"{self.cur_idx+1} / {len(self.data)}행 수정 중")
        self.prev_btn.configure(state="normal" if self.cur_idx > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.cur_idx < len(self.data)-1 else "disabled")

    def update_row(self):
        for i, field in enumerate(self.fieldnames):
            self.data[self.cur_idx][field] = self.entries[i].get()
        self.save_csv()

    def go_prev(self):
        self.update_row()
        if self.cur_idx > 0:
            self.cur_idx -= 1
            self.show_row()

    def go_next(self):
        self.update_row()
        if self.cur_idx < len(self.data)-1:
            self.cur_idx += 1
            self.show_row()

    def save_csv(self):
        try:
            header = ['T', 'D', 'P', 'E']
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                for data in self.data:
                    row = {
                        'T': data['k'],
                        'D': data['km'],
                        'P': f"{data['s']}/{data['m']}",
                        'E': data['p']
                    }
                    writer.writerow(row)
        except Exception as e:
            tk.messagebox.showerror("저장 실패", str(e))

if __name__ == '__main__':
    ctk.set_appearance_mode("light")
    app = CsvRowEditorApp()
    app.mainloop()
