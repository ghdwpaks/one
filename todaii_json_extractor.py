from __future__ import annotations
from __future__ import print_function
MULTIPROCESSING_COUNT = 10
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import json
import multiprocessing as mp
from functools import partial
from todaii_extractor import atomic_json_write, file_lock, p, us, monitor
from copy import deepcopy as d 
import time
from multiprocessing import Manager

BASE_DIR = Path(r"C:\\todaii")  # 또는 Path.home() / "AppData/Local/todaii"
BASE_DIR.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성
URL_JSON_DEFAULT_PATH = str(BASE_DIR / "jsonform_todaii_urls.json")
DATA_JSON_DEFAULT_PATH = str(BASE_DIR / "jsonform_todaii_data.json")



URL_JSON_LOCK = None

def first_setter() :
    global URL_JSON_DEFAULT_PATH

    data = None
    with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["viewed_url_list"] = list(set(data["viewed_url_list"]))
    data["schedule_url_list"] = list(set(d(data["schedule_url_list"] + data["stage_url_list"])))

    data["stage_url_list"] = []

    data["schedule_url_list"] = list(set(data["schedule_url_list"]))

    for i in data["viewed_url_list"] :
        if i in data["schedule_url_list"] :
            #schedule_url_list 에서 'viewed_url_list 의 url' 제거
            data["schedule_url_list"] = [x for x in data["schedule_url_list"] if x != i]
            p("1",end="")


    atomic_json_write(URL_JSON_DEFAULT_PATH, data)
    #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)

def get_text(text) :
    if bool(re.search(r"<[^>]+>", text)) :
        soup = BeautifulSoup(text, "html.parser")
        for rt in soup.find_all("rt"):
            rt.decompose()
        return soup.get_text()
    else : 
        return text


def pop_news_id_from_schedule() :

    # stage 에서 꺼내고
    with file_lock(URL_JSON_DEFAULT_PATH):
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return_url = None
        try : 
            return_url = data['schedule_url_list'].pop()
        except IndexError as e :
            p("url_stage_and_pop IndexError e :",e)

        if not return_url : 
            return None
        
        data['stage_url_list'].append(return_url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)
        return return_url
    

def url_unusable(url) :
    global URL_JSON_DEFAULT_PATH
    with file_lock(URL_JSON_DEFAULT_PATH):
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if url in data['stage_url_list']:
            data['stage_url_list'].remove(url)
            data['unusable_url_list'].append(url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)


def url_viewed_and_pop(url) :
    global URL_JSON_DEFAULT_PATH
    with file_lock(URL_JSON_DEFAULT_PATH):
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if url in data['stage_url_list']:
            data['stage_url_list'].remove(url)
            data['viewed_url_list'].append(url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)


def safe_get_json(news_id, timeout=10, retries=19, retry_delay=10):
    url = f"https://api2.easyjapanese.net/api/news/get-list?news_id={news_id}&lang=ko&furigana=true"
    """
    요청 실패 시 일정 시간 뒤 재시도하는 JSON GET 함수
    """
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 400 and \
                resp.json()["message"] == "News not found" :
                    url_unusable(news_id)
                    return False
            
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            print(f"[Timeout] {attempt}/{retries}회 시도 실패. {retry_delay}초 후 재시도...")
        except requests.exceptions.RequestException as e:
            print(f"[Request error] {e} — 재시도 {attempt}/{retries}")
        time.sleep(retry_delay)

    # 모든 재시도 실패 시 None 반환 (혹은 raise)
    return None


