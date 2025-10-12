
import customtkinter as ctk
import webbrowser
import csv
import sys 
import pyperclip
import ctypes
import requests
from bs4 import BeautifulSoup
import webbrowser
import tempfile
import os
import subprocess
import json
import random

import ast
import unicodedata
import time
from collections import Counter


from multiprocessing import Pool, cpu_count
from requests.exceptions import HTTPError









def extract_kousei_parts(detail_url: str):
    """
    상세페이지에서, <span class="separator2">가 있는 <li>만,
    해당 li의 출력 텍스트(예: '广＋心')를 리스트에 담아 반환
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    print("detail_url :",detail_url)
    
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


def open_kanji_detail_by_unicoded_word(unicoded_word: str):
    """
    지정한 유니코드 한자(16진수)에 대한 jitenon 검색 결과 페이지에서
    class에 'ajax'와 'color1'이 모두 포함된 첫번째 <a>의 href로 이동
    """

    while True : 
        try : 
            url = f"https://kanji.jitenon.jp/cat/search?getdata=-{unicoded_word}-"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 요청 실패시 예외 발생
            break
        except HTTPError as e:
            # 429 (Too Many Requests)일 때만 재시도
            if e.response is not None and e.response.status_code == 429:
                print("429 Too Many Requests — 60초 후 재시도합니다.")
                time.sleep(60)
                continue
            else:
                # 다른 HTTP 오류는 그대로 던져서 프로그램이 멈춤
                raise


    soup = BeautifulSoup(response.text, "html.parser")
    return_url = None
    # 모든 <a> 태그 중 class에 ajax, color1 둘 다 포함된 첫번째 태그 찾기
    for a in soup.find_all("a"):
        class_list = a.get("class", [])
        if "ajax" in class_list and "color1" in class_list:
            return_url = f"{a.get("href")}#m_kousei"
            #webbrowser.open(return_url)
            return return_url
        
    print(f"unicoded_word : {unicoded_word} / class에 'ajax'와 'color1'이 모두 포함된 <a> 태그를 찾을 수 없습니다.")
    for a in soup.find_all("a"):
        class_list = a.get("class", [])
        if "ajax" in class_list :
            return_url = f"{a.get("href")}#m_kousei"
            #webbrowser.open(return_url)
            return return_url
        
    print(f"unicoded_word : {unicoded_word} / class에 'ajax'가 모두 포함된 <a> 태그를 찾을 수 없습니다.")



target_list = ["話","語","文","私","考","習","成","例","単","言","日","確","練","思","自","今","実","構","分","理","果","方","中","一","間","状","本","使","際","問","時","的","感","法","作","出","態","提","何","解","書","学","正","認","意","用","葉","造","案","直","要","現","強","点","勉","題","伝","然","会","明","対","度","内","知","違","況","容","心","形","目","不","韓","整","場","見","修","国","表","持","安","後","大","章","効","記","遅","味","観","頭","前","動","必","質","気","合","少","信","聞","緒","詞","面","化","手","身","能","立","体","定","改","善","部","段","再","主","階","憶","難","最","人","力","昨","秒","識","通","次","流","回","行","切","察","短","以","覚","近","完","上","準","由","眠","重","説","余","番","返","換","望","希","向","決","悪","多","相","性","備","価","先","結","評","困","式","視","裕","探","応","断","可","特","補","訓","訳","長","順","願","止","情","子","別","発","翻","適","論","答","事","具","関","接","足","繰","着","類","含","判","全","組","根","団","選","変","処","生","験","同","新","途","元","十","外","求","基","即","負","始","配","敗","誰","挙","因","機","析","指","曖","誤","夫","担","当","有","図","件","条","失","素","経","昧","続","起","置","減","混","役","宙","取","興","設","原","悩","疑","索","活","渡","圧","反","朝","欲","高","証","差","早","簡","声","慣","録","速","示","試","運","計","型","乱","率","供","初","象","宇","丈","係","純","述","似","非","制","替","進","迷","瞬","項","復","利","期","努","落","従","種","筋","比","引","共","受","他","縮","践","注","教","台","彙","翌","小","移","姿","択","張","交","検","景","和","読","込","代","較","音","下","名","数","来","予","勢","釈","買","摘","常","背","残","埋","写","支","承","浮","物","傾","了","地","固","測","限","丁","工","為","母","握","脈","旨","得","申","描","戦","良","急","志","焦","標","紙","保","囲","禁","柔","句","肢","核","範","黙","湧","般","頼","伺","想","報","超","責","嬉","食","材","座","程","序","絶","誠","援","様","増","寧","徴","開","慎","終","飾","料","演","談","在","集","把","針","仰","沿","戻","口","雑","調","異","略","振","越","軸","降","抜","普","拠","割","参","値","無","軟","複","展","統","優","入"]



res = []
for target in target_list : 
    parts = extract_kousei_parts(open_kanji_detail_by_unicoded_word(f"{format(ord(target), '04X')}"))
    for part in parts : res.extend(list(part))

    
''''
def process_target(target):
    # target 하나를 처리하는 함수
    parts = extract_kousei_parts(
        open_kanji_detail_by_unicoded_word(f"{format(ord(target), '04X')}")
    )
    # 각 part를 list로 확장해 반환
    res = []
    for part in parts:
        res.extend(list(part))
    return res

if __name__ == "__main__":
    with Pool(cpu_count()) as pool:
        results = pool.map(process_target, target_list)

    # 결과 평탄화 (2차원 리스트 → 1차원 리스트)
    res = [item for sublist in results for item in sublist]
'''

print("res :",res)



{'k': '話', 's': 'わ', 'm': 'はなし·はなす', 'p': '言 (7획)'}
{'k': '優', 's': 'ゆう', 'm': 'すぐれる·やさしい', 'p': '亻 (2획)'}
{'k': '入', 's': 'にゅう', 'm': 'いる·いれる·はいる', 'p': '入 (2획)'}