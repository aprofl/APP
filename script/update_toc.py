import os
import re
import yaml
import urllib.parse

# YAML 로드 함수
def load_yaml(content):
    return yaml.safe_load(content)

# 메타데이터에서 타이틀, weight, 그리고 cascade.type을 추출하는 함수
def extract_metadata(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            metadata_match = re.match(r"---(.*?)---", content, re.DOTALL)
            if metadata_match:
                metadata = load_yaml(metadata_match.group(1))
                title = metadata.get('title', os.path.splitext(os.path.basename(file_path))[0])
                weight = metadata.get('weight', float('inf'))
                cascade_type = metadata.get('cascade', {}).get('type', 'default')
                return title, weight, cascade_type
            else:
                # YAML 메타데이터가 없을 때 기본값 반환
                if logLevel < 4:
                    print(f"No YAML metadata found in {file_path}")
                return os.path.splitext(os.path.basename(file_path))[0], float('inf'), 'default'
    except Exception as e:
        if logLevel < 4:
            print(f"Error extracting metadata from {file_path}: {e}")
    return os.path.splitext(os.path.basename(file_path))[0], float('inf'), 'default'


# TOC 생성 함수: 'docs'가 아닌 경우 TOC 생성을 생략
def generate_toc(folder_path, base_folder_path=None, level=0):
    if base_folder_path is None:
        base_folder_path = folder_path

    toc_lines = []  # 문자열 대신 리스트로 조립
    indent = "  " * level
    items = []

    for item in sorted(os.listdir(folder_path)):
        item_path = os.path.join(folder_path, item)

        if item.startswith('.') or item.startswith('_'):
            continue

        if os.path.isdir(item_path):
            index_file_path = os.path.join(item_path, '_index.md')
            if os.path.exists(index_file_path):
                title, weight, cascade_type = extract_metadata(index_file_path)
                if cascade_type != 'docs':  # 'docs'가 아니면 스킵
                    if(logLevel < 2):
                        print(f"Skipping TOC for {item_path} (cascade.type: {cascade_type})")
                    continue
            else:
                title, weight = item, float('inf')

            items.append((title, item_path, weight))
        elif item.endswith('.md') and item != "_index.md":
            title, weight, _ = extract_metadata(item_path)
            items.append((title, item_path, weight))

    # weight 순으로 정렬
    items.sort(key=lambda x: (x[2] if x[2] is not None else float('inf'), x[0]))

    for title, item_path, _ in items:
        relative_path = os.path.relpath(item_path, base_folder_path)
        relative_path = urllib.parse.quote(relative_path.lower().replace(os.sep, '/'))  # 경로를 URL 형식으로 인코딩

        if os.path.isdir(item_path):
            toc_lines.append(f"{indent}- [{title}]({relative_path}/)")
            toc_lines.extend(generate_toc(item_path, base_folder_path, level + 1).splitlines())
        else:
            relative_path = os.path.splitext(relative_path)[0]
            toc_lines.append(f"{indent}- [{title}]({relative_path})")

    return "\n".join(toc_lines)

# _index.md 파일 업데이트 함수
def update_index_file(index_file_path, folder_path):
    try:
        with open(index_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        title, _, cascade_type = extract_metadata(index_file_path)

        # TOC 생성을 위한 조건 체크
        if cascade_type != 'docs':
            if(logLevel < 2):
                print(f"Skipping TOC for {folder_path} (cascade.type: {cascade_type})")
            return

        # 기존 TOC 제거 (## Table of Contents부터 문서 끝까지 제거)
        stripped_content = re.sub(r"## Table of Contents.*", "", original_content, flags=re.DOTALL).strip()

        # TOC 생성
        toc = generate_toc(folder_path)
        new_content = stripped_content + f"\n\n## Table of Contents\n\n{toc}"

        with open(index_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
    except Exception as e:
        if(logLevel < 4):
            print(f"Error updating {index_file_path}: {e}")

# 모든 _index.md 파일 검색 및 업데이트
def update_all_index_files(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_') and not d.startswith('#')]
        for file_name in files:
            if file_name == "_index.md":
                index_file_path = os.path.join(root, file_name)
                update_index_file(index_file_path, root)

# 스크립트 실행
source_dir = os.environ.get('SOURCE_DIR', os.path.join(os.getcwd(), 'content'))
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("Update_TOC start")
update_all_index_files(source_dir)
if(logLevel < 3):
    print("Update_TOC end")
print()
