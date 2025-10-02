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

TASK_SUBJECT_LIST = ["hatsuon", "imi", "daily", "jlpt"]
GEN_TASK_SUBJECT_LIST = ["hatsuon", "imi"]


#GPT_MODEL = "gpt-4o-mini"
GPT_MODEL = "gpt-5-nano"

# 표준 라이브러리
import os
import re
import time
import subprocess
import json
import ast
import threading
from pathlib import Path
from urllib.parse import quote
from multiprocessing import Pool, cpu_count, Process, Manager

# 서드파티 라이브러리
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import openai



api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

def custom_print(var,color="gr",end="\n") :
    if color == "gr" :  print(f"\033[32m{str(var)}\033[0m",end=end)
    elif color == "or" : print(f"\033[38;5;208m{str(var)}\033[0m",end=end)
    elif color == "br" : print(f"\033[38;5;94m{str(var)}\033[0m",end=end)
    elif color == "re" : print(f"\033[31m{str(var)}\033[0m",end=end)
    elif color == "ye" : print(f"\033[33m{str(var)}\033[0m",end=end)
    elif color == "bl" : print(f"\033[34m{str(var)}\033[0m",end=end)


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
    elif prompt_type == "is_right_jlpt" : #is use in jlpt well
        return f"JLPT N2에 합격하기 위해 '{parts[0]}' 를 외워야 하는 중요도를 판별하라. 필수라면 3, 외우면 도움이 되지만 필수는 아니면 2, 전혀 필요 없다면 1을 출력하라. 출력은 반드시 숫자 하나만 한다."
    elif prompt_type == "is_right_daily" : #is use in daily well
        return f"'{parts[0]}'가 일본의 일상생활에서 자주 사용되는 글자인지 판별하라. 자주 사용된다면 1, 그렇지 않다면 0을 출력하라. 출력은 숫자 하나만 한다."
    

def is_kanji_word(word):
    return bool(re.fullmatch(r'[\u4E00-\u9FFF]{2,}', word))


def to_dict(lst):
    return dict([(i+1, v) for i, v in enumerate(lst)])

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
    
def only_number(s) :
    return re.sub(r"\D", "", s)
    

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

            t = clean_up(elements[0].text)
            end_keyword = "민중서림 엣센스 일한사전"
            t = t.split(end_keyword)[0]
            t_splited = t.split("\n")

            발음 = t_splited[0].split("[")[0].strip()
            발음 = 발음.replace(kan,"").strip()
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



