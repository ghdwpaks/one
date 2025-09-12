import threading
_sem = threading.Semaphore(10)
word_list = [
{'kan': '問題', 'sound': 'もんだい', 'mean': '[명사] 1.문제 2.(시험 등) 해답을 요구하는 물음 3.토론·연구 등의 대상이 되는 사항, 해결해야 할 사항, 과제'},
{'kan': '好奇心', 'sound': 'こうきしん', 'mean': '[명사] 호기심, 신기하거나 모르는 것에 대한 흥미나 관심.'},




]

import re
import os
import openai
from copy import deepcopy as d
import sys
import io
import time

_sem = threading.Semaphore(10)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

ask_fin = ""


def is_contains_korean(text: str) -> bool:
    return bool(re.search("[\uac00-\ud7a3]", text))


def custom_print(var, color="gr", end="\n"):
    if color == "gr":
        print(f"\033[32m{str(var)}\033[0m", end=end)
    elif color == "or":
        print(f"\033[38;5;208m{str(var)}\033[0m", end=end)
    elif color == "br":
        print(f"\033[38;5;94m{str(var)}\033[0m", end=end)
    elif color == "re":
        print(f"\033[31m{str(var)}\033[0m", end=end)
    elif color == "ye":
        print(f"\033[33m{str(var)}\033[0m", end=end)


def remove_square_brackets(text: str) -> str:
    return re.sub(r"\[.*?\]", "", text)


def remove_dot_after_char(text: str) -> str:
    return re.sub(r"([가-힣a-zA-Z_])\.", r"\1", text)


def ask_gpt(question: str) -> str:
    global api_key
    e = None
    for _ in range(1000):
        try:
            messages = [
                {"role": "system", "content": ""},
                {"role": "user", "content": question},
            ]
            response = openai.OpenAI(api_key=api_key).chat.completions.create(
                model="gpt-4o-mini", messages=messages, temperature=0.9
            )
            return clean_up(response.choices[0].message.content)
        except Exception as e:
            if "429" in str(e) or "timeout" in str(e):
                time.sleep(10)
            print("ask_gpt e :", e)
            return None
    print("ask_gpt e :", e)
    return None


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


def apply_edit(idx, key, value):
    global word_list
    word_list[idx][key] = value


def s(question_type, part1, part2=None, part3=None):
    global ask_fin
    questions = {
        "mean_answer": f"{part1} 의 한국어 뜻을 한 단어로 알려줘.{part2}.{ask_fin}",
        "mean_final_answer": f"{part1} 의 뜻이 {part2} 라는 주장에 관해서, [1:문제없음], [2:이상함] 으로, 번호만 대답해줘. {ask_fin}",
        "sound_answer": f"{part1} 의 발음을 히라가나로 적어줘.{part2}.{ask_fin}",
        "sound_final_answer": f"'{part1} 의 뜻을 히라가나로 표현한것이 {part2} 이다.' 라는 주장에 관해서, [1:문제없음], [2:히라가나로 표현되지 않았거나, 이상함] 으로, 번호만 대답해줘. {ask_fin}",
    }
    return questions.get(question_type)


# --- 저장 함수 추가 ---
def save_progress():
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer

    print("[")
    for i in word_list:
        custom_print(i)
    print("]")

    sys.stdout = original_stdout
    captured_word_output = buffer.getvalue()
    with open("temps\\captured_word_output.txt", "w", encoding="utf-8") as f:
        f.write(captured_word_output)


def processing(idx: int, target_type: str) -> str:
    with _sem:
        loop_size = 10
        global word_list
        word_list_idx_kan = word_list[idx]["kan"]

        if target_type == "mean":
            for loop in range(loop_size):
                try:
                    answer = ask_gpt(s("mean_answer", word_list_idx_kan))
                    final_answer = ask_gpt(s("mean_final_answer", word_list_idx_kan, answer))
                    if final_answer == "2":
                        continue
                    apply_edit(idx, "edited_mean", answer)
                    apply_edit(idx, "is_good_mean", True)
                    save_progress()  # ✅ 저장
                    break
                except Exception:
                    continue
        else:
            for loop in range(loop_size):
                try:
                    answer = ask_gpt(s("sound_answer", word_list_idx_kan))
                    final_answer = ask_gpt(s("sound_final_answer", word_list_idx_kan, answer))
                    if final_answer == "2":
                        continue
                    apply_edit(idx, "edited_sound", answer)
                    apply_edit(idx, "is_good_sound", True)
                    save_progress()  # ✅ 저장
                    break
                except Exception:
                    continue


for i in range(len(word_list)):
    word_list[i]["mean"] = remove_dot_after_char(
        remove_square_brackets(word_list[i]["mean"].strip())
    ).strip()
    word_list[i]["edited_mean"] = ""
    word_list[i]["edited_sound"] = ""
    word_list[i]["is_good_mean"] = False
    word_list[i]["is_good_sound"] = False

os.system("cls")
ask_fin = "가장 짧게. 본론만. 추가 질문 없이. 서두없이."

threads = []
for i in range(len(word_list)):
    t = threading.Thread(target=processing, args=(i, "mean"))
    t.start()
    threads.append(t)

for i in range(len(word_list)):
    t = threading.Thread(target=processing, args=(i, "sound"))
    t.start()
    threads.append(t)

for i in threads:
    i.join()

print("진행상황이 temps\\captured_word_output.txt 에 저장됐습니다.")


