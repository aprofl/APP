@echo off

set SOURCE_DIR=D:\Manual\App
set TARGET_DIR=%CD%

set SOURCE_STATIC_DIR=%SOURCE_DIR%\resources
set TARGET_CONTENT_DIR=%TARGET_DIR%\Content
set TARGET_STATIC_DIR=%TARGET_DIR%\\Static
set REF_FILE=%TARGET_DIR%\Script\word_ref.json
set LOGLEVEL=1
: loglevel: 1-debug 2-info 3-error 4-none
:: 환경 변수 확인을 위한 출력
echo Source Dir: %SOURCE_DIR%
echo Target Dir: %TARGET_CONTENT_DIR%

::python script/cleanup_file.py
::if %errorlevel% neq 0 (
::    echo Error occurred in script/cleanup_file.py
::    exit /b %errorlevel%
::)

: D2 Rendering server
start "" "%~dp0\script\d2server.exe"
for /f "tokens=2" %%a in ('tasklist ^| findstr /i "d2server.exe"') do set PID=%%a

python script/add_index.py
if %errorlevel% neq 0 (
    echo Error occurred in script/add_index.py
    exit /b %errorlevel%
)

:: 메타데이터 추가 스크립트 실행
python script/add_meta.py
if %errorlevel% neq 0 (
    echo Error occurred in script/add_meta.py
    exit /b %errorlevel%
)

python script/add_slug.py
if %errorlevel% neq 0 (
    echo Error occurred in script/add_slug.py
    exit /b %errorlevel%
)

python script/update_toc.py
if %errorlevel% neq 0 (
    echo Error occurred in script/update_toc.py
    exit /b %errorlevel%
)

python script/remove_ref.py
if %errorlevel% neq 0 (
    echo Error occurred in script/remove_ref.py
    exit /b %errorlevel%
)

python script/add_ref_by_bold.py
if %errorlevel% neq 0 (
    echo Error occurred in script/add_ref_by_bold.py
    exit /b %errorlevel%
)

:: 상대 경로 링크를 절대 경로 링크로 변경
python script/change_link.py
if %errorlevel% neq 0 (
    echo Error occurred in script/change_link.py
    exit /b %errorlevel%
)

:: 이미지 링크 를 md 표준 형식으로 변경
python script/change_image.py
if %errorlevel% neq 0 (
    echo Error occurred in script/change_image.py
    exit /b %errorlevel%
)
 
python script/cleanup_code.py
if %errorlevel% neq 0 (
    echo Error occurred in script/cleanup_code.py
    exit /b %errorlevel%
)

python script/check_link.py
if %errorlevel% neq 0 (
    echo Error occurred in script/check_link.py
    exit /b %errorlevel%
)

python script/sync.py
if %errorlevel% neq 0 (
    echo Error occurred in script/sync.py
    exit /b %errorlevel%
)

python script/update_index_link.py
if %errorlevel% neq 0 (
    echo Error occurred in script/update_index_link.py
    exit /b %errorlevel%
)

python script/change_d2.py
if %errorlevel% neq 0 (
    echo Error occurred in script/change_d2.py
    exit /b %errorlevel%
)

python script/change_marp.py
if %errorlevel% neq 0 (
    echo Error occurred in script/change_marp.py
    exit /b %errorlevel%
)

:: python script/add_sitemap.py
:: if %errorlevel% neq 0 (
::     echo Error occurred in script/add_sitemap.py
::     exit /b %errorlevel%
:: )

:: public 폴더 삭제
rmdir /s /q public

:: Hugo 서버 시작 및 캐시 무시
hugo server --gc --minify --ignoreCache --disableFastRender

: d2 rendering server 종료
taskkill /PID %PID% /F