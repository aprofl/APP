import os
import re
import yaml

def is_markdown_file(file):
    return file.endswith('.md')

def is_referenced_image(file, md_directory):
    # 이미지 파일이 마크다운 파일에서 참조되고 있는지 확인하는 함수.    
    file_name = os.path.basename(file)
    for root, dirs, md_files in os.walk(md_directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for md_file in md_files:
            if is_markdown_file(md_file):
                md_file_path = os.path.join(root, md_file)
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if file_name in content:
                        return True
    return False

def remove_unreferenced_images_and_files(directory, md_directory):
    # 참조되지 않는 이미지 파일과 기타 파일을 삭제하는 함수.    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            file_path = os.path.join(root, file)
            if not is_markdown_file(file) and not is_referenced_image(file_path, md_directory):
                os.remove(file_path)
                if(logLevel < 2):
                    print(f"Deleted unreferenced file: {file_path}")

def remove_empty_markdown_files(directory):
    # 내용이 없거나 메타데이터만 있는 마크다운 파일을 삭제하는 함수.    
    metadata_pattern = re.compile(r"---(.*?)---", re.DOTALL)

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            if is_markdown_file(file) and file != "_index.md":
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                metadata_match = metadata_pattern.match(content)
                if metadata_match:
                    metadata_content = metadata_match.group(1)
                    remaining_content = content[metadata_match.end():].strip()
                    if not remaining_content:
                        os.remove(file_path)
                        if(logLevel < 2):
                            print(f"Deleted empty markdown file: {file_path}")

def remove_bak_files(directory):
    # .bak 파일을 삭제하는 함수.
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for file in files:
            if file.endswith('.bak'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                if(logLevel < 2):
                    print(f"Deleted .bak file: {file_path}")

# def remove_orphan_index_files(directory):
#     # .md 파일이나 서브 폴더가 없는데 _index.md 파일이 있는 경우 해당 _index.md 파일을 제거하는 함수.
#     for root, dirs, files in os.walk(directory):
#         # .md 파일이나 서브 폴더가 없는지 확인
#         has_md_files_or_subdirs = any(is_markdown_file(f) for f in files if f != "_index.md") or bool(dirs)
#         
#         if not has_md_files_or_subdirs:
#             index_file_path = os.path.join(root, "_index.md")
#             if os.path.exists(index_file_path):
#                 os.remove(index_file_path)
#                 print(f"Deleted orphan _index.md file: {index_file_path}")

# 디렉토리 경로 설정
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
source_static_dir = os.environ.get('SOURCE_STATIC_DIR', source_dir + r"\resources")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("cleanup_file start")
# 참조되지 않는 이미지 파일과 기타 파일 삭제
remove_unreferenced_images_and_files(source_static_dir, source_dir)

# 내용이 없거나 메타데이터만 있는 마크다운 파일 삭제
remove_empty_markdown_files(source_dir)

# .bak 파일 삭제
remove_bak_files(source_dir)

if(logLevel < 3):
    print(f"cleanup_file end. ")
print()
# .md 파일이나 서브 폴더가 없는데 _index.md 파일이 있는 경우 제거
#print(f"Cleanup File : orphan_index_files")
#remove_orphan_index_files(md_directory_path)
