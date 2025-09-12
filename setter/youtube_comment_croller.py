
import os
import time
import csv
from typing import List, Dict, Set
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------------
BASE_DIR = "temps"
COMMENTS_DIR = os.path.join(BASE_DIR, "comments")
VISITED_FILE = os.path.join(BASE_DIR, "visited_videos.txt")
os.makedirs(COMMENTS_DIR, exist_ok=True)




# ---------------------------------------------------------------------
# YouTube 클라이언트 생성
# ---------------------------------------------------------------------
def get_youtube_client(api_key: str):
    """YouTube API 클라이언트 생성"""
    return build("youtube", "v3", developerKey=api_key)


# ---------------------------------------------------------------------
# 방문 영상 관리
# ---------------------------------------------------------------------
def load_visited_videos() -> Set[str]:
    """이미 방문한 영상 ID 목록 불러오기"""
    if not os.path.exists(VISITED_FILE):
        return set()
    with open(VISITED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


def mark_video_as_visited(video_id: str) -> None:
    """방문한 영상 ID 기록"""
    with open(VISITED_FILE, "a", encoding="utf-8") as f:
        f.write(video_id + "\n")

# ---------------------------------------------------------------------
# 채널 핸들(@xxxx) → channelId 변환
# ---------------------------------------------------------------------
def get_channel_id_from_handle(youtube, handle: str) -> str:
    """
    채널 핸들(@xxxx) → 채널 ID(UCxxxx) 변환
    """
    if not handle.startswith("@"):
        raise ValueError("채널 핸들은 반드시 '@'로 시작해야 합니다.")

    request = youtube.channels().list(
        part="id",
        forHandle=handle
    )
    response = request.execute()

    if response.get("items"):
        channel_id = response["items"][0]["id"]
        print(f"[INFO] 핸들 {handle} → 채널 ID {channel_id}")
        return channel_id
    else:
        raise ValueError(f"[ERROR] 채널 핸들을 찾을 수 없음: {handle}")


# ---------------------------------------------------------------------
# 영상 및 댓글 가져오기
# ---------------------------------------------------------------------
def get_video_ids_from_channel(youtube, channel_id: str, max_results: int = 5) -> List[str]:
    """특정 채널에서 최신 영상 ID 가져오기"""
    print(f"[INFO] 채널 {channel_id}의 최신 영상 {max_results}개 가져오는 중...")
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        order="date",
        maxResults=max_results,
        type="video",
    )
    response = request.execute()
    video_ids = [item["id"]["videoId"] for item in response["items"]]
    print(f"[INFO] 채널 {channel_id} → {len(video_ids)}개 영상 ID 수집 완료")
    return video_ids


def get_top_level_comments(youtube, video_id: str, max_pages: int = 5) -> List[Dict[str, str]]:
    """특정 영상의 최상위 댓글 가져오기"""
    print(f"[INFO] 영상 {video_id} 댓글 수집 시작 (최대 {max_pages} 페이지)...")
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100,
    )
    page_count = 0

    try:
        while request and page_count < max_pages:
            response = request.execute()
            print(f"[DEBUG] 영상 {video_id} → {page_count+1}페이지 수집 중...")
            for item in response["items"]:
                text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append({"video_id": video_id, "comment": text})
            request = youtube.commentThreads().list_next(request, response)
            page_count += 1
            time.sleep(0.2)
    except HttpError as e:
        print(f"[WARN] 영상 {video_id} 댓글 수집 실패 → {e}")
    print(f"[INFO] 영상 {video_id} → 총 {len(comments)}개 댓글 수집 완료")
    return comments


# ---------------------------------------------------------------------
# 저장 기능
# ---------------------------------------------------------------------
def save_comments_to_file(video_id: str, comments: List[Dict[str, str]]) -> None:
    """댓글을 CSV 파일로 저장"""
    filename = os.path.join(COMMENTS_DIR, f"{video_id}.csv")
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "comment"])
        writer.writeheader()
        writer.writerows(comments)
    print(f"[INFO] 영상 {video_id} 댓글 저장 완료 → {filename}")


import os

API_KEY = "AIzaSyAdVBI-tESMIurYGu-yd4oJwqUnjRt3DnE"
CHANNEL_IDS = [
    "UCJFZiqLMntJufDCHc6bQixg",  # Hololive Official
    "UC1CfXB_kRs3C-zaeTG3oGyg",  # Vtuber
    "UCp6993wxpyDPHUpavwDFqgg",
    "UCDqI2jOz0weumE8s7paEk6g",
    "UCvaTdHTWBGv3MKj3KVqJVCw",
    "UChAnqc_AY5_I3Px5dig3X1Q",
    "UCp-5t9SrOQwXMU7iIjQfARg",
    "UCdn5BQ06XqgXoAxIhbqw5Rg",
    "UC1DCedRgGHBdm81E1llLhOQ",
    "UCdyqAaZDKHXg4Ahi7VENThQ",
    "UCCzUftO8KOVkV4wQG1vkUvg",
    "UC1uv2Oq6kNxgATlCiez59hw",
    "UCqm3BQLlJfvkTsX_hvm0UmA",
    "UCFKOVgVbGmX65RxO3EtH3iw",
    "UCAWSyEs_Io8MtpY3m-zqILA",
    "UCUKD-uaobj9jiqB-VXt71mA",
    "UCENwRMx5Yh42zWpzURebzTw",
    "UCs9_O1tRPMQTHQ-N_L6FU2g",
    "UC6eWCld0KwmyHFbAqK3V-Rw",
    "UC_vMYWcDjmfdpH6r4TTn1MQ",
    "UCMGfV7TVTmHhEErVJg1oHBQ",
    "UCWQtYtq9EOB4-I5P-3fh8lA",
]

def resolve_channel_ids(youtube, channel_ids):
    resolved = []
    for cid in channel_ids:
        if cid.startswith("@"):
            try:
                ucid = get_channel_id_from_handle(youtube, cid)
                resolved.append(ucid)
            except Exception as e:
                print(f"[WARN] {cid} 변환 실패 → {e}")
        else:
            resolved.append(cid)
    return resolved

def main():
    youtube = get_youtube_client(API_KEY)
    visited_videos = load_visited_videos()

    # ✅ 핸들(@xxx)을 UCID로 변환
    final_channel_ids = resolve_channel_ids(youtube, CHANNEL_IDS)

    for channel_id in final_channel_ids:
        print(f"[START] 채널 {channel_id} 처리 시작")
        video_ids = get_video_ids_from_channel(youtube, channel_id, max_results=10)

        for vid in video_ids:
            if vid in visited_videos:
                print(f"[SKIP] 이미 방문한 영상 {vid}, 건너뜀")
                continue

            comments = get_top_level_comments(youtube, vid, max_pages=10)
            save_comments_to_file(vid, comments)
            mark_video_as_visited(vid)

            visited_videos.add(vid)

        print(f"[DONE] 채널 {channel_id} 처리 완료\n")

    print(f"[RESULT] 모든 채널 처리 완료. 개별 결과는 {COMMENTS_DIR} 폴더 확인.")


if __name__ == "__main__":
    main()
