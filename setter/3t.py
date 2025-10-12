import os
import tempfile
from gtts import gTTS
from playsound import playsound
import openai
import re

import threading
import random; 


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

client = openai.OpenAI(api_key=api_key)

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
        raise ValueError("입력된 문장이 없습니다.")

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


def ask_gpt_translate(sentence: str) -> str:
    question = f"[{sentence}]의 한국어 뜻을 알려줘. 답변에는 오직 뜻만 포함하고, 부가 설명이나 다른 내용은 절대 포함하지 마. 대괄호 기호는 대답에서 제외해줘."
    try : 
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9
        )
        print(response.choices[0].message.content,end="\n:")
        #return clean_up(response.choices[0].message.content)
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None



def ask_gpt_is_good(sentence: str) -> str:
    question = f"[{sentence}]가 정상적인지 아닌지 🟢 와 🔴 중에 하나로 알려줘. 답변에는 이 글자들 중 단 하나만 출력 가능하고, 부가 설명이나 다른 내용은 절대 포함하지 마."
    try : 
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9
        )
        print(response.choices[0].message.content,end="\n:")

        #return clean_up(response.choices[0].message.content)
    except Exception as e:
        print("return_sentence_prompt e :",e)
        return None
    

def target_getter(target) :
    
    if "·" in target :
        target = target.split("·")
        
    

    if isinstance(target,str) :
        print(target)
    elif isinstance(target,list) :
        for cell in range(len(target)) :
            print(target[cell],end="")
            if not cell == len(target) - 1 :
                print("",end=" , ")


    if isinstance(target,str) and \
        not any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in target): 
        return True


    if isinstance(target,str) :
        speak_japanese(target)
        input()
    elif isinstance(target,list) :
        for cell in target :
            speak_japanese(cell)
            input()

t = [
["火","か","ひ·ほ","불, 열"],
["花","か","はな","꽃, 식물"],
["雨","う","あま·あめ","비, 하늘"],
["月","がつ·げつ","つき","달, 하늘"],
["金","きん·こん","かな·かね","금속, 재물"],
["玉","ぎょく","たま","구슬, 보석"],
["貝","","かい","조개, 화폐"],
["右","う·ゆう","みぎ","오른쪽, 방향"],
["下","か·げ","おりる·くだる·した","아래, 내려감"],
["空","くう","あく·あける·から·そら","비다, 하늘, 공간"],
["見","けん","みる·みえる·みせる","보다, 보이다"],
["学","がく","まなぶ","배우다"],
["休","きゅう","やすむ·やすめる","쉬다"],
["犬","けん","いぬ","개, 동물"],
["音","おん·いん","おと·ね","소리, 음악"],
["円","えん","まるい","둥글다, 돈, 형태"],
["五","ご","いつ·いつつ","숫자 다섯"],
]

