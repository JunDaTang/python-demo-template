# PDF目录标签处理工具

一个简洁高效的Python工具，用于处理PDF文件的目录标签（书签），支持导入/导出XML格式。

## 功能特性

- 📄 **提取PDF书签**：从PDF文件提取目录结构，保存为XML格式
- 📤 **导入XML书签**：将XML格式的书签添加到PDF文件
- 📋 **列出书签结构**：查看PDF文件的目录层次
- 🔄 **格式兼容**：与现有XML书签格式完全兼容
- 🧪 **完整测试**：包含pytest测试用例，确保功能稳定

## 命令行使用

### 查看帮助

```bash
python main.py --help
```

输出：
```
usage: main.py [-h] {extract,add,list} ...

PDF目录标签处理工具

positional arguments:
  {extract,add,list}  命令
    extract           从PDF提取书签到XML
    add               从XML添加书签到PDF
    list              列出PDF书签

options:
  -h, --help          show this help message and exit

示例用法:
  # 提取PDF书签到XML
  python main.py extract document.pdf bookmarks.xml
  
  # 从XML添加书签到PDF
  python main.py add document.pdf bookmarks.xml output.pdf
  
  # 列出PDF书签
  python main.py list document.pdf
  
  # 显示帮助
  python main.py --help
```

### 命令详解

#### 1. 提取PDF书签到XML

```bash
python main.py extract <pdf文件> <xml输出文件>
```

**示例：**
```bash
python main.py extract "data/提取目录定制引用/input/尚硅谷大模型技术之数学基础1.2.1.pdf" "output/bookmarks.xml"
```

**输出示例：**
```
正在从PDF提取书签...
  PDF文件: data/提取目录定制引用/input/尚硅谷大模型技术之数学基础1.2.1.pdf
  输出XML: output/bookmarks.xml
成功导出 3 个书签到 output/bookmarks.xml
成功: 提取成功
  提取到 3 个顶级书签
  总书签数: 40
```

#### 2. 从XML添加书签到PDF

```bash
python main.py add <输入pdf> <书签xml> <输出pdf>
```

**示例：**
```bash
python main.py add "input.pdf" "bookmarks.xml" "output_with_bookmarks.pdf"
```

**输出示例：**
```
正在添加书签到PDF...
  输入PDF: input.pdf
  书签XML: bookmarks.xml
  输出PDF: output_with_bookmarks.pdf
成功添加 3 个书签到 output_with_bookmarks.pdf
成功: 添加成功
  添加了 3 个顶级书签
  总书签数: 40
```

#### 3. 列出PDF书签结构

```bash
python main.py list <pdf文件>
```

**示例：**
```bash
python main.py list "document.pdf"
```

**输出示例：**
```
正在列出PDF书签...
  PDF文件: document.pdf
找到 3 个顶级书签

书签结构:
+- 第 1 章高等数学 (页码: 0)
  +- 1.1导数 (页码: 0)
    +- 1.1.1导数的概念 (页码: 0)
    +- 1.1.2基本函数的导数 (页码: 1)
    +- 1.1.3导数的求导法则 (页码: 1)
    +- 1.1.4利用导数求极值 (页码: 2)
    +- 1.1.5二阶导数 (页码: 2)
  +- 1.2偏导与梯度 (页码: 3)
    +- 1.2.1偏导数 (页码: 3)
    +- 1.2.2方向导数 (页码: 4)
    +- 1.2.3梯度 (页码: 5)
```

## 快速开始

### 安装依赖

```bash
pip install pypdf
```

### 基本用法示例

```bash
# 1. 提取书签
python main.py extract document.pdf bookmarks.xml

# 2. 查看书签
python main.py list document.pdf

# 3. 添加书签
python main.py add document.pdf bookmarks.xml output.pdf
```

## 高级功能

### 1. 使用Python API

```python
from utils.toc_bookmarks_utils import PDFBookmarksHandler

# 提取书签
bookmarks = PDFBookmarksHandler.extract_from_pdf("input.pdf")

# 导出到XML
PDFBookmarksHandler.export_to_xml(bookmarks, "output.xml")

# 从XML导入
bookmarks = PDFBookmarksHandler.import_from_xml("bookmarks.xml")

# 添加到PDF
PDFBookmarksHandler.add_to_pdf("input.pdf", bookmarks, "output.pdf")
```

### 2. 转换为Obsidian引用链接

```bash
python demo/提取目录定制引用/xml_to_obsidian.py
```

将XML书签转换为Obsidian格式的Markdown文件，便于知识管理。

### 3. 批量导出PDF书签

```bash
python demo/提取目录定制引用/export_pdf_bookmarks.py
```

## 项目结构

```
pdf-tools/
├── main.py                    # 命令行入口
├── utils/
│   └── toc_bookmarks_utils.py # 核心处理类
├── tests/                     # 测试用例
├── demo/                      # 示例脚本
├── data/                      # 示例数据
└── README.md                  # 本文档
```

## 技术细节

- **核心库**：使用 `pypdf` 处理PDF文件
- **XML格式**：兼容标准书签XML格式
- **页码处理**：正确提取0-based页面索引
- **错误处理**：完善的异常处理和日志输出

## 测试

运行所有测试用例：

```bash
python -m pytest tests/test_toc_bookmarks_utils.py -v
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。
