
import customtkinter as ctk
import webbrowser
import csv
import sys 
import pyperclip
import ctypes
import requests
from bs4 import BeautifulSoup
import webbrowser
import tempfile
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

MAX_RETRIES = 10
RETRY_DELAY = 2  # 초 단위

cpu_count = os.cpu_count() or 1
max_workers = min(32, cpu_count + 4)  # Python 기본값 공식
max_workers = max_workers // 2


class DevNull:
    def write(self, msg):
        pass
    def flush(self):
        pass

def k2u(kanji) :
    return f"{format(ord(kanji), '04X')}"


def driver_get(url) : 
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # 로그 레벨 최소화

    service = Service(log_output=subprocess.DEVNULL)  # 로그 숨김
    service = Service(log_output=subprocess.DEVNULL)
    os.environ['WDM_LOG'] = '0'



    for attempt in range(1, MAX_RETRIES + 1):
        try:
            driver = webdriver.Chrome(options=options, service=service)
            driver.get(url)
            break  # 성공 시 반복 종료
        except Exception as e:
            print(f"[{attempt}/{MAX_RETRIES}] 드라이버 실행/접속 실패: {e}")
            if attempt == MAX_RETRIES:
                raise  # 마지막 시도도 실패하면 예외 발생
            time.sleep(RETRY_DELAY)  # 재시도 전 대기
    return driver


class ExeMain : 

    def open_kanji_detail_by_unicoded_word(self, unicoded_word: str):
            """
            지정한 유니코드 한자(16진수)에 대한 jitenon 검색 결과 페이지에서
            class에 'ajax'와 'color1'이 모두 포함된 첫번째 <a>의 href로 이동
            """
            url = f"https://kanji.jitenon.jp/kousei/list?data={unicoded_word}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 요청 실패시 예외 발생

            soup = BeautifulSoup(response.text, "html.parser")
            result = []
            # 모든 <a> 태그 중 class에 ajax, color1 둘 다 포함된 첫번째 태그 찾기
            for a in soup.find_all("a"):
                class_list = a.get("class", [])
                if "color1" in class_list:
                    result.append(a.get_text(strip=True))
            
            return result




    def getCommonlyUsedKanji():
        app = ctk.CTk()
        app.title("한자 단어 출력")
        app.geometry("400x200")

        input_label = ctk.CTkLabel(app, text="한자 단어를 입력하세요:")
        input_label.pack(pady=(30, 10))

        entry = ctk.CTkEntry(app, width=200, font=("Arial", 18))
        entry.pack()

        output_label = ctk.CTkLabel(app, text="", font=("Arial", 24))
        output_label.pack(pady=(20, 10))

        result = {"word": None}  # 반환할 값 저장

        def show_kanji(event=None):
            word = entry.get().strip()
            result["word"] = word
            app.destroy()  # 창 닫기

        btn = ctk.CTkButton(app, text="출력", command=show_kanji)
        btn.pack(pady=(10, 0))

        def focus_next(event=None):
            btn.focus_set()
            return "break"

        entry.bind("<Return>", show_kanji)
        entry.bind("<Tab>", focus_next)

        app.mainloop()
        return result["word"]



