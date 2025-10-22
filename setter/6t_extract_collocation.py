KAN_LIST = list("虫村石字学右竹足天林正夕貝空糸")

#pip install regex
import ast, json, os
import regex as re
from collections import OrderedDict

SRC_TXT = r"C:\\t\\one\\words\\mext\\ops\\2_grade_sentences.txt"  # 미사용이면 지워도 됨
SRC_JSON = "temps/todaii_sentences.json"
OUT_DIR  = "./temps"



def uniq(seq):
    seen = OrderedDict()
    for x in seq:
        if x and x not in seen:
            seen[x] = 1
    return list(seen.keys())

JP_RUN = r"[\p{Script=Han}\p{Hiragana}\p{Katakana}ー]+"

def clean_chunk(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^[\s「『（(［\[\-]+", "", s)
    s = re.sub(r"[\s」』）)\]］、。，．！？…・：;：；\-]+$", "", s)
    return s[:18]

def build_patterns(T: str):
    raw_patterns = [
        rf"{T}を[\p{{Hiragana}}ー]+",
        rf"{T}が[\p{{Hiragana}}ー]+",
        rf"{T}は[\p{{Hiragana}}ー]+",
        rf"{T}[にで][\p{{Hiragana}}ー]+",
        rf"{T}(だらけ|的|性)",
        rf"(?<!\p{{Script=Han}}){T}\p{{Script=Han}}+",  # 합성어(앞에 한자 금지)
        rf"{T}[\p{{Hiragana}}]+",
        rf"{T}(?:を|が|は|に|へ|で|と|から|まで|の)(?:{JP_RUN}){{0,2}}",
        rf"{T}(?:き)?(?:{JP_RUN})",
    ]
    return [re.compile(p) for p in raw_patterns]

MIN_VERB = re.compile(r"\p{Script=Han}[\p{Hiragana}ー]{0,3}")
def normalize_collocation(T: str, chunk: str) -> str:
    m = re.search(rf"^{T}(だらけ|的|性)", chunk)
    if m:
        return T + m.group(1)
    m = re.search(rf"^({T})([をがはにで])(.+)$", chunk)
    if m:
        tail = m.group(3)
        mv = MIN_VERB.search(tail)
        return f"{m.group(1)}{m.group(2)}{mv.group(0) if mv else ''}"
    m = re.search(rf"^(?<!\p{{Script=Han}}){T}\p{{Script=Han}}+", chunk)
    if m:
        return m.group(0)[:3]
    m = re.search(rf"^{T}[\p{{Hiragana}}ー]{{1,4}}", chunk)
    if m:
        return m.group(0)
    return chunk[:6]

def extract_for_T(sent: str, T: str):
    hits = []
    for rx in build_patterns(T):
        for m in rx.finditer(sent):
            raw = clean_chunk(m.group(0))
            if len(raw) >= 2 and T in raw:
                norm = normalize_collocation(T, raw)
                if len(norm) >= 2 and norm != T:
                    hits.append(norm)
    return uniq(hits)

# ----- 데이터 로드 -----
with open(SRC_JSON, encoding="utf-8") as f:
    data = json.load(f)["data"]  # 문장 리스트라고 가정

os.makedirs(OUT_DIR, exist_ok=True)

# ----- 처리 -----
final_result = {}
for kan in KAN_LIST:
    # 해당 한자가 '단독 글자'로 포함된 문장만 필터(한자 양옆이 한자 아님)
    pat_single = re.compile(fr'(?<!\p{{Script=Han}}){kan}(?!\p{{Script=Han}})')
    r = [s for s in data if pat_single.search(s)]

    # 파일로 기록(원하면 생략 가능)
    with open(f"{OUT_DIR}/6t{kan}_r_file.txt", "w", encoding="utf-8") as f:
        print(kan, file=f)
        print(r, file=f)

    # 콜로케 추출
    out = []
    for s in r:
        out += extract_for_T(s, kan)
    final_result[kan] = uniq(out)

# 확인
print("result :", final_result)
print("*"*88)
for k, v in final_result.items():
    print(k, v)
