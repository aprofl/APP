import os
import yaml

# sitemap 생성 함수 정의
def generate_sitemap(source_dir, sitemap_filename):
    sitemap = []
    directories = []

    # root 디렉토리부터 시작해 하위 폴더까지 순회
    for root, dirs, files in os.walk(source_dir):
        # 디렉토리 이름이 '.' 또는 '_'로 시작하는 경우 제외
        if any(part.startswith(('.', '_')) for part in root.replace(source_dir, '').split(os.sep)):
            continue

        # 현재 디렉토리 경로의 깊이를 계산하여 헤딩 레벨을 설정
        depth = root.replace(source_dir, '').count(os.sep)
        heading_prefix = '#' * depth
        if depth == 1:
            directories.append((root, f"{heading_prefix} {os.path.basename(root)}"))
        elif depth > 1:
            directories.append((root, f"{heading_prefix} {os.path.basename(root)}"))

    # 파일 순회 및 weight에 따른 정렬 준비
    files_info = []
    for root, dirs, files in os.walk(source_dir):
        # 디렉토리 이름이 '.' 또는 '_'로 시작하는 경우 제외
        if any(part.startswith(('.', '_')) for part in root.replace(source_dir, '').split(os.sep)):
            continue

        for file in files:
            # 파일 이름이 '.' 또는 '_'로 시작하거나 '.md' 확장자가 아닌 경우 제외
            if file.startswith(('.', '_')) or not file.endswith('.md') or file == sitemap_filename:
                continue

            file_path = os.path.join(root, file)
            weight = 10000  # 기본 weight 값 설정

            # YAML 프론트매터에서 weight 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    content = f.read()
                    if content.startswith('---'):
                        front_matter, _ = content.split('---', 2)[1:]
                        metadata = yaml.safe_load(front_matter)
                        if 'weight' in metadata:
                            weight = metadata['weight']
                except Exception as e:
                    if(logLevel < 4):
                      print(f"Warning: {file_path}에서 메타데이터 읽기 실패 - {e}")

            # 파일 정보 추가 (경로, 파일 이름, weight)
            files_info.append((root, file, weight))

    # weight에 따라 파일 정렬
    files_info.sort(key=lambda x: (x[0], x[2]))

    # 디렉토리와 파일을 sitemap에 추가
    for dir_info in directories:
        root, heading = dir_info
        sitemap.append(heading)

        for file_info in files_info:
            file_root, file, _ = file_info
            if file_root == root:
                # '.md' 확장자를 제외한 파일 이름을 불릿 포인트로 추가
                sitemap.append(f"- {os.path.splitext(file)[0]}")

    # 빈 줄이 2회 이상 삽입되지 않도록 최종 정리
    final_sitemap = []
    for line in sitemap:
        if line.strip() or (final_sitemap and final_sitemap[-1].strip()):
            final_sitemap.append(line)

    # 최종적으로 파일에 기록
    with open(os.path.join(source_dir, sitemap_filename), 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_sitemap))

# 소스 디렉토리와 사이트맵 파일 이름 설정
source_dir = os.getenv('SOURCE_DIR', r".")  # 기본적으로 현재 디렉토리 사용
sitemap_filename = "_Map.md"
logLevel = int(os.environ.get('LOGLEVEL', 1))

# 사이트맵 생성
print(f"add_sitemap start")
generate_sitemap(source_dir, sitemap_filename)
if(logLevel < 3):
  print(f"add_sitemap end. path : {sitemap_filename}")
print()
