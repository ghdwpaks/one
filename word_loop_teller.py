import os
import tempfile
import pandas as pd
from gtts import gTTS
from playsound import playsound
import winsound

import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000000 | 0x00000001 | 0x00000002
)


def beep_sound():
    winsound.Beep(440, 200)  # 1000Hz, 200ms

def speak_text(text: str, lang: str):
    if not text.strip():
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang=lang)
        tts.save(fp.name)
        temp_path = fp.name

    try:
        playsound(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except PermissionError:
            pass


def speak_words_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.sample(frac=1).reset_index(drop=True)
    for _, row in df.iterrows():
        japanese_word = str(row["T"])
        korean_meaning = str(row["D"])

        print(f"{japanese_word} : {str(row['P'])} : {korean_meaning}")
        speak_text(japanese_word, lang="ja")
        speak_text(korean_meaning, lang="ko")

        
        beep_sound()


if __name__ == "__main__":
    csv_file = "words\\loop_target.csv"
    while True :
        speak_words_from_csv(csv_file)