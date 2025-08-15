import csv
# editor.py

import csv
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog


import os
import sys
import shutil
import platform

# CSV 파일 읽기
def read_and_process_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        processed_data = []
        for row in reader:
            # 필드 이름 변경
            row['k'] = row.pop('T')  # 'T' -> 'k'
            row['km'] = row.pop('D')  # 'D' -> 'km'
            if 'E' in row.keys() : 
                row['p'] = row.pop('E')
            else :
                row['p'] = ""

            if "/" in row['P'] :
                p_split = row.pop('P').split('/')  # 'P'를 'E'로 나누어 처리
                row['s'] = p_split[0] if len(p_split) > 0 else ""  # 'p'로 첫 번째 값 저장
                row['m'] = p_split[1] if len(p_split) > 1 else ""  # 'm'로 두 번째 값 저장
            else :
                row['s'] = row.pop('P')
                row['m'] = ""

            processed_data.append(row)
    return processed_data




def open_csv(self=None,called_from_one=None):
    # 파일 선택 다이얼로그
    file_path = filedialog.askopenfilename(
        title="CSV 파일 선택",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not file_path:
        tk.messagebox.showwarning("파일 선택", "CSV 파일을 선택해야 합니다.")
        return
    if called_from_one : 
        return file_path
    self.csv_file_path = file_path
    self.data = tool.read_and_process_csv(file_path=self.csv_file_path)
    if self.data:
        self.fieldnames = list(self.data[0].keys())
    else:
        tk.messagebox.showerror("오류", "CSV 파일을 읽을 수 없습니다.")
        return

    # 파일 열기 버튼 비활성화 및 숨김
    self.open_btn.configure(state="disabled")
    self.open_btn.pack_forget()
    self.show_editor()




def get_chrome_path():
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path

    elif system == "Darwin":  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path

    elif system == "Linux":
        chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
        if chrome_path:
            return chrome_path

    return None
