import os
import re

def remove_index_references(source_dir):
    # 코드 블럭을 감지하는 정규식 패턴
    code_block_pattern = re.compile(r'(```[\s\S]*?```|`[^`]*`)')
    # _index 참조를 제거하는 정규식 패턴 (코드 블럭 외부에서만 적용)
    index_pattern = re.compile(r'(\[.*?\]\(.*?)/_index\)')

    # 주어진 디렉토리 내의 모든 파일을 순회
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]        
        for file in files:
            file_path = os.path.join(root, file)

            # 파일이 .md 확장자를 가졌는지 확인
            if file.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 코드 블럭을 제외한 부분만 찾기
                modified_content = ""
                last_end = 0
                
                for match in code_block_pattern.finditer(content):
                    # 코드 블럭 시작 전의 텍스트에 대해 _index 링크 제거
                    before_code_block = content[last_end:match.start()]
                    modified_content += index_pattern.sub(r'\1)', before_code_block)
                    # 코드 블럭은 그대로 추가
                    modified_content += match.group(0)
                    last_end = match.end()

                # 마지막 코드 블럭 이후의 텍스트 처리
                modified_content += index_pattern.sub(r'\1)', content[last_end:])

                # 파일이 변경된 경우에만 다시 저장
                if content != modified_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    if(logLevel < 2):
                        print(f"\tModified: {file_path}")


# 기본 디렉토리를 설정하거나 환경 변수를 사용
target_dir = os.environ.get('TARGET_CONTENT_DIR', os.path.join(os.getcwd(), 'content'))
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"update_index_link start")
remove_index_references(target_dir)

if(logLevel < 3):
    print(f"update_index_link end")
print()
