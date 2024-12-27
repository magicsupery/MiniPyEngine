# export_directory_structure.py

import os
import sys
from collections import deque


def get_language_from_extension(extension):
    """
    根据文件扩展名返回对应的语言名称，用于代码块的语法高亮。
    如果未知，则返回空字符串。
    """
    extension = extension.lower()
    mapping = {
        '.py': 'python',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'cpp',
        '.java': 'java',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.sh': 'bash',
        '.rb': 'ruby',
        '.go': 'go',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.glsl': 'glsl',
        # 添加更多映射根据需要
    }
    return mapping.get(extension, '')


def traverse_directory(root_path, exclude_dirs=None):
    """
    遍历目录，返回一个列表，包含目录和文件的层级信息。
    每个元素是一个元组 (path, depth, is_dir)

    参数:
    - root_path: 根目录路径
    - exclude_dirs: 一个集合，包含要排除的目录名称（不区分大小写）
    """
    if exclude_dirs is None:
        exclude_dirs = set()
    else:
        # 确保所有排除的目录名称为小写，以实现不区分大小写的匹配
        exclude_dirs = set(dir_name.lower() for dir_name in exclude_dirs)

    tree = []
    queue = deque()
    queue.append((root_path, 0))  # (path, depth)

    while queue:
        current_path, depth = queue.popleft()
        tree.append((current_path, depth, True))  # 目录

        try:
            with os.scandir(current_path) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        # 检查是否在排除列表中
                        if entry.name.lower() in exclude_dirs:
                            print(f"Skipping excluded directory: {entry.path}", file=sys.stderr)
                            continue
                        queue.append((entry.path, depth + 1))
                    else:
                        tree.append((entry.path, depth + 1, False))  # 文件
        except PermissionError:
            print(f"Permission denied: {current_path}", file=sys.stderr)
            continue

    return tree


def format_directory_tree(tree, root_path):
    """
    格式化目录树为文本形式，不包含文件内容。
    """
    output_lines = []
    root_path = os.path.abspath(root_path)
    for path, depth, is_dir in tree:
        # 计算相对路径
        rel_path = os.path.relpath(path, root_path)
        parts = rel_path.split(os.sep)
        indent = '    ' * depth
        if is_dir:
            line = f"{indent}- {parts[-1]}"
            output_lines.append(line)
        else:
            line = f"{indent}---- {parts[-1]}"
            output_lines.append(line)
    return '\n'.join(output_lines)


def format_file_contents(tree, root_path):
    """
    格式化每个文件的内容为代码块形式，附带文件路径作为标题。
    """
    output_lines = []
    root_path = os.path.abspath(root_path)
    for path, depth, is_dir in tree:
        if is_dir:
            continue  # 只处理文件
        rel_path = os.path.relpath(path, root_path)
        # 获取文件扩展名
        _, ext = os.path.splitext(path)
        language = get_language_from_extension(ext)
        if not language:
            print(f"Unknown language for file: {path}", file=sys.stderr)
            continue
        # 添加文件标题
        output_lines.append(f"\n### `{rel_path}`\n")
        # 添加代码块开始
        if language:
            code_block_start = f"```{language}"
        else:
            code_block_start = "```"
        output_lines.append(code_block_start)
        # 尝试读取文件内容
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 添加代码内容，避免 Markdown 解析问题，使用缩进
            output_lines.append(content)
        except Exception as e:
            output_lines.append(f"# Error reading file: {e}")
        # 添加代码块结束
        output_lines.append("```")
    return '\n'.join(output_lines)


EXCLUDE_DIRS = [
    '.git',
    '.idea',
    '.vscode',
    '__pycache__',
    'venv',
    'node_modules',
    'build',
    'dist',
    'output',
    'tools',
    'example'
]


def main():
    if len(sys.argv) != 3:
        print("Usage: python export_directory_structure.py /path/to/directory  /path/to/output")
        sys.exit(1)

    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"Error: {root_directory} is not a valid directory.")
        sys.exit(1)

    tree = traverse_directory(root_directory, exclude_dirs=EXCLUDE_DIRS)

    with open(sys.argv[2], 'w', encoding='utf-8') as f:

        # 阶段1：输出目录结构
        f.write("# 项目目录结构\n")
        f.write(format_directory_tree(tree, root_directory))
        f.write("\n# 代码内容\n")
        f.write(format_file_contents(tree, root_directory))


if __name__ == "__main__":
    main()