td = {"火": {"e": [{"w": "火山", "ws": "かざん", "m": "화산", "s": "火山が爆発した。", "ss": "かざんがばくはつした。", "sm": "화산이 폭발했다."},{"w": "火を消す", "ws": "ひをけす", "m": "불을 끄다", "s": "火を消した。", "ss": "ひをけした。", "sm": "불을 껐다."}]},"花": {"e": [{"w": "花屋", "ws": "はなや", "m": "꽃집", "s": "花屋でバラを買った。", "ss": "はなやでばらをかった。", "sm": "꽃집에서 장미를 샀다."},{"w": "花が咲く", "ws": "はながさく", "m": "꽃이 피다", "s": "庭で花が咲いた。", "ss": "にわではながさいた。", "sm": "정원에 꽃이 피었다."}]},"雨": {"e": [{"w": "雨天", "ws": "うてん", "m": "우천, 비 오는 날", "s": "雨天のため試合は中止になった。", "ss": "うてんのためしあいはちゅうしになった。", "sm": "비가 와서 경기가 취소되었다."},{"w": "雨が降る", "ws": "あめがふる", "m": "비가 내리다", "s": "夜に雨が降った。", "ss": "よるにあめがふった。", "sm": "밤에 비가 내렸다."}]},"月": {"e": [{"w": "月曜日", "ws": "げつようび", "m": "월요일", "s": "月曜日は仕事がある。", "ss": "げつようびはしごとがある。", "sm": "월요일에는 일이 있다."},{"w": "月が出る", "ws": "つきがでる", "m": "달이 뜨다", "s": "山の上に月が出た。", "ss": "やまのうえにつきがでた。", "sm": "산 위로 달이 떠올랐다."}]},"金": {"e": [{"w": "金属", "ws": "きんぞく", "m": "금속", "s": "金属は熱で溶ける。", "ss": "きんぞくはねつでとける。", "sm": "금속은 열에 녹는다."},{"w": "お金を払う", "ws": "おかねをはらう", "m": "돈을 내다", "s": "お金を払った。", "ss": "おかねをはらった。", "sm": "돈을 냈다."}]},"玉": {"e": [{"w": "水玉", "ws": "みずたま", "m": "물방울 무늬", "s": "水玉のシャツを着た。", "ss": "みずたまのしゃつをきた。", "sm": "물방울 무늬 셔츠를 입었다."},{"w": "玉を投げる", "ws": "たまをなげる", "m": "공(구슬)을 던지다", "s": "子どもが玉を投げた。", "ss": "こどもがたまをなげた。", "sm": "아이가 공을 던졌다."}]},"貝": {"e": [{"w": "貝殻", "ws": "かいがら", "m": "조개껍데기", "s": "浜辺で貝殻を拾った。", "ss": "はまべでかいがらをひろった。", "sm": "해변에서 조개껍데기를 주웠다."},{"w": "貝を食べる", "ws": "かいをたべる", "m": "조개를 먹다", "s": "貝を焼いて食べた。", "ss": "かいをやいてたべた。", "sm": "조개를 구워 먹었다."}]},"右": {"e": [{"w": "右手", "ws": "みぎて", "m": "오른손", "s": "右手にペンを持つ。", "ss": "みぎてにぺんをもつ。", "sm": "오른손에 펜을 들었다."},{"w": "右に曲がる", "ws": "みぎにまがる", "m": "오른쪽으로 돌다", "s": "角を右に曲がった。", "ss": "かどをみぎにまがった。", "sm": "모퉁이에서 오른쪽으로 돌았다."}]},"下": {"e": [{"w": "地下鉄", "ws": "ちかてつ", "m": "지하철", "s": "地下鉄で通勤する。", "ss": "ちかてつでつうきんする。", "sm": "지하철로 출근한다."},{"w": "下に置く", "ws": "したにおく", "m": "아래에 두다", "s": "箱を下に置いた。", "ss": "はこをしたにおいた。", "sm": "상자를 아래에 두었다."}]},"空": {"e": [{"w": "空港", "ws": "くうこう", "m": "공항", "s": "空港で友達を迎えた。", "ss": "くうこうでともだちをむかえた。", "sm": "공항에서 친구를 맞이했다."},{"w": "空を見る", "ws": "そらをみる", "m": "하늘을 보다", "s": "空を見上げた。", "ss": "そらをみあげた。", "sm": "하늘을 올려다보았다."}]},"見": {"e": [{"w": "見学", "ws": "けんがく", "m": "견학", "s": "工場を見学した。", "ss": "こうじょうをけんがくした。", "sm": "공장을 견학했다."},{"w": "映画を見る", "ws": "えいがをみる", "m": "영화를 보다", "s": "映画を見た。", "ss": "えいがをみた。", "sm": "영화를 봤다."}]},"学": {"e": [{"w": "学生", "ws": "がくせい", "m": "학생", "s": "彼は大学の学生だ。", "ss": "かれはだいがくのがくせいだ。", "sm": "그는 대학생이다."},{"w": "日本語を学ぶ", "ws": "にほんごをまなぶ", "m": "일본어를 배우다", "s": "日本語を学んでいる。", "ss": "にほんごをまなんでいる。", "sm": "일본어를 배우고 있다."}]},"休": {"e": [{"w": "休日", "ws": "きゅうじつ", "m": "휴일", "s": "休日に出かけた。", "ss": "きゅうじつにでかけた。", "sm": "휴일에 외출했다."},{"w": "少し休む", "ws": "すこしやすむ", "m": "잠시 쉬다", "s": "少し休もう。", "ss": "すこしやすもう。", "sm": "잠깐 쉬자."}]},"犬": {"e": [{"w": "番犬", "ws": "ばんけん", "m": "집 지키는 개", "s": "番犬が吠えた。", "ss": "ばんけんがほえた。", "sm": "집 지키는 개가 짖었다."},{"w": "犬を飼う", "ws": "いぬをかう", "m": "개를 기르다", "s": "犬を飼っている。", "ss": "いぬをかっている。", "sm": "개를 기르고 있다."}]},"音": {"e": [{"w": "音楽", "ws": "おんがく", "m": "음악", "s": "音楽を聴くのが好きだ。", "ss": "おんがくをきくのがすきだ。", "sm": "음악 듣는 것을 좋아한다."},{"w": "音がする", "ws": "おとがする", "m": "소리가 나다", "s": "外で音がした。", "ss": "そとでおとがした。", "sm": "밖에서 소리가 났다."}]},"円": {"e": [{"w": "円形", "ws": "えんけい", "m": "원형", "s": "円形のテーブルを使う。", "ss": "えんけいのてーぶるをつかう。", "sm": "원형 테이블을 사용한다."},{"w": "百円を出す", "ws": "ひゃくえんをだす", "m": "100엔을 내다", "s": "百円を出した。", "ss": "ひゃくえんをだした。", "sm": "100엔을 냈다."}]},"五": {"e": [{"w": "五月", "ws": "ごがつ", "m": "5월", "s": "五月は花がきれいだ。", "ss": "ごがつははながきれいだ。", "sm": "5월에는 꽃이 예쁘다."},{"w": "五つ数える", "ws": "いつつかぞえる", "m": "다섯을 세다", "s": "五つ数えた。", "ss": "いつつかぞえた。", "sm": "다섯을 셌다."}]}}





