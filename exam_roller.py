from __future__ import annotations
SOURCE_FILE_CSV_PATH = "z_out175734_1_20.csv"







import os
import re

import pandas as pd
import threading
from copy import deepcopy as d

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import msvcrt

import json
from filelock import FileLock
from threading import Lock
import subprocess

import ctypes
import sys


# ===== 1) DiversitySamplerSync 추가 (임포트 아래 아무 곳) =====
import math
from difflib import SequenceMatcher
from collections import defaultdict, Counter

import os, random, time
from dataclasses import dataclass
from typing import Optional, Protocol

class DiversitySamplerSync:
    """
    프롬프트/도메인 독립. 후보 다중 생성 + MMR 선택 + 키별 메모리.
    동기(OpenAI sync)로 동작해서 현재 스레드 구조에 바로 맞물림.
    """
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.OpenAI = OpenAI
        self.client = self.OpenAI(api_key=api_key)
        self.model = model
        self.memory = defaultdict(list)  # key -> 최근 채택 결과들

        # 샘플링 공간(가벼운 가변화를 통해 시드 분산)
        self.t_low, self.t_high = 0.75, 1.05
        self.pp_low, self.pp_high = 0.3, 0.8
        self.fp_low, self.fp_high = 0.5, 0.9
        self.top_p = 1.0
        self.max_tokens = 128
        self.candidates = 4     # 후보 m개 생성
        self.mmr_alpha = 0.65   # 품질:다양성 가중
        self.ngram_n = 3
        self.memory_size = 64

    def _score_quality(self, s: str) -> float:
        L = len(s)
        if L < 8: return 0.2
        if L > 120: return 0.4
        q = 0.6 + (0.2 if s.endswith(("。",".","!","?")) else 0.0)
        punct = sum(1 for ch in s if ch in "\"'`[]{}()")
        q -= min(0.3, punct * 0.03)
        return max(0.0, min(1.0, q))

    def _ngram_counts(self, s: str, n: int) -> Counter:
        s = s.strip()
        return Counter([s[i:i+n] for i in range(max(0, len(s)-n+1))])

    def _overlap_ratio(self, a: str, b: str, n: int) -> float:
        ca, cb = self._ngram_counts(a, n), self._ngram_counts(b, n)
        if not ca or not cb: return 0.0
        inter = sum((ca & cb).values())
        denom = min(sum(ca.values()), sum(cb.values()))
        return inter/denom if denom else 0.0

    def _mem_penalty(self, key: str, text: str) -> float:
        hist = self.memory.get(key, [])[-self.memory_size:]
        if not hist: return 0.0
        ng = [self._overlap_ratio(text, h, self.ngram_n) for h in hist]
        sim = [SequenceMatcher(None, text, h).ratio() for h in hist]
        return (sum(ng)/len(ng))*0.6 + (sum(sim)/len(sim))*0.4

    def _one_candidate(self, system: str, user: str) -> str:
        import random, time
        # 마이크로 지터: 병렬 동시 도달 분산
        time.sleep(random.uniform(0.008, 0.04))
        t  = random.uniform(self.t_low,  self.t_high)
        pp = random.uniform(self.pp_low, self.pp_high)
        fp = random.uniform(self.fp_low, self.fp_high)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role":"system","content":system},
                      {"role":"user","content":user}],
            temperature=t, top_p=self.top_p,
            presence_penalty=pp, frequency_penalty=fp,
            max_tokens=self.max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def generate(self, *, key: str, system: str, user: str) -> str:
        # 1) 후보 생성
        cands = [self._one_candidate(system, user) for _ in range(self.candidates)]

        # 2) 점수(품질/중복) → MMR 선택
        alpha = self.mmr_alpha
        best_i, best_score = 0, -1e9
        for i, c in enumerate(cands):
            q = self._score_quality(c)
            with_others = 0.0
            if len(cands) > 1:
                sims = [SequenceMatcher(None, c, o).ratio() for j,o in enumerate(cands) if j != i]
                with_others = sum(sims)/len(sims)
            red = 0.6*self._mem_penalty(key, c) + 0.4*with_others
            score = alpha*q - (1-alpha)*red
            if score > best_score:
                best_score, best_i = score, i
        chosen = cands[best_i]

        # 3) 메모리 업데이트
        self.memory[key].append(chosen)
        if len(self.memory[key]) > self.memory_size:
            self.memory[key] = self.memory[key][-self.memory_size:]
        return chosen


