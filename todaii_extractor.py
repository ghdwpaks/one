from __future__ import annotations
from __future__ import print_function
from pathlib import Path

BASE_DIR = Path(r"C:\\todaii")  # 또는 Path.home() / "AppData/Local/todaii"
BASE_DIR.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성

URL_JSON_DEFAULT_PATH = str(BASE_DIR / "todaii_urls.json")
SENTENCE_JSON_DEFAULT_PATH = str(BASE_DIR / "todaii_sentences.json")
GRAMMER_JSON_DEFAULT_PATH = str(BASE_DIR / "todaii_grammers.json")
URL_HEAD = "https://japanese.todaiinews.com/detail/"
THREAD_COUNT = 10
#print("URL_JSON_DEFAULT_PATH :",URL_JSON_DEFAULT_PATH)
#print("SENTENCE_JSON_DEFAULT_PATH :",SENTENCE_JSON_DEFAULT_PATH)
#print("GRAMMER_JSON_DEFAULT_PATH :",GRAMMER_JSON_DEFAULT_PATH)


import json
from contextlib import nullcontext
from typing import Iterable, List, Set, Any
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy as d
import argparse
import re
import sys
from typing import Iterable, List, Optional, Sequence, Tuple

import json
import os
import threading
from threading import Lock
import requests
from bs4 import BeautifulSoup, Tag
import time
import psutil
import json
import tempfile
from typing import Any
import contextlib
import os, json, tempfile, time, random, stat
from typing import Any
# path: scripts/extract_urls.py
"""
Goal: Fetch a web page and print ALL discoverable URL links found in the HTML.
Target default page: https://japanese.todaiinews.com/detail/6bbeda18be7e72d8430e5e88a33dd815?hl=ko-KR

Pseudocode (plan):
- Parse CLI args: url (default to target), optional timeout.
- Build UrlExtractor(url, timeout[, session]).
- UrlExtractor.fetch(): GET page with desktop UA; return (html, final_url).
- UrlExtractor.extract_urls_from_html(html, page_url):
  - soup = BeautifulSoup(html, best_parser())
  - base = <base href> if present else page_url
  - scan DOM attributes (href/src/srcset/etc.), style url(...), <source>/<track>,
    <meta http-equiv="refresh">, and meta content absolute URLs.
  - normalize against base; keep non-HTTP schemes; filter meaningless; dedupe order.
- main(): call extractor.run(); print one URL per line. Exit non-zero on network errors.

Why comments are minimal: Behavior is clear; comments focus on decisions that affect results or safety.
"""

import argparse
import re
import sys
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin, urlparse

from requests.exceptions import Timeout, RequestException
try:
    import requests
    from bs4 import BeautifulSoup
except Exception as exc:  # pragma: no cover
    print(
        "Missing dependencies. Please install: pip install requests beautifulsoup4 lxml",
        file=sys.stderr,
    )
    raise


DEFAULT_URL = (
    "https://japanese.todaiinews.com/detail/6bbeda18be7e72d8430e5e88a33dd815?hl=ko-KR"
)



#url use setter
def uu(url) :
    if not URL_HEAD in url : 
        url = f"{URL_HEAD}{url}"
    return url
        
#url save setter
def us(url) :
    if URL_HEAD in url : 
        url.replace(URL_HEAD, "")
    return url
    

    
URL_JSON_LOCK = threading.RLock()
SENTENCE_JSON_LOCK = threading.RLock()
GRAMMER_JSON_LOCK = threading.RLock()

def _robust_replace(src: str, dst: str, *, attempts: int = 60) -> None:
    """Windows의 일시적 핸들 점유(백신/인덱서/동시 읽기)를 재시도로 우회."""
    last_exc = None
    # 대상이 읽기전용이면 교체가 막히므로 먼저 권한 회복 시도
    if os.name == "nt" and os.path.exists(dst):
        try:
            os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass

    for i in range(attempts):
        try:
            os.replace(src, dst)
            return
        except PermissionError as e:
            last_exc = e
            # 짧은 지수백오프 + 지터(수 ms): AV/인덱서/다른 핸들 해제 대기
            time.sleep(min(0.5, 0.005 * (2 ** min(i, 8))) + random.random() * 0.01)
        except OSError as e:
            # 드물게 발생하는 공유위반 등도 동일 처리
            last_exc = e
            time.sleep(0.01 + random.random() * 0.02)
    # 그래도 실패하면 원인 확인을 위해 예외 재발행
    raise last_exc


