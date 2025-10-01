import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path

MAIN_SOURCE_FILE_PATH = ""
MAIN_MIDDLE_OUT_FILE_PATH = "./temps/near_2_scraped_info.txt"
MAIN_RESULT_FILE_PATH = ""


#MAIN_SOURCE_FILE_PATH = "./temps/near_1_setter_target_data.txt"
#MAIN_MIDDLE_OUT_FILE_PATH = "./temps/near_2_scraped_info.txt"
#MAIN_RESULT_FILE_PATH = "./temps/near_3_info.txt"

# 공통
import os
import re
import time
import subprocess
from multiprocessing import Pool, cpu_count

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# scrape_from_file_titles.py 전용
from pathlib import Path
from urllib.parse import quote
from multiprocessing import Process, Manager
import requests

# tool_multi_scraper_kanji.py 전용
import json
import ast
import openai

import threading



api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

def get_prompt(prompt_type,parts) : 
    for i in range(len(parts)) :
        if not parts[i] : parts[i] = "없다"
    if prompt_type == "ask_imi" : 
        return f"'{parts[0]}'에 (여러 뜻이 있더라도,) '가장 일반적이고 주된 의미'을 한국어로 단 하나만 출력해. '다른 설명, 괄호, 따옴표, 문장'은 절대 붙이지 말고, 한글 단어만 출력해."
    elif prompt_type == "ask_hatsuon" : 
        return f"'{parts[0]}'의 발음을 히라가나로 출력해. '다른 설명, 괄호, 따옴표, 문장'은 절대 붙이지 말고, 히라가나만 출력해."
    elif prompt_type == "is_right_hatsuon" : 
        return f"'{parts[0]}'의 발음이 '{parts[1]}'이라는 주장이 있다. 맞으면 1, 틀리면 0. 숫자 하나만 출력해."
    elif prompt_type == "is_right_imi" : 
        return f"'{parts[0]}'의 의미가 '{parts[1]}'이라는 주장이 있다. 맞으면 1, 틀리면 0. 숫자 하나만 출력해."




def is_kanji_word(word):
    return bool(re.fullmatch(r'[\u4E00-\u9FFF]{2,}', word))

def remove_square_brackets(text: str) -> str:
    return re.sub(r"\[.*?\]", "", text)

def clean_up(s: str) -> str:
    try:
        text = s.replace("[", "").replace("]", "")
        pattern = r"([가-힣a-zA-Z_])\."
        replaced = re.sub(pattern, r"\1", text)
        replaced = remove_square_brackets(replaced)
        return re.sub(
            r"[^\w\s\uAC00-\uD7A3\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", "", replaced
        )
    except Exception as e:
        print("clean_up e :", e)
        return None
    
def fetch_page(query, page, headers):
    url = "https://kotobank.jp/search"
    params = {"q": query, "p": page}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print("fetch_page error:", e)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    dls = soup.select("section.searchSerp dl")
    if not dls:
        return []
    results = []
    for dl in dls:
        title_tag = dl.find("h4")
        if title_tag:
            title = title_tag.get_text(strip=True)
            if is_kanji_word(title):
                results.append(title)
    return results


def scrape_kotobank(query, max_pages=50):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    titles = set()
    for p in range(1, max_pages + 1):
        try:
            page_titles = fetch_page(query, p, headers)
            if not page_titles:
                break
            for t in page_titles:
                titles.add(t)
        except Exception as e:
            print("scrape_kotobank error:", e)
            continue
        time.sleep(0.5)
    return [t for t in sorted(titles) if len(t) < 5]


def extract_kanji_from_file(filepath):
    text = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    kanji_list = re.findall(r'[\u4E00-\u9FFF]', text)
    return sorted(set(kanji_list))


MAX_RETRIES = 10
RETRY_DELAY = 3