def run_setting_in_new_cmd():
    print("run_setting_in_new_cmd")
    CREATE_NEW_CONSOLE = 0x00000010
    SW_SHOWMINIMIZED = 2

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = SW_SHOWMINIMIZED

    # 자신의 파일명 자동 추출
    pyfile = os.path.abspath(__file__)
    subprocess.Popen(
        [sys.executable, pyfile, "set"],
        creationflags=CREATE_NEW_CONSOLE,
        startupinfo=si
    )











class SourceSetter :


    def __init__(self) :
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")
        self.diversity = DiversitySamplerSync(api_key=self.api_key, model="gpt-4o-mini")

        # 전역 변수: 스레드별 결과 저장



        with open("source.json", 'r', encoding='utf-8') as file:
            root = json.load(file)
        self.main_id_list = root["data_id_list"][0]
        self.second_main_id_list = root["data_id_list"][1]
        self.task_version = root["task_version"]
        self.ignored_id_list = root["ignored_id_list"]
        source_file_csv_path = root["source_file_csv_path"]


        # csv 읽기 (한자어를 인덱스로 사용)
        df = pd.read_csv(source_file_csv_path, index_col=0)
        self.df_row_count = df.shape[0]

        # 인덱스를 'T'로 이동, 기존 컬럼은 오른쪽으로 shift
        df_reset = df.reset_index()
        df_reset.columns = ['T', 'D', 'P', 'P_unused'] if len(df_reset.columns) == 4 else ['T', 'D', 'P']

        # 불필요한 컬럼 제거
        if 'P_unused' in df_reset.columns:
            df_reset = df_reset.drop('P_unused', axis=1)


        # 딕셔너리 리스트로 변환
        self.source_list = df_reset.to_dict(orient='records')

        for i, item in enumerate(self.source_list, start=1):
            item["idx"] = i

        self.chrome_semaphore = threading.Semaphore(20)  # 최대 5개만 동시 실행


        self.main_id_list = []
        self.second_main_id_list = []
        self.main_id_list_lock = threading.Lock()
        self.second_main_id_list_lock = threading.Lock()

        self.list_lock = threading.Lock()
        self.second_list_lock = threading.Lock()


        self.first_group_threads_status = None
        self.second_group_threads_status = None
        self.task_version = 0

        self.threads = []
        self.thread_number = -1

    def safe_append(self,data_idx,group_number) :

        if data_idx in self.ignored_id_list : return


        if group_number == 1 :
            while data_idx in self.main_id_list:
                time.sleep(0.3)
                
        else : 
            while data_idx in self.second_main_id_list:
                time.sleep(0.3)


        if data_idx in self.ignored_id_list : return
        
        if group_number == 1 :
            with self.list_lock:
                
                if data_idx in self.ignored_id_list : return
        
                self.main_id_list.append(data_idx)
        else : 
            with self.second_list_lock:
                self.second_main_id_list.append(data_idx)

        return

    def clean_up(self,s: str) -> str :
        try : 
            text = s.replace('[', '').replace(']', '')
            pattern = r'([가-힣a-zA-Z_])\.'
            replaced = re.sub(pattern, r'\1', text)
            return replaced
        except Exception as e:
            print("clean_up e :",e)
            return None

    # --- exam_roller.py : ask_gpt()만 교체 ---------------------------------
    def ask_gpt(self, question: str) -> str:
        try:
            # 병렬 시 동일시드/경로 수렴을 약간 분산
            time.sleep(random.uniform(0.01, 0.08))

            messages = [
                {"role": "system",
                "content": "Follow the instruction exactly. Output only what is requested. No explanations."},
                {"role": "user", "content": question}
            ]
            import openai
            response = openai.OpenAI(api_key=self.api_key).chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.85,       # 약간만 가열
                top_p=1.0,
                presence_penalty=0.5,   # 새 토큰 출현 유도
                frequency_penalty=0.7,  # 반복 억제
                max_tokens=128,
            )
            return self.clean_up(response.choices[0].message.content)
        except Exception as e:
            print("ask_gpt e :", e)
            return None

    def get_kanji_words(self,sentence: str) -> str :
        try :  
            return re.findall(r'[\u4e00-\u9fff]{2,}', sentence)
        except Exception as e:
            print("return_sentence_prompt e :",e)
            return None
        
    def create_answer(self, result_data, status, request_type, word_or_sen):
        try:
            create_func = None

            if request_type == "create_sentence":
                create_func = self.s("create_sentence", word_or_sen)
            elif request_type == "create_reading":
                create_func = self.s("create_reading", word_or_sen)
            elif request_type == "create_meaning":
                create_func = self.s("create_meaning", word_or_sen)

            for _ in range(5):
                answer = self.diversity.generate(
                    key=word_or_sen,
                    system="Follow the instruction exactly. Output only what is requested. No explanations.",
                    user=create_func
                )
                    #answer = self.ask_gpt(create_func)

                result_data[request_type.replace("create_", "", 1)] = answer
                check_sentence = self.s(
                    request_type.replace("create_", "check_", 1),
                    word_or_sen, answer
                )
                if self.ask_gpt(check_sentence) == "y":
                    status["is_good"] = True
                    return
                else:
                    status["is_good"] = False
            return
        except Exception as e:
            print("create_answer e :", e)
            return None
        
        
            
    '''
    def s(self,question_type,part1,part2=None):
        questions = {
            "create_sentence":f"[{part1}]라는 단어를 포함시켜서 일본어 예문 하나를 작성해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, 그 문장만을 반환해줘.",
            "create_reading" : f"[{part1}]해당 문장을 읽는 방법을 히라가나로 알려줘. 끊어읽어야하는 부분마다 ' / ' 을 삽입해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, 그 문장만을 반환해줘. 'hello my friend.' 를 '헬로 / 마이 / 프렌드' 같은 방식으로.",
            "check_reading":f"[{part1}]이 문장을 읽는 방법이 [{part2}] 라는 주장이 정상적인지 아닌지 y 와 n 로 대답해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "create_meaning" : f"[{part1}]해당 문장을 해석해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, 그 문장만을 반환해줘.",
            "check_meaning":f"[{part1}]이 문장의 뜻이 [{part2}] 라는 주장이 정상적인지 아닌지 y 와 n 로 대답해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "check_word_reading" : f"{part1}를 읽는 방법이 {part2}가 맞아? 맞으면 'y'만, 틀리면 올바른 발음만 정확히 알려줘. 답변에 다른 부가 설명이나 내용은 절대 포함하지 말고, 오직 한 가지만 반환해.",
            "check_sentence":f"[{part1}]해당 문장이 정상적인지 아닌지 y 와 n 로 대답해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "word_meaning":f"{part1} 의 한국어 뜻을 한 단어로 알려줘. 답변에는 오직 뜻만 포함하고, 부가 설명이나 다른 내용은 절대 포함하지 마."
        }
        try : 
            return questions[question_type]
        except Exception as e:
            print("s e :",e)
            return None
    '''
        

    def s(self, question_type, part1, part2=None):
        # 상투문장 몇 개만 간단히 금지(필요시 추가)
        if question_type == "create_sentence":
            # 문체/시점/길이 힌트를 아주 가볍게 넣어 초반 토큰 분기 확대
            style = random.choice(["会話体", "丁寧体", "カジュアル", "フォーマル", "独白"])
            voice = random.choice(["一人称", "三人称"])
            #length = random.choice(["13~18字", "18~24字", "24~32字"])
            length = "13~18字"
            # 작은 논스는 모델 출력에 보이지 않지만(문장 외 금지했으므로) 내부 분기만 유도하는 힌트
            nonce = str(random.randint(1000, 9999))
            return (
                f"[diversity:{nonce}] 「{part1}」を必ず含めて、日本語の自然な例文を1文だけ作成。"
                f"文体:{style}、視点:{voice}、長さ:{length}。句点で終了。"
                "出力はその文のみ。説明・翻訳・引用符は禁止。"
            )

        questions = {
            "create_reading": f"[{part1}]해당 문장을 읽는 방법을 히라가나로 알려줘. 끊어읽어야하는 부분마다 ' / ' 을 삽입해줘. "
                            "너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, 그 문장만을 반환해줘.",
            "check_reading":  f"[{part1}]이 문장을 읽는 방법이 [{part2}] 라는 주장이 정상적인지 아닌지 y 와 n 로 대답해줘. "
                            "너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "create_meaning": f"[{part1}]해당 문장을 한국어 해석해줘. 너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, 그 문장만을 반환해줘.",
            "check_meaning":  f"[{part1}]이 문장의 뜻이 [{part2}] 라는 주장이 정상적인지 아닌지 y 와 n 로 대답해줘. "
                            "너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "check_word_reading": f"{part1}를 읽는 방법이 {part2}가 맞아? 맞으면 'y'만, 틀리면 올바른 발음만 정확히 알려줘. "
                                "답변에 다른 부가 설명이나 내용은 절대 포함하지 말고, 오직 한 가지만 반환해.",
            "check_sentence": f"[{part1}]해당 문장이 정상적인지 아닌지 y 와 n 로 대답해줘. "
                            "너의 대답을 그대로 사용자에게 보여줄테니까, 모든 부가요소들은 제거하고서, y 또는 n 만 반환해줘.",
            "word_meaning":   f"{part1} 의 한국어 뜻을 한 단어로 알려줘. 답변에는 오직 뜻만 포함하고, 부가 설명이나 다른 내용은 절대 포함하지 마."
        }
        return questions[question_type]

    def remove_brackets(self,text):
        try : 
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
        except Exception as e:
            print("remove_brackets e :",e)
            return None
        

    def get_word_reading_info(self,words_info,word) : 
        with self.chrome_semaphore:
            driver = None
            try : 
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920x1080')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(options=options)
                driver.get(f"https://ja.dict.naver.com/#/search?query={word}&range=all")
                elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
                )
                t = None
                try : 
                    t = self.remove_brackets(elements[0].text)
                except : 
                    t
                end_keyword = "민중서림 엣센스 일한사전"
                t = t.split(end_keyword)[0]
                t_splited = t.split("\n")
                word_reading = t_splited[0].split("[")[0].strip()
                word_reading = self.clean_up(word_reading)
                gpt_answer = self.ask_gpt(self.s("check_word_reading",word,words_info))
                if not gpt_answer == "y" :
                    word_reading = self.clean_up(gpt_answer)

                for loc in range(len(words_info)):
                    if words_info[loc]["word"] == word:
                        words_info[loc]["word_reading"] = self.clean_up(word_reading)

            except Exception as e:
                print("get_word_reading_info e :",e)
                words_info[loc]["word_reading"] = ""
                return None
            finally : 
                if driver :
                    driver.quit()
                    return
                
    def record_json(self,data, group_number, file_path='source.json'):
        
        """
        source.json의 'data' 리스트 내 group_number번째 리스트에 data를 append
        :param data: 추가할 dict 데이터
        :param group_number: 0-base 인덱스 (예: 첫번째 그룹은 0)
        :param file_path: JSON 파일 경로
        """
           
        group_number = group_number - 1

        lock_path = file_path + '.lock'
        with FileLock(lock_path):
            if not data["idx"] in self.ignored_id_list :
                # 파일 읽기 및 유효성 검사
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            root = json.load(f)
                        if not (isinstance(root, dict) and "data" in root and isinstance(root["data"], list)):
                            raise ValueError("source.json의 최상위는 dict이고, 'data' 키에 리스트가 있어야 합니다.")
                    except (json.JSONDecodeError, Exception):
                        root = {"data": [[], []]}
                else:
                    root = {"data": [[], []]}
                

                # 데이터 추가

                root["data"][group_number].append(data)
                root["data_id_list"][group_number].append(data["idx"])
                root["task_version"] = root["task_version"] + 1


                # 파일 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(root, f, ensure_ascii=False, indent=2)

    def get_word_meaning_info(self,words_info,word) :
        try : 
            result = self.ask_gpt(self.s("word_meaning",word))
            for loc in range(len(words_info)):
                if words_info[loc]["word"] == word:
                    words_info[loc]["word_meaning"] = self.clean_up(result)
        except Exception as e:
            print("get_word_meaning_info e :",e)
            return None

    def apply_status(self,group_number,source_list_idx) :
        if group_number == 1 :
            with self.main_id_list_lock:
                self.first_group_threads_status[source_list_idx] = 0
        else : 
            with self.second_main_id_list_lock:
                self.second_group_threads_status[source_list_idx] = 0

    def worker(self,source_list_idx,group_number):
        main_info = self.source_list[source_list_idx]
        main_info_idx = main_info["idx"]
        
        if main_info_idx in self.ignored_id_list : 
            self.apply_status(group_number,source_list_idx)
            return
        result_data = None
        try : 

            sentence, reading = None, None
            status = {"is_good": True}
            main_word = main_info["T"]
            words_processes = []
            words_info = []

            result_data = {
                "idx":main_info_idx,
                "sentence":sentence
            }
            
            for _ in range(5):
                if not words_processes == [] : 
                    words_processes = []
                if not words_info == [] : 
                    words_info = []

                create_sentence_thread = threading.Thread(target=self.create_answer, args=(
                    result_data,
                    status,
                    "create_sentence",
                    main_word
                ), daemon=True)
                create_sentence_thread.start()

                

                sentence = None
                while True : 
                    if result_data["sentence"] : 
                        sentence = result_data["sentence"]
                        break
                    time.sleep(0.001)

                
                
                words = self.get_kanji_words(sentence)
                if status["is_good"] == False : continue

                words_info = None
                if main_word in words:
                    words.remove(main_word)
                words_info = [
                    {"word": w, "word_reading": "", "word_meaning": ""}
                    for w in words
                ]
                
                if status["is_good"] == False : continue

                for word in words :
                    t = threading.Thread(target=self.get_word_reading_info, args=(words_info, word,), daemon=True)
                    t.start()
                    words_processes.append(t)
                
                if status["is_good"] == False : continue

                for word in words :
                    t = threading.Thread(target=self.get_word_meaning_info, args=(words_info, word,), daemon=True)
                    t.start()
                    words_processes.append(t)
                    
                    
                if status["is_good"] == False : continue

                result_data["reading"] = ""
                result_data["meaning"] = ""
                
                create_reading_thread = threading.Thread(target=self.create_answer, args=(
                        result_data,
                        status,
                        "create_reading",
                        sentence
                    ), daemon=True)
                create_reading_thread.start()

                create_meaning_thread = threading.Thread(target=self.create_answer, args=(
                        result_data,
                        status,
                        "create_meaning",
                        sentence
                    ), daemon=True)
                create_meaning_thread.start()

                for t in words_processes :
                    t.join()
                    
                create_reading_thread.join()
                create_meaning_thread.join()
                create_sentence_thread.join()
                
                if status["is_good"] == False : continue

                print('status["is_good"] :',status["is_good"])
                print('type(status["is_good"]) :',type(status["is_good"]))

                result_data["main_word"] = main_word
                result_data["sentence"] = sentence
                result_data["words_info"] = words_info
                result_data["main_word_reading"] = main_info["P"]
                result_data["main_word_meaning"] = main_info["D"]
                result_data["is_good"] = status["is_good"]
                result_data["contacted"] = False

                print('result_data["is_good"] :',result_data["is_good"])
                print('type(result_data["is_good"]) :',type(result_data["is_good"]))

                
                self.safe_append(main_info_idx,group_number)
                self.record_json(result_data, group_number)
                self.apply_status(group_number,source_list_idx)
                

                self.threads[self.thread_number] = None
                
                return

            
            result_data = {
                "idx":main_info_idx,
                "is_good":False
                }
            
            
            self.safe_append(main_info_idx,group_number)
            self.record_json(result_data, group_number)
            
            self.apply_status(group_number,source_list_idx)

            self.threads[self.thread_number] = None

            return
            
        except Exception as e:
            print("worker e :",e)
            result_data = {
                "idx":main_info_idx,
                "is_good":False
                }
            
            self.safe_append(main_info_idx,group_number)
            self.record_json(result_data, group_number)

            self.apply_status(group_number,source_list_idx)

            self.threads[self.thread_number] = None
            return
            

    def main_list_controler(self):
        
        first_group_list_keys = list(range(len(self.source_list)))
        random.shuffle(first_group_list_keys)
        self.first_group_threads_status = [1]*len(self.source_list)

        second_group_list_keys = list(range(len(self.source_list)))
        random.shuffle(second_group_list_keys)
        self.second_group_threads_status = [1]*len(self.source_list)

        
        for i in range(len(first_group_list_keys)):
            self.thread_number += 1
            t = threading.Thread(target=self.worker, args=(i,1))
            t.start()
            self.threads.append(t)

        for i in range(len(second_group_list_keys)):
            self.thread_number += 1
            t = threading.Thread(target=self.worker, args=(i,2))
            t.start()
            self.threads.append(t)



        # 메인 루프에서 결과를 읽는 부분
        while True :
            
            if all(x == 0 for x in self.first_group_threads_status) :
                #2그룹 모든 스레드의 역할 수행 완료
                #1그룹의 정보반환 준비 시작
                random.shuffle(first_group_list_keys)
                self.first_group_threads_status = [1]*len(first_group_list_keys)

                if len(self.ignored_id_list) == len(first_group_list_keys) : break

                for i in range(len(first_group_list_keys)):
                    self.thread_number += 1
                    t = threading.Thread(target=self.worker, args=(i,1))
                    t.start()
                    self.threads.append(t)

            else :
                time.sleep(0.5)

            if all(x == 0 for x in self.second_group_threads_status) :
                #1그룹 모든 스레드의 역할 수행 완료
                #2그룹의 정보반환 준비 시작
                random.shuffle(second_group_list_keys)
                self.second_group_threads_status = [1]*len(second_group_list_keys)

                if len(self.ignored_id_list) == len(first_group_list_keys) : break

                for i in range(len(second_group_list_keys)):
                    self.thread_number += 1
                    t = threading.Thread(target=self.worker, args=(i,2))
                    t.start()
                    self.threads.append(t)


            else :
                time.sleep(0.5)
    def main(self):

        
        threading.Thread(target=self.main_list_controler).start()
        

        
        file_path = 'source.json'
        lock_path = file_path + '.lock'
        
        while True:
            

            with FileLock(lock_path):
                file_task_version = None
                # 1. 빠르게 self.task_version 라인만 읽기
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line.startswith('"task_version"'):
                            value = line.split(':', 1)[1].strip(' ,')
                            file_task_version = int(value)
                            break

                # 2. 다르면 전체 파싱
                if file_task_version != self.task_version:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        root = json.load(file)
                    self.main_id_list = root["data_id_list"][0]
                    self.second_main_id_list = root["data_id_list"][1]
                    self.task_version = root["task_version"]
                    self.ignored_id_list = root["ignored_id_list"]

            if len(self.ignored_id_list) >= self.df_row_count :
                break



            time.sleep(0.01)  # 너무 바쁘게 돌지 않도록 약간 쉼







