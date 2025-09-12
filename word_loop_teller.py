import os
import tempfile
import pandas as pd
from gtts import gTTS
from playsound import playsound
import winsound
import uuid
import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000000 | 0x00000001 | 0x00000002
)


TEMP_DIR = os.environ.get("TEMP", "setter\\temps")
os.makedirs(TEMP_DIR, exist_ok=True)  # 경로 없으면 생성


def beep_sound():
    winsound.Beep(440, 200)  # 1000Hz, 200ms

def speak_text(text: str, lang: str):
    if not text.strip():
        return

    # 안전한 랜덤 파일명 생성
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    temp_path = os.path.join(TEMP_DIR, filename)

    tts = gTTS(text=text, lang=lang)
    tts.save(temp_path)

    try:
        playsound(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except PermissionError:
            pass

def is_jp(word: str):
    for ch in word:
        code = ord(ch)
        # Hangul syllables
        if 0xAC00 <= code <= 0xD7AF:
            return "ko"
        # Hiragana
        elif 0x3040 <= code <= 0x309F:
            return "ja"
        # Katakana
        elif 0x30A0 <= code <= 0x30FF:
            return "ja"
        # CJK Unified Ideographs (Kanji)
        elif 0x4E00 <= code <= 0x9FFF:
            return "ja"
    return "ko"

def speak_words_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.sample(frac=1).reset_index(drop=True)
    for _, row in df.iterrows():
        japanese_word = str(row["T"])
        korean_meaning = str(row["D"])

        print(f"{japanese_word} : {str(row['P'])} : {korean_meaning}")
        speak_text(japanese_word, lang=is_jp(japanese_word))
        speak_text(korean_meaning, lang=is_jp(korean_meaning))

        
        beep_sound()


if __name__ == "__main__":
    csv_file = "words\\230835\\230835_1_60_focus.csv"
    while True :
        speak_words_from_csv(csv_file)