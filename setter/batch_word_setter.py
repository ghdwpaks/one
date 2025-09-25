NEAR_SCRAPED_INFO_FILE_PATH = "temps/near_scraped_info.txt"
RESULT_OUTPUT_FILE_PATH = "temps/result.txt"

import ctypes; from time import sleep
ES_CONTINUOUS,ES_SYSTEM_REQUIRED,ES_DISPLAY_REQUIRED=0x80000000,1,2
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED)


# file: batch_test.py

from openai import OpenAI
import time
import os
import json
from copy import deepcopy as d
import threading
import re
import ast
temp_path = "./temps/"
local_batch_task_number = 0
def do_task(tasks_sentences,filename,result_dict) :
    global local_batch_task_number
    

    local_batch_task_number = local_batch_task_number + 1
    tasks = []
    for i in tasks_sentences :
                
        messages = [
            {"role": "user", "content": tasks_sentences[i]}
        ]

        tasks.append(
            {
                "custom_id": f"{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-5-nano",
                    "messages" : messages
                }
            }
        )


    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    fname = f"{temp_path}batch_input{local_batch_task_number}.jsonl"
    with open(fname, "w", encoding="utf-8") as f:
        for obj in tasks:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    # 2. 업로드
    batch_file = client.files.create(
        file=open(fname, "rb"),
        purpose="batch"
    )

    # 3. 배치 작업 생성
    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    
    # 4. 1초마다 상태 체크 → 완료되면 저장
    i = 1
    while True:
        '''
        status info
        validating : the input file is being validated before the batch can begin
        failed : the input file has failed the validation process
        in_progress : the input file was successfully validated and the batch is currently being run
        finalizing : the batch has completed and the results are being prepared
        completed : the batch has been completed and the results are ready
        expired : the batch was not able to be completed within the 24-hour time window
        cancelling : the batch is being cancelled (may take up to 10 minutes)
        cancelled : the batch was cancelled
        '''
        
        b = client.batches.retrieve(batch.id)
        if i % 5 == 0 or i == 0:
            print(f"{local_batch_task_number}:{b.status}")
        if hasattr(b, "status") and b.status in [
            "in_progress",
            "validating",
            "finalizing"
        ] : 
            pass
        elif hasattr(b, "status") and b.status == "completed":
            # 결과 파일 가져오기
            output = client.files.content(b.output_file_id).text
            os.makedirs("./temps", exist_ok=True)
            with open(f"{temp_path}{filename}", "w", encoding="utf-8") as f:
                f.write(output)
            break
        else :
            output = client.files.content(b.output_file_id).text
            with open(f"{temp_path}batch{local_batch_task_number}_error{i}.txt", "w", encoding="utf-8") as f:
                f.write(output)
        time.sleep(300)
        i += 1

    
    with open(f"{temp_path}{filename}", "r", encoding="utf-8") as f:
        for line in f:
            try:
                loaded_data = json.loads(line)
                content = loaded_data["response"]["body"]["choices"][0]["message"]["content"].strip()
                result_dict[int((loaded_data['custom_id']))] = content
            except Exception as e:
                print(f"Error parsing line: {e}")
    return result_dict





def only_wants(dict_data,type="num"):
    sen = ""
    if type == "jp" :
        sen = r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
    elif type == "num" :
        sen = r'\D'
    
    for i in dict_data :
        dict_data[i] = re.sub(sen, '', dict_data[i])
    return dict_data

def make_dict(n: int) -> dict:
    return {i: {} for i in range(n)}

def to_dict(lst):
    return dict([(i+1, v) for i, v in enumerate(lst)])


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





