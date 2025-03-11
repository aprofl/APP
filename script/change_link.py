import os
import re

def find_file_recursively(root_dir, search_dir, filename):
    """
    파일을 검색합니다. 현재 디렉토리부터 시작하여 부모 디렉토리로 이동합니다.
    """
    for dirpath, _, filenames in os.walk(search_dir):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    
    parent_dir = os.path.dirname(search_dir)
    if parent_dir and parent_dir != root_dir:
        return find_file_recursively(root_dir, parent_dir, filename)
    
    return None

def read_file_with_fallback(file_path):
    """
    파일을 열어 내용을 읽습니다. UTF-8 디코딩이 실패하면 latin-1로 시도합니다.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def is_external_link(link):
    """
    링크가 외부 링크인지 확인합니다.
    """
    return link.startswith('http://') or link.startswith('https://')

def convert_links_to_absolute(root_dir):
    """
    옵시디언 링크와 Markdown 링크를 절대 경로로 변환합니다.
    """
    log_changes = []  # 변경된 항목을 기록할 로그 리스트
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'}  # 이미지 확장자 목록

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # . 또는 _로 시작하는 디렉토리 제외
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and not d.startswith('_')]
        
        for filename in filenames:
            # _index.md 파일은 제외
            if filename == "_index.md":
                continue

            file_path = os.path.join(dirpath, filename)
            
            # 파일 내용 읽기
            content = read_file_with_fallback(file_path)
            original_content = content

            # 옵시디언 및 Markdown 링크 패턴 검색
            obsidian_links = re.findall(r'\[\[([^\]]+)\]\]', content)
            markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

            # 변경 로그를 저장하기 위한 리스트
            file_log_changes = []

            # 옵시디언 링크 변환
            for link in obsidian_links:
                # 이미지 확장자 제외
                base_name = os.path.basename(link)
                if os.path.splitext(base_name)[1].lower() in image_extensions:
                    continue

                # 외부 링크는 변환하지 않음
                if is_external_link(link):
                    continue

                # .md 확장자 추가해 파일 찾기
                if '.' not in base_name:
                    base_name += '.md'

                # 파일을 현재 디렉토리부터 찾아서 가장 가까운 파일 사용
                absolute_path = find_file_recursively(root_dir, dirpath, base_name)
                
                if absolute_path:
                    # 절대 경로로 변환하고 .md 확장자 제거
                    root_relative_path = os.path.relpath(absolute_path, root_dir)
                    root_relative_path_no_ext = os.path.splitext(root_relative_path)[0]

                    # _index로 끝나는 링크는 변경하지 않음
                    if not root_relative_path_no_ext.endswith('_index'):
                        # 절대 경로 생성
                        new_link = f'[{link}](/' + root_relative_path_no_ext.replace("\\", "/") + ')'
                        if new_link != f'[{link}]({link})':  # Avoid redundant replacement
                            content = content.replace(f'[[{link}]]', new_link)
                            # 변경 로그 추가
                            file_log_changes.append(f"Changed: [[{link}]] -> {new_link}")

            # Markdown 링크 변환
            for title, link in markdown_links:
                # 파일명 얻기
                base_name = os.path.basename(link)
                if os.path.splitext(base_name)[1].lower() in image_extensions:
                    continue

                # 외부 링크는 변환하지 않음
                if is_external_link(link):
                    continue

                # .md 확장자 추가해 파일 찾기
                if '.' not in base_name:
                    base_name += '.md'

                # 파일을 현재 디렉토리부터 찾아서 가장 가까운 파일 사용
                absolute_path = find_file_recursively(root_dir, dirpath, base_name)

                if absolute_path:
                    # 절대 경로로 변환하고 .md 확장자 제거
                    root_relative_path = os.path.relpath(absolute_path, root_dir)
                    root_relative_path_no_ext = os.path.splitext(root_relative_path)[0]

                    # _index로 끝나는 링크는 변경하지 않음
                    if not root_relative_path_no_ext.endswith('_index'):
                        # 절대 경로 생성
                        new_link = f'[{title}](/' + root_relative_path_no_ext.replace("\\", "/") + ')'
                        if new_link != f'[{title}]({link})':  # Avoid redundant replacement
                            content = content.replace(f'[{title}]({link})', new_link)
                            # 변경 로그 추가
                            file_log_changes.append(f"\t\tChanged: [{title}]({link}) -> {new_link}")

            # 파일 내용 업데이트
            if original_content != content:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as file:
                    file.write(content)
                
                # 로그에 변경 사항 추가
                log_changes.append(f"\tFile: {file_path}")
                log_changes.extend(file_log_changes)

    return log_changes


# 소스 디렉토리 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))
# 옵시디언 및 Markdown 링크를 절대 경로로 변환
log_changes = convert_links_to_absolute(source_dir)

# 로그 출력
print("Changes_link start")
if(logLevel < 2):
    for log in log_changes:
        print(log)
if(logLevel < 3):
    print("Changes_link end")
print()

