# file: kanji_counter_txt.py
import re
import pandas as pd
from collections import Counter
import os

KANJI_REGEX = re.compile(r"[\u4E00-\u9FFF]")

def extract_standalone_kanji(sentence: str):
    """문장에서 주변에 다른 한자가 없는 단독 한자만 추출"""
    if not isinstance(sentence, str):
        return []
    result = []
    for i, char in enumerate(sentence):
        if not KANJI_REGEX.match(char):
            continue
        prev_char = sentence[i - 1] if i > 0 else ""
        next_char = sentence[i + 1] if i < len(sentence) - 1 else ""
        if not KANJI_REGEX.match(prev_char) and not KANJI_REGEX.match(next_char):
            result.append(char)
    return result


def process_csv(file_path: str, comment_col: str = "comment") -> Counter:
    """CSV 파일 처리 (지정 컬럼 기준)"""
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    if comment_col not in df.columns:
        raise ValueError(f"'{comment_col}' 컬럼이 없습니다.")
    counter = Counter()
    for text in df[comment_col]:
        counter.update(extract_standalone_kanji(text))
    return counter


def process_txt(file_path: str) -> Counter:
    """TXT 파일 처리 (모든 라인 전체 텍스트 대상)"""
    counter = Counter()
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            counter.update(extract_standalone_kanji(line.strip()))
    return counter


def save_counter_to_csv(counter: Counter, output_file: str):
    """Counter 결과를 CSV로 저장"""
    df = pd.DataFrame(counter.items(), columns=["kanji", "count"])
    df = df.sort_values(by="count", ascending=False)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"[INFO] 저장 완료 → {output_file}")


if __name__ == "__main__":
    # 입력 파일 (CSV 또는 TXT, 모두 UTF-8)
    input_file = "temps\\kanji_counter_txt_target.csv"
    output_file = "temps\\standalone_kanji_count.csv"

    ext = os.path.splitext(input_file)[1].lower()
    if ext == ".csv":
        result = process_csv(input_file)
    elif ext == ".txt":
        result = process_txt(input_file)
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")

    print("파일 전체에서 단독 한자 등장 횟수 (상위 20개):")
    for kanji, cnt in result.most_common(20):
        print(f"{kanji}: {cnt}회")

    save_counter_to_csv(result, output_file)