def auto_checker_main(file_path) :
    global temp_path
    global RESULT_OUTPUT_FILE_PATH

    kanji_words, kanji_hatsuon, kanji_imi, hatsuon_is_good, imi_is_good = load_data(file_path=file_path)
   
    


    tasks_sentences = {}
    for i in kanji_words :
        if not (i in hatsuon_is_good and hatsuon_is_good[i]) :
            tasks_sentences[i] = f"'{kanji_words[i]}'의 발음을 히라가나로만 출력해. 다른 설명, 괄호, 따옴표, 문장은 절대 붙이지 말고 히라가나 문자열만 출력해."

    gpt_hatsuon = d(kanji_words)

    filename = "gpt_hatsuon.txt"
    gpt_hatsuon = only_wants(
            do_task(
                tasks_sentences=tasks_sentences,
                filename=filename,
                result_dict=gpt_hatsuon
            ),
            type = "jp"
        )

    tasks_sentences = {}
    for i in kanji_words :
        if not (i in hatsuon_is_good and hatsuon_is_good[i]) :
            tasks_sentences[i] = f"'{kanji_words[i]}'의 발음은 '{kanji_hatsuon[i]}' 이라는 0번째 주장, 그리고 '{gpt_hatsuon[i]}'이라는 1번째 주장이 있다. 이 주장들중에 더 옳은 주장의 번호를 출력해. 오로지 0 과 1 중에 하나만 출력해. 반드시 숫자 하나만 출력해야 하고, 다른 단어, 문장, 기호는 절대 쓰지 마."

    filename = "gpt_hatsuon_select.txt"
    gpt_hatsuon_select = d(kanji_words)
    gpt_hatsuon_select = only_wants(
            do_task(
                tasks_sentences=tasks_sentences,
                filename=filename,
                result_dict=gpt_hatsuon_select
            ),
            type = "num"
        )
        
    right_hatsuon = {}
    for i in gpt_hatsuon_select :
        if int(gpt_hatsuon_select[i]) == 0 : #기존거
            right_hatsuon[i]=f"{kanji_hatsuon[i]}"

        elif int(gpt_hatsuon_select[i]) == 1 : #신규
            right_hatsuon[i]=f"{gpt_hatsuon[i]}"

    confirm_try_count = 3

    hatsuon_task_list = {}
    for task_number in range(confirm_try_count) : 
        tasks_sentences = {}
        for i in kanji_words :
            if not (i in hatsuon_is_good and hatsuon_is_good[i]) :
                tasks_sentences[i] = f"'{kanji_words[i]}'의 발음이 '{right_hatsuon[i]}'이라는 주장이 있다. 이 주장이 맞으면 1, 틀리면 0을 출력해. 반드시 숫자 하나만 출력해야 하고, 다른 단어, 문장, 기호는 절대 쓰지 마."

        hatsuon_task_list[task_number] = tasks_sentences

    threads = []
    hatsuon_result_number_list = make_dict(len(hatsuon_task_list))

    for task_number in hatsuon_task_list :
        t = threading.Thread(target=do_task, args=(
            hatsuon_task_list[task_number],
            f"gpt_hatsuon_confirmed{task_number}.txt",
            hatsuon_result_number_list[task_number]
            ))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()



    # result_writer.py
    
    hatsuon_is_good={}
    for i in kanji_words : 
        if not (i in hatsuon_is_good and hatsuon_is_good[i]) :
            passable = True
            for j in hatsuon_result_number_list:
                if int(hatsuon_result_number_list[j][i]) == 0:
                    passable = False
                    break
            hatsuon_is_good[i] = passable
        else :
            hatsuon_is_good[i] = True


    #################################################################################################################################################################################################################################



    
    tasks_sentences = {}
    for i in kanji_words :
        if not (i in imi_is_good and imi_is_good[i]) :
            tasks_sentences[i] = f"'{kanji_words[i]}'에 (여러 뜻이 있더라도,) '가장 일반적이고 주된 의미'을 한국어로 단 하나만 출력해. 다른 설명, 괄호, 따옴표, 문장은 절대 붙이지 말고, 한글 단어만 출력해."


    gpt_imi = d(kanji_words)

    filename = "gpt_imi.txt"
    gpt_imi = only_wants(
            do_task(
                tasks_sentences=tasks_sentences,
                filename=filename,
                result_dict=gpt_imi
            ),
            type = "jp"
        )

    tasks_sentences = {}
    for i in kanji_words :
        if not (i in imi_is_good and imi_is_good[i]) :
            tasks_sentences[i] = f"'{kanji_words[i]}'의 '가장 대표적인 단 하나의 의미'가 '{kanji_imi[i]}' 이라는 0번째 주장, 그리고 '{gpt_imi[i]}'이라는 1번째 주장이 있다. 이 주장들중에 더 옳은 주장의 번호를 출력해. 오로지 0 과 1 중에 하나만 출력해. 반드시 숫자 하나만 출력해야 하고, 다른 단어, 문장, 기호는 절대 쓰지 마."




    filename = "gpt_imi_select.txt"
    gpt_imi_select = d(kanji_words)
    gpt_imi_select = only_wants(
            do_task(
                tasks_sentences=tasks_sentences,
                filename=filename,
                result_dict=gpt_imi_select
            ),
            type = "num"
        )
        
    right_imi = {}
    for i in gpt_imi_select :
        if int(gpt_imi_select[i]) == 0 : #기존거
            right_imi[i]=f"{kanji_imi[i]}"

        elif int(gpt_imi_select[i]) == 1 : #신규
            right_imi[i]=f"{gpt_imi[i]}"

    confirm_try_count = 3

    imi_task_list = {}
    for task_number in range(confirm_try_count) : 
        tasks_sentences = {}
        for i in kanji_words :
            if not (i in imi_is_good and imi_is_good[i]) :
                tasks_sentences[i] = f"'{kanji_words[i]}'에 여러 뜻이 있더라도, 가장 일반적이고 주된 의미가 '{right_imi[i]}'이라는 주장이 있다. 이 주장이 맞으면 1, 틀리면 0을 출력해. 반드시 숫자 하나만 출력해야 하고, 다른 단어, 문장, 기호는 절대 쓰지 마."

        imi_task_list[task_number] = tasks_sentences

    threads = []
    imi_result_number_list = make_dict(len(imi_task_list))

    for task_number in imi_task_list :
        
        t = threading.Thread(target=do_task, args=(
            imi_task_list[task_number],
            f"gpt_imi_confirmed{task_number}.txt",
            imi_result_number_list[task_number]
            ))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()



    # result_writer.py
    
    imi_is_good={}
    for i in kanji_words : 
        
        if not (i in imi_is_good and imi_is_good[i]) :
            imi_is_good[i] = all(int(imi_result_number_list[j][i]) != 0 for j in imi_result_number_list)










    #################################################################################################################################################################################################################################







    all_passable = True
    with open(f"{RESULT_OUTPUT_FILE_PATH}", "w", encoding="utf-8") as f:
        for i in kanji_words:
            if not hatsuon_is_good or not imi_is_good : 
                all_passable = False

            f.write(json.dumps(
                {
                    "kan": kanji_words[i], 
                    "sound": right_hatsuon[i], 
                    "mean": right_imi[i], 
                    "is_done_sound": hatsuon_is_good[i], 
                    "is_done_mean": imi_is_good[i]
                },
                ensure_ascii=False
                )+"\n")
    
    


    return all_passable


all_passable = auto_checker_main(file_path=NEAR_SCRAPED_INFO_FILE_PATH) 
print("*"*88)
if all_passable : raise()
while True :
    all_passable = auto_checker_main(file_path=RESULT_OUTPUT_FILE_PATH) 
    print("*"*88)
    if all_passable :
        break

print("breaked"*88)