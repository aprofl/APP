import os
import re
import urllib.parse

def change_image_names_and_update_links(directory, md_directory):   
    space_pattern = re.compile(r'\s')
    md_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    obsidian_pattern = re.compile(r'!\[\[([^\]]+)\]\]')
    code_block_pattern = re.compile(r'(```[\s\S]+?```|`[^`]+`)')

    file_mapping = {}  # old_file_name -> new_file_name

    # 파일 이름 변경
    for root, dirs, files in os.walk(directory):    
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            old_file_path = os.path.join(root, file)
            new_file_name = file
            if space_pattern.search(new_file_name):
                new_file_name = space_pattern.sub('_', new_file_name)
            
            new_file_path = os.path.join(root, new_file_name)

            # 파일 이름 변경
            if old_file_path != new_file_path:
                os.rename(old_file_path, new_file_path)
                if(logLevel < 2):
                  print(f"Renamed: {old_file_path} -> {new_file_path}")

                # 파일 이름 매핑 저장
                file_mapping[file] = new_file_name

    # 마크다운 파일 링크 업데이트
    for md_root, _, md_files in os.walk(md_directory):
        for md_file in md_files:
            if md_file.endswith(".md"):
                md_file_path = os.path.join(md_root, md_file)
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # 코드 블럭과 코드 블럭 외부를 분리하여 처리
                parts = code_block_pattern.split(content)
                updated_parts = []
                
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        # 코드 블럭 외부의 텍스트 처리
                        def replace_md_links(match):
                            alt_text = match.group(1)
                            file_path = match.group(2)
                            file_name = os.path.basename(file_path)
                            if file_name in file_mapping:
                                new_file_name = file_mapping[file_name]
                                return f'![{alt_text}](/resources/{new_file_name})'
                            return match.group(0)

                        def replace_obsidian_links(match):
                            file_name = match.group(1)
                            new_file_name = file_mapping.get(file_name, file_name)
                            return f'![{new_file_name}](/resources/{new_file_name})'

                        part = md_pattern.sub(replace_md_links, part)
                        updated_part = obsidian_pattern.sub(replace_obsidian_links, part)
                    else:
                        # 코드 블럭 내부는 그대로 유지
                        updated_part = part
                    updated_parts.append(updated_part)
                
                updated_content = ''.join(updated_parts)

                # 파일을 업데이트된 내용으로 덮어쓰기 (변경된 경우에만)
                if original_content != updated_content:
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    if(logLevel < 2):
                        print(f"Updated links in: {md_file_path}")

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
source_static_dir = os.environ.get('SOURCE_STATIC_DIR', source_dir + r"\resources")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("Change_image start")
# 이미지 파일 이름 변경 및 링크 업데이트 함수 호출
change_image_names_and_update_links(source_static_dir, source_dir)
if(logLevel < 3):
  print("Change_imange end")
print()