class KanjiWordCollector : 

    def get_jlpt_words_from_jisho(self,kanji: str):
        
        driver = driver_get(f"https://jisho.org/search/{quote(kanji)}%20%23words%20%23jlpt")
        jlpt_words = []
        time.sleep(5)
        try : 
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.concept_light.clearfix'))
            )
            entries = driver.find_elements(By.CSS_SELECTOR, '.concept_light.clearfix')
            for idx, entry in enumerate(entries):
                jlpt_tags = entry.find_elements(By.CSS_SELECTOR, '.concept_light-tag.label')
                tag_texts = [tag.text.lower() for tag in jlpt_tags]
                if any('jlpt' in t for t in tag_texts):
                    try:
                        text_elem = entry.find_element(By.CSS_SELECTOR, '.text')
                        word = text_elem.text.strip()
                        if word:
                            jlpt_words.append(word)
                    except Exception as e:
                        pass
        finally : 
            driver.quit()

        return jlpt_words

    def remove_hiragana_if_not_multiple_kanji(word):
        # 한자(統一表記법) 범위: \u4e00-\u9fff
        kanji_count = len(re.findall(r'[\u4e00-\u9fff]', word))
        if kanji_count >= 2:
            return word
        # 히라가나, 가타카나 제거
        return re.sub(r'[ぁ-ゖァ-ヺ]+', '', word)



    def remove_hiragana_if_not_multiple_kanji(self,item):
        """
        입력값이 문자열이면 한 개만 처리, 리스트면 map 적용 후 리스트 반환.
        한자가 2개 이상이면 원본 반환,
        그렇지 않으면 히라가나(ぁ-ゖ) 및 가타카나(ァ-ヺ) 제거
        """
        def process(word):
            kanji_count = len(re.findall(r'[\u4e00-\u9fff]', word))
            if kanji_count >= 2:
                return word
            return re.sub(r'[ぁ-ゖァ-ヺ]+', '', word)
        if isinstance(item, str):
            return process(item)
        elif isinstance(item, list):
            return [process(w) for w in item]
        else:
            raise TypeError('입력값은 str 또는 list만 허용됩니다.')
        

    def main(self,kanji_list) : 
        result = []
        # 병렬 처리(스레드 수는 환경에 따라 조정, 너무 크면 CPU/RAM 과부하)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_kanji = {executor.submit(self.get_jlpt_words_from_jisho, kanji): kanji for kanji in kanji_list}
            for future in as_completed(future_to_kanji):
                kanji = future_to_kanji[future]
                try:
                    words = future.result()
                    result.extend(words)
                except Exception as exc:
                    print(f"[ERROR] {kanji} 처리 중 예외 발생:", exc)
        result = self.remove_hiragana_if_not_multiple_kanji(result)
        result = [word for word in result if len(word) >= 2]
        return result




