import os

def remove_index_md_files(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        for filename in files:
            if filename == '_index.md':
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    if(logLevel < 2):
                        print(f'Removed: {file_path}')
                except OSError as e:
                    if(logLevel < 4):
                        print(f'Error removing {file_path}: {e}')

# 예시 디렉토리 경로
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
logLevel = int(os.environ.get('LOGLEVEL', 1))

print("remove_index start")
remove_index_md_files(source_dir)
if(logLevel < 3):
    print("remove_index end")
print()
