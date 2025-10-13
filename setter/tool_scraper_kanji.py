k = ["話","優","入"]
l = [

]

import re
import os

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_brackets(text):
    # 숫자와 점 다음에 오는 괄호를 처리하는 정규 표현식
    numbered_bracket_pattern = re.compile(r"\d+\.\s*\([^)]+\)")
    
    # 숫자와 점 다음에 오는 괄호를 일시적으로 보호하기 위한 플레이스홀더
    placeholders = {}
    
    # numbered_bracket_pattern에 해당하는 모든 부분을 찾아서 일시적으로 대체
    def protect_numbered_brackets(match):
        placeholder = f"PLACEHOLDER_{len(placeholders)}"
        placeholders[placeholder] = match.group(0)
        return placeholder
    
    # 보호할 괄호 부분 대체
    protected_text = numbered_bracket_pattern.sub(protect_numbered_brackets, text)
    
    # 보호하지 않은 일반 괄호 처리
    def replace(match):
        content = match.group(1)
        if re.fullmatch(r"[\uAC00-\uD7AF]{1,3}", content):
            return f"({content})"
        else:
            return ""

    result = re.sub(r"\(([^)]+)\)", replace, protected_text)
    
    # 보호했던 부분을 원래대로 복구
    for placeholder, original in placeholders.items():
        result = result.replace(placeholder, original)
    
    return result

def find_next_sentence(text, keyword, number=1):
    # 텍스트를 줄바꿈으로 분리하여 문장 리스트 생성
    sentences = text.split('\n')
    # 키워드가 포함된 문장을 찾고 다음 문장을 반환
    for i in range(len(sentences) - 1):
        if keyword in sentences[i]:
            return sentences[i + number]  # 다음 문장 반환
    return "키워드를 포함하는 문장이 없습니다."

 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

for kan in k :
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # 로그 레벨 최소화

    service = Service(log_output=subprocess.DEVNULL)  # 로그 숨김
    service = Service(log_output=subprocess.DEVNULL)
    os.environ['WDM_LOG'] = '0'
    driver = webdriver.Chrome(options=options, service=service)  # ChromeDriver 필요
    driver.get(f"https://ja.dict.naver.com/#/search?query={kan}&range=all")

    if len(kan) > 1 : 
        
        # 원하는 데이터 추출
        try : 
            elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
            )
        except TimeoutException :
            t = {"kan":kan,"sound":"","mean":""}
            print("ghdwpaks"*3,t)
            l.append(t)
            continue
        
        t = remove_brackets(elements[0].text)
        #한자, 발음, 뜻,
        end_keyword = "민중서림 엣센스 일한사전"
        t = t.split(end_keyword)[0]

        t_splited = t.split("\n")
        발음 = t_splited[0].split("[")[0].strip()
        
        
        뜻 = ""
        품사 = find_next_sentence(t, '단어장에 저장')
        뜻_부분 = find_next_sentence(t, '단어장에 저장', number=2)
        pattern = r'^\d+\.'
        if re.match(pattern, 뜻_부분):
            뜻_부분 = ""
            #뜻이 여러개
            
            뜻_시작_줄 = 0 
            for i in range(len(t_splited) - 1):
                if '단어장에 저장' in t_splited[i]:
                    i = i + 1
                    break


            뜻 += f""
            while True :
                i += 1
                if len(t_splited)-1 <= i   : break # -1 은 문단 뒤에 있는 '민중서림 엣센스 일한사전' 부분을 없애기 위해서이다.
                if re.match(pattern, t_splited[i]) : #숫자가 맞는지
                    뜻 += f"{t_splited[i]}".strip() # 숫자
                    i += 1
                    뜻 += f"{t_splited[i]}".strip().replace(".","")+" " # 의미
                else :
                    뜻 += f""
                    
                    continue #품사 기록하고 처음으로 돌아가기
                    
        else:
            #뜻이 한개
            뜻 = f"{뜻_부분}"

        t = {
            "kan":kan,
            "sound":발음,
            "mean":뜻.strip()
            }
        #print("*"*88,"\n","ghdwpaks"*3,t)
        print("ghdwpaks"*3,t)
        l.append(t)


    
    else : 




        elements = None
        # 원하는 데이터 추출
        try : 
            elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
            )
        except TimeoutException :
            t = {"k": kan, "s": "", "m": "", "p": ""}
            print("ghdwpaks"*3,t)
            l.append(t)
            continue


        # 원하는 데이터 추출
        #elements = driver.find_elements(By.CLASS_NAME, "addition_info")  # 클래스 이름을 변경해야 할 수 있음
        for element in elements:

            #단일글자라면
            t = {"k":kan,"s":"","m":"","p":""}

            # 줄 단위로 텍스트를 분리
            lines = element.text.strip().split("\n")

            # "음독"과 "훈독" 다음 줄의 내용을 추출하여 t 변수에 추가
            for i, line in enumerate(lines):
                if line == "음독" and i + 1 < len(lines):
                    t["s"] += lines[i + 1]  # 음독 다음 줄을 "s"에 추가
                elif line == "훈독" and i + 1 < len(lines):
                    t["m"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
                '''
                elif line == "부수" and i + 1 < len(lines):
                    t["p"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
                '''
                    
            print("ghdwpaks"*3,t)
            l.append(t)
            break

    driver.quit()

print(l)



