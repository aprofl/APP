import os
import re

def remove_metadata_from_files(directory):
    total_files_count = 0
    removed_count = 0
    not_found_count = 0
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            if file.endswith(".md"):
                total_files_count += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 코드 블럭 패턴
                    code_block_pattern = re.compile(r'```[\s\S]+?```')
                    metadata_pattern = re.compile(r'^---.*?^---\s*', flags=re.DOTALL | re.MULTILINE)
                    
                    def replace_metadata(match):
                        block = match.group(0)
                        # 코드 블럭이 아닌 경우 메타데이터를 제거
                        if not code_block_pattern.search(block):
                            return metadata_pattern.sub('', block)
                        return block
                    
                    # 메타데이터 블록을 찾고 제거
                    new_content = re.sub(metadata_pattern, replace_metadata, content)
                    
                    if new_content != content:
                        try:
                            # 원본 파일 백업
                            backup_path = file_path + ".bak"
                            with open(backup_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # 파일을 업데이트
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            if(logLevel < 2):
                                print(f"Removed metadata from {file_path}, backup created at {backup_path}")
                            removed_count += 1
                        except Exception as e:
                            if(logLevel < 4):
                                print(f"Error writing to {file_path}: {e}")
                    else:
                        if(logLevel < 2):
                            print(f"No metadata found in {file_path}")
                        not_found_count += 1
                except OSError as e:
                    if(logLevel < 4):
                        print(f"Error reading {file_path}: {e}")
                    not_found_count += 1
    
    return total_files_count, removed_count, not_found_count

# 디렉토리 경로를 설정하세요
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("remove_meta start")
total_files_count, removed_count, not_found_count = remove_metadata_from_files(source_dir)

if(logLevel < 3):
    print(f"remove_meta end. processed: {total_files_count}, removed: {removed_count}, not found: {not_found_count}")
print()