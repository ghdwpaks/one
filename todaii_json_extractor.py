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
from multiprocessing import Manager, Event
import httpx
import orjson
import sys
import ctypes
from queue import Empty
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000000 | 0x00000001 | 0x00000002
)
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

    with httpx.Client(timeout=timeout) as client:
        for attempt in range(1, retries + 1):
            try:
                resp = client.get(url)
                if resp.status_code == 400 and resp.json().get("message") == "News not found":
                    url_unusable(news_id)
                    return False
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                time.sleep(retry_delay)

    # --- 모든 재시도 실패 시 ---
    if retries >= 10:  
        # schedule_url_list 에 다시 넣기
        with file_lock(URL_JSON_DEFAULT_PATH):
            with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # stage 에 남아있으면 빼고 다시 schedule 로
            if news_id in data["stage_url_list"]:
                data["stage_url_list"].remove(news_id)
            data["schedule_url_list"].append(news_id)

            atomic_json_write(URL_JSON_DEFAULT_PATH, data)

        sys.exit(0)  # 해당 워커만 종료
    return None


def json_extractor_cell(queue):
    try:
        news_id = pop_news_id_from_schedule()
        if not news_id:
            return
        res = safe_get_json(news_id)
        if res is False or not res:
            return

        res_c = res["result"]["content"]
        res_g = res["result"]["grammar"]
        res_q = res["result"]["question"]
        res_v = res["result"]["vocabulary"]

        content = [get_text(i['text']) for i in res_c]
        grammar = [get_text(i['content_new']) for i in res_g]

        question = []
        for i in res_q: 
            q_dict = {
                "q": get_text(i['question']),
                "a": [get_text(j) for j in i['answers']],
                "c": int(i['correctAnswer'])-1
            }
            question.append(q_dict)

        vocabulary = []
        for i in res_v: 
            soup = BeautifulSoup(i['word'], "html.parser")
            for ruby in soup.find_all("ruby"):
                rb, rt = ruby.find("rb"), ruby.find("rt")
                if rb and rt:
                    ruby.replace_with(rt.get_text())
                else:
                    ruby.unwrap()
            sound = soup.get_text().strip()

            voc = {
                "w": get_text(i['word']),
                "s": sound,
                "m": get_text(i['mean']),
                "k": get_text(i['kind'])
            }
            vocabulary.append(voc)

        # 파일 쓰기 안 하고 writer 프로세스에게 전달
        queue.put((news_id, content, grammar, question, vocabulary))
    finally:
        return



def writer_process(queue, stop_signal, flush_signal):
    with open(DATA_JSON_DEFAULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    dumps = lambda obj: orjson.dumps(obj, option=orjson.OPT_SORT_KEYS).decode()
    loads = orjson.loads

    existing_content = set(data.get("content", []))
    existing_grammar = set(data.get("grammar", []))
    existing_question = {dumps(q) for q in data.get("question", [])}
    existing_vocab = {dumps(v) for v in data.get("vocabulary", [])}

    buffer = []  # 임시 버퍼

    while True:
        
        try : 
            msg = queue.get(timeout=1)
        except Empty:
            # 메시지가 없을 뿐이니 무시하고 다시 루프
            continue
        if msg == stop_signal:
            # 남은거 기록 후 종료
            if buffer:
                _flush(buffer, data, existing_content, existing_grammar,
                       existing_question, existing_vocab)
            break
        elif msg == flush_signal:
            # 50개마다 기록
            if buffer:
                _flush(buffer, data, existing_content, existing_grammar,
                       existing_question, existing_vocab)
                buffer.clear()
        else:
            buffer.append(msg)


def _flush(buffer, data, existing_content, existing_grammar,
           existing_question, existing_vocab):
    for news_id, content, grammar, question, vocabulary in buffer:
        new_content = [c for c in content if c not in existing_content]
        new_grammar = [g for g in grammar if g not in existing_grammar]
        new_question = [q for q in question if orjson.dumps(q, option=orjson.OPT_SORT_KEYS).decode() not in existing_question]
        new_vocab = [v for v in vocabulary if orjson.dumps(v, option=orjson.OPT_SORT_KEYS).decode() not in existing_vocab]

        if new_content:
            data.setdefault("content", []).extend(new_content)
            existing_content.update(new_content)
        if new_grammar:
            data.setdefault("grammar", []).extend(new_grammar)
            existing_grammar.update(new_grammar)
        if new_question:
            data.setdefault("question", []).extend(new_question)
            existing_question.update(orjson.dumps(q, option=orjson.OPT_SORT_KEYS).decode() for q in new_question)
        if new_vocab:
            data.setdefault("vocabulary", []).extend(new_vocab)
            existing_vocab.update(orjson.dumps(v, option=orjson.OPT_SORT_KEYS).decode() for v in new_vocab)

        url_viewed_and_pop(news_id)

    atomic_json_write(DATA_JSON_DEFAULT_PATH, data)



def run():
    limit = 50
    queue = mp.Queue()
    stop_signal = "__STOP__"
    flush_signal = "__FLUSH__"

    # writer 프로세스 시작
    writer = mp.Process(target=writer_process, args=(queue, stop_signal, flush_signal))
    writer.start()

    # 워커 프로세스 시작
    processes = [mp.Process(target=json_extractor_cell, args=(queue,))
                 for _ in range(MULTIPROCESSING_COUNT)]
    for p in processes:
        p.start()

    c = 0
    try:
        while True:
            for i in range(len(processes)):
                if not processes[i].is_alive():
                    # 워커 재시작
                    processes[i] = mp.Process(target=json_extractor_cell, args=(queue,))
                    processes[i].start()
                    c += 1

                    # 50개마다 flush 요청
                    if c >= limit:
                        queue.put(flush_signal)
                        c = 0
    except KeyboardInterrupt:
        print("KeyboardInterrupt - shutting down...")
        # 워커들 종료
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()

        # writer 종료
        queue.put(flush_signal)
        queue.put(stop_signal)
        writer.join()

        # 모니터 종료
        if monitor_proc.is_alive():
            monitor_proc.terminate()
    finally:
        # 종료 시 flush 및 writer stop 보장
        queue.put(flush_signal)
        queue.put(stop_signal)
        writer.join()

def init_locks():
    global URL_JSON_LOCK
    manager = Manager()
    URL_JSON_LOCK = manager.Lock()




def monitor():
    try : 
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


                print(f"{sta}\t|{sch}|{view}|{un}||{content_list}|{grammar_list}|{question_list}|{vocabulary_list}")
            except PermissionError : pass

            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Monitor stopped")


if __name__ == '__main__':
    mp.set_start_method("spawn")  # Windows 호환성 (fork 대신 spawn)
    init_locks()
    first_setter()
    monitor_proc = mp.Process(target=monitor, daemon=True)
    monitor_proc.start()
    run()







