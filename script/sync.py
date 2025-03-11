import os
import filecmp
import shutil
import re

def sync_directories(source_dir, target_dir):
    """
    Sync the target directory to match the source directory.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    comparison = filecmp.dircmp(source_dir, target_dir)

    # Update files that are new or have changed
    for file_name in comparison.left_only + comparison.diff_files:
        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_dir, file_name)

        # Skip directories that start with . or _
        if os.path.isdir(source_file) and (os.path.basename(source_file).startswith('.') or os.path.basename(source_file).startswith('_')):
            continue

        if os.path.isdir(source_file):
            if os.path.exists(target_file):
                shutil.rmtree(target_file)
            shutil.copytree(source_file, target_file)
        else:
            shutil.copy2(source_file, target_file)

    # Delete files that are no longer present in the source directory
    for file_name in comparison.right_only:
        target_file = os.path.join(target_dir, file_name)
        if os.path.isdir(target_file):
            shutil.rmtree(target_file)
        else:
            os.remove(target_file)

    # Recursively sync subdirectories
    for subdir in comparison.common_dirs:
        source_subdir = os.path.join(source_dir, subdir)
        target_subdir = os.path.join(target_dir, subdir)

        # Skip directories that start with . or _
        if os.path.basename(source_subdir).startswith('.') or os.path.basename(source_subdir).startswith('_'):
            continue

        sync_directories(source_subdir, target_subdir)

def replace_links_in_md_files(target_dir):
    """
    Replace '%20' with '-' in the link paths of all Markdown files in the target directory,
    excluding links inside code blocks.
    """
    for dirpath, _, filenames in os.walk(target_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                file_path = os.path.join(dirpath, filename)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Split the content into segments outside of code blocks
                segments = re.split(r'(```[\s\S]*?```)', content)

                # Replace '%20' with '-' only in link paths outside of code blocks
                def replace_link_path(match):
                    link_text = match.group(1)
                    link_path = match.group(2).replace('%20', '-')  # Replace only in link path
                    return f'[{link_text}]({link_path})'

                # Process each segment
                for i in range(len(segments)):
                    # If the segment is not a code block
                    if not segments[i].startswith('```'):
                        # Replace all occurrences of '%20' with '-' in links
                        segments[i] = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link_path, segments[i])

                # Rejoin the segments
                new_content = ''.join(segments)

                # Write changes back to the file if changes were made
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    if(logLevel < 2):
                        print(f"Updated: {file_path}")


current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.dirname(current_dir)
source_dir = os.environ.get('SOURCE_DIR', r"D:\obsidian")
source_static_dir = os.environ.get('SOURCE_STATIC_DIR', os.path.join(source_dir, "resources"))
target_content_dir = os.environ.get('TARGET_CONTENT_DIR', os.path.join(target_dir, "Content"))
target_static_dir = os.environ.get('TARGET_STATIC_DIR', os.path.join(target_dir, "Static"))
logLevel = int(os.environ.get('LOGLEVEL', 1))

print(f"Sync start")
sync_directories(source_dir, target_content_dir)
sync_directories(source_static_dir, target_static_dir)
# Replace '%20' with '-' in link paths in all .md files in the target directory
replace_links_in_md_files(target_content_dir)
if(logLevel < 3):
    print(f"sync end")
print()
