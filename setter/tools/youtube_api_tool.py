# youtube_api_tool.py
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
