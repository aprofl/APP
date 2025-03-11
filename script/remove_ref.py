import os
import re
import json
import yaml

def load_references(ref_file):
    """JSON 파일에서 키-경로 쌍을 로드하여 평탄화하여 반환"""
    with open(ref_file, 'r', encoding='utf-8') as f:
        sections = json.load(f)
    
    # 섹션 구분 없이 모든 항목을 평탄화 (key: "캡슐화", value: "/dotnet/oop/기초/4대원칙/캡슐화")
    flat_references = {key: url for section in sections.values() for key, url in section.items()}
    
    return flat_references

def remove_reference_links(content, references):
    """글 내에서 주어진 키가 참조링크로 있는 경우, 참조 링크를 해제"""
    # 패턴: [단어](링크) 또는 [단어 (추가설명)](링크)
    reference_pattern = re.compile(r'\[(?P<word>.*?)\]\((?P<url>.*?)\)')
    
    def replace_reference(match):
        word = match.group('word').strip()
        
        # 키가 정확하게 포함된 경우 참조 해제
        for key in references:
            if key in word:
                # 단어만 남기고 링크 제거
                return f"**{word}**"  # 링크 제거
        return match.group(0)  # 일치하지 않으면 그대로 반환

    # 패턴 적용: 키가 포함된 참조 링크만 제거
    modified_content = reference_pattern.sub(replace_reference, content)
    return modified_content

def remove_backlinks_from_metadata(content):
    """메타데이터에서 backlinks 항목을 제거"""
    # 메타데이터 구역을 찾아서 처리 (YAML 형식의 메타데이터는 ---로 감쌈)
    metadata_pattern = re.compile(r'^---\s*\n([\s\S]*?)\n---\s*\n', re.MULTILINE)
    match = metadata_pattern.match(content)
    
    if match:
        # 메타데이터만 추출
        metadata_content = match.group(1)
        yaml_content = yaml.safe_load(metadata_content)
        
        # backlinks 항목 제거
        if 'backlinks' in yaml_content:
            del yaml_content['backlinks']
        
        # 업데이트된 YAML 내용을 다시 메타데이터로 변환
        updated_metadata = yaml.dump(yaml_content, allow_unicode=True, sort_keys=False).strip()
        content = f"---\n{updated_metadata}\n---\n" + content[match.end():]
    
    return content

def process_md_files_in_directory(source_dir, references):
    """주어진 디렉토리 내의 모든 .md 파일을 순회하며 참조 링크 및 backlinks 항목을 제거"""
    for root, dirs, files in os.walk(source_dir):
        # _나 .그리고 #으로 시작하는 디렉토리는 제외
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_') and not d.startswith('#')]

        for file in files:
            # _나 .으로 시작하는 파일, 그리고 #으로 시작하는 파일은 제외
            if not file.startswith('.') and not file.startswith('_') and not file.startswith('#') and file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 참조 링크 제거
                modified_content = remove_reference_links(content, references)

                # backlinks 항목 제거
                modified_content = remove_backlinks_from_metadata(modified_content)

                # 파일이 수정된 경우 저장
                if modified_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    if(logLevel < 2):
                        print(f"Modified: {file_path}")


# JSON 참조 파일 경로 설정 (환경변수에서 불러오거나 기본 경로 사용)
ref_file = os.environ.get('REF_FILE', os.path.join(os.getcwd(), 'word_ref.json'))

# 검색할 타겟 디렉토리 설정 (환경변수에서 불러오거나 기본 경로 사용)
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("remove_ref start")
references = load_references(ref_file)
process_md_files_in_directory(source_dir, references)

if(logLevel < 3):
    print("remove_ref end")
print()
