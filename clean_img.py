import os
import re
import argparse
import sys
from pathlib import Path
from urllib.parse import unquote

# 支持的图片扩展名
IMG_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.tiff'}


def get_files(directory, extensions=None):
    """递归获取目录下所有匹配扩展名的文件"""
    path = Path(directory)
    if not path.exists():
        print(f"错误: 目录不存在 -> {directory}")
        sys.exit(1)

    files = []
    for p in path.rglob('*'):
        if p.is_file():
            if extensions is None or p.suffix.lower() in extensions:
                files.append(p)
    return files


def extract_image_refs(md_file):
    """从 Markdown 文件中提取引用的图片文件名"""
    refs = set()
    try:
        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            # 1. 匹配标准 Markdown 图片语法: ![alt](path)
            md_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            for match in md_pattern.findall(content):
                # 去掉可能存在的 title 部分，例如 "img.png 'title'"
                url = match.split()[0] if match else ""
                # 提取文件名
                filename = Path(unquote(url)).name
                if filename:
                    refs.add(filename)

            # 2. 匹配 HTML 图片语法: <img src="path">
            html_pattern = re.compile(r'<img.*?src=["\'](.*?)["\']', re.IGNORECASE)
            for match in html_pattern.findall(content):
                filename = Path(unquote(match)).name
                if filename:
                    refs.add(filename)

            # 3. [新增] 匹配 Obsidian/Wiki 语法: ![[filename]]
            # 正则解释：!? 表示感叹号可选（防止有人写 [[img.png]] 也作为引用）
            # \[\[(.*?)\]\] 提取双括号内的内容
            wiki_pattern = re.compile(r'!?\[\[(.*?)\]\]')
            for match in wiki_pattern.findall(content):
                # Obsidian 可能包含大小参数，例如 ![[image.png|100]]
                # 我们只需要 | 符号前面的部分
                url = match.split('|')[0].strip()
                # 提取文件名并解码
                filename = Path(unquote(url)).name
                if filename:
                    refs.add(filename)

    except Exception as e:
        print(f"读取文件出错 {md_file}: {e}")

    return refs


def main():
    parser = argparse.ArgumentParser(description="删除未被 Markdown 引用的图片工具 (支持 Obsidian 语法)")
    parser.add_argument('md_dir', help="Markdown 文件所在的目录路径")
    parser.add_argument('img_dir', help="图片所在的目录路径")
    parser.add_argument('--delete', action='store_true',
                        help="【危险】如果不加此参数，仅打印将要删除的文件。加上此参数将真正执行删除。")

    args = parser.parse_args()

    md_dir = Path(args.md_dir)
    img_dir = Path(args.img_dir)

    print(f"[-] 正在扫描 Markdown 目录: {md_dir}")
    md_files = get_files(md_dir, {'.md', '.markdown'})
    print(f"    发现 {len(md_files)} 个 Markdown 文件")

    print(f"[-] 正在扫描 图片 目录: {img_dir}")
    image_files = get_files(img_dir, IMG_EXTENSIONS)

    image_map = {}
    for img in image_files:
        if img.name not in image_map:
            image_map[img.name] = []
        image_map[img.name].append(img)

    print(f"    发现 {len(image_files)} 个图片文件")

    # 提取所有引用
    print("[-] 正在分析 Markdown 引用 (含 Obsidian 语法)...")
    referenced_filenames = set()
    for md in md_files:
        refs = extract_image_refs(md)
        referenced_filenames.update(refs)

    print(f"    在文档中找到了 {len(referenced_filenames)} 个唯一的图片引用")

    # 找出未引用的图片
    to_delete = []
    for img_name, img_paths in image_map.items():
        if img_name not in referenced_filenames:
            to_delete.extend(img_paths)

    # 结果处理
    if not to_delete:
        print("\n[√] 太棒了！没有发现冗余图片，所有图片都被引用了。")
        return

    print(f"\n[!] 发现 {len(to_delete)} 个未引用的图片：")

    total_size = 0
    for p in to_delete:
        try:
            size = p.stat().st_size
            total_size += size
            print(f"    [未引用] {p.relative_to(img_dir)} ({size / 1024:.2f} KB)")
        except:
            print(f"    [未引用] {p}")

    print(f"\n    总计可释放空间: {total_size / 1024 / 1024:.2f} MB")

    # 执行删除逻辑
    if args.delete:
        confirm = input("\n[警告] 确定要永久删除上述文件吗？(输入 'yes' 确认): ")
        if confirm.lower() == 'yes':
            deleted_count = 0
            for p in to_delete:
                try:
                    os.remove(p)
                    print(f"    [已删除] {p.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"    [删除失败] {p.name}: {e}")
            print(f"\n[√] 清理完成，共删除了 {deleted_count} 个文件。")
        else:
            print("\n[x] 操作已取消。")
    else:
        print("\n[提示] 当前为预览模式。请在命令后加上 --delete 参数来执行真正的删除操作。")


if __name__ == "__main__":
    main()