def driver_get(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    service = Service(log_output=subprocess.DEVNULL)
    os.environ["WDM_LOG"] = "0"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            driver = webdriver.Chrome(options=options, service=service)
            driver.get(url)
            return driver
        except Exception as e:
            print("[%d/%d] driver error: %s" % (attempt, MAX_RETRIES, e))
            if attempt == MAX_RETRIES:
                return None
            time.sleep(RETRY_DELAY)
    return None


def process_target(target):
    url = "https://jisho.org/search/%s%%20%%23words%%20%%23jlpt" % quote(target)
    driver = driver_get(url)
    if not driver:
        return []
    jlpt_words = []
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".concept_light.clearfix"))
        )
        entries = driver.find_elements(By.CSS_SELECTOR, ".concept_light.clearfix")
        for entry in entries:
            try:
                tags = entry.find_elements(By.CSS_SELECTOR, ".concept_light-tag.label")
                tag_texts = [t.text.lower() for t in tags]
                if any("jlpt" in t for t in tag_texts):
                    word = entry.find_element(By.CSS_SELECTOR, ".text").text.strip()
                    if word and target in word and len(word) > 1:
                        jlpt_words.append(word)
            except Exception:
                continue
    except TimeoutException:
        print("Timeout on:", target)
    except Exception as e:
        print("process_target error:", e)
    finally:
        driver.quit()
    return jlpt_words


def retry_wrapper(func, arg, max_attempts=30, delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(arg)
            return result
        except Exception as e:
            print("[attempt %d/%d] error on %s: %s" % (attempt, max_attempts, arg, e))
            time.sleep(delay)
    print("Max attempts reached for:", arg)
    return []


def safe_process_target(target):
    return retry_wrapper(process_target, target)


def safe_scrape_kotobank(k):
    return retry_wrapper(scrape_kotobank, k)


def run_jlpt(kanjis, pool_size, return_dict):
    with Pool(pool_size) as pool:
        jlpt_results = pool.map(safe_process_target, kanjis)
    result = []
    for r in jlpt_results:
        result.extend(r)
    print("JLPT result:", result)
    return_dict["jlpt"] = result


def run_kotobank(kanjis, pool_size, return_dict):
    with Pool(pool_size) as pool:
        kotobank_results = pool.map(safe_scrape_kotobank, kanjis)
    all_titles = []
    for r in kotobank_results:
        all_titles.extend(r)
    return_dict["kotobank"] = all_titles

def save_to_txt(final, filepath="./temps/near_words_result.txt"):
    
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(final, ensure_ascii=False))

    print("Results saved to", filepath)


