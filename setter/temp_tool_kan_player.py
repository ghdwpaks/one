import os
import tempfile
from gtts import gTTS
from playsound import playsound
import openai
import re

import threading
import random; 
import msvcrt

import ctypes
import sys

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

client = openai.OpenAI(api_key=api_key)


def hide_cursor():
    """Windows 콘솔 커서 숨기기"""
    class CONSOLE_CURSOR_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_int),
                    ("bVisible", ctypes.c_bool)]

    handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    cursor_info = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(cursor_info))
    cursor_info.bVisible = False
    ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

def show_cursor():
    """Windows 콘솔 커서 복원"""
    class CONSOLE_CURSOR_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_int),
                    ("bVisible", ctypes.c_bool)]

    handle = ctypes.windll.kernel32.GetStdHandle(-11)
    cursor_info = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(cursor_info))
    cursor_info.bVisible = True
    ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

def wait_key_no_cursor(prompt=""):
    """CMD에서 커서 깜빡임 없이 엔터 대기"""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    hide_cursor()
    try:
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):  # Enter 입력 시 종료
                break
    finally:
        show_cursor()
        print("", end="", flush=True)


def clean_up(s: str) -> str :
    try : 
        text = s.replace('[', '').replace(']', '')
        
        pattern = r'([가-힣a-zA-Z_])\.'
        replaced = re.sub(pattern, r'\1', text)
        print("replaced :",replaced)
        return replaced
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None

def speak_japanese(text: str, slow: bool = False):
    if not text.strip():
        print("[speak_japanese]:입력된 문장이 없습니다.")
        return 
    # 임시 mp3 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang="ja", slow=slow)
        tts.save(fp.name)
        temp_path = fp.name

    try:
        playsound(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except PermissionError:
            pass  # 재생 중이면 OS가 나중에 정리


def ask_gpt_translate(sentence: str) -> str:
    question = f"[{sentence}]의 한국어 뜻을 알려줘. 답변에는 오직 뜻만 포함하고, 부가 설명이나 다른 내용은 절대 포함하지 마. 대괄호 기호는 대답에서 제외해줘."
    try : 
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9
        )
        print(response.choices[0].message.content,end="\n:")
        #return clean_up(response.choices[0].message.content)
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None



def ask_gpt_is_good(sentence: str) -> str:
    question = f"[{sentence}]가 정상적인지 아닌지 🟢 와 🔴 중에 하나로 알려줘. 답변에는 이 글자들 중 단 하나만 출력 가능하고, 부가 설명이나 다른 내용은 절대 포함하지 마."
    try : 
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9
        )
        print(response.choices[0].message.content,end="\n:")

        #return clean_up(response.choices[0].message.content)
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None
    

def target_getter(target) :
    
    if "·" in target :
        target = target.split("·")
        
    

    if isinstance(target,str) :
        print(target)
    elif isinstance(target,list) :
        for cell in range(len(target)) :
            print(target[cell],end="")
            if not cell == len(target) - 1 :
                print("",end=" , ")


    if isinstance(target,str) and \
        not any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in target): 
        return True


    if isinstance(target,str) :
        speak_japanese(target)
        wait_key_no_cursor()
    elif isinstance(target,list) :
        for cell in target :
            speak_japanese(cell)
            wait_key_no_cursor()

td = {
    "kun":{
        "早": {"はやい": "早い","はやまる": "早まる","はやめる": "早める"},
        "天": {"あま": "天","あめ": "天"},
        "入": {"いる": "入る","いれる": "入れる","はいる": "入る"},
        "木": {"き": "木","こ": "木"},
        "目": {"め": "目","ま": "目"},
        "下": {"おりる": "下りる","おろす": "下ろす","くださる": "下さる","くだす": "下す","くだる": "下る","さがる": "下がる","さげる": "下げる","した": "下","しも": "下","もと": "下"},
        "空": {"あく": "空く","あける": "空ける","から": "空","そら": "空"},
        "上": {"あがる": "上がる","あげる": "上げる","うえ": "上","うわ": "上","かみ": "上","のぼる": "上る","のぼす": "上す","のぼせる": "上せる"},
        "正": {"ただしい": "正しい","ただす": "正す","まさ": "正"},
        "生": {"いかす": "生かす","いきる": "生きる","いける": "生ける","うまれる": "生まれる","うむ": "生む","なま": "生","はえる": "生える","はやす": "生やす","おう": "生う","き": "生"},
        "青": {"あお": "青","あおい": "青い"},
        "赤": {"あか": "赤","あかい": "赤い","あからむ": "赤らむ","あからめる": "赤らめる"}
    },
    "imi": {
        "早": {"はやい": "빠르다","はやまる": "성급해지다","はやめる": "앞당기다"},
        "天": {"あま": "하늘","あめ": "비"},
        "入": {"いる": "들어가다","いれる": "넣다","はいる": "들다"},
        "木": {"き": "나무","こ": "N"},
        "目": {"め": "눈","ま": "N"},
        "下": {"おりる": "내려오다","おろす": "내리다","くださる": "주시다","くだす": "내리다","くだる": "내려가다","さがる": "내려가다","さげる": "내리다","した": "아래","しも": "아래","もと": "밑"},
        "空": {"あく": "비다","あける": "비우다","から": "비어 있다","そら": "하늘"},
        "上": {"あがる": "오르다","あげる": "올리다","うえ": "위","うわ": "위","かみ": "위","のぼる": "올라가다","のぼす": "올리다","のぼせる": "올리다"},
        "正": {"ただしい": "옳다","ただす": "바로잡다","まさ": "바름·정직"},
        "生": {"いかす": "살리다","いきる": "살다","いける": "살다","うまれる": "태어나다","うむ": "낳다","なま": "생","はえる": "나다","はやす": "기르다","おう": "N","き": "살아 있는 것"},
        "青": {"あお": "푸르다","あおい": "푸르다"},
        "赤": {"あか": "붉다","あかい": "붉다","あからむ": "붉어지다","あからめる": "붉히다"}
    }
}

