k = ["日本","大統領","発表","会社","中国","警察","死亡","女性","男性","去年","今年","政府","必要","影響","予定","理由","世界","事故","確認","東京","問題","可能性","攻撃","一方","事件","場所","時間","病院","被害","発生","億円","値段","仕事","選手","万円","今回","地震","万人","関税","今月","今後","自分","場合","逮捕","説明","原因","試合","情報","韓国","内容","対応","記事","結果","地域","状況","以上","一部","調査","建物","指摘","参加","家族","一緒","学校","先月","映画","年前","人気","合意","値上","日午前","販売","大学","新型","安全","方針","政権","日本人","避難","石破総理大臣","大切","危険","価格","日午後","現場","飛行機","見通","現在","写真","生活","相次","専門家","判断","支援","人以上","上昇","気象庁","年間","利用","計画","目指","大雨","運転","住宅","病気","心配","外国人","会談","法律","主張","企業","容疑者","名前","対象","投稿","午後","公開","輸入","意見","国内","来年","火事","状態","研究","見込","工場","大会","大谷選手","懸念","活動","様子","施設","当時","予想","気温","回目","午前","商品","地元","捜査","実施","首都","現地","記録","戦争","気持","関係","協議","取材","拡大","検討","非常","通信","協力","動画","強調","交渉","中心","反対","住民","経済","開催","増加","映像","首相","注意","爆発","禁止","複数","自民党","強化","各地","団体","発見","技術","全国","最大","報告","大阪","旅行","国民","遺体","会議","会場","来月","自宅","週間","外国","空港","警視庁","使用","関税措置","優勝","自動車","対策","北海道","消防","選挙","有名","記述","批判","大規模","台風","部屋","準備","本当","紹介","実現","市場","輸出","開発","日間","提供","感染","全部","時期","台湾","最初","観測","北朝鮮","警察官","裁判","当局","地球","地区","南部","大幅","税金","津波","最後","十分","学生","店舗","重要","平均","海外","時半","上回","電気","導入","東京都","警戒","日夜","連絡","撮影","支持","勉強","火災","決定","措置","減少","殺害","通報","母親","再開","方法","拘束","記者会見","国連","生産","議論","平和","熱中症","衝突","裁判所","搬送","市民","関係者","道路","注目","自身","職員","大手","最近","事実","利益","設置","停止","月日","電話","観光客","日本円","出席"]
l = [

]

import re
import os

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_brackets(text):
    # 숫자와 점 다음에 오는 괄호를 처리하는 정규 표현식
    numbered_bracket_pattern = re.compile(r"\d+\.\s*\([^)]+\)")
    
    # 숫자와 점 다음에 오는 괄호를 일시적으로 보호하기 위한 플레이스홀더
    placeholders = {}
    
    # numbered_bracket_pattern에 해당하는 모든 부분을 찾아서 일시적으로 대체
    def protect_numbered_brackets(match):
        placeholder = f"PLACEHOLDER_{len(placeholders)}"
        placeholders[placeholder] = match.group(0)
        return placeholder
    
    # 보호할 괄호 부분 대체
    protected_text = numbered_bracket_pattern.sub(protect_numbered_brackets, text)
    
    # 보호하지 않은 일반 괄호 처리
    def replace(match):
        content = match.group(1)
        if re.fullmatch(r"[\uAC00-\uD7AF]{1,3}", content):
            return f"({content})"
        else:
            return ""

    result = re.sub(r"\(([^)]+)\)", replace, protected_text)
    
    # 보호했던 부분을 원래대로 복구
    for placeholder, original in placeholders.items():
        result = result.replace(placeholder, original)
    
    return result

def find_next_sentence(text, keyword, number=1):
    # 텍스트를 줄바꿈으로 분리하여 문장 리스트 생성
    sentences = text.split('\n')
    # 키워드가 포함된 문장을 찾고 다음 문장을 반환
    for i in range(len(sentences) - 1):
        if keyword in sentences[i]:
            return sentences[i + number]  # 다음 문장 반환
    return "키워드를 포함하는 문장이 없습니다."

 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


for kan in k :
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # 로그 레벨 최소화

    service = Service(log_output=subprocess.DEVNULL)  # 로그 숨김
    service = Service(log_output=subprocess.DEVNULL)
    os.environ['WDM_LOG'] = '0'
    driver = webdriver.Chrome(options=options, service=service)  # ChromeDriver 필요
    driver.get(f"https://ja.dict.naver.com/#/search?query={kan}&range=all")

    if len(kan) > 1 : 
        
        # 원하는 데이터 추출
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "has-saving-function"))
        )
        
        t = remove_brackets(elements[0].text)
        #한자, 발음, 뜻,
        end_keyword = "민중서림 엣센스 일한사전"
        t = t.split(end_keyword)[0]

        t_splited = t.split("\n")
        발음 = t_splited[0].split("[")[0].strip()
        
        
        뜻 = ""
        품사 = find_next_sentence(t, '단어장에 저장')
        뜻_부분 = find_next_sentence(t, '단어장에 저장', number=2)
        pattern = r'^\d+\.'
        print("*"*88)
        if re.match(pattern, 뜻_부분):
            뜻_부분 = ""
            #뜻이 여러개
            
            뜻_시작_줄 = 0 
            for i in range(len(t_splited) - 1):
                if '단어장에 저장' in t_splited[i]:
                    i = i + 1
                    break


            뜻 += f"[{t_splited[i]}] "#품사
            while True :
                i += 1
                if len(t_splited)-1 <= i   : break # -1 은 문단 뒤에 있는 '민중서림 엣센스 일한사전' 부분을 없애기 위해서이다.
                if re.match(pattern, t_splited[i]) : #숫자가 맞는지
                    뜻 += f"{t_splited[i]}".strip() # 숫자
                    i += 1
                    뜻 += f"{t_splited[i]}".strip().replace(".","")+" " # 의미
                else :
                    padding = ""
                    if not 뜻[-1] == " " :
                        padding = " "
                    #품사가 있다는 의미
                    뜻 += f"{padding}/ [{t_splited[i]}] "#품사
                    
                    continue #품사 기록하고 처음으로 돌아가기
                    
        else:
            #뜻이 한개
            뜻 = f"[{품사}] {뜻_부분}"

        print("발음 :",발음)
        print("뜻 :",뜻)
        t = {
            "kan":kan,
            "sound":발음,
            "mean":뜻.strip()
            }
        print("ghdwpaks"*3,t)
        l.append(t)


    
    else : 



        # 원하는 데이터 추출
        elements = driver.find_elements(By.CLASS_NAME, "addition_info")  # 클래스 이름을 변경해야 할 수 있음
        for element in elements:
            print("len(kan) :",len(kan))

            #단일글자라면
            t = {"k":kan,"s":"","m":"","p":""}

            # 줄 단위로 텍스트를 분리
            lines = element.text.strip().split("\n")

            # "음독"과 "훈독" 다음 줄의 내용을 추출하여 t 변수에 추가
            for i, line in enumerate(lines):
                if line == "음독" and i + 1 < len(lines):
                    t["s"] += lines[i + 1]  # 음독 다음 줄을 "s"에 추가
                elif line == "훈독" and i + 1 < len(lines):
                    t["m"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
                elif line == "부수" and i + 1 < len(lines):
                    t["p"] += lines[i + 1]  # 훈독 다음 줄을 "m"에 추가
            print(t)
            l.append(t)

    driver.quit()

print(l)



