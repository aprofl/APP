import os
import re
import yaml

# 메타데이터 템플릿
metadata_template = {
    "title": "{title}",
    "weight": 10,
    "categories": [],
    "tags": [],
    "toc": True,
    "sidebar": {
        "hide": False,
    },
    "cascade": {
        "type": "docs",
    },
    "slug": "{slug}",
    "url": "{url}"
}

# YAML 로드 및 덤프 도우미 함수
def load_yaml(content):
    return yaml.safe_load(content)

def dump_yaml(metadata):
    return yaml.dump(metadata, sort_keys=False, default_flow_style=False, allow_unicode=True)

# 파일 경로로부터 카테고리와 태그를 추출하는 함수
def extract_categories_and_tags(file_path, base_dir):
    relative_path = os.path.relpath(file_path, base_dir)
    parts = relative_path.split(os.sep)
    
    category = parts[0]
    tags = parts[:-1]  # 파일 이름을 제외한 모든 폴더
    
    return category, tags

# 파일 경로로부터 URL과 슬러그를 생성하는 함수
def generate_slug_and_url(file_path, base_dir):
    relative_path = os.path.relpath(file_path, base_dir)
    slug = os.path.splitext(relative_path)[0]
    url = slug.replace("\\", "/").replace(" ", "-").lower()
    return slug, url

# 메타데이터를 업데이트하거나 추가하는 함수
def update_metadata(content, title, category, tags, file_path, base_dir):
    new_metadata = metadata_template.copy()
    new_metadata["title"] = title
    new_metadata["categories"] = [category]
    new_metadata["tags"] = tags

    # _index.md 파일이 아닌 경우에만 slug 및 url 추가
    if os.path.basename(file_path) != "_index.md":
        slug, url = generate_slug_and_url(file_path, base_dir)
        new_metadata["slug"] = slug
        new_metadata["url"] = url

    # 기존 메타데이터가 있는지 확인
    metadata_match = re.match(r"^---\s*([\s\S]*?)\s*---\n?", content, re.MULTILINE)
    if metadata_match:
        existing_metadata_str = metadata_match.group(1)
        existing_metadata = load_yaml(existing_metadata_str)
        original_metadata = existing_metadata.copy()  # 변경 전 메타데이터 저장

        # 새로운 메타데이터와 기존 메타데이터를 병합
        for key, value in new_metadata.items():
            if key not in existing_metadata:
                existing_metadata[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in existing_metadata[key]:
                        existing_metadata[key][subkey] = subvalue

        # slug와 url 업데이트
        if os.path.basename(file_path) != "_index.md":
            slug, url = generate_slug_and_url(file_path, base_dir)
            existing_metadata['slug'] = slug
            existing_metadata['url'] = url

        if existing_metadata != original_metadata:  # 메타데이터 변경 시 업데이트
            updated_metadata_str = dump_yaml(existing_metadata)
            new_metadata_block = f"---\n{updated_metadata_str}---\n"
            updated_content = content[:metadata_match.start()] + new_metadata_block + content[metadata_match.end():]
            return updated_content, 'updated'
        else:
            return content, 'unchanged'
    else:
        # 메타데이터가 없는 경우 새 메타데이터 추가
        new_metadata_str = dump_yaml(new_metadata)
        new_metadata_block = f"---\n{new_metadata_str}---\n"
        return new_metadata_block + content, 'added'

# 특정 디렉토리 내의 모든 파일에 메타데이터 추가 또는 업데이트
def add_metadata_to_files(directory):
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

                    title = os.path.splitext(file)[0]
                    category, tags = extract_categories_and_tags(file_path, directory)
                    updated_content, status = update_metadata(content, title, category, tags, file_path, directory)

                    if status == 'updated':
                        updated_count += 1
                    elif status == 'added':
                        added_count += 1

                    if status in ('updated', 'added'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        if logLevel < 2:
                            print(f"Updated metadata in {file_path}")
                except Exception as e:
                    if logLevel < 4:
                        print(f"Error processing {file_path}: {e}")
                    ignored_count += 1

    return total_files_count, updated_count, ignored_count, added_count

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"add_meta start")
total_files_count, updated_count, ignored_count, added_count = add_metadata_to_files(source_dir)

if logLevel < 3:
    print(f"add_meta end. Total: {total_files_count}, updated: {updated_count}, ignored: {ignored_count}, added: {added_count}")