def json_extractor_cell():
    news_id = pop_news_id_from_schedule()
    if not news_id:
        return
    
    url = f"https://api2.easyjapanese.net/api/news/get-list?news_id={news_id}&lang=ko&furigana=true"
    res = safe_get_json(news_id)
    if res == False : 
        return
    if not res : return
    print("news_id :",news_id)

    res_c = res["result"]["content"]
    res_g = res["result"]["grammar"]
    res_q = res["result"]["question"]
    res_v = res["result"]["vocabulary"]


    content = []
    grammar = []
    question = []
    vocabulary = []

    for i in res_c : 
        content.append(get_text(i['text']))

    for i in res_g : 
        grammar.append(get_text(i['content_new']))

    for i in res_q : 
        q_dict = {
            "q":get_text(i['question']),
            "a":[],
            "c":int(i['correctAnswer'])-1
        }
        answers = i['answers']
        for j in answers :
            q_dict["a"].append(get_text(j))
        question.append(q_dict)
        
    for i in res_v : 
        soup = BeautifulSoup(i['word'], "html.parser")

        # 각 ruby 태그 처리
        for ruby in soup.find_all("ruby"):
            rb = ruby.find("rb")
            rt = ruby.find("rt")
            if rb and rt:
                # rb 텍스트 대신 rt(후리가나) 사용
                ruby.replace_with(rt.get_text())
            else:
                ruby.unwrap()  # 안전 fallback
        
        sound = soup.get_text().strip()

        voc = {}
        voc["w"] = get_text(i['word']) #한자단어 word
        voc["s"] = sound #후리가나 sound
        voc["m"] = get_text(i['mean']) #뜻 mean
        voc["k"] = get_text(i['kind']) #문법구분 kind

        vocabulary.append(voc)

    with file_lock(DATA_JSON_DEFAULT_PATH):
        with open(DATA_JSON_DEFAULT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        default_content = data.get("content", [])
        default_grammar = data.get("grammar", [])
        default_question = data.get("question", [])
        default_vocabulary = data.get("vocabulary", [])




        # 집합 연산으로 중복 제거
        result_content = list(set(content) - set(default_content))
        result_grammar = list(set(grammar) - set(default_grammar))

        result_question = list(
            {json.dumps(q, ensure_ascii=False, sort_keys=True) for q in question}
            - {json.dumps(q, ensure_ascii=False, sort_keys=True) for q in default_question}
        )
        result_question = [json.loads(q) for q in result_question]

        
        result_vocabulary = list(
            {json.dumps(v, ensure_ascii=False, sort_keys=True) for v in vocabulary}
            - {json.dumps(v, ensure_ascii=False, sort_keys=True) for v in default_vocabulary}
        )
        result_vocabulary = [json.loads(v) for v in result_vocabulary]




        # 결과 반영
        data["content"].extend(result_content)
        data["grammar"].extend(result_grammar)
        data["question"].extend(result_question)
        data["vocabulary"].extend(result_vocabulary)

        atomic_json_write(DATA_JSON_DEFAULT_PATH, data)

    url_viewed_and_pop(news_id)







def run():
    global MULTIPROCESSING_COUNT
    
    processes = [mp.Process(target=json_extractor_cell) for _ in range(MULTIPROCESSING_COUNT)]

    for p in processes:
        p.start()

    while True:
        for i in range(len(processes)):
            if not processes[i].is_alive():
                processes[i] = mp.Process(target=json_extractor_cell,args=())
                processes[i].start()

def init_locks():
    global URL_JSON_LOCK
    manager = Manager()
    URL_JSON_LOCK = manager.Lock()




def monitor():
    
    while True:
        data = None
        try : 
            sch, sta, view, un, content_list, grammar_list, question_list, vocabulary_list = None, None, None, None, None, None, None, None


            with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)

                sch = len(data["schedule_url_list"])
                sta = len(data["stage_url_list"])
                view = len(data["viewed_url_list"])
                un = len(data["unusable_url_list"])


            with open(DATA_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)
                content_list = len(data["content"])
                grammar_list = len(data["grammar"])
                question_list = len(data["question"])
                vocabulary_list = len(data["vocabulary"])


            print(f"{sta}|{sch}|{view}|{un}||{content_list}|{grammar_list}|{question_list}|{vocabulary_list}")
        except PermissionError : pass

        time.sleep(1)


if __name__ == '__main__':
    mp.set_start_method("spawn")  # Windows 호환성 (fork 대신 spawn)
    init_locks()
    first_setter()
    monitor_proc = mp.Process(target=monitor, daemon=True)
    monitor_proc.start()
    run()