def near_word_scraper_main_func() :
    global MAIN_SOURCE_FILE_PATH
    filepath = MAIN_SOURCE_FILE_PATH
    kanjis = extract_kanji_from_file(filepath)

    pool_size = max(2, cpu_count() // 2)
    manager = Manager()
    return_dict = manager.dict()

    # 두 시즌을 동시에 실행
    p1 = Process(target=run_jlpt, args=(kanjis, pool_size, return_dict))
    p2 = Process(target=run_kotobank, args=(kanjis, pool_size, return_dict))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    result = return_dict.get("jlpt", [])
    all_titles = return_dict.get("kotobank", [])

    final = list(set(result + all_titles))
    save_to_txt(final)


def remove_brackets(text):
    numbered_bracket_pattern = re.compile(r"\d+\.\s*\([^)]+\)")
    placeholders = {}

    def protect_numbered_brackets(match):
        placeholder = f"PLACEHOLDER_{len(placeholders)}"
        placeholders[placeholder] = match.group(0)
        return placeholder

    protected_text = numbered_bracket_pattern.sub(protect_numbered_brackets, text)

    def replace(match):
        content = match.group(1)
        if re.fullmatch(r"[\uAC00-\uD7AF]{1,3}", content):
            return f"({content})"
        else:
            return ""

    result = re.sub(r"\(([^)]+)\)", replace, protected_text)

    for placeholder, original in placeholders.items():
        result = result.replace(placeholder, original)

    return result


def find_next_sentence(text, keyword, number=1):
    sentences = text.split('\n')
    for i in range(len(sentences) - 1):
        if keyword in sentences[i]:
            return sentences[i + number]
    return ""


def scrape_kanji(kan):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    service = Service(log_output=subprocess.DEVNULL)
    os.environ['WDM_LOG'] = '0'
    driver = webdriver.Chrome(options=options, service=service)

    try:
        driver.get(f"https://ja.dict.naver.com/#/search?query={kan}&range=all")

        if len(kan) > 1:
            try:
                elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
                )
            except TimeoutException:
                return {"kan": kan, "sound": "", "mean": ""}

            t = remove_brackets(elements[0].text)
            end_keyword = "민중서림 엣센스 일한사전"
            t = t.split(end_keyword)[0]
            t_splited = t.split("\n")

            발음 = t_splited[0].split("[")[0].strip()
            #품사 = find_next_sentence(t, '단어장에 저장')
            뜻_부분 = find_next_sentence(t, '단어장에 저장', number=2)
            pattern = r'^\d+\.'
            뜻 = ""

            if re.match(pattern, 뜻_부분):
                뜻_시작_줄 = 0
                for i in range(len(t_splited) - 1):
                    if '단어장에 저장 優位' in t_splited[i]:
                        i = i + 1
                        break

                뜻 += f"[{t_splited[i]}] "
                while True:
                    i += 1
                    if len(t_splited) - 1 <= i:
                        break
                    if re.match(pattern, t_splited[i]):
                        뜻 += f"{t_splited[i]}".strip()
                        i += 1
                        뜻 += f"{t_splited[i]}".strip().replace(".", "") + " "
                    else:
                        padding = "" if 뜻[-1] == " " else " "
                        뜻 += f"{padding}/ [{t_splited[i]}] "
                        continue
            else:
                뜻 = re.sub(r"([가-힣a-zA-Z_])\.", r"\1", 뜻) # 문자+점 → 문자
                뜻 = 뜻.strip()

            return {"kan": kan, "sound": 발음, "mean": 뜻}

        else:
            try:
                elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
                )
            except TimeoutException:
                return {"k": kan, "s": "", "m": "", "p": ""}

            for element in elements:
                t = {"k": kan, "s": "", "m": "", "p": ""}
                lines = element.text.strip().split("\n")

                for i, line in enumerate(lines):
                    if line == "음독" and i + 1 < len(lines):
                        t["s"] += lines[i + 1]
                    elif line == "훈독" and i + 1 < len(lines):
                        t["m"] += lines[i + 1]
                    elif line == "부수" and i + 1 < len(lines):
                        t["p"] += lines[i + 1]
                return t

    finally:
        driver.quit()