t = [
["千",'せん','ち','천'],
["川",'せん','かわ','강'],
["先",'せん','さき','앞'],
["早",'そう·さっ','はやい·はやまる·はやめる','이르다'],
["草",'そう','くさ','풀'],
["村",'そん','むら','마을'],
["竹",'ちく','たけ','대나무'],
["虫",'ちゅう','むし','벌레'],
["町",'ちょう','まち','읍·거리'],
["天",'てん','あま·あめ','하늘'],
["田",'でん','た','논'],
["土",'と·ど','つち','흙'],
["入",'にゅう','いる·いれる·はいる','들어가다'],
["年",'ねん','とし','해'],
["百",'ひゃく','','백'],
["文",'ぶん·もん','ふみ','글'],
["木",'ぼく·もく','き·こ','나무'],
["本",'ほん','もと','책·근본'],
["名",'みょう·めい','な','이름'],
["目",'もく·ぼく','め·ま','눈'],
["林",'りん','はやし','숲'],
]


random.shuffle(t)

t_len = 4




'''
#한자보이기
for i in t : 
    dont_need_imi = False
    for j in range(t_len) :
        print_target_list = i[j].split("·")

        header = ""
        if j == 2 :
            header = "-"

        for k in print_target_list : 
            if header :
                if len(print_target_list) > 1 : 
                    print(f"{header}{k}")
                    speak_japanese(k)
                    wait_key_no_cursor()
                    print(f"{td["imi"][i[0]][k]}")
                    print()
                    dont_need_imi = True
                else : 
                    print(f"{header}{k}")
                    speak_japanese(k)
                
            else :
                if dont_need_imi and j == 3 :
                    pass
                else : 
                    print(f"{k}")
            wait_key_no_cursor()
    print("\n\n\n\n")

'''

#음독보이기
for i in t : 
    target = i[2]

    if "·" in target :
        target = target.split("·")
        
    if not any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in target): 
        continue


    if isinstance(target,str) :
        print(target)
        speak_japanese(target)
        wait_key_no_cursor()
    elif isinstance(target,list) :
        for cell in target :
            print(cell)
            speak_japanese(cell)
            wait_key_no_cursor()

    print("\n\n")



'''
#한자보고 음독맞추기
for i in range(len(t)) : 
    target = t[i][0]
    

    print(target)

    td_l = td[target]["e"]
    for td_cell in td_l :
        #w,ws,m,s,ss
        print(td_cell["w"])
        print(td_cell["ws"])
        speak_japanese(td_cell["w"])
        wait_key_no_cursor()
        print(td_cell["m"])
        wait_key_no_cursor()
        print(td_cell["s"])
        print(td_cell["ss"])
        speak_japanese(td_cell["s"])
        wait_key_no_cursor()
        print(td_cell["sm"])
        wait_key_no_cursor()

    wait_key_no_cursor()

    target_getter(t[i][1])
    target_getter(t[i][2])

'''

        



'''
#한자보고 음독맞추기
for i in range(len(t)) : 
    target = t[i][0]
    
    td_l = td[target]["e"]
    for td_cell in td_l :
        print(td_cell["w"])
        if wait_key_no_cursor() == "1" : print(f'{td_cell["ws"]}\n{td_cell["m"]}')
        print()
        print(td_cell["s"])
        if wait_key_no_cursor() == "1" : print(f'{td_cell["ss"]}\n{td_cell["sm"]}')
        print()
        print()
'''