# Enter를 누를 때마다 result에서 랜덤 콜로케 1개 출력(q로 종료)
import random

from setter.tools.code_tool_hide_cursor import nocur
from setter.tools.tool import ask_gpt, naver_dictionary_open
import threading

from tkinter.filedialog import askopenfilename
import ast
NEAR_INFO_FILE_PATH = askopenfilename(title="관련 정보 파일 선택", filetypes=[("All Files", "*.*")])

with open(NEAR_INFO_FILE_PATH, "r", encoding="utf-8") as f:
    text = f.read().strip()

data = ast.literal_eval(text)


# result 예: {"空": ["空港", "空を見"], "虫": ["虫を防ぐ"], "村": []}
# 이미 위에서 result가 만들어져 있다고 가정합니다.

# 비어있는 항목 제거
all_items = [(k, v) for k, vs in data.items() for v in vs]
if not all_items:
    print("결과가 비어 있습니다."); exit()

print("Enter=랜덤 콜로케, q=종료")

while True:
    random.shuffle(all_items)
    for T, result_t in all_items:
        print(result_t)
        while True :
            answer = nocur()
            if answer == "a" :
                results = {}
                
                def run_sound():
                    results["sound"] = ask_gpt(f"{result_t} の読み方をひらがなだけで出力してください。他の言葉を一切書かないでください。")

                def run_mean():
                    results["mean"] = ask_gpt(f"{result_t} 이 문장의 의미를 자연스러운 한국어 한 어구로 표현해. 단어를 나열하지 말고, 문맥상 어색하지 않은 간단한 표현으로만 출력해.")

                t1 = threading.Thread(target=run_sound)
                t2 = threading.Thread(target=run_mean)
                t1.start(); t2.start()
                t1.join(); t2.join()
                
                print(f'{T}')
                print(f'{results["sound"]}')
                print(f'{results["mean"]}')
                print('\n')
            elif answer == "z" : 
                naver_dictionary_open(target=T)
            else : 
                break
    print("Done"*88)