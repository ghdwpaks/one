
import re

#이미 적재된 단어 정보
org_file_path = "total_word.txt"
content = ""
org_word_list = [] #이미 적제된 한자 리스트
with open(org_file_path, 'r', encoding='utf-8') as file:
    # 파일 내용 읽기
    content = file.read()
    # 파일 내용 출력
content = content.split("\n")
for i in content : 
    org_word_list.append(i.split(",")[0]) 
    

#이미 적재된 단어 정보
org_file_path = "total_kanji.txt"
content = ""
org_kan_list = [] #이미 적제된 한자 리스트
with open(org_file_path, 'r', encoding='utf-8') as file:
    # 파일 내용 읽기
    content = file.read()
    # 파일 내용 출력
content = content.split("\n")
for i in content : 
    org_kan_list.append(i.split(",")[0]) 


org_file_path = "tt.txt"
org_file_path = "aka_51.txt"

content = ""
# 파일 열기
with open(org_file_path, 'r', encoding='utf-8') as file:
    # 파일 내용 읽기
    content = file.read()
    # 파일 내용 출력



def extract_hanja_words(text):
    
    pattern = r'[\u4e00-\u9fff]{2,}'#한자 범위를 사용하여 2글자 이상의 한자 단어를 찾는 정규식 패턴
    pattern = r'[\u4e00-\u9fff]'#한자 범위를 사용하여 단일 한자 글자를 찾는 정규식 패턴
    # 텍스트에서 패턴에 해당하는 모든 단어를 찾음
    hanja_words = re.findall(pattern, text)
    return hanja_words

# 사용 예시
hanja_words = extract_hanja_words(content)
hanja_words = list(set(hanja_words))

# 이미 적제된 한자를 제외한, 새로운 한자만 출력
unique_words = [word for word in hanja_words if word not in org_word_list]
unique_words = [word for word in hanja_words if word not in org_kan_list]

for i in unique_words : print(i,end=",")

print("\n\n\n"+"*"*88+"\n\n\n")

for i in unique_words : print(f"\"{i}\"",end=",")
