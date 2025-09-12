# youtube_merge_comment.py
import os
import glob
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.join("temps", "comments")
OUTPUT_DIR = "temps"  # 결과 저장 폴더

import re


def clean_comment(text: str) -> str:
    if not isinstance(text, str):
        return text

    # 1) 타임스탬프 제거 (00:01, 00:01:16 등)
    text = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", "", text)

    # 2) 박스 드로잉 문자(┗ ┠ ┏ ┓ ┳ ┻ 등) 제거
    text = re.sub(r"[\u2500-\u257F]", "", text)

    # 3) 양 끝 공백 정리
    return text.strip()


def remove_timestamps(text: str) -> str:
    if not isinstance(text, str):
        return text
    # 00:01, 00:01:16 형태 모두 제거
    return re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", "", text).strip()

# -----------------------------------------------------
# 일본어 여부 판별 함수
# -----------------------------------------------------
def contains_japanese(text: str) -> bool:
    if not isinstance(text, str):
        return False
    # 히라가나, 가타카나, 한자
    jp_pattern = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")
    return bool(jp_pattern.search(text))

# -----------------------------------------------------
# CSV 병합 + 일본어 필터링
# -----------------------------------------------------
def merge_comment_csvs(base_dir=BASE_DIR, output_dir=OUTPUT_DIR):
    # 출력 폴더 없으면 생성
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}_youtube_comment.csv")

    csv_files = glob.glob(os.path.join(base_dir, "*.csv"))
    if not csv_files:
        print("[WARN] CSV 파일이 없습니다.")
        return

    print(f"[INFO] {len(csv_files)}개 CSV 파일 병합 시작...")

    all_dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding="utf-8-sig")
            all_dataframes.append(df)
        except Exception as e:
            print(f"[WARN] {file} 읽기 실패 → {e}")

    if not all_dataframes:
        print("[ERROR] 병합할 데이터가 없습니다.")
        return

    merged_df = pd.concat(all_dataframes, ignore_index=True)

    if "comment" in merged_df.columns:
        merged_df = merged_df.dropna(subset=["comment"])
        merged_df = merged_df[merged_df["comment"].astype(str).str.strip() != ""]

        # 정리 함수 적용 (타임스탬프 + 특수문자 제거)
        merged_df["comment"] = merged_df["comment"].apply(clean_comment)

        # 타임스탬프 제거
        merged_df["comment"] = merged_df["comment"].apply(remove_timestamps)

        # 일본어 포함 여부 필터링
        filtered_df = merged_df[merged_df["comment"].apply(contains_japanese)]
    else:
        print("[WARN] comment 컬럼이 없습니다. 필터링 없이 저장합니다.")
        filtered_df = merged_df

    filtered_df[["comment"]].to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"[INFO] 병합 및 일본어 필터링 완료 → {output_file}")

if __name__ == "__main__":
    merge_comment_csvs()