def atomic_json_write(path: str, obj: Any) -> None:
    """
    임시파일에 완전 기록+fsync 후, 대상 절대경로로 원자적 교체.
    Windows의 일시적 잠금을 재시도로 우회.
    """
    # 절대경로 고정(스레드별 CWD 변동/상대경로 혼동 방지)
    dst_abs = os.path.abspath(path)
    dir_path = os.path.dirname(dst_abs) or "."

    # 직렬화 선행(쓰기 도중 예외 최소화)
    data_bytes = json.dumps(obj, ensure_ascii=False, indent=4).encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=dir_path)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data_bytes)
            f.flush()
            os.fsync(f.fileno())  # 본문 내구성

        # Windows에서 간헐적 PermissionError를 재시도로 해소
        _robust_replace(tmp_path, dst_abs)

        # 가능하면 디렉터리 메타데이터 flush
        try:
            dfd = os.open(dir_path, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            pass
    finally:
        # 실패 시 tmp 정리(성공 시 이미 move됨)
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def first_setter() : 

    data = None
    with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["viewed_url_list"] = list(set(data["viewed_url_list"]))
    data["schedule_url_list"] = list(set(d(data["schedule_url_list"] + data["stage_url_list"])))

    data["stage_url_list"] = []

    data["schedule_url_list"] = list(set(data["schedule_url_list"]))

    for i in data["viewed_url_list"] :
        if i in data["schedule_url_list"] :
            #schedule_url_list 에서 'viewed_url_list 의 url' 제거
            data["schedule_url_list"] = [x for x in data["schedule_url_list"] if x != i]
            print("1",end="")


    atomic_json_write(URL_JSON_DEFAULT_PATH, data)
    #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)


    data = None
    with open(SENTENCE_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f : data = json.load(f)
    data["data"] = list(set(data["data"]))
    atomic_json_write(SENTENCE_JSON_DEFAULT_PATH, data)
    #with open(SENTENCE_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f : json.dump(data, f, ensure_ascii=False, indent=4)

    data = None
    with open(GRAMMER_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f : data = json.load(f)
    data["data"] = list(set(data["data"]))
    atomic_json_write(GRAMMER_JSON_DEFAULT_PATH, data)
    #with open(GRAMMER_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f : json.dump(data, f, ensure_ascii=False, indent=4)



def requests_get(url,params=None,headers=None) :

    
    resp = requests.get(
            url, 
            params=params,
            headers=headers,
            timeout=T.t()
        )
    p("resp :",resp)
    return resp


def grammer_requests_get(news_id,) :
    API_URL = "https://api2.easyjapanese.net/api/news/get-list"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }
    # 1) API 호출
    p("news_id :",news_id)
    params = {"news_id": news_id, "lang": "ko", "furigana": True}
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=T.t())
    p("resp.url :",resp.url)
    return resp
    
    

def _fsync_dir(path: str) -> None:
    """디렉터리 메타데이터까지 내구성 보장(가능할 때만)."""
    try:
        dir_path = os.path.dirname(os.path.abspath(path)) or "."
        fd = os.open(dir_path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except Exception:
        # 일부 OS/FS(특히 Windows)에서는 디렉터리 fsync 불가
        pass




@contextlib.contextmanager
def file_lock(path: str):
    """
    path+'.lock' 파일에 대해 가능한 경우 파일잠금 적용.
    프로세스 간 동시 쓰기 가능성이 있을 때 atomic_json_write 앞뒤로 감싸서 사용:
        with file_lock(URL_JSON_DEFAULT_PATH):
            atomic_json_write(URL_JSON_DEFAULT_PATH, data)
    """
    lock_file = open(path + ".lock", "a+", encoding="utf-8", errors="ignore")
    try:
        locked = False
        try:
            import fcntl  # POSIX
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            locked = True
        except Exception:
            try:
                import msvcrt  # Windows
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
                locked = True
            except Exception:
                # 락 미지원 환경: 베스트 에포트
                pass
        yield
    finally:
        try:
            if locked:
                try:
                    import fcntl
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                except Exception:
                    try:
                        import msvcrt
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except Exception:
                        pass
        finally:
            lock_file.close()






def p(*values,is_print=True):
    return
    if is_print :
        s = f"{values[0]}"
        if len(values) > 1 : 
            for i in range(1,len(values)) :
                s = f"{s} {values[i]}"
        
        print(s)

#GlobalTimeoutBackoff
class T:
    _lock = threading.RLock()
    _value = 5
    
    @classmethod
    def t(cls):
        #current_timeout
        with cls._lock:
            return cls._value
    
    @classmethod
    def s(cls):
        #report_success
        with cls._lock:
            cls._value = 5


    @classmethod
    def f(cls):
        #report_fail
        with cls._lock:
            cls._value = cls._value + 1


class UrlExtractor:
    """HTML link/asset discovery with normalization and deduplication."""

    URL_ATTRS = {
        "href",
        "src",
        "srcset",
        "data-src",
        "data-href",
        "data-url",
        "poster",
        "action",
        "formaction",
        "cite",
        "manifest",
    }

    STYLE_URL_RE = re.compile(r"url\(([^)]+)\)", re.IGNORECASE)

    def __init__(
        self,
        url: str = DEFAULT_URL,
        timeout: float = 15.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self.session = session or requests.Session()

    # ---- network ----
    def fetch(self) -> tuple[str, str]:
        """Return (html, final_url). Desktop UA to avoid basic bot blocks.
        Why raise: Let CLI decide exit codes; library users can handle exceptions.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
        while True : 
            try : 
                resp = self.session.get(self.url, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                T.s()
                break
            except Timeout:
                T.f()
                p(f"fallback_extract_from_html Timeout {self.url}")
                continue

        resp.encoding = resp.apparent_encoding or resp.encoding
        return resp.text, str(resp.url)

    # ---- parsing helpers ----
    @staticmethod
    def best_parser() -> str:
        """Prefer lxml for robustness, fall back to stdlib parser."""
        try:
            import lxml  # type: ignore  # noqa: F401
            return "lxml"
        except Exception:
            return "html.parser"

    @staticmethod
    def resolve_base_url(soup: BeautifulSoup, page_url: str) -> str:
        base_tag = soup.find("base", href=True)
        if base_tag and base_tag.get("href"):
            # Why: Honor author-provided base URL if valid.
            return urljoin(page_url, base_tag["href"])
        return page_url

    @staticmethod
    def is_meaningful(url: str) -> bool:
        if not url:
            return False
        u = url.strip()
        if u in {"#", "/#", "javascript:", "javascript:void(0)", "void(0)", "about:blank"}:
            return False
        if u.lower().startswith("javascript:"):
            return False
        return True

    @staticmethod
    def looks_like_url(value: str) -> bool:
        try:
            parsed = urlparse(value)
            if parsed.scheme in {"http", "https", "mailto", "tel", "ftp", "data"}:
                return True
            if value.startswith("//"):
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def parse_srcset(value: str) -> Iterable[str]:
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            url_only = part.split()[0]
            if url_only:
                yield url_only

    @classmethod
    def from_style(cls, value: str) -> Iterable[str]:
        for m in cls.STYLE_URL_RE.findall(value or ""):
            yield m.strip().strip('\'"')

    def normalize(self, candidate: str, base_url: str) -> Optional[str]:
        if not self.is_meaningful(candidate):
            return None
        u = candidate.strip().strip('\'"')
        low = u.lower()
        # Why: Preserve intent for non-HTTP schemes.
        if low.startswith(("mailto:", "tel:", "data:", "ftp:", "ws:", "wss:")):
            return u
        return urljoin(base_url, u)

    @classmethod
    def extract_meta_refresh(cls, soup: BeautifulSoup) -> Iterable[str]:
        for meta in soup.find_all(
            "meta", attrs={"http-equiv": re.compile(r"^refresh$", re.I)}, content=True
        ):
            content = meta.get("content", "")
            for chunk in content.split(";"):
                if "url=" in chunk.lower():
                    _, _, val = chunk.partition("=")
                    val = val.strip().strip('\'"')
                    if val:
                        yield val

    @classmethod
    def extract_meta_content_urls(cls, soup: BeautifulSoup) -> Iterable[str]:
        candidates = []
        for meta in soup.find_all("meta", content=True):
            content = meta.get("content", "").strip()
            if not content:
                continue
            if cls.looks_like_url(content):
                candidates.append(content)
        return candidates

    # ---- core ----
    def extract_urls_from_html(self, html: str, page_url: str) -> List[str]:
        soup = BeautifulSoup(html, features=self.best_parser())
        base_url = self.resolve_base_url(soup, page_url)

        ordered: List[str] = []
        seen: Set[str] = set()

        def add(raw: Optional[str]) -> None:
            if raw is None:
                return
            normalized = self.normalize(raw, base_url)
            if not normalized:
                return
            if normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)

        # Attributes on all tags
        for tag in soup.find_all(True):
            style_val = tag.get("style")
            if style_val:
                for u in self.from_style(style_val):
                    add(u)

            for attr in self.URL_ATTRS:
                if attr not in tag.attrs:
                    continue
                val = tag.get(attr)
                if not val:
                    continue
                if attr == "srcset":
                    for u in self.parse_srcset(str(val)):
                        add(u)
                else:
                    add(str(val))

        # <source>/<track> inside media containers
        for src_tag in soup.find_all(["source", "track"]):
            for key in ("src", "srcset"):
                val = src_tag.get(key)
                if not val:
                    continue
                if key == "srcset":
                    for u in self.parse_srcset(str(val)):
                        add(u)
                else:
                    add(str(val))

        # Meta-based URLs
        for u in self.extract_meta_refresh(soup):
            add(u)
        for u in self.extract_meta_content_urls(soup):
            add(u)

        return ordered

    def run(self) -> List[str]:
        html, final_url = self.fetch()
        return self.extract_urls_from_html(html, final_url)


    # Convenience: programmatic API and facade

    def urlExtractor_main(url: str, timeout: float = 15.0) -> List[str]:
        """
        Programmatic entry point matching: urlExtractor.main("https://...")
        Returns the list of discovered URLs instead of printing them.
        """
        
        extractor = UrlExtractor(url=url, timeout=timeout)
        return extractor.run()

class _ExtractorNamespace:
    # why: quick, discoverable API without instantiating a class
    def main(self, url: str, timeout: float = 15.0) -> List[str]:
        main_result = UrlExtractor.urlExtractor_main(url, timeout)
        result = []
        for url in main_result : 
            if "https://japanese.todaiinews.com/detail/" in url:
                edited_url = url.split("?")[0]
                if "#" in edited_url : 
                    edited_url = edited_url.split("#")[0]
                edited_url = us(edited_url)
                result.append(edited_url)
        result = list(set(result))
        return result

class SentenceExtractor:
    """Extracts Japanese sentences (grammar examples + visible article content)."""
    global DEFAULT_URL

    def __init__(self):
        pass
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
    API_ENDPOINT: str = "https://api2.easyjapanese.net/api/news/get-list"

    # Unicode ranges for Japanese scripts and related punctuation
    UNICODE_RANGES: Sequence[Tuple[str, str]] = (
        ("\u3040", "\u309F"),  # Hiragana
        ("\u30A0", "\u30FF"),  # Katakana
        ("\u31F0", "\u31FF"),  # Katakana Phonetic Extensions
        ("\u3400", "\u4DBF"),  # CJK Ext A
        ("\u4E00", "\u9FFF"),  # CJK Unified Ideographs
        ("\u3000", "\u303F"),  # CJK Symbols/Punctuation
        ("\uFF01", "\uFF0F"),  # Fullwidth Latin punct 1
        ("\uFF1A", "\uFF20"),  # Fullwidth Latin punct 2
        ("\uFF3B", "\uFF40"),  # Fullwidth Latin punct 3
        ("\uFF5B", "\uFF65"),  # Fullwidth Latin punct 4
        ("\uFF66", "\uFF9F"),  # Halfwidth Katakana
    )
    EXTRA_PUNCT = set("…‥—–‐‑―")

    LANG_MAP = {
        "en-US": "en",
        "vi-VN": "vi",
        "ko-KR": "ko",
        "de-DE": "de",
        "th-TH": "th",
        "fr-FR": "fr",
        "id-ID": "id",
        "zh-CN": "zh-CN",
        "zh-TW": "zh-TW",
    }

    HIDDEN_CLASS_CUES = {
        "hidden",
        "d-none",
        "sr-only",
        "visually-hidden",
        "is-hidden",
        "u-hidden",
    }

    _essential_space_re = re.compile(r"[ \u3000\t\x0b\f\r]+")

    # ---------------
    # Utilities
    # ---------------
    @staticmethod
    def ensure_utf8_stdio() -> None:
        """Help Windows terminals render UTF-8 (CLI만 해당)."""
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            except Exception:
                pass

    @classmethod
    def _char_in_ranges(cls, ch: str) -> bool:
        cp = ord(ch)
        for start, end in cls.UNICODE_RANGES:
            if ord(start) <= cp <= ord(end):
                return True
        return False

    @classmethod
    def filter_to_japanese_only(cls, text: str) -> str:
        kept: List[str] = []
        for ch in text:
            if ch.isspace():
                kept.append(ch)
                continue
            if ch in cls.EXTRA_PUNCT or cls._char_in_ranges(ch):
                kept.append(ch)
        return "".join(kept)

    @classmethod
    def tidy_lines(cls, text: str, joiner: str = "\n") -> str:
        """Normalize spaces and drop empty lines for consistent line-based output."""
        lines: List[str] = []
        for raw in text.splitlines():
            s = cls._essential_space_re.sub(" ", raw).strip()
            if s:
                lines.append(s)
        return joiner.join(lines)

    # ---------------
    # Parsing helpers
    # ---------------
    @staticmethod
    def strip_html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n", strip=True)

    @staticmethod
    def parse_news_id_from_url(url: str) -> Optional[str]:
        m = re.search(r"/detail/([^/?#]+)", url)
        return m.group(1) if m else None

    @classmethod
    def parse_lang_from_url(cls, url: str) -> str:
        m = re.search(r"[?&]hl=([\w-]+)", url)
        full = m.group(1) if m else "ko-KR"
        return cls.LANG_MAP.get(full, "en")

    # ---------------
    # Grammar examples via official API (fallback to HTML if empty)
    # ---------------
    @classmethod
    def fetch_grammar_examples(cls, news_id: str, lang_code: str, url) -> list[str]:
        p("SentenceExtractor fetch_grammar_examples lang_code :",lang_code)
        p("SentenceExtractor fetch_grammar_examples news_id :",news_id)
        p("SentenceExtractor fetch_grammar_examples url :",url)


        # 출력 인코딩을 명시(왜: Windows cmd에서 한글/일문 혼용 시 글자깨짐 방지)
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        resp = None
        while True : 
            try : 
                resp = grammer_requests_get(news_id)
                resp.raise_for_status()
                T.s()
                break
            except Timeout:
                T.f()
                p(f"fallback_extract_from_html Timeout {url}")
                continue

        # 2) JSON 파싱
        try:
            payload = resp.json()
        except json.JSONDecodeError as e:
            p(f"[ERROR] JSON decode failed: {e}", file=sys.stderr)

        # 3) vocabulary 배열 찾아가기(왜: 서비스별로 경로가 바뀌어도 최대한 유연하게 수용)
        vocab_list = None
        candidates = [
            ("result", "vocabulary"),
            ("vocabulary",),
            ("result", "vocabList"),
            ("data", "vocabulary"),
        ]
        for path in candidates:
            node = payload
            for key in path:
                node = node.get(key) if isinstance(node, dict) else None
                if node is None:
                    break
            if isinstance(node, list):
                vocab_list = node
                break

        if vocab_list is None:
            # 진단용 출력(왜: 실패 시 무엇이 왔는지 최소한 확인)
            p("[ERROR] Can't locate vocabulary array in JSON.", file=sys.stderr)
            p(json.dumps(payload, ensure_ascii=False)[:1000], file=sys.stderr)

        # 4) 행 문자열 합성 규칙
        #    - 후리가나 완전 제거: word가 "表記|ふりがな" 형태면 '|' 왼쪽만 사용
        #    - 의미/유형/레벨은 존재하는 것만 포함
        rows = []
        for item in vocab_list:
            word_raw = item.get("word", "")
            if not isinstance(word_raw, str):
                word_raw = str(word_raw) if word_raw is not None else ""
            base_word = word_raw.split("|", 1)[0]  # 왜: '|' 오른쪽은 후리가나 → 요구사항상 삭제
            base_word = re.sub(r"<[^>]+>", "", base_word).strip()  # 혹시 모를 태그 제거

            rows.append(base_word)

        p("SentenceExtractor fetch_grammar_examples rows :",rows)
        p("SentenceExtractor fetch_grammar_examples type(rows) :",type(rows))
        return rows

    @classmethod
    def fallback_extract_from_html(cls, url: str) -> list[str]:

        resp = None

        while True :
            try:
                p("SentenceExtractor fetch_grammar_examples url :",url)
                resp = requests_get(url, headers={"User-Agent": cls.USER_AGENT})
                resp.raise_for_status()
                T.s()
                break
            except Timeout:
                T.f()
                p(f"fallback_extract_from_html Timeout {url}")
                continue

        soup = BeautifulSoup(resp.text, "html.parser")
        node = soup.select_one("div.content") or soup
        text = node.get_text("\n", strip=True)
        jp = cls.filter_to_japanese_only(text)
        cleaned = cls.tidy_lines(jp, "\n")
        return [ln for ln in cleaned.splitlines() if ln]

    # ---------------
    # Visible content extraction
    # ---------------
    @classmethod
    def fetch_html(cls, url: str) -> str:

        resp = None

        while True :
            try:
                resp = requests_get(url, headers={"User-Agent": cls.USER_AGENT})
                resp.raise_for_status()
                T.s()
                break
            except Timeout:
                T.f()
                p(f"fetch_html Timeout {url}")
                continue

        if not resp.encoding:
            resp.encoding = resp.apparent_encoding
        return resp.text

    @staticmethod
    def _normalize_style_value(val) -> str:
        if not val:
            return ""
        if isinstance(val, (list, tuple, set)):
            val = " ".join(map(str, val))
        return str(val)

    @classmethod
    def _has_hidden_inline_style(cls, tag: Tag) -> bool:
        style = cls._normalize_style_value(tag.get("style"))
        style_min = style.replace(" ", "").lower()
        return any(k in style_min for k in ("display:none", "visibility:hidden", "opacity:0"))

    @staticmethod
    def _classes_as_set(tag: Tag) -> set:
        raw = tag.get("class")
        if not raw:
            return set()
        if isinstance(raw, (list, tuple, set)):
            return set(map(str, raw))
        return {str(raw)}

    @classmethod
    def select_content_container(cls, soup: BeautifulSoup) -> Optional[Tag]:
        css_path = (
            "body#body div.box-default.box-content-default "
            "div.row div#detail.col-md-9.no-pd-right.no-pd-mb "
            "div.box-detail div.content"
        )
        node = soup.select_one(css_path)
        if node:
            return node
        for alt in ["#detail .box-detail .content", "#detail .content", ".box-detail .content"]:
            node = soup.select_one(alt)
            if node:
                return node
        return None

    @classmethod
    def prune_hidden_elements(cls, root: Tag) -> None:
        """Drop non-visible nodes (why: 화면 텍스트만 유지)."""
        for t in list(root.find_all(True)):
            name = getattr(t, "name", None)
            name = name.lower() if isinstance(name, str) else ""
            try:
                if name in {"script", "style", "noscript", "template", "svg"}:
                    t.decompose()
                    continue
                if t.has_attr("hidden") or t.get("aria-hidden") == "true":
                    t.decompose()
                    continue
                classes = cls._classes_as_set(t)
                if cls.HIDDEN_CLASS_CUES & classes:
                    t.decompose()
                    continue
                if cls._has_hidden_inline_style(t):
                    t.decompose()
                    continue
            except Exception:
                try:
                    t.decompose()
                except Exception:
                    pass

    @classmethod
    def extract_visible_japanese_lines(cls, url: str) -> list[str]:
        p("extract_visible_japanese_lines url :",url)
        html = cls.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        container = cls.select_content_container(soup)
        if not container:
            raise RuntimeError("콘텐츠 컨테이너를 찾지 못했습니다. 사이트 구조가 바뀐 듯 합니다.")
        cls.prune_hidden_elements(container)
        raw_text = container.get_text(separator="\n", strip=True)
        jp_only = cls.filter_to_japanese_only(raw_text)
        cleaned = cls.tidy_lines(jp_only, "\n")
        return [ln for ln in cleaned.splitlines() if ln]

    # ---------------
    # Public API (순수 함수 형태)
    # ---------------
    @classmethod
    def run(
        cls,
        url: Optional[str] = None,
        news_id: Optional[str] = None,
        lang: str = "",
    ) -> tuple[list[str], list[str]]:
        p("SentenceExtractor run url :",url)
        p("SentenceExtractor run news_id :",news_id)
        p("SentenceExtractor run lang :",lang)
        final_url = url
        final_news_id = news_id or cls.parse_news_id_from_url(final_url)
        lang_code = lang or cls.parse_lang_from_url(final_url)

        p("SentenceExtractor run final_url :",final_url)
        p("SentenceExtractor run final_news_id :",final_news_id)
        p("SentenceExtractor run lang_code :",lang_code)

        try:
            grammar_lines = cls.fetch_grammar_examples(final_news_id, lang_code, url)
        except Exception as e :
            p("SentenceExtractor run 1 grammar_lines e :",e)
            grammar_lines = []
        p("SentenceExtractor run grammar_lines :",grammar_lines)
        if not grammar_lines:
            try:
                grammar_lines = cls.fallback_extract_from_html(final_url)
            except Exception as e :
                p("SentenceExtractor run 2 grammar_lines e :",e)
                grammar_lines = []



        try:
            content_lines = cls.extract_visible_japanese_lines(final_url)
        except Exception as e :
            p("SentenceExtractor run content_lines e :",e)
            content_lines = []
        p("SentenceExtractor run content_lines :",content_lines)
        content_lines = "".join(content_lines)
        content_lines = content_lines.split("。")
        p("content_lines :",content_lines)
        p("type(content_lines) :",type(content_lines))
        for idx in range(len(content_lines)) :
            content_lines[idx] = content_lines[idx] + "。"

        if '' in content_lines : 
            content_lines.remove('')

        p("len(content_lines) :",len(content_lines))
        p('type(grammar_lines) :',type(grammar_lines))

        p("grammar_lines :",grammar_lines)
        return content_lines, grammar_lines

    @classmethod
    def main(
        cls,
        url: Optional[str] = None,
        /,
        *,
        news_id: Optional[str] = None,
        lang: str = "",
    ) -> tuple[list[str], list[str]]:
        """High-level entrypoint. 반환값은 (grammar_list, content_list)."""
        p("SentenceExtractor main url :",url)
        p("SentenceExtractor main news_id :",news_id)
        p("SentenceExtractor main lang :",lang)
        return cls.run(url, news_id, lang)

    # ---------------
    # CLI
    # ---------------
    @classmethod
    def build_argparser(cls) -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(add_help=True)
        p.add_argument("url", nargs="?", default=None, help="Todaii 뉴스 상세 URL")
        p.add_argument("--news-id", dest="news_id", default=None, help="뉴스 ID 직접 지정")
        p.add_argument(
            "--lang", dest="lang", default="", help="API lang 코드(예: ko, en, vi) — 미지정 시 URL에서 추정"
        )
        return p

    @classmethod
    def cli(cls, argv: Iterable[str] | None = None) -> int:
        cls.ensure_utf8_stdio()
        args = cls.build_argparser().parse_args(list(argv) if argv is not None else None)

        url: Optional[str] = args.url
        news_id: Optional[str] = args.news_id
        lang: str = args.lang

        try:
            grammar_lines, content_lines = cls.run(url, news_id, lang)
        except Exception as e:
            sys.stderr.write(f"[ERROR] {e}\n")
            return 1

        p("=== GRAMMAR SENTENCES ===")
        if grammar_lines:
            p("\n".join(grammar_lines))
        else:
            p("(예문을 찾지 못했습니다)")

        p("\n=== VISIBLE CONTENT ===")
        if content_lines:
            p("\n".join(content_lines))
        else:
            p("(본문 텍스트를 찾지 못했습니다)")
        return 0


def url_roller(url) :
    urlExtractor = _ExtractorNamespace()
    extracted_url_ids = urlExtractor.main(url)
    p("len(extracted_url_ids) :",len(extracted_url_ids))
    apply_urls_json_in_schedule(extracted_url_ids)


def sentence_roller(url) :
    p("sentence_roller url :",url)
    p()
    sentences,grammers = SentenceExtractor.main(url)
    p("type(sentences) :",type(sentences))
    p("len(sentences) :",len(sentences))
    apply_sentences(sentences,grammers)

def roller_cell() :
    url = url_stage_and_pop()
    p("url :",url)
    if url : 
        url = uu(url)
        t_url, t_sen = None, None
        t_url = threading.Thread(target=url_roller,args=(url,)) ; t_url.start()
        t_sen = threading.Thread(target=sentence_roller,args=(url,)) ; t_sen.start()

        t_url.join()
        t_sen.join()

        url_viewed_and_pop(url)
    else :
        t_url = None
        t_url = threading.Thread(target=url_roller,args=("https://japanese.todaiinews.com/",)) ; t_url.start()
        t_url.join()



def url_collector_cell(keyword) :
    global URL_JSON_LOCK
    url = "https://mazii.net/api/news/search"
    data = {"keyword": str(keyword),"limit": 99999,"type": "easy"}
    results = requests.post(url, data=data).json().get("results", [])
    url_ids = []
    for result in results :
        url_ids.append(result["id"])


    with URL_JSON_LOCK:
        data = None
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        json_urls = d(data['viewed_url_list']+data['stage_url_list']+data['schedule_url_list'])

        result_list = []
        result_list_lock = Lock()
        threads = []

        for url_id in url_ids :
            t = threading.Thread(target=is_in_list,args=(
                    result_list,
                    result_list_lock,
                    url_id,
                    json_urls
                ))
            t.start()
            threads.append(t)

        for t in threads : t.join()

        result_list = list(set(result_list))
        data['schedule_url_list'].extend(result_list)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)
        
        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)






def is_in_list(result_list,result_list_lock,url,json_urls) :
    if not url in json_urls :
        with result_list_lock :
            result_list.append(url)


def apply_sentences(sentences,grammers) :
    global SENTENCE_JSON_LOCK
    global GRAMMER_JSON_LOCK

    with SENTENCE_JSON_LOCK :
        data = None
        with open(SENTENCE_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result_list = []
        result_list_lock = Lock()
        threads = []
        sentences = list(set(sentences))
        for sentence in sentences :
            t = threading.Thread(target=is_in_list,args=(
                    result_list,
                    result_list_lock,
                    sentence,
                    data["data"]
                ))
            t.start()
            threads.append(t)
        
        for t in threads : t.join()

        result_list = list(set(result_list))
        data['data'].extend(result_list)

        atomic_json_write(SENTENCE_JSON_DEFAULT_PATH, data)

        #with open(SENTENCE_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)


            
    with GRAMMER_JSON_LOCK :
        data = None
        with open(GRAMMER_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data["data"]
        result_list = []
        result_list_lock = Lock()
        threads = []
        for grammer in grammers :
            t = threading.Thread(target=is_in_list,args=(
                    result_list,
                    result_list_lock,
                    grammer,
                    data["data"]
                ))
            t.start()
            threads.append(t)
        
        for t in threads : t.join()

        result_list = list(set(result_list))
        data['data'].extend(result_list)

        atomic_json_write(GRAMMER_JSON_DEFAULT_PATH, data)

        #with open(GRAMMER_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)


def apply_urls_json_in_schedule(url_ids):
    #추출한 새로운 url 을 스케줄에 적용하기
    global URL_JSON_LOCK
    with URL_JSON_LOCK:
        data = None
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        json_urls = d(data['viewed_url_list']+data['stage_url_list']+data['schedule_url_list'])

        result_list = []
        result_list_lock = Lock()
        threads = []

        for url_id in url_ids :
            t = threading.Thread(target=is_in_list,args=(
                    result_list,
                    result_list_lock,
                    url_id,
                    json_urls
                ))
            t.start()
            threads.append(t)

        for t in threads : t.join()

        result_list = list(set(result_list))
        data['schedule_url_list'].extend(result_list)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)
        
        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)

def url_stage_and_pop() :
    global URL_JSON_LOCK

    # stage 에서 꺼내고
    with URL_JSON_LOCK:
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return_url = None
        try : 
            return_url = data['schedule_url_list'].pop()
        except IndexError as e :
            p("url_stage_and_pop IndexError e :",e)

        if not return_url : 
            return None
        
        data['stage_url_list'].append(return_url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f:json.dump(data, f, ensure_ascii=False, indent=4)
        return return_url
    

def url_viewed_and_pop(url) :
    global URL_JSON_LOCK
    global URL_JSON_DEFAULT_PATH
    with URL_JSON_LOCK:
        with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if url in data['stage_url_list']:
            data['stage_url_list'].remove(url)
            data['viewed_url_list'].append(url)

        atomic_json_write(URL_JSON_DEFAULT_PATH, data)

        #with open(URL_JSON_DEFAULT_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)








def run():
    global THREAD_COUNT
    threads = [threading.Thread(target=roller_cell) for _ in range(THREAD_COUNT)]
    url_threads = [None]*THREAD_COUNT
    keyword = 0
    for i in threads :
        i.start()

    '''
    for i in range(len(url_threads)) :
        keyword = keyword + 1
        url_threads[i] = threading.Thread(target=url_collector_cell,args=(keyword,))
        url_threads[i].start()
    '''
        


    while True:
        for i in range(len(threads)) :
            if not threads[i].is_alive() :
                threads[i] = threading.Thread(target=roller_cell)
                threads[i].start()
                
        '''
        for i in range(len(url_threads)) :
            if not url_threads[i].is_alive() :
                keyword = keyword + 1
                url_threads[i] = threading.Thread(target=url_collector_cell,args=(keyword,))
                url_threads[i].start()
        '''

        #p(f"Started roller_cell thread | CPU: {cpu_usage}% | RAM: {memory_usage}%")

        







def monitor():
    
    while True:
        data = None
        try : 
            with open(URL_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)

                url_sch_list = len(data["schedule_url_list"])
                url_sta_list = len(data["stage_url_list"])
                url_vie_list = len(data["viewed_url_list"])

            sen_list = None
            with open(SENTENCE_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)
                sen_list = len(data["data"])

            gra_list = None
            with open(GRAMMER_JSON_DEFAULT_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)
                gra_list = len(data["data"])
            print(f"{url_sta_list}|{url_sch_list}|{url_vie_list}|{sen_list}|{gra_list}|{T.t()}")
        except PermissionError : pass

        time.sleep(1)


if __name__ == '__main__':
    first_setter()
    threading.Thread(target=monitor,daemon=True).start()
    run()
    '''
    for i in range(20) :
        threading.Thread(target=monitor_and_run,daemon=True).start()
    while True : 
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        #p(f"{cpu_usage}|{memory_usage}|{T.t()}")
        



        time.sleep(0.05)
    '''

