dict_objects = [
{'k': '人', 's': 'じん·にん', 'm': 'ひと', 'p': '人', 'km': "인(간)"},
{'k': '日', 's': 'じつ·にち', 'm': 'か·ひ', 'p': '日', 'km': "일"},
{'k': '月', 's': 'がつ·げつ', 'm': 'つき', 'p': '月', 'km': "월"},
{'k': '年', 's': 'ねん', 'm': 'とし', 'p': '干', 'km': "년"},
{'k': '行', 's': 'ぎょう·こう·あん', 'm': 'いく·おこなう·ゆく', 'p': '行', 'km': "(향)하다, 가다"},
{'k': '出', 's': 'しゅつ·すい', 'm': 'だす·でる', 'p': '凵', 'km': "내다, 나가다"},
{'k': '言', 's': 'げん·ごん', 'm': 'いう·こと', 'p': '言', 'km': "말하다, 말"},
{'k': '上', 's': 'じょう·しょう', 'm': 'あがる·あげる·うえ·うわ·かみ·のぼる·のぼす·のぼせる', 'p': '一', 'km': "오르다, 위"},
{'k': '話', 's': 'わ', 'm': 'はなし·はなす', 'p': '言', 'km': "이야기(하다)"},
{'k': '見', 's': 'けん', 'm': 'みえる·みせる·みる', 'p': '見', 'km': "보(이)다"},
{'k': '続', 's': 'ぞく', 'm': 'つづく·つづける', 'p': '糸', 'km': "계속[하/되]다"},
{'k': '多', 's': 'た', 'm': 'おおい', 'p': '夕', 'km': "많다"},
{'k': '使', 's': 'し', 'm': 'つかう', 'p': '亻', 'km': "사용하다(쓰다)"},
{'k': '受', 's': 'じゅ', 'm': 'うかる·うける', 'p': '又', 'km': "받다"},
{'k': '中', 's': 'じゅう·ちゅう', 'm': 'なか', 'p': '丨', 'km': "안"},
{'k': '入', 's': 'にゅう', 'm': 'いる·いれる·はいる', 'p': '入', 'km': "들어가다, 넣다"},
{'k': '考', 's': 'こう', 'm': 'かんがえる', 'p': '耂', 'km': "생각하다"},
{'k': '新', 's': 'しん', 'm': 'あたらしい·あらた·にい', 'p': '斤', 'km': "새로운"},
{'k': '大', 's': 'たい·だい', 'm': 'おお·おおいに·おおきい', 'p': '大', 'km': "큰, 크다"},
{'k': '何', 's': 'か', 'm': 'なに·なん', 'p': '亻', 'km': "무슨"},
{'k': '取', 's': 'しゅ', 'm': 'とる', 'p': '又', 'km': "쥐다"},
{'k': '高', 's': 'こう', 'm': 'たか·たかい·たかまる·たかめる', 'p': '高', 'km': "높(이)다"},
{'k': '子', 's': 'し·す', 'm': 'こ', 'p': '子', 'km': "애(, 아이)"},
{'k': '国', 's': 'こく', 'm': 'くに', 'p': '口', 'km': "국(가)"},
{'k': '歳', 's': 'さい·せい', 'm': '', 'p': '止', 'km': "세(월)"},
{'k': '思', 's': 'し', 'm': 'おもう', 'p': '心', 'km': "생각"},
{'k': '対', 's': 'たい·つい', 'm': '', 'p': '寸', 'km': "대(답)"},
{'k': '始', 's': 'し', 'm': 'はじまる·はじめる', 'p': '女', 'km': "시작하(게되)다"},
{'k': '作', 's': 'さ·さく', 'm': 'つくる', 'p': '亻', 'km': "만들다"},
{'k': '増', 's': 'ぞう', 'm': 'ふえる·ふやす·ます', 'p': '土', 'km': "늘리(게되)다"},
{'k': '約', 's': 'やく', 'm': '', 'p': '糸', 'km': "약(속)"},
{'k': '今', 's': 'こん·きん', 'm': 'いま', 'p': '人', 'km': "(지)금"},
{'k': '述', 's': 'じゅつ', 'm': 'のべる', 'p': '辶', 'km': "말하다(고하다)"},
{'k': '調', 's': 'ちょう', 'm': 'しらべる·ととのう·ととのえる', 'p': '言', 'km': "조사하다, 갖추(어지)다"},
{'k': '少', 's': 'しょう', 'm': 'すくない·すこし', 'p': '小', 'km': "적다, 조금"},
{'k': '万', 's': 'まん·ばん', 'm': '', 'p': '一', 'km': "만"},
{'k': '分', 's': 'ぶ·ふん·ぶん', 'm': 'わかつ·わかる·わかれる·わける', 'p': '刀', 'km': "알(게되)다, 나누다, 가르다"},
{'k': '車', 's': 'しゃ', 'm': 'くるま', 'p': '車', 'km': "자동차"},
{'k': '前', 's': 'ぜん', 'm': 'まえ', 'p': '刂', 'km': "앞"},
{'k': '起', 's': 'き', 'm': 'おきる·おこす·おこる', 'p': '走', 'km': "일어나다, 일으키다"},
{'k': '売', 's': 'ばい', 'm': 'うる·うれる', 'p': '士', 'km': "팔(리)다"},
{'k': '時', 's': 'じ', 'm': 'とき', 'p': '日', 'km': "시(기), ~때"},
{'k': '金', 's': 'きん·こん', 'm': 'かな·かね', 'p': '金', 'km': "돈"},
{'k': '亡', 's': 'ぼう·もう', 'm': 'ない', 'p': '亠', 'km': "없다"},
{'k': '州', 's': 'しゅう', 'm': 'す', 'p': '川', 'km': "주(행정구역)"},
{'k': '来', 's': 'らい', 'm': 'くる·きたす·きたる', 'p': '木', 'km': "오다"},
{'k': '下', 's': 'か·げ', 'm': 'おりる·おろす·くださる·くだす·くだる·さがる·さげる·した·しも·もと', 'p': '一', 'km': "내리다, 아래"},
{'k': '決', 's': 'けつ', 'm': 'きまる·きめる', 'p': '氵', 'km': "정해지다, 정하다"},
{'k': '示', 's': 'じ·し', 'm': 'しめす', 'p': '示', 'km': "가리키다"},
{'k': '合', 's': 'かっ·がっ·ごう', 'm': 'あう·あわす·あわせる', 'p': '口', 'km': "합치다, 더하다"},
{'k': '男', 's': 'だん·なん', 'm': 'おとこ', 'p': '田', 'km': "남(성)"},
{'k': '込', 's': '', 'm': 'こむ·こめる', 'p': '辶', 'km': "복잡하다"},
{'k': '持', 's': 'じ', 'm': 'もつ', 'p': '扌', 'km': "가지다"},
{'k': '進', 's': 'しん', 'm': 'すすむ·すすめる', 'p': '辶', 'km': "나아가(게 시키)다"},
{'k': '引', 's': 'いん', 'm': 'ひく·ひける', 'p': '弓', 'km': "인(력), 끌다"},
{'k': '円', 's': 'えん', 'm': 'まるい', 'p': '冂', 'km': "둥글다"},
{'k': '強', 's': 'きょう·ごう', 'm': 'つよい·つよまる·つよめる·しいる', 'p': '弓', 'km': "강해지(게하)다"},
{'k': '明', 's': 'みょう·めい', 'm': 'あかす·あからむ·あかり·あかるい·あかるむ·あきらか·あく·あくる·あける', 'p': '日', 'km': "밝다"},
{'k': '初', 's': 'しょ', 'm': 'はじめ·はじめて·はつ·そめる·うい', 'p': '刀', 'km': "(최)초, 처음"},
{'k': '向', 's': 'こう', 'm': 'むかう·むく·むける·むこう', 'p': '口', 'km': "향하(게하)다"},
{'k': '同', 's': 'どう', 'm': 'おなじ', 'p': '口', 'km': "같다"},
{'k': '食', 's': 'しょく·じき', 'm': 'くう·たべる·くらう', 'p': '食', 'km': "먹다"},
{'k': '近', 's': 'きん', 'm': 'ちかい', 'p': '辶', 'km': "가깝다"},
{'k': '呼', 's': 'こ', 'm': 'よぶ', 'p': '口', 'km': "부르다"},
{'k': '位', 's': 'い', 'm': 'くらい', 'p': '亻', 'km': "~정도"},
{'k': '後', 's': 'ご·こう', 'm': 'あと·うしろ·のち·おくれる', 'p': '彳', 'km': "뒤, 나중"},
{'k': '氏', 's': 'し', 'm': 'うじ', 'p': '氏', 'km': "성(씨)"},
{'k': '乗', 's': 'じょう', 'm': 'のせる·のる', 'p': '丿', 'km': "(탑)승(하다)"},
{'k': '物', 's': 'ぶつ·もつ', 'm': 'もの', 'p': '牛', 'km': "물건"},
{'k': '広', 's': 'こう', 'm': 'ひろい·ひろがる·ひろげる·ひろまる·ひろめる', 'p': '广', 'km': "넓(어지)다"},
{'k': '次', 's': 'じ·し', 'm': 'つぎ·つぐ', 'p': '欠', 'km': "다음, 뒤를 잇다"},
{'k': '軍', 's': 'ぐん', 'm': '', 'p': '車', 'km': "군(대)"},
{'k': '開', 's': 'かい', 'm': 'あく·あける·ひらく·ひらける', 'p': '門', 'km': "열(리)다"},
{'k': '降', 's': 'こう', 'm': 'おりる·おろす·ふる', 'p': '阝左', 'km': "내리다"},
{'k': '伝', 's': 'でん', 'm': 'つたう·つたえる·つたわる', 'p': '亻', 'km': "전하다"},
{'k': '求', 's': 'きゅう', 'm': 'もとめる', 'p': '氺', 'km': "(요)구하다"},
{'k': '買', 's': 'ばい', 'm': 'かう', 'p': '貝', 'km': "사다"},
{'k': '水', 's': 'すい', 'm': 'みず', 'p': '水', 'km': "물"},
{'k': '家', 's': 'か·け', 'm': 'いえ·や', 'p': '宀', 'km': "집"},
{'k': '雨', 's': 'う', 'm': 'あま·あめ', 'p': '雨', 'km': "비"},
{'k': '億', 's': 'おく', 'm': '', 'p': '亻', 'km': "억"},
{'k': '止', 's': 'し', 'm': 'とまる·とめる', 'p': '止', 'km': "멈추(게하)다"},
{'k': '間', 's': 'かん·けん', 'm': 'あいだ·ま', 'p': '門', 'km': "사이"},
{'k': '生', 's': 'しょう·せい', 'm': 'いかす·いきる·いける·うまれる·うむ·なま·はえる·はやす·おう·き', 'p': '生', 'km': "생"},
{'k': '集', 's': 'しゅう', 'm': 'あつまる·あつめる·つどう', 'p': '隹', 'km': "모이다, 모으다"},
{'k': '米', 's': 'べい·まい', 'm': 'こめ', 'p': '米', 'km': "밥, 쌀"},
{'k': '店', 's': 'てん', 'm': 'みせ', 'p': '广', 'km': "가게"},
{'k': '含', 's': 'がん', 'm': 'ふくむ·ふくめる', 'p': '口', 'km': "포함하다, 포함시키다"},
{'k': '回', 's': 'かい·え', 'm': 'まわす·まわる', 'p': '口', 'km': "돌(리)다"},
{'k': '代', 's': 'たい·だい', 'm': 'かえる·かわる·よ·しろ', 'p': '亻', 'km': "대신하다"},
{'k': '変', 's': 'へん', 'm': 'かえる·かわる', 'p': '夂', 'km': "바꾸다, 바뀌다"},
{'k': '住', 's': 'じゅう', 'm': 'すまう·すむ', 'p': '亻', 'km': "살(게하)다"},
{'k': '私', 's': 'し', 'm': 'わたくし·わたし', 'p': '禾', 'km': "저"},
{'k': '関', 's': 'かん', 'm': 'かかわる·せき', 'p': '門', 'km': "관(계,되다)"},
{'k': '方', 's': 'ほう', 'm': 'かた', 'p': '方', 'km': "쪽, 편"},
{'k': '最', 's': 'さい', 'm': 'もっとも', 'p': '日', 'km': "가장 "},
{'k': '知', 's': 'ち', 'm': 'しる', 'p': '失', 'km': "알다"},
{'k': '終', 's': 'しゅう', 'm': 'おえる·おわる', 'p': '糸', 'km': "종(료)하다"},
{'k': '打', 's': 'だ', 'm': 'うつ', 'p': '扌', 'km': "치다"},
{'k': '立', 's': 'りつ·りゅう', 'm': 'たつ·たてる', 'p': '立', 'km': "서다, 세우다"},
]


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