class ExamRoller :

    def __init__(self) :
        #self.run_setter()

        self.my_lock = Lock()

        self.source_file_path = 'source.json'
        self.lock_path = self.source_file_path + '.lock'

        self.task_version = 0

        default_data = {
                "task_version": 1,
                "source_file_csv_path": SOURCE_FILE_CSV_PATH,
                "ignored_id_list": [],
                "data_id_list": [[],[]],
                "data": [[],[]]
            }


        root = None
        with open("source.json", 'r', encoding='utf-8') as file:
            root = json.load(file)

        self.source_file_csv_path = root["source_file_csv_path"]
        if not self.source_file_csv_path == SOURCE_FILE_CSV_PATH :
            with open("source.json", "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)


        self.ignored_id_list = []
        self.main_data = None
        self.id_list = None


        self.viewed_id_list = []
        self.group_id_list = [0,1]
        self.group_index_stack = 0
        self.group_index = self.group_id_list[0]
        self.target_index = 0

        self.target_item = None
        self.printed_info = False


        df = pd.read_csv(self.source_file_csv_path, index_col=0)
        self.row_count = df.shape[0]

    def check_fin(self) :
        try :

            if self.row_count <= len(self.ignored_id_list) : 
                return True
            else :
                return False
        except Exception as e:
            print("check_fin e :",e)
    
    def run_setter(self) :
        try : 

            CREATE_NEW_CONSOLE = 0x00000010
            SW_SHOWMINIMIZED = 2

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = SW_SHOWMINIMIZED

            subprocess.Popen(
                [sys.executable, "source_setter.py"],
                creationflags=CREATE_NEW_CONSOLE,
                startupinfo=si
            )
        except Exception as e:
            print("run_setter e :",e)
        

    def link(self,line,word,url=None) :
        if not url :
            url = f"https://ja.dict.naver.com/#/search?query={word}"
        

        return f"\033]8;;{url}\033\\{line}\033]8;;\033\\"



    def print_item(self,item) :
        try : 
            prints = json.dumps(item, ensure_ascii=False, indent=2)
            for line in prints.splitlines():
                self.print_line(line)
        except Exception as e:
            print("print_item e :",e)

    def print_line(self,line) :
        try : 
            print(f"\033[32m{line}\033[0m")
        except Exception as e:
            print("print_line e :",e)

    def apply_idx(self,item) :
        try : 
            self.viewed_id_list.append(item["idx"])
            self.target_index = item["idx"]
            self.target_item = item
        except Exception as e:
            print("apply_idx e :",e)



    def roller(self) :
        
        while True :
            #print("r")
            try : 
                root = None
                
                with FileLock(self.lock_path):
                    with open("source.json", 'r', encoding='utf-8') as file:
                        root = json.load(file)

                if not self.task_version == root["task_version"] :
                    self.task_version = root["task_version"]
                    self.ignored_id_list = root["ignored_id_list"]
                    self.source_file_csv_path = root["source_file_csv_path"]
                    self.main_data = root["data"][self.group_index]
                    self.id_list = root["data_id_list"][self.group_index]
                time.sleep(0.5)

                if len(self.ignored_id_list) >= self.row_count : break

            except Exception as e:
                print("roller e :",e)
                return None
                    


    def get_root(self) :
        
        if os.path.exists(self.source_file_path):
            try:
                with open(self.source_file_path, 'r', encoding='utf-8') as f:
                    root = json.load(f)
                if not (isinstance(root, dict) and "data" in root and isinstance(root["data"], list)):
                    raise ValueError("source.json의 최상위는 dict이고, 'data' 키에 리스트가 있어야 합니다.")
            except (json.JSONDecodeError, Exception):
                root = {"data": [[], []]}
        else:
            root = {"data": [[], []]}
        return root


    def custom_pop(self) :


        try : 
            
            root = None
            result = None
            while True : 
                with FileLock(self.lock_path):
                    root = self.get_root()
                    
                    
                    # 데이터 추가
                    data_list = root["data"][self.group_index]

                    for i, item in enumerate(data_list):
                        if item["idx"] not in self.viewed_id_list:
                            result = data_list.pop(i)
                            break 

                        
                    if self.check_fin() : break
                    
                    if not result : 
                        continue

                    root["data"][self.group_index] = d(data_list)

                    data_id_list = root["data_id_list"][self.group_index]
                    root["data_id_list"][self.group_index] = [x for x in data_id_list if x != result["idx"]]

                    root["task_version"] = root["task_version"] + 1

                    # 파일 저장
                    with open(self.source_file_path, 'w', encoding='utf-8') as f:
                        json.dump(root, f, ensure_ascii=False, indent=2)

                    return result
            return result
                

        except Exception as e:
            print("custom_pop e :",e)
        


    def append_ignore(self) :
        try : 
            root = None
            with FileLock(self.lock_path):
                root = self.get_root()

                self.ignored_id_list = root["ignored_id_list"]
                self.ignored_id_list.append(self.target_index)
                root["ignored_id_list"] = self.ignored_id_list

                for gruop_id in self.group_id_list : 
                    data_id_list = root["data_id_list"][gruop_id]
                    data_id_list = [x for x in data_id_list if x != self.target_index]

                    data = root["data"][gruop_id]
                    data = [item for item in data if item["idx"] != self.target_index]

                    root["data_id_list"][gruop_id] = data_id_list
                    root["data"][gruop_id] = data
                root["task_version"] = root["task_version"] + 1

                # 파일 저장
                with open(self.source_file_path, 'w', encoding='utf-8') as f:
                    json.dump(root, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("append_ignore e :",e)


    def main_checkout(self) :
        try : 
            item = None
            while True : 
                item = self.custom_pop()
                if self.check_fin() : break
                if not item == None : break

            if self.check_fin() : return True
            
            self.apply_idx(item)
            #self.print_item(item)
            self.printed_info = False
            os.system('cls')

            #print_line
            if self.target_item and self.target_item["is_good"] == True : 
                self.print_line(self.target_item["sentence"])

            return False
        except Exception as e:
            print("main_checkout e :",e)




    def swap_group_info(self) :
        try : 
            if len(self.viewed_id_list) >= self.row_count - len(self.ignored_id_list) :
                self.viewed_id_list = []
                self.group_index_stack = self.group_index_stack + 1
                self.group_index = self.group_id_list[self.group_index_stack % 2]
        except Exception as e:
            print("swap_group_info e :",e)

    def main(self):
        
        threading.Thread(target=self.roller).start()

        print("in_ready")
        while True:
            
            if self.check_fin() : break

            if msvcrt.kbhit():
                last_key = None

                while msvcrt.kbhit():
                    last_key = msvcrt.getwch()

                if last_key == 'a':
                    if self.main_data:
                        if self.main_checkout() : break
                        
                elif last_key == "d" :
                    if self.main_data:
                        if self.target_index :
                            self.append_ignore()
                        if self.main_checkout() : break

                elif last_key == "w" :
                    
                    if self.printed_info : 
                        #이미 보이고있는중
                        if self.target_item : 
                            os.system('cls')
                            self.print_line(self.target_item["sentence"])
                            
                            self.printed_info = False
                    elif not self.printed_info : 
                        #보이고있지 않는 상태
                        print()
                        if self.target_item : 
                            if self.target_item["is_good"] == True : 

                                self.print_line(self.target_item["reading"])
                                self.print_line(self.target_item["meaning"])
                                print()
                                print(f'{self.target_item["main_word"]} / {self.target_item["main_word_reading"]} / {self.target_item["main_word_meaning"]}')
                                for word_info in self.target_item["words_info"] :
                                    self.print_line(
                                        self.link(
                                                f"{word_info["word"]} / {word_info["word_reading"]} / {word_info["word_meaning"]}",
                                                word_info["word"]
                                            )
                                        )
                            self.printed_info = True




            self.swap_group_info()


            time.sleep(0.01)
        print("Fin.")





if __name__ == "__main__":
    

    if sys.platform == "win32":
        class CONSOLE_CURSOR_INFO(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_int),
                        ("bVisible", ctypes.c_bool)]
        handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        cursor = CONSOLE_CURSOR_INFO()
        cursor.dwSize = 1
        cursor.bVisible = False  # 커서 보이지 않게
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor))

    

    print("sys.argv :",sys.argv)
    print("type(sys.argv) :",type(sys.argv))
    print("len(sys.argv) :",len(sys.argv))
    print("type(len(sys.argv)) :",type(len(sys.argv)))
    multi = 1
    open_sub_cmd = False
    try : 
        #다시 돌아올때 사용될 부분
        print("sys.argv[1] :",sys.argv[1])
        print("type(sys.argv[1]) :",type(sys.argv[1]))
        open_sub_cmd = len(sys.argv) > 1 and str(sys.argv[1]) == "set"
    except IndexError : 
        pass
    
    try : 
        print("sys.argv[1] :",sys.argv[1])
        print("type(sys.argv[1]) :",type(sys.argv[1]))
        if len(sys.argv) > 1 and (sys.argv[1]).isdigit() :
            multi = int(sys.argv[1])
    except IndexError : 
        pass


    if open_sub_cmd :
            

        print("setting")
        SourceSetter().main()
    else:
        print('multi :',multi)
        for i in range(multi) :
            run_setting_in_new_cmd()

        # 아래는 직접 실행창에서만 동작
        ExamRoller().main()
