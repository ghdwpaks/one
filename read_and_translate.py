import os
import tempfile
from gtts import gTTS
from playsound import playsound
import openai
import re

import threading

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
    

while True : 
    sentence = input(":")
    if sentence : 
        speak_japanese(sentence)
        
        threading.Thread(target=ask_gpt_translate, args=(sentence,), daemon=True).start()
        threading.Thread(target=ask_gpt_is_good, args=(sentence,), daemon=True).start()