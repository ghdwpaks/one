# file: extract_braces_to_dict.py
import re
import ast
import msvcrt
import os
import sys
import io
import time
import webbrowser
import platform
import shutil
from datetime import datetime
import pyperclip
import builtins
import ctypes


def extract_braces_as_dicts(file_path: str) -> list[dict]:
    """
    Extracts each { ... } block from a file and converts it into a dictionary.
    Expected format inside braces: key:value, key2:value2
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 중괄호 안의 내용 추출
    brace_contents = re.findall(r"\{(.*?)\}", text, flags=re.DOTALL)

    dict_list = []
    for content in brace_contents:
        # key:value 쌍 분리 (쉼표 기준)
        pairs = [pair.strip() for pair in content.split(",") if ":" in pair]
        obj_dict = {}
        for pair in pairs:
            key, value = pair.split(":", 1)
            obj_dict[key.strip()] = value.strip()
        dict_list.append(obj_dict)

    return dict_list

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



def extract_dicts(file_path: str) -> list[dict]:
    """
    Reads a file, extracts {...} blocks, and converts each to a Python dict.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # { ... } 블록 추출 (줄바꿈 포함 가능)
    brace_blocks = re.findall(r"\{.*?\}", text, flags=re.DOTALL)

    dict_list = []
    for block in brace_blocks:
        try:
            # 안전하게 문자열을 Python 객체로 변환
            obj = ast.literal_eval(block)
            if isinstance(obj, dict):
                dict_list.append(obj)
        except Exception as e:
            print(f"변환 실패: {block[:50]}... ({e})")

    return dict_list


def hide_cursor():
    class CONSOLE_CURSOR_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_int),
                    ("bVisible", ctypes.c_bool)]

    hStdOut = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
    cursor_info = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(hStdOut, ctypes.byref(cursor_info))
    cursor_info.bVisible = False  # 커서 숨기기
    ctypes.windll.kernel32.SetConsoleCursorInfo(hStdOut, ctypes.byref(cursor_info))


def custom_print(var,color="gr",end="\n") :
    if color == "gr" :  print(f"\033[32m{str(var)}\033[0m",end=end)
    elif color == "or" : print(f"\033[38;5;208m{str(var)}\033[0m",end=end)
    elif color == "br" : print(f"\033[38;5;94m{str(var)}\033[0m",end=end)
    elif color == "re" : print(f"\033[31m{str(var)}\033[0m",end=end)
    elif color == "ye" : print(f"\033[33m{str(var)}\033[0m",end=end)
    elif color == "bl" : print(f"\033[34m{str(var)}\033[0m",end=end)

def pXO(is_good) :
    if is_good :
        custom_print("O",color="bl",end=" ")
    else : 
        custom_print("X",color="re",end=" ")
def custom_cls() :
    print("\n\n\n")
    os.system('cls')




dict_objects = None

file_path = "captured_output.txt"
dict_objects = extract_dicts(file_path)
print("dict_objects :",dict_objects)
print("type(dict_objects) :",type(dict_objects))

print("추출된 dict 객체 리스트:")
for i in range(len(dict_objects)):
    dict_objects[i]["original_mean_selected"] = None
    dict_objects[i]["original_sound_selected"] = None



hide_cursor()
custom_cls()

i = 0
selected_type = "mean"
last_key = ""
while True : 
    if i >= len(dict_objects) : 
        if selected_type == "mean" :
            selected_type = "sound"
            i = 0
        else : 
            break
    
    
    
    
    if dict_objects[i][f"{selected_type}"] == dict_objects[i][f"edited_{selected_type}"] and \
        not last_key == "a": 
        i += 1 ; continue


    
    print(dict_objects[i]["kan"])
    custom_print(dict_objects[i][f"{selected_type}"],color="ye")

    pXO(dict_objects[i][f"is_good_{selected_type}"])
    custom_print(dict_objects[i][f"edited_{selected_type}"],color="br")
    
    

    last_key = msvcrt.getwch()  # 입력이 올 때까지 대기
    if last_key == "w":
        dict_objects[i][f"original_{selected_type}_selected"] = True
    elif last_key == "s":
        dict_objects[i][f"original_{selected_type}_selected"] = False
    elif last_key == "a":
        
        
        i = i - 1
        
        
        
        
        if selected_type == "sound" and i <= -1: 
            i = len(dict_objects) - 1
            
            selected_type = "mean"
            
        custom_cls()
        continue
    elif last_key == "d" or \
        last_key == " ":
        pass
    elif last_key == "e":
        pyperclip.copy(f"{dict_objects[i]["kan"]}")
        custom_cls()
        continue
    elif last_key == "f" or last_key == ":" or last_key == ";":
        
        user_input = input(":")
        dict_objects[i][f"edited_{selected_type}"] = user_input
        dict_objects[i][f"original_{selected_type}_selected"] = False
        i += 1
        custom_cls()
        continue
    elif last_key == "=":
        break
    elif last_key == "q" :
        
        url = f"https://ja.dict.naver.com/#/search?query={dict_objects[i]["kan"]}"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(get_chrome_path()))
        webbrowser.get('chrome').open(url)
        custom_cls()
        continue
    
    custom_cls()
    i += 1

# 표준 출력 백업
original_stdout = sys.stdout

# 메모리 버퍼 생성
buffer = io.StringIO()
sys.stdout = buffer  # 출력 내용을 버퍼에 저장

custom_cls()

print("T,D,P")
for i in dict_objects :

    s = i['edited_sound']
    if i['original_sound_selected'] :
        s = i["sound"]

    m = i['edited_mean']
    if i['original_mean_selected'] :
        m = i["mean"]

    if '"' in m : m = f'\"{m}\"'
    if '"' in s : s = f'\"{s}\"'
    
    print(f"{i['kan']},{m},{s}")



# 표준 출력 복원
sys.stdout = original_stdout

# 버퍼 내용 가져오기
captured_output = buffer.getvalue()

# 저장
with open(f"z_out{datetime.now().strftime("%H%M%S")}.csv", "w", encoding="utf-8") as f:
    f.write(captured_output)

print(f'출력 내용이 z_out{datetime.now().strftime("%H%M%S")}.csv 에 저장되었습니다.')
