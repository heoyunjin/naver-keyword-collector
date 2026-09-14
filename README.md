# naver-keyword-collector

네이버 검색광고 API로 연관키워드 월간 검색수를 매일 수집하는 스크립트.

## 설정

1. `.env.example`을 `.env`로 복사하고 네이버 검색광고 API 키를 채운다.
2. `python naver_keyword_collector.py` 실행 시 `naver_keywords_YYYYMMDD.json`이 생성된다.

## 자동 실행

Windows 작업 스케줄러 `NaverKeywordCollector` 작업이 매일 오전 9시에
`run_naver_keyword_collector.bat`을 실행한다 (PC가 로그인 상태여야 함).
