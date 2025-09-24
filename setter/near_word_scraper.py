# file: scrape_from_file_titles.py
import re
import os
import time
import subprocess
from pathlib import Path
from urllib.parse import quote
from multiprocessing import Pool, cpu_count, Process, Manager

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# tool_multi_scraper_kanji.py
import re
import os
import time
import json
import subprocess
from multiprocessing import Pool, cpu_count

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import ast

def is_kanji_word(word):
    return bool(re.fullmatch(r'[\u4E00-\u9FFF]{2,}', word))


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
    filepath = "./temps/data.txt"
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

    with open("./temps/near_scraped_info.txt", "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Saved {len(results)} results to ./temps/near_scraped_info.txt")


if __name__ == "__main__":
    near_word_scraper_main_func()
    tool_multi_scraper_kanji_main()
    
