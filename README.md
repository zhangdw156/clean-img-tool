# Clean Img Tool (Markdown图片清理工具)

这是一个安全、轻量级的 Python 命令行工具，用于自动检测并清理 Markdown 文档中未被引用的“僵尸”图片。特别适用于维护 Obsidian 知识库、Hexo/Hugo 博客或技术文档项目，帮助你释放磁盘空间并保持项目整洁。

## ✨ 核心特性

*   **🛡️ 安全优先**：默认开启 **Dry Run (空跑模式)**，仅列出待删除文件，绝不误删。必须显式添加参数才会执行删除。
*   **🔍 深度扫描**：递归遍历指定目录及其所有子目录。
*   **🧠 智能识别**：
    *   同时支持标准 Markdown 语法 `![alt](url)` 和 HTML 语法 `<img src="url">`。
    *   自动处理 URL 编码（例如能正确匹配 `image%20name.png` 和 `image name.png`）。
*   **🚀 零依赖/现代化**：基于 Python 标准库编写，通过 `uv` 进行极速管理和分发。

## 📦 安装

本项目推荐使用现代化 Python 包管理器 [uv](https://github.com/astral-sh/uv) 进行安装和管理。

### 方式一：作为全局工具安装（推荐）
如果你想在电脑的任意目录下直接使用 `clean-img` 命令：

```bash
# 在项目根目录下运行
uv tool install . --force