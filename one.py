csv_file_path = "z_out175734_21_41.csv"

#Caps Lock 주의!!!

#1 : 네이버 일본어 사전에서 부수 검색
#2 : 네이버 일본어 사전에서 음독 검색
#3 : 네이버 일본어 사전에서 훈독 검색
#4 : 네이버 일본어 사전에서 한국어 뜻 검색
#Q : GPT 한테 할 질문 복사
#E : 현재 보고있는 한자 복사

#Ctrl + 3 : 한자와 (여러개의) 훈독을 여러줄로 VS Code 로 열기

#(복수한자단어시험의 경우)
#현재 단어의 
#z : 1번째 한자 검색
#x : 2번째 한자 검색
#c : 3번째 한자 검색

#Shift + z : 1번째 한자 복사
#Shift + x : 2번째 한자 복사
#Shift + c : 3번째 한자 복사

#Ctrl + z : 1번째 한자를 GPT에게 질문하는 글 복사
#Ctrl + x : 2번째 한자를 GPT에게 질문하는 글 복사
#Ctrl + c : 3번째 한자를 GPT에게 질문하는 글 복사

#Alt + z : 1번째 한자를 kanji.jitenon.jp 에 검색하고, 구성한자를 VS Code 로 열기
#Alt + x : 2번째 한자를 kanji.jitenon.jp 에 검색하고, 구성한자를 VS Code 로 열기
#Alt + c : 3번째 한자를 kanji.jitenon.jp 에 검색하고, 구성한자를 VS Code 로 열기

#; : 시험종료 및 결과(를 CMD 창에)출력

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

import tool

font_size = 64#32,64
font_info = {
    "title_label":20,
    "info_label":14,
    "num_parts_label":14,
    "current_part_label":14,
    "p_label":font_size,
    "s_label":font_size,
    "m_label":font_size,
    "km_label":font_size,
    "end_label":font_size,
    "kanji_font_size":360,#360,240
}


# CSV 파일 읽기
def read_and_process_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        processed_data = []
        for row in reader:
            # 필드 이름 변경
            row['k'] = row.pop('T')  # 'T' -> 'k'
            row['km'] = row.pop('D')  # 'D' -> 'km'
            if 'E' in row.keys() : 
                row['p'] = row.pop('E')
            else :
                row['p'] = ""

            if "/" in row['P'] :
                p_split = row.pop('P').split('/')  # 'P'를 'E'로 나누어 처리
                row['s'] = p_split[0] if len(p_split) > 0 else ""  # 'p'로 첫 번째 값 저장
                row['m'] = p_split[1] if len(p_split) > 1 else ""  # 'm'로 두 번째 값 저장
            else :
                row['s'] = row.pop('P')
                row['m'] = ""

            processed_data.append(row)
    return processed_data




# 단일한자데이터시트 예시
single_kanji_data = [{'k': '定', 'km': '(결)정', 'p': '宀 (3획)', 's': 'じょう·てい', 'm': 'さだまる·さだめる·さだか', 'knows': 0}]


test_data = read_and_process_csv(csv_file_path)
test_data = single_kanji_data


file_path = tool.open_csv(called_from_one=True)
test_data = read_and_process_csv(file_path)

# CustomTkinter 테마 설정
ctk.set_appearance_mode("dark")  # 다크 모드
ctk.set_default_color_theme("blue")  # 기본 색상 테마


for row in test_data:
    if not "knows" in row.keys() :
        row['knows'] = 0