'''
file_path = "captured_word_output.txt"
dict_objects = extract_dicts(file_path)
'''
print("dict_objects :",dict_objects)
print("type(dict_objects) :",type(dict_objects))

print("추출된 dict 객체 리스트:")

{'k': '立', 's': 'りつ·りゅう', 'm': 'たつ·たてる', 'p': '立', 'km': ''},



for i in range(len(dict_objects)):
    dict_objects[i]["kan"] = dict_objects[i]["k"]
    dict_objects[i]["sound"] = dict_objects[i]["s"]
    dict_objects[i]["meaning_sound"] = dict_objects[i]["m"]
    dict_objects[i]["mean"] = dict_objects[i]["km"]
    dict_objects[i]["is_good_sound"] = ""
    dict_objects[i]["is_good_mean"] = ""
    dict_objects[i]["edited_mean_selected"] = ""
    dict_objects[i]["edited_sound_selected"] = ""
    dict_objects[i]["edited_mean"] = dict_objects[i]["km"]
    dict_objects[i]["edited_sound"] = ""
    dict_objects[i]["original_mean_selected"] = ""
    dict_objects[i]["original_sound_selected"] = ""



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
    custom_print(dict_objects[i][f"meaning_sound"],color="or")

    pXO(dict_objects[i][f"is_good_{selected_type}"])
    custom_print(dict_objects[i][f"edited_{selected_type}"],color="bl")
    
    

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
        while True :
            try : 
                user_input = input(":")
                break
            except KeyboardInterrupt :
                continue

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

print("T,D,P,E")
for i in range(len(dict_objects)) :

    s = f"{dict_objects[i]['sound']}/{dict_objects[i]['meaning_sound']}"
    m = dict_objects[i]["edited_mean"]

    if '"' in m : m = f'\"{m}\"'
    if '"' in s : s = f'\"{s}\"'
    
    p = dict_objects[i]["p"]


    print(f"{dict_objects[i]['kan']},{m},{s},{p}")



# 표준 출력 복원
sys.stdout = original_stdout

# 버퍼 내용 가져오기
captured_word_output = buffer.getvalue()

# 저장
with open(f"{datetime.now().strftime("%H%M%S")}.csv", "w", encoding="utf-8") as f:
    f.write(captured_word_output)

print(f'출력 내용이 {datetime.now().strftime("%H%M%S")}.csv 에 저장되었습니다.')

