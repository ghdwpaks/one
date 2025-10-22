import os
import tempfile
from gtts import gTTS
from playsound import playsound
import re

import msvcrt

import ctypes
import sys


def hide_cursor():
    """Windows 콘솔 커서 숨기기"""
    class CONSOLE_CURSOR_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_int),
                    ("bVisible", ctypes.c_bool)]

    handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    cursor_info = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(cursor_info))
    cursor_info.bVisible = False
    ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

def show_cursor():
    """Windows 콘솔 커서 복원"""
    class CONSOLE_CURSOR_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_int),
                    ("bVisible", ctypes.c_bool)]

    handle = ctypes.windll.kernel32.GetStdHandle(-11)
    cursor_info = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(cursor_info))
    cursor_info.bVisible = True
    ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

def nocur(prompt: str = "") -> str:
    """
    Windows 전용 한 줄 입력 함수.
    - prompt 출력, 커서 숨김, 줄 편집 후 문자열 반환.
    - Ctrl+C: KeyboardInterrupt 발생 (즉시).
    - Ctrl+Z 후 Enter: EOFError (input() 호환).
    - 화살표/홈/엔드는 무시(간단 모드).
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    hide_cursor()
    buf: list[str] = []
    try:
        while True:
            ch = msvcrt.getwch()  # 유니코드 키 1글자

            # Ctrl+C → KeyboardInterrupt (의도적으로 즉시 중단)
            if ch == '\x03':
                raise KeyboardInterrupt

            # Ctrl+Z → EOF (Windows input() 동작과 일치)
            if ch == '\x1a':
                sys.stdout.write('\n')
                sys.stdout.flush()
                raise EOFError

            # Enter → 입력 확정
            if ch in ('\r', '\n'):
                sys.stdout.write('\n')
                sys.stdout.flush()
                return ''.join(buf)

            # Backspace → 한 글자 삭제
            if ch in ('\b', '\x7f'):
                if buf:
                    buf.pop()
                    # 콘솔에서 시각적으로 1칸 지우기
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                continue

            # 특수키(화살표/기능키) 프리픽스 → 다음 코드 소비 후 무시
            if ch in ('\x00', '\xe0'):
                _ = msvcrt.getwch()
                continue

            # 일반 문자 입력
            buf.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
    finally:
        # 예외/종료 모두에서 커서 복구 보장
        show_cursor()



def clean_up(s: str) -> str :
    try : 
        text = s.replace('[', '').replace(']', '')
        
        pattern = r'([가-힣a-zA-Z_])\.'
        replaced = re.sub(pattern, r'\1', text)
        print("replaced :",replaced)
        return replaced
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None

def speak_japanese(text: str, slow: bool = False):
    if not text.strip():
        print("[speak_japanese]:입력된 문장이 없습니다.")
        return 
    # 임시 mp3 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang="ja", slow=slow)
        tts.save(fp.name)
        temp_path = fp.name

    try:
        playsound(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except PermissionError:
            pass  # 재생 중이면 OS가 나중에 정리