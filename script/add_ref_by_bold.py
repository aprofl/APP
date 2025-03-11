import os
import re
import yaml

def load_references(ref_file):
    """JSON 파일에서 키-경로 쌍을 로드하여 평탄화하여 반환"""
    with open(ref_file, 'r', encoding='utf-8') as f:
        sections = yaml.safe_load(f)
    
    # 섹션 구분 없이 모든 항목을 평탄화 (key: "캡슐화", value: "/dotnet/oop/기초/4대원칙/캡슐화")
    flat_references = {key: url for section in sections.values() for key, url in section.items()}
    
    return flat_references

def exclude_metadata_and_code_blocks(content):
    """메타데이터와 코드 블럭의 위치를 찾아 리스트로 반환"""
    metadata_pattern = re.compile(r'^---[\s\S]*?---', re.MULTILINE)
    code_block_pattern = re.compile(r'(```[\s\S]*?```|````[\s\S]*?````)', re.DOTALL)

    matches = []
    for match in metadata_pattern.finditer(content):
        matches.append((match.start(), match.end()))
    for match in code_block_pattern.finditer(content):
        matches.append((match.start(), match.end()))

    return matches

def is_in_exclusion_range(start, end, exclusion_ranges):
    """해당 위치가 메타데이터나 코드블럭에 속하는지 확인"""
    return any(start >= range_start and end <= range_end for range_start, range_end in exclusion_ranges)

def should_skip_reference(word, current_filename, references):
    """참조 경로 파일 이름과 현재 파일 이름이 같은 경우 해당 키는 건너뜀"""
    reference_file = os.path.basename(references.get(word, ""))
    reference_file_no_ext = os.path.splitext(reference_file)[0].replace('-', ' ')
    return current_filename == reference_file_no_ext

def replace_word_with_reference(word, current_filepath, references, word_changes, exclusion_ranges, start, end, source_dir):
    """단어를 참조 링크로 변경"""
    if word in references and word_changes[word] < 2:
        if not should_skip_reference(word, os.path.basename(current_filepath), references) and not is_in_exclusion_range(start, end, exclusion_ranges):
            word_changes[word] += 1
            ref_path = references[word]
            # 현재 파일(B 문서)의 전체 경로를 참조된 파일(A 문서)에 백링크로 추가
            add_backlink(ref_path, current_filepath, source_dir)
            return f"[{word}]({references[word]})"
    return word

def add_backlink(ref_path, source_filepath, source_dir):
    """참조된 파일의 메타데이터에 backlinks 항목 추가"""
    # 참조된 파일(A 문서)의 전체 경로 생성
    ref_full_path = os.path.join(source_dir, ref_path.lstrip('/')).replace('/', os.sep) + '.md'
    if not os.path.exists(ref_full_path):
        return

    # 참조한 문서(B 문서)의 제목을 파일 이름에서 가져오기
    referenced_title = os.path.splitext(os.path.basename(source_filepath))[0].replace('-', ' ')

    # URL 생성: source_filepath의 source_dir 이후 경로만 사용, .md 확장자 생략
    # 공백을 -로 대체하여 URL 생성
    relative_path = os.path.relpath(source_filepath, source_dir)
    absolute_url = '/' + os.path.splitext(relative_path)[0].replace('\\', '/').replace(' ', '-')

    # 참조된 파일(A 문서)에 백링크 추가
    with open(ref_full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata_match = re.match(r'^---[\s\S]*?---', content)
    if metadata_match:
        metadata_content = metadata_match.group()
        metadata = yaml.safe_load(metadata_content.split('---', 2)[1].strip())

        # 기존 backlinks 항목이 없으면 추가
        if 'backlinks' not in metadata:
            metadata['backlinks'] = []

        # 중복되지 않게 새로운 백링크 추가
        new_backlink = {"title": referenced_title, "url": absolute_url}
        if all(b.get("url") != new_backlink["url"] for b in metadata['backlinks']):
            metadata['backlinks'].append(new_backlink)
            if(logLevel < 2):
              print(f"add backlinks: {ref_full_path}, {new_backlink}")

        # 메타데이터 업데이트
        updated_metadata = yaml.dump(metadata, allow_unicode=True, sort_keys=False).strip()
        content = f"---\n{updated_metadata}\n---\n" + content[metadata_match.end():]
    else:
        # 메타데이터가 없으면 새로 추가
        new_backlink = {"title": referenced_title, "url": absolute_url}
        new_metadata = {
            'backlinks': [new_backlink]
        }
        updated_metadata = yaml.dump(new_metadata, allow_unicode=True, sort_keys=False).strip()
        content = f"---\n{updated_metadata}\n---\n" + content
        if(logLevel < 2):
          print(f"add backlinks: {ref_full_path}, {new_backlink}")

    # 파일을 덮어써서 저장
    with open(ref_full_path, 'w', encoding='utf-8') as f:
        f.write(content)

def add_references_in_file(file_path, references, source_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    exclusion_ranges = exclude_metadata_and_code_blocks(content)
    
    modified = False
    modified_words = []
    current_filename = os.path.splitext(os.path.basename(file_path))[0]  # 파일 이름만 추출 (확장자 제외)

    word_changes = {word: 0 for word in references}

    def replace_in_emphasis(match):
        nonlocal modified
        text = match.group(2).strip()
        start, end = match.span(2)

        # 파일의 전체 경로(file_path)를 `replace_word_with_reference`에 전달
        replaced_text = replace_word_with_reference(text, file_path, references, word_changes, exclusion_ranges, start, end, source_dir)
        if replaced_text != text:
            modified = True
            modified_words.append(f"{text}(E)")
        return replaced_text

    emphasis_pattern = re.compile(r'(\*\*|__)(\w[\w\s]*)(\*\*|__)')
    content = emphasis_pattern.sub(replace_in_emphasis, content)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        if(logLevel < 2):
          print(f"\tModified: {file_path} - Changed words: {', '.join(modified_words)}")
        return True
    return False

def process_add_references_in_directory(source_dir, references):
    global total_files_checked, total_files_modified
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_') and not d.startswith('#')]

        for file in files:
            if not file.startswith('.') and not file.startswith('_') and not file.startswith('#') and file.endswith('.md'):
                file_path = os.path.join(root, file)
                total_files_checked += 1
                if add_references_in_file(file_path, references, source_dir):
                    total_files_modified += 1
    
ref_file = os.environ.get('REF_FILE', os.path.join(os.getcwd(), r"d:\aprofl\hextra\script\word_ref.json"))
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))
references = load_references(ref_file)

total_files_checked = 0
total_files_modified = 0

print(f"add_ref_by_bold start. source : {source_dir}")
process_add_references_in_directory(source_dir, references)

if(logLevel < 3):
    print(f"add_ref_by_bold start end. checked: {total_files_checked}. modified: {total_files_modified}")
print()
