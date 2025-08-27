import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from todaii_extractor import atomic_json_write, file_lock, p
import json
import time
import multiprocessing as mp
from multiprocessing import Manager, Event
import orjson
from copy import deepcopy as d

from queue import Empty

import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000000 | 0x00000001 | 0x00000002
)
MULTIPROCESSING_COUNT = 50
def init_locks():
    global URL_JSON_LOCK
    manager = Manager()
    URL_JSON_LOCK = manager.Lock()



BASE_DIR = Path(r"C:\\todaii")  # 또는 Path.home() / "AppData/Local/todaii"
BASE_DIR.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성
URL_JSON_DEFAULT_PATH = str(BASE_DIR / "html_todaii_urls.json")
DATA_JSON_DEFAULT_PATH = str(BASE_DIR / "html_todaii_data.json")



URL_HEAD = "https://japanese.todaiinews.com/detail/"
THREAD_COUNT = 10



def first_setter() :
    global URL_JSON_DEFAULT_PATH

    data = None
    with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["viewed_url_list"] = list(set(data["viewed_url_list"]))
    data["schedule_url_list"] = list(set(
            d(data["schedule_url_list"] + data["stage_url_list"])
        ))

    data["stage_url_list"] = []

    data["schedule_url_list"] = list(set(data["schedule_url_list"]))

    for i in data["viewed_url_list"] :
        if i in data["schedule_url_list"] :
            #schedule_url_list 에서 'viewed_url_list 의 url' 제거
            data["schedule_url_list"] = [x for x in data["schedule_url_list"] if x != i]
            p("1",end="")


    atomic_json_write(URL_JSON_DEFAULT_PATH, data)
    #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)




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


                print(f"{sta}\t|{sch}|{view}|{un}||{content_list}")
            except PermissionError : pass

            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Monitor stopped")

def writer_process(queue, stop_signal, flush_signal):
    with open(DATA_JSON_DEFAULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_content = set(data.get("content", []))

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
                _flush(buffer, data, existing_content)
            break
        elif msg == flush_signal:
            # 50개마다 기록
            if buffer:
                _flush(buffer, data, existing_content)
                buffer.clear()
        else:
            buffer.append(msg)


def _flush(buffer, data, existing_content):
    for news_id, content in buffer:
        new_content = [c for c in content if c not in existing_content]

        if new_content:
            data.setdefault("content", []).extend(new_content)
            existing_content.update(new_content)

        url_viewed_and_pop(news_id)

    atomic_json_write(DATA_JSON_DEFAULT_PATH, data)


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
    

#================================================================================================================================================================================================================================================================================================================================================================================================================================================================        

def clean_japanese_text(raw_html: str) -> list[str]:
    soup = BeautifulSoup(raw_html, "html.parser")

    # rt 제거
    for rt in soup.find_all("rt"):
        rt.decompose()

    # <br> → 개행
    for br in soup.find_all("br"):
        br.replace_with("\n")

    # 텍스트 추출 (공백 최소화)
    text = soup.get_text("", strip=True)  # 구분자 없이 붙임
    text = re.sub(r"\s+", "", text)       # 불필요한 스페이스 제거

    # 문장 단위 분리 (。で区切る)
    sentences = re.split(r"(?<=[。！？])", text)
    return [s.strip() for s in sentences if s.strip()]



def url_unusable(url) :
    global URL_JSON_DEFAULT_PATH
    with file_lock(URL_JSON_DEFAULT_PATH):
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if url in data['stage_url_list']:
            data['stage_url_list'].remove(url)
            data['unusable_url_list'].append(url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

def fetch_article_clean(queue):
    try : 
        news_id = pop_news_id_from_schedule()
        url = f"https://japanese.todaiinews.com/detail/{news_id}?hl=en-US"
        response = requests.get(url, timeout=10)
        if not response.status_code == 200 :
            print("response.text :",response.text)
            url_unusable(news_id)
            return
        response.raise_for_status()

        css_path = (
            "body#body div.box-default.box-content-default "
            "div.row div#detail.col-md-9.no-pd-right.no-pd-mb "
            "div.box-detail div.content"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        soup
        content_div = soup.select_one(css_path)

        if content_div:
            content = clean_japanese_text(str(content_div))
            for s in content:
                p(s)

            
            queue.put((news_id, content))
    finally : 
        return
        





def run():
    limit = 50
    queue = mp.Queue()
    stop_signal = "__STOP__"
    flush_signal = "__FLUSH__"

    # writer 프로세스 시작
    writer = mp.Process(target=writer_process, args=(queue, stop_signal, flush_signal))
    writer.start()

    # 워커 프로세스 시작
    processes = [mp.Process(target=fetch_article_clean, args=(queue,))
                 for _ in range(MULTIPROCESSING_COUNT)]
    for p in processes:
        p.start()

    c = 0
    try:
        while True:
            for i in range(len(processes)):
                if not processes[i].is_alive():
                    # 워커 재시작
                    processes[i] = mp.Process(target=fetch_article_clean, args=(queue,))
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





    

if __name__ == '__main__':
    mp.set_start_method("spawn")  # Windows 호환성 (fork 대신 spawn)
    init_locks()
    first_setter()
    monitor_proc = mp.Process(target=monitor, daemon=True)
    monitor_proc.start()
    run()
