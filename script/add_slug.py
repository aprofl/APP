import os
import re
import yaml

# YAML 로드 및 덤프 도우미 함수
def load_yaml(content):
    return yaml.safe_load(content)

def dump_yaml(metadata):
    return yaml.dump(metadata, sort_keys=False, default_flow_style=False, allow_unicode=True)

# 파일 경로로부터 URL과 슬러그를 생성하는 함수 (경로 포함)
def generate_slug_and_url(file_path, base_dir):
    # base_dir 이후의 경로를 얻고, 공백을 하이픈으로 대체하여 URL-friendly하게 변환
    relative_path = os.path.relpath(file_path, base_dir)
    url = os.path.splitext(relative_path)[0]  # 확장자 제거
    url = url.replace("\\", "/").replace(" ", "-").lower()
    slug = url
    return slug, url

# 메타데이터를 업데이트하거나 추가하는 함수
def update_metadata(content, title, file_path, base_dir):
    # 기존 메타데이터가 있는지 확인
    metadata_match = re.match(r"^---\s*?\n(.*?)\n---\s*?\n", content, re.DOTALL)
    if metadata_match:
        existing_metadata_str = metadata_match.group(1)
        existing_metadata = load_yaml(existing_metadata_str)
        original_metadata = existing_metadata.copy()

        # 파일이 `_index.md`인 경우 slug와 url 필드를 제거, 그 외에는 경로 기반으로 slug와 url 업데이트
        if os.path.basename(file_path) == "_index.md":
            if 'slug' in existing_metadata:
                del existing_metadata['slug']  # slug 필드 제거
            if 'url' in existing_metadata:
                del existing_metadata['url']  # url 필드 제거
        else:
            # slug와 url을 파일 경로 기반으로 새로 생성
            current_slug, current_url = generate_slug_and_url(file_path, base_dir)
            # slug가 없거나 경로와 일치하지 않으면 업데이트
            if 'slug' not in existing_metadata or existing_metadata['slug'] != current_slug:
                existing_metadata['slug'] = current_slug
            # url이 없거나 경로와 일치하지 않으면 업데이트
            if 'url' not in existing_metadata or existing_metadata['url'] != current_url:
                existing_metadata['url'] = current_url

        # 메타데이터가 변경된 경우 업데이트된 메타데이터 반환
        if existing_metadata != original_metadata:
            updated_metadata_str = dump_yaml(existing_metadata)
            new_metadata_block = f"---\n{updated_metadata_str}\n---\n"
            return content.replace(metadata_match.group(0), new_metadata_block), 'updated'
        else:
            return content, 'unchanged'
    else:
        # 메타데이터가 없는 경우 slug와 url을 포함한 새 메타데이터 추가
        new_metadata = {
            "title": title,
            "slug": generate_slug_and_url(file_path, base_dir)[0],
            "url": generate_slug_and_url(file_path, base_dir)[1]
        }
        # _index.md 파일인 경우 slug와 url 필드를 추가하지 않음
        if os.path.basename(file_path) == "_index.md":
            del new_metadata["slug"]
            del new_metadata["url"]

        new_metadata_str = dump_yaml(new_metadata)
        new_metadata_block = f"---\n{new_metadata_str}\n---\n"
        return new_metadata_block + content.lstrip(), 'added'

# 특정 디렉토리 내의 모든 파일에 slug와 url이 없거나 업데이트가 필요하면 추가 또는 수정
def add_or_update_slug_and_url_to_files(directory):
    total_files_count = 0
    updated_count = 0
    ignored_count = 0
    added_count = 0
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            if file.endswith('.md'):
                total_files_count += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 파일 이름을 제목으로 사용 (확장자 제외)
                    title = os.path.splitext(file)[0]
                    updated_content, status = update_metadata(content, title, file_path, directory)

                    if status == 'updated':
                        updated_count += 1
                    elif status == 'added':
                        added_count += 1

                    if status in ('updated', 'added'):
                        try:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(updated_content)
                            if(logLevel < 2):
                                print(f"Updated metadata in {file_path}")
                        except Exception as e:
                            if(logLevel < 4):
                                print(f"Error writing to {file_path}: {e}")
                except Exception as e:
                    if(logLevel < 4):
                        print(f"Error reading {file_path}: {e}")
                    ignored_count += 1

    return total_files_count, updated_count, ignored_count, added_count

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"Add slug and url start.")
total_files_count, updated_count, ignored_count, added_count = add_or_update_slug_and_url_to_files(source_dir)

if(logLevel < 3):
  print(f"Add slug and url end. Total: {total_files_count}, updated: {updated_count}, ignored: {ignored_count}, added: {added_count}")
print()
