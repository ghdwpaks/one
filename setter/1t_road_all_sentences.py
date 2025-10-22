import re, json

tl = list("引雲園遠何科夏家歌画回会海絵外楽活間丸岩顔汽記帰魚京強教近兄形計元原古後語公広交光考行高合谷国黒今細作算市姉思紙寺時室社弱首秋週春書少場新親図数西声星晴切雪船線前組走太体台地池知茶昼朝直通弟店点電冬当答頭同道読内南売買麦半番父風分聞歩毎妹明鳴夜野曜里理話羽角弓牛言戸午工黄才止矢自色食心多長鳥刀東肉馬米母方北万毛門友用来")

#위의 한자를 단독으로 사용하는 문장을 불러와서 반환하는 코드.
#todaii_sentences.json 필요.

td = {}
for t in tl : 
    r = []
    for i in json.load(open("temps/todaii_sentences.json", encoding="utf-8"))["data"] : 
        if re.search(fr'(?<![一-龯]){t}(?![一-龯])', i) : 
            r.append(i)
    td[t] = r

print("#"*888)


f = open('1t_res_file.txt', 'w', encoding="utf-8")
print(td, file=f)


f.close()