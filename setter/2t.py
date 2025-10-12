import os
import tempfile
from gtts import gTTS
from playsound import playsound
import openai
import re

import threading
import random; 


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

client = openai.OpenAI(api_key=api_key)

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
        raise ValueError("입력된 문장이 없습니다.")

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
        input()
    elif isinstance(target,list) :
        for cell in target :
            speak_japanese(cell)
            input()

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
#한자보이기
for i in t : 
    for j in range(t_len) :
        print_target_list = i[j].split("·")

        header = ""
        if j == 2 :
            header = "-"

        for k in print_target_list : 
            print(f"{header}{k}")
            input()
    print("\n\n")

'''

#음독보이기
for i in t : 
    target = i[2]

    if "·" in target :
        target = target.split("·")
        
    print(target)
    if not any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in target): 
        continue


    if isinstance(target,str) :
        speak_japanese(target)
        input()
    elif isinstance(target,list) :
        for cell in target :
            speak_japanese(cell)
            input()

'''


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
        input()
        print(td_cell["m"])
        input()
        print(td_cell["s"])
        print(td_cell["ss"])
        speak_japanese(td_cell["s"])
        input()
        print(td_cell["sm"])
        input()

    input()

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
        if input() == "1" : print(f'{td_cell["ws"]}\n{td_cell["m"]}')
        print()
        print(td_cell["s"])
        if input() == "1" : print(f'{td_cell["ss"]}\n{td_cell["sm"]}')
        print()
        print()
'''