import os
import re
import urllib.parse

# 파일이 존재하는지 확인하는 함수
def file_exists(source_dir, file_path):
    file_path = urllib.parse.unquote(file_path)  # URL 디코딩
    file_path = file_path.replace('/', os.sep).replace('\\', os.sep)
    return os.path.exists(os.path.join(source_dir, file_path))

# 마크다운 파일에서 링크를 추출하는 함수
def extract_links(content):
    # 코드 블럭 패턴
    code_block_pattern = re.compile(r'(```[\s\S]+?```|`[^`]+`)')
    
    # 코드 블럭 안의 내용을 제거
    content_without_code_blocks = code_block_pattern.sub('', content)
    
    # 이미지 링크, 옵시디언 링크, 일반 링크 추출
    md_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')  # 이미지 링크 패턴
    obsidian_pattern = re.compile(r'!\[\[([^\]]+)\]\]')  # 옵시디언 링크 패턴
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')  # 일반 링크 패턴
    
    links = set()  # 중복 제거를 위한 set 사용
    links.update(md_pattern.findall(content_without_code_blocks))
    links.update(obsidian_pattern.findall(content_without_code_blocks))
    links.update(link_pattern.findall(content_without_code_blocks))
    
    return [link[1] if isinstance(link, tuple) else link for link in links]

# 마크다운 파일을 처리하는 함수
def process_markdown_files(base_path):
    broken_links = {
        "Anchor": [],
        "Image": [],
        "Internal": [],
    }
    
    for md_root, dirs, md_files in os.walk(base_path):
        # _나 .으로 시작하는 디렉토리 제외
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        
        for md_file in md_files:            
            if md_file.endswith(".md") and md_file != "_index.md":  # _index.md 파일 제외
                md_file_path = os.path.join(md_root, md_file)
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                links = extract_links(content)
                for link in links:
                    if link.startswith('#'):
                        # 앵커 링크는 현재 파일 내에 해당 앵커가 존재하는지 확인
                        anchor = link[1:]
                        if not re.search(r'^#+\s+' + re.escape(anchor), content, re.MULTILINE):
                            broken_links["Anchor"].append((md_file_path, link, md_file_path))
                    elif link.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # 이미지 링크를 base_path를 기준으로 확인
                        image_path = os.path.join(base_path, link.lstrip('/').replace('/', os.sep))
                        if not os.path.exists(image_path):
                            broken_links["Image"].append((md_file_path, link, image_path))
                    elif not re.match(r'http[s]?://', link):
                        # 내부 링크
                        if not link.endswith('.md') and not '.' in os.path.basename(link):
                            link += '.md'
                        internal_path = os.path.join(base_path, link.lstrip('/').replace('/', os.sep))
                        if not file_exists(base_path, internal_path):
                            broken_links["Internal"].append((md_file_path, link, internal_path))
    
    return broken_links

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\Obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))
# 마크다운 파일 처리 및 깨진 링크 찾기
broken_links = process_markdown_files(source_dir)

# 깨진 링크 출력
print("check_link start")
if(logLevel < 2):
    for link_type, links in broken_links.items():
        if links:
            print(f"\t{link_type} Links:")
            for md_file, link, actual_path in links:
                print(f"\t\tFile: {md_file}, Link: {link}, Path: {actual_path}")
if(logLevel < 3):
    print("check_link end")
print()