class FlashcardApp(ctk.CTk):
    def __init__(self):
        
        super().__init__()
        self.disable_capslock()
        self.title("플래시카드 - 뜻 화면과 단어 화면 전환")
        self.geometry("400x500")
        self.resizable(False, False)

        # 화면 전환을 위한 변수
        self.is_meaning_screen = True
        self.current_index = 0  # 현재 단어 인덱스
        self.visited = [False] * len(test_data)  # 방문 여부를 추적하는 리스트
        self.remaining_data = test_data  # 방문 여부를 추적하는 리스트

        # '뜻 화면' 구성
        self.meaning_frame = ctk.CTkFrame(self)
        self.setup_meaning_frame()

        # '단어 화면' 구성
        self.word_frame = ctk.CTkFrame(self)
        self.setup_word_frame()

        # 첫 화면은 '뜻 화면'
        self.show_word_screen()

        # 키보드 입력 바인딩
        self.bind("<Up>", self.toggle_screen)  # 화살표 위쪽 키로 화면 전환
        
        self.bind("<Left>", self.unknown_action)  # 왼쪽 방향키로 '모르겠어요'
        self.bind("<Right>", self.known_action)  # 오른쪽 방향키로 '알겠어요'

        self.bind("w", self.toggle_screen);self.bind("W", self.toggle_screen) # 화살표 위쪽 키로 화면 전환
        

        self.bind("a", self.unknown_action);self.bind("A", self.unknown_action) # 'a' 키 입력으로 '모르겠어요'
        self.bind("d", self.known_action);self.bind("D", self.known_action) # 'd' 키 입력으로 '알겠어요'
        
        
        self.bind("1", lambda event: self.search(1))
        self.bind("2", lambda event: self.search(2))
        self.bind("3", lambda event: self.search(3, event=event))
        self.bind("4", lambda event: self.search(4))
        self.bind("q", lambda event: self.search(11));self.bind("Q", lambda event: self.search(11))
        self.bind("e", lambda event: self.search(12));self.bind("E", lambda event: self.search(12))
        self.bind(";", lambda event: self.search(13))


        word = self.remaining_data[self.current_index]['k']
        self.search_keys = ["z", "x", "c"]  # 할당할 키 목록

        #여러개의 한자를 시험볼 경우의 1,2,3 번째 한자 검색
        for i, key in enumerate(self.search_keys):
            if len(word) > i:
                self.bind(key, lambda event, w=key: self.search(target=1,word=w)) #소문자 입력 감지
                self.bind(key.upper(), lambda event, w=key: self.search(target=1,word=w)) #대문자 입력 감지

        #여러개의 한자를 시험볼 경우의 1,2,3 번째 한자 복사
        for i, key in enumerate(self.search_keys):
            if len(word) > i:
                self.bind(f"<Shift-{key}>", lambda event, w=key: self.search(target=2,word=w)) #소문자 입력 감지
                self.bind(f"<Shift-{key.upper()}>", lambda event, w=key: self.search(target=2,word=w)) #대문자 입력 감지

        #여러개의 한자를 시험볼 경우의 1,2,3 번째 한자에 대한 GPT 질문글 복사
        for i, key in enumerate(self.search_keys):
            if len(word) > i:
                self.bind(f"<Control-{key}>", lambda event, w=key: self.search(target=3,word=w)) #소문자 입력 감지
                self.bind(f"<Control-{key.upper()}>", lambda event, w=key: self.search(target=3,word=w)) #대문자 입력 감지

        #여러개의 한자를 시험볼 경우의 1,2,3 번째 한자 복사
        for i, key in enumerate(self.search_keys):
            if len(word) > i:
                self.bind(f"<Alt-{key}>", lambda event, w=key: self.search(target=4,word=w)) #소문자 입력 감지
                self.bind(f"<Alt-{key.upper()}>", lambda event, w=key: self.search(target=4,word=w)) #대문자 입력 감지
        

        self.bind(f"<Control-{3}>", lambda event, w=3: self.search(target=5,word=w)) #소문자 입력 감지
        


        #여러개의 한자를 시험볼 경우의 1,2,3 번째 한자
        #z : 검색
        #x : 복사
        #c : 에 대한 GPT 질문글 복사
        word = self.remaining_data[self.current_index]['k']
        modifiers = [("", 1), ("<Shift-", 2), ("<Control-", 3)]  # (키 접두어, target 값)

        for i, key in enumerate(self.search_keys):
            if len(word) > i:
                for mod, target in modifiers:
                    self.bind(f"{mod}{key}>", lambda event, w=key, t=target: self.search(target=t, word=w))
                    self.bind(f"{mod}{key.upper()}>", lambda event, w=key, t=target: self.search(target=t, word=w))

        self.resizable(True, True)

        self.num_parts = 1  # 분할 개수
        self.current_part = 1  # 현재 선택된 부분


        # 진행 바 추가
        self.progress_bar = ctk.CTkProgressBar(self, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)  # 초기 진행률: 0%

        shortcuts = self.load_shortcuts_from_json('setting.json')
        self.bind_shortcuts_from_setting(shortcuts)


        # 초기 화면 구성
        self.show_initial_screen()

        #self.focus_set()




    def load_shortcuts_from_json(self,json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get('shortcuts', [])

    def to_tkinter_key(self,key):
        # "Ctrl+z" → "<Control-z>", "Shift+z" → "<Shift-Z>", "Alt+x" → "<Alt-x>" 등 변환
        key = key.replace('Ctrl', 'Control')
        if '+' in key:
            mods, k = key.split('+')
            # 대소문자 구분 주의! (tkinter는 대문자=Shift)
            if 'Shift' in mods:
                k = k.upper()
            return f'<{mods}-{k}>'
        else:
            # 방향키는 그대로, 일반키는 대소문자 구분 없이 2개 바인딩 필요
            return key

    def bind_shortcuts_from_setting(self, shortcuts):
        for shortcut in shortcuts:
            key = shortcut['key']
            tk_key = self.to_tkinter_key(key)
            action_name = shortcut['action']
            params = shortcut.get('params', {})
            # 함수 가져오기(존재하지 않으면 skip)
            action = getattr(self, action_name, None)
            if not action:
                print(f"경고: {action_name} 함수가 없습니다.")
                continue

            # 파라미터 유무에 따라 람다로 감싸기 (event는 항상 넘겨야 함)
            if params:
                # dict를 **로 넘길 수 있도록 처리
                def make_callback(action, params):
                    return lambda event=None: action(event=event, **params)
                callback = make_callback(action, params)
            else:
                callback = action

            # 일반키면 대/소문자 모두 바인딩
            if len(key) == 1 and key.isalpha():
                self.bind(key, callback)
                self.bind(key.upper(), callback)
            else:
                self.bind(tk_key, callback)



    def extract_kousei_parts(self, detail_url: str):
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

    def open_kanji_detail_by_unicoded_word(self, unicoded_word: str):
        """
        지정한 유니코드 한자(16진수)에 대한 jitenon 검색 결과 페이지에서
        class에 'ajax'와 'color1'이 모두 포함된 첫번째 <a>의 href로 이동
        """
        url = f"https://kanji.jitenon.jp/cat/search?getdata=-{unicoded_word}-"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 요청 실패시 예외 발생

        soup = BeautifulSoup(response.text, "html.parser")
        return_url = None
        # 모든 <a> 태그 중 class에 ajax, color1 둘 다 포함된 첫번째 태그 찾기
        for a in soup.find_all("a"):
            class_list = a.get("class", [])
            if "ajax" in class_list and "color1" in class_list:
                return_url = f"{a.get("href")}#m_kousei"
                webbrowser.open(return_url)
                return return_url
            
        print(f"unicoded_word : {unicoded_word} / class에 'ajax'와 'color1'이 모두 포함된 <a> 태그를 찾을 수 없습니다.")
        for a in soup.find_all("a"):
            class_list = a.get("class", [])
            if "ajax" in class_list :
                return_url = f"{a.get("href")}#m_kousei"
                webbrowser.open(return_url)
                return return_url
            
        print(f"unicoded_word : {unicoded_word} / class에 'ajax'가 모두 포함된 <a> 태그를 찾을 수 없습니다.")



    def update_progress_bar(self):
        """진행 바 업데이트"""
        progress = (self.current_index + 1) / len(self.remaining_data)  # 진행률 계산
        self.progress_bar.set(progress)  # 진행률 업데이트

    def show_initial_screen(self):
        """시험 설정 화면 표시"""
        # 설명 텍스트
        self.title_label = ctk.CTkLabel(self, text="시험 설정", font=("맑은 고딕", 20))
        self.title_label.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text=f"총 단어 수: {len(self.remaining_data)}", font=("맑은 고딕", 14))
        self.info_label.pack()

        # 등분 설정
        self.num_parts_label = ctk.CTkLabel(self, text=f"등분: {self.num_parts}", font=("맑은 고딕", 14))
        self.num_parts_label.pack(pady=5)

        self.num_parts_minus = ctk.CTkButton(self, text="-", command=lambda: self.update_num_parts(-1), width=50)
        self.num_parts_minus.pack(side="left", padx=5)

        self.num_parts_plus = ctk.CTkButton(self, text="+", command=lambda: self.update_num_parts(1), width=50)
        self.num_parts_plus.pack(side="left", padx=5)

        # 파트 선택
        self.current_part_label = ctk.CTkLabel(self, text=f"파트: {self.current_part}", font=("맑은 고딕", 14))
        self.current_part_label.pack(pady=5)

        self.current_part_minus = ctk.CTkButton(self, text="-", command=lambda: self.update_current_part(-1), width=50)
        self.current_part_minus.pack(side="left", padx=5)

        self.current_part_plus = ctk.CTkButton(self, text="+", command=lambda: self.update_current_part(1), width=50)
        self.current_part_plus.pack(side="left", padx=5)

        # 설정 완료 버튼
        self.start_button = ctk.CTkButton(self, text="시작하기", command=self.start_exam)
        self.start_button.pack(pady=20)

    def update_num_parts(self, change):
        """등분 값 업데이트"""
        max_parts = len(self.remaining_data)
        self.num_parts = max(1, min(self.num_parts + change, max_parts))  # 1 이상, 데이터 길이 이하
        self.num_parts_label.configure(text=f"등분: {self.num_parts}")

    def update_current_part(self, change):
        """현재 파트 값 업데이트"""
        self.current_part = max(1, min(self.current_part + change, self.num_parts))  # 1 이상, 등분 값 이하
        self.current_part_label.configure(text=f"파트: {self.current_part}")

    def start_exam(self):
        """시험 데이터 설정 및 시작"""
        # 선택된 데이터를 분할
        total = len(self.remaining_data)
        chunk_size = total // self.num_parts
        start_idx = (self.current_part - 1) * chunk_size
        end_idx = start_idx + chunk_size

        self.remaining_data = self.remaining_data[start_idx:end_idx]
        
        self.visited = [False] * len(self.remaining_data)  # 방문 여부를 추적하는 리스트

        # 설정 완료 후 기존 시험 로직으로 넘어가기

        self.destroy_initial_screen()

    def destroy_initial_screen(self):
        """초기 설정 화면 삭제"""
        self.title_label.destroy()
        self.info_label.destroy()
        self.num_parts_label.destroy()
        self.num_parts_minus.destroy()
        self.num_parts_plus.destroy()
        self.current_part_label.destroy()
        self.current_part_minus.destroy()
        self.current_part_plus.destroy()
        self.start_button.destroy()

        self.focus_set()

    # '뜻 화면' 구성
    def setup_meaning_frame(self):
        # 파란색 영역 (p)
        self.p_label = ctk.CTkLabel(self.meaning_frame, text="",  text_color="#ADD8E6", font=("나눔바른고딕", font_info["p_label"]), height=60)
        self.p_label.pack(pady=5, fill="x")

        # 어두운 초록 영역 (s)
        self.s_label = ctk.CTkLabel(self.meaning_frame, text="", text_color="#90EE90", font=("나눔바른고딕", font_info["s_label"]), height=30)
        self.s_label.pack(pady=5, fill="x")

        # 보라색 영역 (m)
        self.m_label = ctk.CTkLabel(self.meaning_frame, text="", text_color="#DDA0DD", font=("나눔바른고딕", font_info["m_label"]), height=30)
        self.m_label.pack(pady=5, fill="x")

        # 회색 영역 (km)
        self.km_label = ctk.CTkLabel(self.meaning_frame, text="", text_color="#E0E0E0", font=("나눔바른고딕", font_info["km_label"]), height=30)
        self.km_label.pack(pady=5, fill="x")

        
        self.end_label = ctk.CTkLabel(self.meaning_frame, text="", text_color="#E0E0E0", font=("나눔바른고딕", font_info["end_label"]), height=30)

        # 노란색 버튼 (모르겠어요)
        self.unknown_button = ctk.CTkButton(self.meaning_frame, text="모르겠어요", fg_color="darkgoldenrod", hover_color="gold",
                                            command=self.unknown_action)
        self.unknown_button.pack(side="left", padx=10, pady=10, expand=True)

        # 초록색 버튼 (알겠어요)
        self.known_button = ctk.CTkButton(self.meaning_frame, text="알겠어요", fg_color="darkgreen", hover_color="green",
                                          command=self.known_action) 
        self.known_button.pack(side="right", padx=10, pady=10, expand=True)


    # '단어 화면' 구성
    def setup_word_frame(self):
        self.word_label = ctk.CTkLabel(self.word_frame, text="", font=("Arial", font_info["kanji_font_size"]), text_color="white")
        self.word_label.place(relx=0.5, rely=0.5, anchor="center")

    # '뜻 화면' 표시
    def show_meaning_screen(self):
        self.is_meaning_screen = True
        self.word_frame.pack_forget()  # 단어 화면 숨기기
        self.meaning_frame.pack(fill="both", expand=True)  # 뜻 화면 표시
        self.update_meaning_screen()

    # '단어 화면' 표시
    def show_word_screen(self):
        self.is_meaning_screen = False
        self.meaning_frame.pack_forget()  # 뜻 화면 숨기기
        self.word_frame.pack(fill="both", expand=True)  # 단어 화면 표시
        self.update_word_screen()

    # 화면 전환
    def toggle_screen(self, event=None):
        if self.is_meaning_screen:
            self.show_word_screen()
        else:
            self.show_meaning_screen()

    # 뜻 화면 업데이트
    def update_meaning_screen(self):
        data = self.remaining_data[self.current_index]
        self.p_label.configure(text=f"{data['p']}")#부수 및 획수: 
        self.s_label.configure(text=f"{data['s']}")#음독: 
        self.m_label.configure(text=f"{data['m']}")#훈독: 
        self.km_label.configure(text=f"{data['km']}")#한국어 뜻: 

    # 단어 화면 업데이트    
    def update_word_screen(self):
        data = self.remaining_data[self.current_index]
        self.word_label.configure(text=data['k'])

    # '모르겠어요' 버튼 동작
    def unknown_action(self, event=None):
        self.next_card()

    # '알겠어요' 버튼 동작
    def known_action(self, event=None):
        current_kanji = self.remaining_data[self.current_index]
        if type(current_kanji['knows']) == type(int()) :
            current_kanji['knows'] += 1  # knows 값 증가
        else : 
            current_kanji['knows'] = True  # knows 값 증가
        self.next_card()

    # 다음 카드로 이동
    def next_card(self,selected_end=False):
        # 현재 카드를 방문 처리
        self.visited[self.current_index] = True
        # 방문 여부 확인
        if all(self.visited) or selected_end:  # 모든 카드가 방문되었으면 종료
            self.progress_bar.set(1)  # 진행률 100%
            temp_data = []
            for word in self.remaining_data :
                if word['knows'] in [0,False] :
                    temp_data.append(word)
            self.remaining_data = temp_data
            self.remaining_data = [card for card in self.remaining_data if card['knows'] in [0,False]]


            if not self.remaining_data:
                sys.exit()
            else:
                print("시험을 다시 시작합니다.")
                print("*"*88)
                print(self.remaining_data)
                print("*"*88)
                self.restart_with_knows_zero()


        self.update_progress_bar()  # 진행 바 업데이트
        # 다음 카드로 이동
        self.current_index = (self.current_index + 1) % len(self.remaining_data)
        if self.is_meaning_screen:
            self.update_meaning_screen()
        else:
            self.update_word_screen()


    def search_radical(self, event=None):
        url = f"https://ja.dict.naver.com/#/search?query={self.p_label.cget("text")}"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(tool.get_chrome_path()))
        webbrowser.get('chrome').open(url)
        
    def search(self, target=None, word=None, event=None):

        #target 은 숫자, word 는 (들어온다면) 한자 정보 인입


        if word : 
            #복수한자를 시험보는 경우
            if target == 1 : #검색
                target = self.word_label.cget("text")[self.search_keys.index(word)]
                self.naver_dictionary_open(target=target)
            elif target == 2 : #복사
                target = self.word_label.cget("text")[self.search_keys.index(word)]
                pyperclip.copy(f"{target}")
            elif target == 3 : #GPT 질문 복사
                target = self.word_label.cget("text")[self.search_keys.index(word)]
                pyperclip.copy(f"{target}가 어떤 부속 한자로 이루어져있는지 알려줘. 부속 한자의 뜻, 역할, 암시, 그리고 이 부속한자들의 전체적인 의미에 대해서 알려줘.")
            elif target == 4 : 
                target = self.word_label.cget("text")[self.search_keys.index(word)]
                url = self.open_kanji_detail_by_unicoded_word(f"{format(ord(target), '04X')}")

                parts = self.extract_kousei_parts(url)
                for part_idx in range(len(parts)):
                    parts[part_idx] = f"{parts[part_idx]}{target}"
                self.open_txt_on_vscode(parts)
            elif target == 5 : 
                kanji = self.word_label.cget("text")[self.search_keys.index(word)]
                
                targets = self.m_label.cget("text").split("·")
                target_list = []

                for target in targets :
                    target_list.append(f"{kanji} {target}")
                    
                self.open_txt_on_vscode(target_list)

        else : 
            #단일한자를 시험보는경우
            if target == 1 : #부수
                target = self.p_label.cget("text")
                target = target.split("(")[0].strip() #(N획) 구문 제거
            elif target == 2 : #음독
                target = self.s_label.cget("text")
            elif target == 4 : #한국어 뜻
                target = self.km_label.cget("text")
            elif target == 3 : #훈독
                if event and event.state == 12 :
                    #ctrl 이 눌렸을때.
                    kanji = self.word_label.cget("text")
                    targets = self.m_label.cget("text").split("·")
                    target_list = []
                    for target in targets :
                        target_list.append(f"{kanji} {target}")
                    self.open_txt_on_vscode(target_list)
                    return
                elif event and event.state == 8 :
                    #ctrl 이 눌리지 않을때 
                    target = self.m_label.cget("text")

            if not target in [11,12,13] :
                url = f"https://ja.dict.naver.com/#/search?query={target}"
                
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(tool.get_chrome_path()))
                webbrowser.get('chrome').open(url)

            else : 
                if target == 11 : 
                    target = self.word_label.cget("text")
                    pyperclip.copy(f"{target}가 어떤 부속 한자로 이루어져있는지 알려줘. 부속 한자의 뜻, 역할, 암시, 그리고 이 부속한자들의 전체적인 의미에 대해서 알려줘.")
                elif target == 12 : 
                    target = self.word_label.cget("text")
                    pyperclip.copy(f"{target}")
                elif target == 13 :
                    self.next_card(selected_end=True)

    def open_txt_on_vscode(self, strings):
        # 임시 txt 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
            tmp.write('\n'.join(strings))
            tmp_filename = tmp.name

        # VSCode에서 파일 열기
        if sys.platform.startswith("win"):
            subprocess.Popen(['code', tmp_filename], shell=True)
        else:
            subprocess.Popen(['code', tmp_filename])
            
    def on_key_press(self, event=None):
        """사용자가 아무 키나 입력했을 때 다음 진행"""
        self.end_label.pack_forget()  # 뜻 화면 숨기기
        self.unbind("<Key>")  # 키 이벤트 해제
        self.restart_with_knows_zero()  # 다음 진행 호출 (예: knows 0만으로 시험 재시작)


    def restart_with_knows_zero(self, event=None) :

        print("다음 시험을 시작합니다: knows가 0인 카드만 포함")
        self.current_index = 0
        
        self.visited = [False] * len(self.remaining_data)

        self.update_meaning_screen()

    def disable_capslock(self=None):
        """Caps Lock을 강제로 해제"""
        caps_state = ctypes.windll.user32.GetKeyState(0x14)  # Caps Lock 키 상태 확인
        if caps_state == 1:  # Caps Lock이 활성화되어 있으면
            ctypes.windll.user32.keybd_event(0x14, 0, 0, 0)  # Caps Lock 키 누름
            ctypes.windll.user32.keybd_event(0x14, 0, 2, 0)  # Caps Lock 키 뗌
            
    def naver_dictionary_open(self=None, target="") :

        
        url = f"https://ja.dict.naver.com/#/search?query={target}"
        
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(tool.get_chrome_path()))
        webbrowser.get('chrome').open(url)
        
# 앱 실행
if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()

