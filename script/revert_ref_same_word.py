import os
import re

def revert_references_in_file(file_path):
    """파일 이름과 같은 단어가 참조로 처리된 부분을 원래 텍스트로 복원"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False
    base_filename = os.path.splitext(os.path.basename(file_path))[0]  # 파일 이름(확장자 제외)

    # 참조 패턴 ([]() 형태의 참조 링크)
    reference_pattern = re.compile(r'\[(?P<word>{})\]\([^\)]+\)'.format(re.escape(base_filename)))

    # 참조를 원래 텍스트로 복원하는 함수
    def revert_reference(match):
        nonlocal modified
        modified = True
        return match.group('word')  # 참조를 원래 단어로 복원

    # 파일 이름과 동일한 단어가 참조된 부분을 복원
    modified_content = reference_pattern.sub(revert_reference, content)

    # 파일이 변경된 경우에만 다시 저장
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        if(logLevel < 2):
            print(f"Reverted: {file_path}")
        return True
    return False

def revert_references_in_directory(source_dir):
    """주어진 디렉토리 내의 모든 .md 파일에서 파일 이름과 같은 단어의 참조를 복원"""
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
                if revert_references_in_file(file_path):
                    total_files_modified += 1

# 기본 타겟 디렉토리 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"revert_ref_same_word start")
revert_references_in_directory(source_dir)
if(logLevel < 3):
    print("revert_ref_same_word end. checked: {total_files_checked}, modified: {total_files_modified}")
print()