def save_data(file_path, loaded_data):
    kanji_word = loaded_data["kanji_word"]
    kanji_hatsuon = loaded_data["kanji_hatsuon"]
    kanji_imi = loaded_data["kanji_imi"]

    is_jlpt_common = loaded_data["is_jlpt_common"]
    is_daily_common = loaded_data["is_daily_common"]

    with open(file_path, "w", encoding="utf-8") as f:
        for idx in kanji_word :
            item = {
                "kan": kanji_word[idx],
                "sound": kanji_hatsuon[idx],
                "mean": kanji_imi[idx],
                "is_jlpt_common": is_jlpt_common[idx],
                "is_daily_common": is_daily_common[idx]
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def load_data(file_path):
    kanji_word = []
    kanji_hatsuon = []
    kanji_imi = []
    is_hatsuon_good = []
    is_imi_good = []
    is_jlpt_common = []
    is_daily_common = []
    t=open(file_path,encoding="utf-8").read().splitlines()

    for i in t :
        try : 
            i = json.loads(i)
        except json.decoder.JSONDecodeError :
            i = ast.literal_eval(i)

        kanji_word.append(i["kan"])
        kanji_hatsuon.append(i["sound"])
        kanji_imi.append(i["mean"])

        try : is_hatsuon_good.append(i["is_done_sound"])
        except : pass
        try : is_imi_good.append(i["is_done_mean"])
        except : pass
        try : is_jlpt_common.append(i["is_jlpt_common"])
        except : pass
        try : is_daily_common.append(i["is_daily_common"])
        except : pass

    kanji_word = to_dict(kanji_word)
    kanji_hatsuon = to_dict(kanji_hatsuon)
    kanji_imi = to_dict(kanji_imi)
    is_hatsuon_good = to_dict(is_hatsuon_good)
    is_imi_good = to_dict(is_imi_good)
    is_jlpt_common = to_dict(is_jlpt_common)
    is_daily_common = to_dict(is_daily_common)

    result = {}
    result["kanji_word"] = kanji_word
    result["kanji_hatsuon"] = kanji_hatsuon
    result["kanji_imi"] = kanji_imi
    result["is_hatsuon_good"] = is_hatsuon_good
    result["is_imi_good"] = is_imi_good
    result["is_jlpt_common"] = is_jlpt_common
    result["is_daily_common"] = is_daily_common
    
    return result




def ask_gpt(
        question_dict, 
        question_idx, 
        question_subject, 
        result_dict, 
        need_only_number=True):

    global api_key
    global GPT_MODEL
    e = None
    for _ in range(1000):
        try:
            messages = [
                {"role": "system", "content": ""},
                {"role": "user", "content": question_dict[question_subject][question_idx]},
            ]
            response = openai.OpenAI(api_key=api_key).chat.completions.create(
                model=GPT_MODEL, messages=messages
                #, temperature=0.9
            )
            answer = response.choices[0].message.content
            
            answer = clean_up(answer)
            if need_only_number == True :
                #숫자만 반환
                answer = only_number(answer)

            result_dict[question_subject][question_idx] = answer
            return
        except Exception as e:
            custom_print(f"ask_gpt e : {e}",color="ye")
            if "429" in str(e) or "timeout" in str(e):
                time.sleep(60)
    return None

def get_tail(task_subject) :
    if task_subject in ["hatsuon", "imi"] : 
        return "_good"
    elif task_subject in ["jlpt","daily"] : 
        return "_common"


def validate_gpt_task(loaded_data) :
    
    is_good = {}
    task_dict = {}
    threads = []

    for task_subject in TASK_SUBJECT_LIST : 
        
        tail = get_tail(task_subject)
        is_good[task_subject] = {}
        task_dict[task_subject] = {}
        
        kanji_word_list = loaded_data[f"kanji_word"]

        for idx in kanji_word_list :
            kanji_target = loaded_data.get(f"kanji_{task_subject}",{}).get(idx,None)
            if task_subject in GEN_TASK_SUBJECT_LIST :
                if (not loaded_data[f"is_{task_subject}{tail}"].get(idx)) and \
                    kanji_target : #의미가 없으면, 물어보지도 않고 곧바로 False.
                    task_dict[task_subject][idx] = get_prompt(
                        f"is_right_{task_subject}",
                        [
                            kanji_word_list[idx],
                            kanji_target,
                        ]
                    )
                elif not kanji_target :
                    is_good[task_subject][idx] = False
            else : 
                task_dict[task_subject][idx] = get_prompt(f"is_right_{task_subject}",[kanji_word_list[idx]])

        for task_idx in task_dict[task_subject] :
            t = threading.Thread(target=ask_gpt, args=(
                task_dict,
                task_idx,
                task_subject,
                is_good,
                True
                ))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    gpt_task_result = {}
    gpt_task_result["is_good"] = is_good
    gpt_task_result["task_dict"] = task_dict



    return gpt_task_result


def generate_gpt_task(loaded_data) :
    task_dict = {}
    threads = []

    gpt_res = {}
    for task_subject in GEN_TASK_SUBJECT_LIST : 
        gpt_res[task_subject] = {}
        task_dict[task_subject] = {}
        is_good_dict = loaded_data[f"is_{task_subject}_good"]
        for idx in is_good_dict :
            if not is_good_dict[idx] :
                #if not good
                task_dict[task_subject][idx] = get_prompt(f"ask_{task_subject}",[loaded_data["kanji_word"][idx]])
            
        for idx in task_dict[task_subject] :
            t = threading.Thread(target=ask_gpt, args=(
                task_dict,
                idx,
                task_subject,
                gpt_res,
                False
                ))
            threads.append(t)
            t.start()
        

    for t in threads:
        t.join()
    
    return gpt_res

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
    else:
        print("파일 선택이 취소되었습니다.")


    print('MAIN_SOURCE_FILE_PATH :',MAIN_SOURCE_FILE_PATH)
    print('MAIN_MIDDLE_OUT_FILE_PATH :',MAIN_MIDDLE_OUT_FILE_PATH)
    print('MAIN_RESULT_FILE_PATH :',MAIN_RESULT_FILE_PATH)
    #
    near_word_scraper_main_func()
    tool_multi_scraper_kanji_main()
    #
    
    loaded_data = load_data(file_path=MAIN_MIDDLE_OUT_FILE_PATH)
    
    gpt_task_result = validate_gpt_task(loaded_data)


    for task_subject in TASK_SUBJECT_LIST :
        task_res = gpt_task_result["is_good"][task_subject]
        for idx in task_res :
            tail = get_tail(task_subject)
            gpt_res = int(task_res[idx])
            if task_subject in ["hatsuon", "imi", "daily"] :
                if gpt_res == 0 :
                    loaded_data[f"is_{task_subject}{tail}"][idx] = False
                elif gpt_res == 1 :
                    loaded_data[f"is_{task_subject}{tail}"][idx] = True

            elif task_subject == "jlpt" :
                loaded_data[f"is_{task_subject}{tail}"][idx] = gpt_res



    gpt_res = generate_gpt_task(loaded_data)

    for res_subject in gpt_res :
        for idx in gpt_res[res_subject] :
            loaded_data[f"kanji_{res_subject}"][idx] = gpt_res[res_subject][idx]

    save_data(
        MAIN_RESULT_FILE_PATH, 
        loaded_data
        )
    print("#"*88)


    


    
