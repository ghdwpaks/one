import webbrowser
from urllib.parse import quote


wl = ["風","田","阜","入","音","酉","斗","弓","方","又","比","矢","皿","文","面","辛","首","氏","臼","頁","高","馬","山","甘","工","用","車","飛","足","刀","長","欠","皮","肉","里","人","鬼","豆","乙","寸","矛","瓜","糸","舟","犬","八","己","牙","穴","走","十","玉","羽","臣","非","士","雨","土","爪","牛","米","老","水","耳","石","子","生","食","自","止","立","目","舌","貝","川","示","手","缶","見","夕","色","日","干","言","骨","谷","几","大","女","斤","白","角","王","赤","辰","戶","月","羊","至","支","門","戈","毛","虫","竹","瓦","木","血","行","口","火","一","衣","香","二","巾","身","力","邑","心","片","卜","革","玄","靑","父","小"

]
# 열고 싶은 URL 입력
base_url = "https://ja.dict.naver.com/#/search?range=all&query="

chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))

print(base_url+quote("女性", encoding="utf-8"))
webbrowser.get("chrome").open(base_url+quote("女性", encoding="utf-8"))


for i in wl : 
    webbrowser.get("chrome").open(base_url+quote(i, encoding="utf-8"))




