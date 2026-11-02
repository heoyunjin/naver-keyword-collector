@echo off
cd /d "C:\Users\PC\Downloads\naver-keyword-collector"
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set TODAY=%%d
if exist "naver_keywords_summary_%TODAY%.json" exit /b 0
python naver_keyword_collector.py >> naver_keyword_task.log 2>&1
git add -A -- ":!naver_keyword_task.log" >> naver_keyword_task.log 2>&1
git commit -m "Daily keyword data update %date%" >> naver_keyword_task.log 2>&1
git push >> naver_keyword_task.log 2>&1
