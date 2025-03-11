import os
import re

def remove_references_in_metadata_and_code_blocks(content):
    """메타데이터와 코드 블럭 내의 참조를 제거"""
    # 메타데이터 패턴 (---으로 감싼 YAML 블록)
    metadata_pattern = re.compile(r'(^---[\s\S]*?---)', re.MULTILINE)
    
    # 코드 블럭 패턴 (``` 또는 ```` 사이의 코드 블럭)
    code_block_pattern = re.compile(r'(```.*?```|````.*?````)', re.DOTALL)
    
    # 참조 패턴 ([]() 형태의 참조 링크 제거)
    reference_pattern = re.compile(r'\[(?P<text>[^\]]+?)\]\([^\)]+?\)')
    
    # 메타데이터에서 참조 제거
    def remove_references_in_match(match):
        content = match.group(0)
        return reference_pattern.sub(r'\g<text>', content)
    
    # 메타데이터와 코드 블럭을 찾아 각각의 참조를 제거
    content = metadata_pattern.sub(remove_references_in_match, content)
    content = code_block_pattern.sub(remove_references_in_match, content)
    
    return content

def remove_references_in_file(file_path):
    """파일 내에서 메타데이터와 코드 블럭 안의 참조를 제거"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 메타데이터와 코드 블럭 안의 참조 제거
    modified_content = remove_references_in_metadata_and_code_blocks(content)

    # 파일이 변경된 경우에만 다시 저장
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        if(logLevel < 2):
            print(f"\tModified: {file_path}")
        return True
    return False

def remove_references_in_directory(source_dir):
    """주어진 디렉토리 내의 모든 .md 파일을 순회하며 메타데이터와 코드 블럭 안의 참조를 제거"""
    total_files_checked = 0
    total_files_modified = 0
    
    for root, dirs, files in os.walk(source_dir):
        # _나 .으로 시작하는 디렉토리는 제외
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]

        for file in files:
            # _나 .으로 시작하는 파일은 제외
            if not file.startswith('.') and not file.startswith('_') and file.endswith('.md'):
                file_path = os.path.join(root, file)
                total_files_checked += 1
                if remove_references_in_file(file_path):
                    total_files_modified += 1
    
# 기본 타겟 디렉토리 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"remove_ref_in_meta start. {source_dir}")
remove_references_in_directory(source_dir)

if(logLevel < 3):
    print("remove_ref_in_meta end. checked: {total_files_checked}, modified: {total_files_modified}")
print()
