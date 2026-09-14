"""
네이버 검색광고 API - 연관키워드(월간 검색수) 수집 스크립트
옆커폰 당근 프로젝트 - 휴대폰 기종별 검색량 수집용

사용법:
    python naver_keyword_collector.py

설정:
- API 키는 코드가 아니라 같은 폴더의 .env 파일(NAVER_API_KEY, NAVER_SECRET_KEY,
  NAVER_CUSTOMER_ID)에서 읽어옵니다. .env는 .gitignore로 제외되어 GitHub에 올라가지
  않습니다. 새 PC에서 쓸 때는 .env.example을 복사해 .env로 만들고 값을 채우세요.
"""

import os
import time
import hmac
import hashlib
import base64
import json
import urllib.request
import urllib.parse
import urllib.error


def load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


load_env_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ["NAVER_API_KEY"]
SECRET_KEY = os.environ["NAVER_SECRET_KEY"]
CUSTOMER_ID = os.environ["NAVER_CUSTOMER_ID"]

BASE_URL = "https://api.searchad.naver.com"
URI = "/keywordstool"
METHOD = "GET"


def make_signature(timestamp: str, method: str, uri: str, secret_key: str) -> str:
    message = f"{timestamp}.{method}.{uri}"
    # 네이버 공식 예제 기준: secret_key는 base64 디코딩하지 않고 그대로 UTF-8 바이트로 사용
    hashed = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(hashed.digest()).decode("utf-8")


def get_keyword_volume(keywords: list[str]) -> dict:
    """
    keywords: 조회할 기종명 리스트 (최대 5개, 예: ["갤럭시Z폴드8", "아이폰17"])
    반환: 네이버 API 원본 응답(dict). 결과 안의 각 항목에
          relKeyword(연관키워드), monthlyPcQcCnt(PC 월간검색수),
          monthlyMobileQcCnt(모바일 월간검색수)가 들어 있습니다.
    """
    timestamp = str(round(time.time() * 1000))
    signature = make_signature(timestamp, METHOD, URI, SECRET_KEY)

    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": API_KEY,
        "X-Customer": CUSTOMER_ID,
        "X-Signature": signature,
    }

    params = {
        "hintKeywords": ",".join(keywords),
        "showDetail": "1",
    }
    url = f"{BASE_URL}{URI}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"\n[네이버 서버 응답 - HTTP {e.code}]")
        print(body)
        raise


if __name__ == "__main__":
    # 옆커폰 주력 기종 기준 예시 키워드 (필요에 맞게 수정하세요)
    target_keywords = ["갤럭시Z폴드8", "갤럭시Z플립8", "아이폰17"]

    result = get_keyword_volume(target_keywords)

    def to_num(v):
        # 네이버 API는 검색량이 낮으면 숫자 대신 "< 10" 같은 문자열을 줌
        if v is None:
            return 0
        if isinstance(v, (int, float)):
            return v
        s = str(v).strip()
        if s.startswith("<"):
            return 5  # "< 10" 등 -> 정렬용으로 작은 값 처리
        try:
            return float(s.replace(",", ""))
        except ValueError:
            return 0

    rows = result.get("keywordList", [])
    rows.sort(key=lambda r: to_num(r.get("monthlyPcQcCnt")) + to_num(r.get("monthlyMobileQcCnt")), reverse=True)

    print(f"{'키워드':20s} {'PC검색수':>10s} {'모바일검색수':>12s}")
    for r in rows[:30]:
        print(f"{r.get('relKeyword',''):20s} {str(r.get('monthlyPcQcCnt','')):>10s} {str(r.get('monthlyMobileQcCnt','')):>12s}")

    # 오늘 날짜로 결과 저장 (대시보드 갱신용 원본 데이터)
    out_name = f"naver_keywords_{time.strftime('%Y%m%d')}.json"
    with open(out_name, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n저장 완료: {out_name}")