#random.shuffle(t)


'''
#한자보이기
for i in t : 
    target = i[0]
    print(target)
    input()

'''

'''
#음독보이기
for i in t : 
    target = i[2]

    if "·" in target :
        target = target.split("·")
        
    print(target)
    if not any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' for c in target): 
        continue


    if isinstance(target,str) :
        speak_japanese(target)
        input()
    elif isinstance(target,list) :
        for cell in target :
            speak_japanese(cell)
            input()

'''



'''
#한자보고 음독맞추기
for i in range(len(t)) : 
    target = t[i][0]
    

    print(target)

    td_l = td[target]["e"]
    for td_cell in td_l :
        #w,ws,m,s,ss
        print(td_cell["w"])
        print(td_cell["ws"])
        speak_japanese(td_cell["w"])
        input()
        print(td_cell["m"])
        input()
        print(td_cell["s"])
        print(td_cell["ss"])
        speak_japanese(td_cell["s"])
        input()
        print(td_cell["sm"])
        input()

    input()

    target_getter(t[i][1])
    target_getter(t[i][2])


'''
        




#한자보고 음독맞추기
for i in range(len(t)) : 
    target = t[i][0]
    


    td_l = td[target]["e"]
    for td_cell in td_l :
        print(td_cell["w"])
        if input() == "1" : print(f'{td_cell["ws"]}\n{td_cell["m"]}')
        print()
        print(td_cell["s"])
        if input() == "1" : print(f'{td_cell["ss"]}\n{td_cell["sm"]}')
        print()
        print()