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
import time
import webbrowser
import re


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
    self.data = read_and_process_csv(file_path=self.csv_file_path)
    if self.data:
        self.fieldnames = list(self.data[0].keys())
    else:
        tk.messagebox.showerror("오류", "CSV 파일을 읽을 수 없습니다.")
        return

    # 파일 열기 버튼 비활성화 및 숨김
    self.open_btn.configure(state="disabled")
    self.open_btn.pack_forget()
    self.show_editor()


def clean_up(s: str) -> str:
    try:
        '''
        "["와 "]" 대괄호를 제거.
        한글/영문/언더바 뒤에 붙은 마침표 "."를 찾아서 제거.

        
        앞뒤 공백을 제거.
        정규식을 이용해 양 끝을 감싸고 있는 가장 바깥 괄호([, {, ()를 반복적으로 제거.
        중첩된 바깥 괄호도 모두 제거.
        끝에 붙은 마침표(.)나 쉼표(,)를 반복적으로 제거하고, 제거 후 남은 공백도 다시 정리.
        마지막으로 정리된 문자열을 반환.

        영문, 숫자, 언더바, 공백, 한글, 히라가나, 가타카나, 한자만 남기고 나머지 특수문자를 제거.
        처리 과정에서 예외가 발생하면 오류 메시지를 출력하고 None을 반환.
        '''
        s = s.strip()
        s = s.replace("[", "").replace("]", "")
        pattern = r"([가-힣a-zA-Z_])\."
        s = re.sub(pattern, r"\1", s)
        s = s.strip()


        s = s.strip()
        # 양 끝의 공백 포함, 가장 바깥 괄호들 반복 제거
        while re.match(r'^\s*[\[\{\(](.*)[\]\}\)]\s*$', s):
            s = re.sub(r'^\s*[\[\{\(](.*)[\]\}\)]\s*$', r'\1', s)
            s = s.strip(" \t\n\r")  # 중간에도 반복 제거
        s = s.strip()


        # 끝에 붙은 온점, 쉼표 제거
        while s and s[-1] in '.,':
            s = s[:-1].rstrip()

        return re.sub(
            r"[^\w\s\uAC00-\uD7A3\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", "", s
        )
    except Exception as e:
        print("clean_up e :", e)
        return None
    

api_key = os.getenv("OPENAI_API_KEY")
# --- exam_roller.py : ask_gpt()만 교체 ---------------------------------
def ask_gpt(question: str,model_name="gpt-4o-mini") -> str:
    try:
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": question}
        ]
        import openai
        response = openai.OpenAI(api_key=api_key).chat.completions.create(
            model=model_name,
            messages=messages,
        )
        return clean_up(response.choices[0].message.content)
    except Exception as e:
        print("ask_gpt e :", e)
        return None
    
def naver_dictionary_open(self=None, target="") :
    url = f"https://ja.dict.naver.com/#/search?query={target}"
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(get_chrome_path()))
    webbrowser.get('chrome').open(url)

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
