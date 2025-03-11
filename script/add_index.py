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
    }
}

# YAML 로드 및 덤프 도우미 함수
def load_yaml(content):
    return yaml.safe_load(content)

def dump_yaml(metadata):
    return yaml.dump(metadata, sort_keys=False, default_flow_style=False, allow_unicode=True)

# 메타데이터를 업데이트하거나 추가하는 함수
def update_metadata(content, title):
    new_metadata = metadata_template.copy()
    new_metadata["title"] = title

    # 기존 메타데이터가 있는지 확인
    metadata_match = re.match(r"^---\s*?\n(.*?)\n---\s*?\n", content, re.DOTALL)
    if metadata_match and not content.startswith('```'):
        existing_metadata_str = metadata_match.group(1)
        existing_metadata = load_yaml(existing_metadata_str)
        original_metadata = existing_metadata.copy()

        # 필요한 필드가 없으면 추가, 있으면 유지
        for key, value in metadata_template.items():
            if key not in existing_metadata:
                existing_metadata[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in existing_metadata[key]:
                        existing_metadata[key][subkey] = subvalue

        # 새로운 메타데이터 YAML 생성
        updated_metadata_str = dump_yaml(existing_metadata)
        new_metadata_block = f"---\n{updated_metadata_str}\n---\n"
        
        if updated_metadata_str.strip() == existing_metadata_str.strip():
            return content, 'unchanged'
        else:
            return content.replace(metadata_match.group(0), new_metadata_block), 'updated'
    else:
        # 메타데이터가 없는 경우 새 메타데이터 추가
        new_metadata_str = dump_yaml(new_metadata)
        new_metadata_block = f"---\n{new_metadata_str}\n---\n"
        return new_metadata_block + content.lstrip(), 'added'

# 특정 디렉토리 내의 모든 폴더에 _index.md 파일 생성
def create_index_files(directory):
    total_index_files_count = 0
    index_added_count = 0
    index_updated_count = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]  # .과 _으로 시작하는 디렉토리 제외
        for dir in dirs:
            folder_path = os.path.join(root, dir)
            index_file_path = os.path.join(folder_path, "_index.md")

            # .md 파일이나 서브 폴더가 있는지 확인
            has_md_files = any(file.endswith('.md') for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)))
            has_sub_folders = any(os.path.isdir(os.path.join(folder_path, sub)) for sub in os.listdir(folder_path))

            if not has_md_files and not has_sub_folders:
                continue

            total_index_files_count += 1

            # _index.md 파일이 이미 있는지 확인
            if os.path.exists(index_file_path):
                # 이미 존재하는 경우 업데이트
                try:
                    with open(index_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    title = os.path.basename(folder_path)
                    
                    updated_content, status = update_metadata(content, title)
                    if status == 'updated':
                        with open(index_file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        index_updated_count += 1
                        if(logLevel < 2):
                          print(f"Updated _index.md in {folder_path}")
                except Exception as e:
                    if(logLevel < 4):
                      print(f"Error updating {index_file_path}: {e}")
            else:
                # 없는 경우 새로 생성
                try:
                    title = os.path.basename(folder_path)

                    new_metadata = metadata_template.copy()
                    new_metadata["title"] = title
                    new_metadata_str = dump_yaml(new_metadata)
                    new_metadata_block = f"---\n{new_metadata_str}\n---\n"
                    
                    with open(index_file_path, 'w', encoding='utf-8') as f:
                        f.write(new_metadata_block)
                    index_added_count += 1
                    if(logLevel < 2):
                      print(f"Created _index.md in {folder_path}")
                except Exception as e:
                    if(logLevel < 4):
                      print(f"Error creating {index_file_path}: {e}")

    return total_index_files_count, index_added_count, index_updated_count

# 디렉토리 경로를 설정하세요 (예: "D:/Obsidian/DocFlow")

source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"Add_index start")
total_index_files_count, index_added_count, index_updated_count = create_index_files(source_dir)

if(logLevel < 3):
  print(f"Add_index end : processed: {total_index_files_count}, added: {index_added_count}, updated: {index_updated_count}")
print()
