import os
import re

# 코드 블럭 주위에 빈 줄을 삽입하는 함수.
def insert_blank_lines_around_code_blocks(content):
    lines = content.split('\n')
    updated_lines = []
    inside_code_block = False

    for i, line in enumerate(lines):
        if line.startswith("```"):
            if not inside_code_block:
                if updated_lines and updated_lines[-1].strip() != '':
                    updated_lines.append('')
                inside_code_block = True
            else:
                inside_code_block = False
                updated_lines.append(line)
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    updated_lines.append('')
                continue
        updated_lines.append(line)

    return '\n'.join(updated_lines)

# 이미지 참조 라인 위아래로 빈 줄을 삽입하는 함수.
def insert_blank_lines_around_images(content):
    md_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    obsidian_pattern = re.compile(r'!\[\[([^\]]+)\]\]')
    code_block_pattern = re.compile(r'(```[\s\S]+?```|`[^`]+`)')
    
    # 코드 블럭과 코드 블럭 외부를 분리하여 처리
    parts = code_block_pattern.split(content)
    updated_parts = []

    for i, part in enumerate(parts):
        if i % 2 == 0:
            lines = part.split('\n')
            updated_lines = []
            for j, line in enumerate(lines):
                if md_pattern.match(line) or obsidian_pattern.match(line):
                    if j > 0 and updated_lines[-1].strip() != '':
                        updated_lines.append('')
                    updated_lines.append(line)
                    if j + 1 < len(lines) and lines[j + 1].strip() != '':
                        updated_lines.append('')
                else:
                    updated_lines.append(line)
            updated_parts.append('\n'.join(updated_lines))
        else:
            updated_parts.append(part)

    return ''.join(updated_parts)

# 2단계 헤딩 (##) 라인 위아래로 빈 줄을 삽입하는 함수.
def insert_blank_lines_around_headings(content):
    heading_pattern = re.compile(r'^##\s.*$', re.MULTILINE)
    code_block_pattern = re.compile(r'(```[\s\S]+?```|`[^`]+`)')

    # 코드 블럭과 코드 블럭 외부를 분리하여 처리
    parts = code_block_pattern.split(content)
    updated_parts = []

    for i, part in enumerate(parts):
        if i % 2 == 0:
            lines = part.split('\n')
            updated_lines = []
            for j, line in enumerate(lines):
                if heading_pattern.match(line):
                    if j > 0 and updated_lines[-1].strip() != '':
                        updated_lines.append('')
                    updated_lines.append(line)
                    if j + 1 < len(lines) and lines[j + 1].strip() != '':
                        updated_lines.append('')
                else:
                    updated_lines.append(line)
            updated_parts.append('\n'.join(updated_lines))
        else:
            updated_parts.append(part)

    return ''.join(updated_parts)

# 이미지 참조 라인과 2단계 헤딩, 코드 블럭 주위에 빈 줄을 삽입하는 함수
def process_markdown_files(md_directory):
    for md_root, dirs, md_files in os.walk(md_directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]        
        for md_file in md_files:
            if md_file.endswith(".md"):
                md_file_path = os.path.join(md_root, md_file)
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # 코드 블럭 주위 빈 줄 삽입
                updated_content = insert_blank_lines_around_code_blocks(content)

                # 이미지 참조 라인 주위 빈 줄 삽입
                updated_content = insert_blank_lines_around_images(updated_content)

                # 2단계 헤딩 주위 빈 줄 삽입                
                updated_content = insert_blank_lines_around_headings(updated_content)

                # 파일을 업데이트된 내용으로 덮어쓰기
                if updated_content != original_content:
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    if(logLevel < 2):
                        print(f"Updated code in: {md_file_path}")

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))
# 마크다운 파일 처리 함수 호출
print(f"Cleanup Code start")
process_markdown_files(source_dir)
if(logLevel < 3):
    print(f"Cleanup Code end")
print()