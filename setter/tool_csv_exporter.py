
import os
import csv
l = [

{'k': '応', 's': 'おう', 'm': 'こたえる', 'p': '心 (4획)','km':'대답하다'},
{'k': '日', 's': 'じつ·にち', 'm': 'か·ひ', 'p': '日 (4획)','km':'해,날'},
{'k': '対', 's': 'たい·つい', 'm': '', 'p': '寸', 'km': ''},
{'k': '始', 's': 'し', 'm': 'はじまる·はじめる', 'p': '女', 'km': ''},

]

#단어,뜻,발음,메모
#T,D,P,E

r = []
header = None
for i in l :
    #단일 한자
    header = [["T","D","P","E"]]
    try :
        r.append([
            i["k"],
            i["km"],
            f"{i["s"]}/{i["m"]}",
            f"{i["p"]}"
        ])
    except KeyError : 
        #복수 한자로 이루어진 단어
        header = [["T","D","P"]]
        r.append([
            i["kan"],
            i["mean"],
            i["sound"],
            ""
        ]) 


rr = []


# 슬라이싱 간격
step = 60  
step = int(len(r)/3)+1
step = int(len(r))

for i in range(0, len(r), step): 
    rr.append(header + r[i:i + step - 1])


print("rr[0] :",rr[0])


for rr_loc in range(len(rr)) : 
    # 폴더 경로
    folder_path = './'

    # 파일 이름
    file_name = f'{rr_loc+1}.csv'

    # 폴더 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 파일 경로
    file_path = os.path.join(folder_path, file_name)

    # CSV 저장
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)  # 최소한의 이스케이프 처리
        print("rr[rr_loc] :",rr[rr_loc])
        writer.writerows(rr[rr_loc])

    print(f"Data saved to {file_path}")