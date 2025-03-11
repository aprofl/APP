import os
import re
import subprocess

# Hugo 글 파일들이 있는 디렉토리 경로 설정
CONTENT_DIR = os.environ.get('TARGET_CONTENT_DIR', r"content")
D2_DIR = "static/diagrams"

# D2 코드 블록 추출을 위한 정규식
D2_BLOCK_PATTERN = re.compile(r'```d2(.*?)```', re.DOTALL)

# 타겟 디렉토리 생성
os.makedirs(D2_DIR, exist_ok=True)

def extract_d2_blocks(content):
    return D2_BLOCK_PATTERN.findall(content)

def convert_d2_to_svg(d2_code, output_path):
    try:
        # D2 CLI를 사용해 SVG로 변환
        process = subprocess.run(['d2', '--theme=200', '-', output_path], input=d2_code.encode('utf-8'), capture_output=True)
        if process.returncode != 0 and logLevel < 4:
            print(f"Error rendering D2 to SVG: {process.stderr.decode('utf-8')}")
    except Exception as e:
        if(logLevel < 4):
          print(f"Failed to run D2 CLI: {e}")

def process_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # D2 코드 블록을 추출
    d2_blocks = extract_d2_blocks(content)

    # D2 코드가 있는 경우에만 처리
    if d2_blocks:
        # 파일 이름에서 글 제목 추출
        title = os.path.splitext(os.path.basename(file_path))[0]

        # 각 D2 코드 블록을 SVG로 변환하고 저장
        for idx, d2_code in enumerate(d2_blocks):
            svg_filename = f"{title}-{idx + 1}.svg".replace(" ", "-")  # 공백을 '-'로 변경
            svg_path = os.path.join(D2_DIR, svg_filename)
            convert_d2_to_svg(d2_code.strip(), svg_path)
            if(logLevel < 2):
              print(f"Converted D2 to SVG: {svg_path}")

            # Markdown 파일 내 D2 코드를 이미지로 대체
            content = content.replace(f"```d2{d2_code}```", f"![D2 Diagram](/diagrams/{svg_filename})")

        # 변경된 내용을 다시 저장
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        if(logLevel < 2):
          print(f"Updated file: {file_path}")  # D2 코드가 변경된 경우에만 로그 출력

def process_all_files():
    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md"):
                process_markdown_file(os.path.join(root, file))

logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"change_d2 start")
process_all_files()
if(logLevel < 3):
    print(f"change_d2 end")
print()