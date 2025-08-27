from __future__ import annotations
from __future__ import print_function
from pathlib import Path
import requests


import json
import multiprocessing as mp
from functools import partial
from todaii_extractor import atomic_json_write, file_lock, p, us, monitor
from copy import deepcopy as d 
THREAD_COUNT = 10


def is_in_list_single(url, json_urls):
    """json_urls 안에 없는 url만 반환"""
    if url not in json_urls:
        return url
    return None


BASE_DIR = Path(r"C:\\todaii")  # 또는 Path.home() / "AppData/Local/todaii"
BASE_DIR.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성
URL_JSON_DEFAULT_PATH = str(BASE_DIR / "todaii_urls.json")


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


def url_collector_cell(keyword):

    # API 요청
    api_url = "https://mazii.net/api/news/search"
    req_data = {"keyword": str(keyword), "limit": 99999, "type": "easy"}
    results = None
    try:
        response = requests.post(api_url, data=req_data, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
    except Exception as e:
        print("url_collector_cell error:", e)
        return

    # 추출된 URL 목록
    url_ids = [us(result.get("id")) for result in results if "id" in result]
    print("len(url_ids) :",len(url_ids))
    with file_lock(URL_JSON_DEFAULT_PATH):
        # 기존 JSON 로드
        with open(URL_JSON_DEFAULT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        json_urls = (
            data.get("viewed_url_list", [])
            + data.get("stage_url_list", [])
            + data.get("schedule_url_list", [])
        )

        # 멀티프로세싱으로 필터링
        with mp.Pool() as pool:
            result_list = pool.map(partial(is_in_list_single, json_urls=json_urls), url_ids)

        # None 제거 + 중복 제거
        result_list = list(set(filter(None, result_list)))

        # 결과 반영
        data["schedule_url_list"].extend(result_list)

        # 원자적 저장
        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

    p(f"url_collector_cell('{keyword}') collected {len(result_list)} new urls")




def run():
    global THREAD_COUNT
    
    processes = [mp.Process(target=url_collector_cell,args=(keyword,)) for keyword in range(THREAD_COUNT)]

    for p in processes:
        p.start()

    keyword = THREAD_COUNT + 1
    while True:
        for i in range(len(processes)):
            if not processes[i].is_alive():
                keyword = keyword + 1
                processes[i] = mp.Process(target=url_collector_cell,args=(keyword,))
                processes[i].start()
                print(keyword)




if __name__ == '__main__':

    
    mp.set_start_method("spawn")  # Windows 호환성 (fork 대신 spawn)
    first_setter()
    monitor_proc = mp.Process(target=monitor, daemon=True)
    monitor_proc.start()
    run()























