import os
import subprocess
import yaml

# 환경 변수 읽기
SOURCE_DIR = os.environ.get('TARGET_CONTENT_DIR', r"content")
TARGET_DIR = "static/slides"
LOGLEVEL = int(os.environ.get('LOGLEVEL', 2))  # Default loglevel: INFO (2)

# 로깅 함수
def log(message, level=2):
    if level >= LOGLEVEL:
        print(message)

MARP_CMD = r"C:\Program Files\nodejs\marp.cmd"  # Marp CLI 경로

# YAML 헤더 파싱 및 수정 함수
def parse_and_update_yaml_header(file_path, slide_path):
    """Markdown 파일의 YAML 헤더를 파싱하고 slide_path를 추가"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines and lines[0].strip() == "---":
        yaml_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            yaml_lines.append(line)
        metadata = yaml.safe_load("\n".join(yaml_lines))
        # cascade.type 지원
        if 'cascade' in metadata and 'type' in metadata['cascade']:
            metadata['type'] = metadata['cascade']['type']

        # slide_path 추가
        metadata['slide_path'] = slide_path

        # 업데이트된 메타데이터 작성
        new_metadata = yaml.dump(metadata, default_flow_style=False).strip()
        rest_of_content = "".join(lines[len(yaml_lines) + 2:])

        # 파일 갱신
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"---\n{new_metadata}\n---\n{rest_of_content}")

# YAML 헤더 파싱 함수
def parse_yaml_header(file_path):
    """Markdown 파일의 YAML 헤더를 파싱"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines and lines[0].strip() == "---":
        yaml_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            yaml_lines.append(line)
        metadata = yaml.safe_load("\n".join(yaml_lines))
        # cascade.type 지원
        if 'cascade' in metadata and 'type' in metadata['cascade']:
            metadata['type'] = metadata['cascade']['type']
        return metadata
    return None

# Marp 변환 함수
def convert_marp_files(source_dir, target_dir):
    """Markdown 파일을 HTML로 변환하고 static/slides에 저장하며 slide_path를 메타데이터에 추가"""
    if not os.path.exists(target_dir):
        log(f"Creating target directory: {target_dir}", 2)
        os.makedirs(target_dir)

    for root, dirs, files in os.walk(source_dir):
        # 디렉토리 필터링 ('.' 또는 '_'로 시작하는 폴더 제외)
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]

        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                file_path = os.path.normpath(file_path)  # 경로 정규화
                metadata = parse_yaml_header(file_path)

                # 'type: slide'인 파일만 처리
                if metadata and metadata.get("type") == "slide":
                    # Markdown 파일의 상대 경로를 기준으로 출력 경로 계산
                    relative_path = os.path.relpath(file_path, source_dir)  # content 기준 상대 경로
                    relative_dir = os.path.dirname(relative_path).lower()  # 디렉토리를 소문자로 변환
                    file_name = os.path.splitext(os.path.basename(relative_path))[0].lower() + ".html"  # 파일 이름도 소문자로 변환
                    output_dir = os.path.join(target_dir, relative_dir)
                    output_path = os.path.join(output_dir, file_name)
                    output_path = os.path.normpath(output_path)  # 경로 정규화
                    os.makedirs(output_dir, exist_ok=True)

                    # Marp 변환 실행
                    try:
                        log(f"Converting {file_path} to {output_path}...", 2)
                        subprocess.run(
                            [MARP_CMD, file_path, "-o", output_path],
                            check=True
                        )
                        log(f"Successfully converted {file_path} to {output_path}", 2)

                        # slide_path URL 생성 및 메타데이터 업데이트
                        slide_url = "/slides/" + os.path.relpath(output_path, target_dir).replace("\\", "/").lower()
                        parse_and_update_yaml_header(file_path, slide_url)

                    except subprocess.CalledProcessError as e:
                        log(f"Error converting {file_path}: {e}", 3)
                    except FileNotFoundError:
                        log(f"Marp CLI not found. Ensure Marp is installed and MARP_CMD is correctly set.", 3)

# 메인 함수
def main():
    log("Starting Marp conversion", 2)

    # SOURCE_DIR 및 TARGET_DIR 확인
    if not os.path.exists(SOURCE_DIR):
        log(f"Source directory not found: {SOURCE_DIR}", 3)
        return
    if not os.path.exists(TARGET_DIR):
        log(f"Target directory not found. Creating: {TARGET_DIR}", 2)
        os.makedirs(TARGET_DIR)

    convert_marp_files(SOURCE_DIR, TARGET_DIR)
    log("Marp conversion completed", 2)

if __name__ == "__main__":
    main()
