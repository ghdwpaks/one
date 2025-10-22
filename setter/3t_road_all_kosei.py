
import requests
from bs4 import BeautifulSoup
import webbrowser
from requests import HTTPError
import time

tl = list("引安")
tl = list("悪安暗医委意育員院飲運泳駅央横屋温化荷界開階寒感漢館岸起期客究急級宮球去橋業曲局銀区苦具君係軽血決研県庫湖向幸港号根祭皿仕死使始指歯詩次事持式実写者主守取酒受州拾終習集住重宿所暑助昭消商章勝乗植申身神真深進世整昔全相送想息速族他打対待代第題炭短談着注柱丁帳調追定庭笛鉄転都度投豆島湯登等動童農波配倍箱畑発反坂板皮悲美鼻筆氷表秒病品負部服福物平返勉放味命面問役薬由油有遊予羊洋葉陽様落流旅両緑礼列練路和")
td = {}

def open_kanji_detail_by_unicoded_word(unicoded_word: str):
    """
    지정한 유니코드 한자(16진수)에 대한 jitenon 검색 결과 페이지에서
    class에 'ajax'와 'color1'이 모두 포함된 첫번째 <a>의 href로 이동
    """
    url = f"https://kanji.jitenon.jp/cat/search?getdata=-{unicoded_word}-"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    while True : 
        response = requests.get(url, headers=headers)
        try : 
            if response.status_code == 429 : 
                print("429")
                time.sleep(60)
                continue

            response.raise_for_status()  # 요청 실패시 예외 발생
            break
        except HTTPError as e: 
            print('HTTPError e :',e)
            time.sleep(60)
            continue

    soup = BeautifulSoup(response.text, "html.parser")
    return_url = None
    # 모든 <a> 태그 중 class에 ajax, color1 둘 다 포함된 첫번째 태그 찾기
    for a in soup.find_all("a"):
        class_list = a.get("class", [])
        if "ajax" in class_list and "color1" in class_list:
            return_url = f"{a.get('href')}#m_kousei"
            #webbrowser.open(return_url)
            return return_url
        
    print(f"unicoded_word : {unicoded_word} / class에 'ajax'와 'color1'이 모두 포함된 <a> 태그를 찾을 수 없습니다.")
    for a in soup.find_all("a"):
        class_list = a.get("class", [])
        if "ajax" in class_list :
            return_url = f"{a.get('href')}#m_kousei"
            #webbrowser.open(return_url)
            return return_url
        
    print(f"unicoded_word : {unicoded_word} / class에 'ajax'가 모두 포함된 <a> 태그를 찾을 수 없습니다.")


    

def extract_kousei_parts(detail_url: str):
    """
    상세페이지에서, <span class="separator2">가 있는 <li>만,
    해당 li의 출력 텍스트(예: '广＋心')를 리스트에 담아 반환
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    res = requests.get(detail_url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    result = []
    # 모든 <li> 검사
    for li in soup.find_all("li"):
        # li 안에 <span class="separator2">가 있으면
        if li.find("span", class_="separator2"):
            text = li.get_text(strip=True)
            result.append(f"{text} = ")
    return result


for target in tl :
    url = open_kanji_detail_by_unicoded_word(f"{format(ord(target), '04X')}")

    parts = extract_kousei_parts(url)
    for part_idx in range(len(parts)):
        parts[part_idx] = f"{parts[part_idx]}{target}"
    td[target] = parts
    print("parts :",parts)

print("td :",td)