class ScraperKanji : 
    def remove_brackets(self,text):
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

    def find_next_sentence(self,text, keyword, number=1):
        # 텍스트를 줄바꿈으로 분리하여 문장 리스트 생성
        sentences = text.split('\n')
        # 키워드가 포함된 문장을 찾고 다음 문장을 반환
        for i in range(len(sentences) - 1):
            if keyword in sentences[i]:
                return sentences[i + number]  # 다음 문장 반환
        return "키워드를 포함하는 문장이 없습니다."

    
    def ScraperMainFunction(self,kanji) :
        kan = kanji
                
        driver = driver_get(f"https://ja.dict.naver.com/#/search?query={kan}&range=all")

        time.sleep(5)  # 페이지 로드 대기

        if len(kan) > 1 : 
            
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'has-saving-function'))
            )

            # 원하는 데이터 추출
            elements = driver.find_elements(By.CLASS_NAME, "has-saving-function")
            
            t = self.remove_brackets(elements[0].text)
            #한자, 발음, 뜻,
            end_keyword = "민중서림 엣센스 일한사전"
            t = t.split(end_keyword)[0]

            t_splited = t.split("\n")
            발음 = t_splited[0].split("[")[0].strip()
            
            
            뜻 = ""
            품사 = self.find_next_sentence(t, '단어장에 저장')
            뜻_부분 = self.find_next_sentence(t, '단어장에 저장', number=2)
            pattern = r'^\d+\.'
            if re.match(pattern, 뜻_부분):
                뜻_부분 = ""
                #뜻이 여러개
                
                뜻_시작_줄 = 0 
                for i in range(len(t_splited) - 1):
                    if '단어장에 저장' in t_splited[i]:
                        i = i + 1
                        break


                뜻 += f"[{t_splited[i]}] "#품사
                while True :
                    i += 1
                    if len(t_splited)-1 <= i   : break # -1 은 문단 뒤에 있는 '민중서림 엣센스 일한사전' 부분을 없애기 위해서이다.
                    if re.match(pattern, t_splited[i]) : #숫자가 맞는지
                        뜻 += f"{t_splited[i]}".strip() # 숫자
                        i += 1
                        뜻 += f"{t_splited[i]}".strip().replace(".","")+" " # 의미
                    else :
                        padding = ""
                        if not 뜻[-1] == " " :
                            padding = " "
                        #품사가 있다는 의미
                        뜻 += f"{padding}/ [{t_splited[i]}] "#품사
                        
                        continue #품사 기록하고 처음으로 돌아가기
                        
            else:
                #뜻이 한개
                뜻 = f"[{품사}] {뜻_부분}"

            t = {
                "kan":kan,
                "sound":발음,
                "mean":뜻.strip()
                }
            #l.append(t)

        else : 
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'addition_info'))
            )

            # 원하는 데이터 추출
            elements = driver.find_elements(By.CLASS_NAME, "addition_info")  # 클래스 이름을 변경해야 할 수 있음
            for element in elements:

                #단일글자라면
                t = {"k":kan,"s":"","m":"","p":"","km":""}

                # 줄 단위로 텍스트를 분리
                lines = element.text.strip().split("\n")

                # "음독"과 "훈독" 다음 줄의 내용을 추출하여 t 변수에 추가
                for i, line in enumerate(lines):
                    if line == "음독" and i + 1 < len(lines):
                        t["s"] += lines[i + 1]  # 음독 다음 줄을 "s"에 추가
                    elif line == "훈독" and i + 1 < len(lines):
                        t["m"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
                    elif line == "부수" and i + 1 < len(lines):
                        t["p"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
                #l.append(t)

        driver.quit()
        return t


    def main(self, target_list) :
        result = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_kanji = {executor.submit(self.ScraperMainFunction, kanji): kanji for kanji in target_list}
            for future in as_completed(future_to_kanji):
                kanji = future_to_kanji[future]
                try:
                    words = future.result()
                    result.append(words)
                except Exception as exc:
                    print(f"[ERROR] {kanji} 처리 중 예외 발생:", exc)
            
            
        return result




class CsvExporter :

    def main(self,target_list,main_kanji_target) :
        target_type = ""
        l = target_list
        
        r = []
        header = None
        for i in l :
            try : 
                

                #단일 한자
                header = [["T","D","P","E"]]
                r.append([
                    i["k"],
                    i["km"],
                    f"{i["s"]}/{i["m"]}",
                    f"{i["p"]}"
                ])
            except : 
                
                #복수 한자로 이루어진 단어
                header = [["T","D","P"]]
                r.append([
                    i["kan"],
                    i["mean"],
                    i["sound"],
                    ""
                ]) 
                target_type = "w"


        rr = []


        # 슬라이싱 간격
        nn = 3
        step = int(len(r)/nn)+1 # 출력되는 파일 수량이 대충 nn 개
        step = 60  # 60개
        step = int(len(r)) # 전체를 한번에 다.

        for i in range(0, len(r), step): 
            rr.append(header + r[i:i + step - 1])




        for rr_loc in range(len(rr)) : 
            # 폴더 경로
            folder_path = CsvExporter.get_desktop_path()

            # 파일 이름
            file_name = f'{main_kanji_target}{target_type}.csv'

            # 폴더 생성
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 파일 경로
            file_path = os.path.join(folder_path, file_name)

            # CSV 저장
            with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)  # 최소한의 이스케이프 처리
                writer.writerows(rr[rr_loc])

            print(f"Data saved to {file_path}")
    
    def get_desktop_path():
        home = os.path.expanduser('~')
        if sys.platform == 'win32':
            return os.path.join(home, 'Desktop')
        elif sys.platform == 'darwin':
            return os.path.join(home, 'Desktop')
        else:
            # 리눅스의 경우 영어/한글 환경 모두 고려
            desktop = os.path.join(home, 'Desktop')
            if not os.path.exists(desktop):
                desktop = os.path.join(home, '바탕화면')
            return desktop

if __name__ == "__main__":
    
    

    '''
    
    scraperKanji = ScraperKanji()
    kanji_word_list_ops = scraperKanji.main(['優位'])
    print(kanji_word_list_ops)
    
    time.sleep(30)
    
    '''



    main_kanji_target = ExeMain.getCommonlyUsedKanji()
    main_kanji_unicode_target = k2u(main_kanji_target)
    print(main_kanji_unicode_target)
    
    kanji_list = ExeMain.open_kanji_detail_by_unicoded_word(
            self=None,
            unicoded_word=main_kanji_unicode_target
        )

    

    

    kanjiWordCollector = KanjiWordCollector()
    kanji_word_list = kanjiWordCollector.main(kanji_list)

    
    scraperKanji = ScraperKanji()
    kanji_list_ops = scraperKanji.main(kanji_list)
    kanji_word_list_ops = scraperKanji.main(kanji_word_list)

    csvExporter = CsvExporter()
    csvExporter.main(kanji_list_ops,main_kanji_target)
    csvExporter.main(kanji_word_list_ops,main_kanji_target)




    print("kanji_list :",kanji_list)
    print("kanji_word_list :",kanji_word_list)
    print("kanji_list_ops :",kanji_list_ops)
    print("kanji_word_list_ops :",kanji_word_list_ops)
    
    