def tool_multi_scraper_kanji_main():
    with open("./temps/near_words_result.txt", "r", encoding="utf-8") as f:
        content = f.read().strip()
        k = ast.literal_eval(content)  

    with Pool(cpu_count()) as pool:
        results = pool.map(scrape_kanji, k)

    with open(MAIN_MIDDLE_OUT_FILE_PATH, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Saved {len(results)} results to {MAIN_MIDDLE_OUT_FILE_PATH}")



def to_dict(lst):
    return dict([(i+1, v) for i, v in enumerate(lst)])

def cl(s):
    
    s = s.strip()
    # 양 끝의 공백 포함, 가장 바깥 괄호들 반복 제거
    while re.match(r'^\s*[\[\{\(](.*)[\]\}\)]\s*$', s):
        s = re.sub(r'^\s*[\[\{\(](.*)[\]\}\)]\s*$', r'\1', s)
    s = s.strip()

    # 끝에 붙은 온점, 쉼표 제거
    while s and s[-1] in '.,':
        s = s[:-1].rstrip()

    return s

def save_data(file_path, kanji_words, kanji_hatsuon, kanji_imi):
    with open(file_path, "w", encoding="utf-8") as f:
        for idx in kanji_words :
            item = {
                "kan": kanji_words[idx],
                "sound": kanji_hatsuon[idx],
                "mean": cl(kanji_imi[idx])
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def load_data(file_path):
    kanji_words = []
    kanji_hatsuon = []
    kanji_imi = []
    hatsuon_is_good = []
    imi_is_good = []
    t=open(file_path,encoding="utf-8").read().splitlines()

    for i in t :
        try : 
            i = json.loads(i)
        except json.decoder.JSONDecodeError :
            i = ast.literal_eval(i)

        kanji_words.append(i["kan"])
        kanji_hatsuon.append(i["sound"])
        kanji_imi.append(i["mean"])
        try :
            hatsuon_is_good.append(i["is_done_sound"])
        except : pass
        try :
            imi_is_good.append(i["is_done_mean"])
        except : pass

    kanji_words = to_dict(kanji_words)
    kanji_hatsuon = to_dict(kanji_hatsuon)
    kanji_imi = to_dict(kanji_imi)
    hatsuon_is_good = to_dict(hatsuon_is_good)
    imi_is_good = to_dict(imi_is_good)


    return kanji_words, kanji_hatsuon, kanji_imi, hatsuon_is_good, imi_is_good



def ask_gpt(question_dict: dict, question_idx: int, result_dict:dict, need_only_char:bool=True):
    global api_key
    e = None
    for _ in range(5):
        try:
            messages = [
                {"role": "system", "content": ""},
                {"role": "user", "content": question_dict[question_idx]},
            ]
            response = openai.OpenAI(api_key=api_key).chat.completions.create(
                model="gpt-4o-mini", messages=messages, temperature=0.9
            )
            answer = response.choices[0].message.content
            if need_only_char == True :
                #숫자도 포함되어 반환
                answer = clean_up(answer)
            result_dict[question_idx] = clean_up(response.choices[0].message.content)
            return
        except Exception as e:
            if "429" in str(e) or "timeout" in str(e):
                time.sleep(10)
            return None
    return None


def only_wants(dict_data,type="num"):
    sen = ""
    if type == "jp" :
        sen = r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
    elif type == "num" :
        sen = r'\D'
    
    for i in dict_data :
        dict_data[i] = re.sub(sen, '', dict_data[i])
    return dict_data

def df(d,dn):
    return
    print("*"*88)
    for i in d : print(f"{dn}[i] :",d[i])
    print("*"*88)

def is_korean(s) :
    # 문자열이 비었는지?
    if not s.strip():
        return False
    # 한글 포함 여부
    if re.search(r'[가-힣]', s):
        return True
    else:
        return False

if __name__ == "__main__":

    
    # Tkinter 기본 창 숨기기
    root = Tk()
    root.withdraw()

    # 1. 사용자에게 파일 선택
    MAIN_SOURCE_FILE_PATH = askopenfilename(title="원본 파일 선택", filetypes=[("All Files", "*.*")])

    if MAIN_SOURCE_FILE_PATH:
        # 2. 결과 파일 경로 생성 (_near.txt 붙이기)
        src_path = Path(MAIN_SOURCE_FILE_PATH)
        MAIN_RESULT_FILE_PATH = src_path.with_name(src_path.stem + "_near.txt")

        print("선택한 원본 파일:", MAIN_SOURCE_FILE_PATH)
        print("결과 파일 경로:", MAIN_RESULT_FILE_PATH)

    else:
        print("파일 선택이 취소되었습니다.")


    print('MAIN_SOURCE_FILE_PATH :',MAIN_SOURCE_FILE_PATH)
    print('MAIN_MIDDLE_OUT_FILE_PATH :',MAIN_MIDDLE_OUT_FILE_PATH)
    print('MAIN_RESULT_FILE_PATH :',MAIN_RESULT_FILE_PATH)


    near_word_scraper_main_func()
    tool_multi_scraper_kanji_main()
    
    kanji_words, kanji_hatsuon, kanji_imi, hatsuon_is_good, imi_is_good = load_data(file_path=MAIN_MIDDLE_OUT_FILE_PATH)

    
    
    threads = []
    checkout_hatsuon_tasks = {}
    gpt_is_good_hatsuon = {}

    for i in kanji_words :
        if not hatsuon_is_good.get(i) and \
            kanji_hatsuon[i] : #의미가 없으면, 물어보지도 않고 곧바로 False.
            checkout_hatsuon_tasks[i] = get_prompt(
                "is_right_hatsuon",
                [
                    kanji_words[i],
                    kanji_hatsuon[i],
                ]
            )
        elif not kanji_hatsuon[i] :
            hatsuon_is_good[i] = False

    df(checkout_hatsuon_tasks,"checkout_hatsuon_tasks")
    for task_number in checkout_hatsuon_tasks :
        t = threading.Thread(target=ask_gpt, args=(
            checkout_hatsuon_tasks,
            task_number,
            gpt_is_good_hatsuon,
            False
            ))
        threads.append(t)
        t.start()


    checkout_imi_tasks = {}
    gpt_is_good_imi = {}
    for i in kanji_words :
        if not imi_is_good.get(i) and\
            is_korean(kanji_imi[i]) : #의미가 없으면, 물어보지도 않고 곧바로 False.
            checkout_imi_tasks[i] = get_prompt(
                "is_right_imi",
                [
                    kanji_words[i],
                    kanji_imi[i]
                ]
            )
        elif not kanji_imi[i] :
            imi_is_good[i] = False
            
    df(checkout_imi_tasks,"checkout_imi_tasks")
    for task_number in checkout_imi_tasks :
        t = threading.Thread(target=ask_gpt, args=(
            checkout_imi_tasks,
            task_number,
            gpt_is_good_imi,
            False
            ))
        threads.append(t)
        t.start()


    for t in threads:
        t.join()

    #hatsuon_is_good = {}
    #imi_is_good = {}

    df(hatsuon_is_good,"hatsuon_is_good")
    for i in gpt_is_good_hatsuon : 
        try : 
            if int(gpt_is_good_hatsuon[i]) == 0 :
                hatsuon_is_good[i]=False
            elif int(gpt_is_good_hatsuon[i]) == 1 :
                hatsuon_is_good[i]=True
        except ValueError : 
            hatsuon_is_good[i] = False

    df(imi_is_good,"imi_is_good")
    for i in gpt_is_good_imi : 
        try : 
            if int(gpt_is_good_imi[i]) == 0 :
                imi_is_good[i]=False
            elif int(gpt_is_good_imi[i]) == 1 :
                imi_is_good[i]=True
        except ValueError : 
            imi_is_good[i] = False

    


    df(hatsuon_is_good,"hatsuon_is_good")
    df(imi_is_good,"imi_is_good")


    generate_hatsuon_tasks = {}
    gpt_hatsuon = {}
    for i in hatsuon_is_good :
        if hatsuon_is_good[i] == False:
            generate_hatsuon_tasks[i] = get_prompt("ask_hatsuon",[kanji_words[i]])
        
    df(generate_hatsuon_tasks,"generate_hatsuon_tasks")
    for task_number in generate_hatsuon_tasks :
        t = threading.Thread(target=ask_gpt, args=(
            generate_hatsuon_tasks,
            task_number,
            kanji_hatsuon
            ))
        threads.append(t)
        t.start()
        

    generate_imi_tasks = {}
    gpt_imi = {}
    for i in imi_is_good :
        if imi_is_good[i] == False:
            generate_imi_tasks[i] = get_prompt("ask_imi",[kanji_words[i]])
        
    df(generate_imi_tasks,"generate_imi_tasks")
    for task_number in generate_imi_tasks :
        t = threading.Thread(target=ask_gpt, args=(
            generate_imi_tasks,
            task_number,
            kanji_imi
            ))
        threads.append(t)
        t.start()
        

    for t in threads:
        t.join()

        
    for i in kanji_imi : 
        kanji_imi[i] = cl(kanji_imi[i])

    save_data(
        MAIN_RESULT_FILE_PATH, 
        kanji_words, 
        kanji_hatsuon, 
        kanji_imi
        )


    


    
