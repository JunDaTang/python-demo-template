# PDF目录标签处理工具

一个简洁的Python类，用于处理PDF目录标签（书签）的导入和导出，支持XML格式。

## 功能特性

- **从PDF提取书签**：读取PDF文件的大纲结构，提取所有书签
- **导出到XML**：将书签保存为XML文件，支持示例XML格式的所有属性
- **从XML导入书签**：读取XML文件，恢复书签结构
- **添加书签到PDF**：将书签添加到PDF文件中
- **简洁实现**：代码行数约280行，易于理解和维护

## 安装依赖

```bash
pip install pypdf
```

## 快速开始

### 基本使用

```python
from utils.toc_bookmarks_utils import PDFBookmarksHandler

# 从PDF提取书签
bookmarks = PDFBookmarksHandler.extract_from_pdf("input.pdf")

# 导出到XML
PDFBookmarksHandler.export_to_xml(bookmarks, "bookmarks.xml")

# 从XML导入书签
imported = PDFBookmarksHandler.import_from_xml("bookmarks.xml")

# 添加书签到PDF
PDFBookmarksHandler.add_to_pdf("input.pdf", imported, "output.pdf")
```

### 命令行使用

```bash
# 从PDF提取书签到XML
python utils/toc_bookmarks_utils.py extract input.pdf bookmarks.xml

# 从XML添加书签到PDF
python utils/toc_bookmarks_utils.py add input.pdf bookmarks.xml output.pdf
```

## 类结构

### PDFBookmarkItem
表示单个书签项：
- `title`: 书签标题
- `page`: 页码（0-based）
- `level`: 层级（1为一级，2为二级...）
- `children`: 子书签列表
- `attributes`: 其他XML属性字典

### PDFBookmarksHandler
主处理类，提供以下静态方法：
- `extract_from_pdf(pdf_path)`: 从PDF提取书签
- `export_to_xml(bookmarks, xml_path)`: 导出书签到XML
- `import_from_xml(xml_path)`: 从XML导入书签
- `add_to_pdf(pdf_path, bookmarks, output_path)`: 添加书签到PDF

## XML格式

支持示例XML格式的所有属性：
```xml
<ITEM 
    INDENT="1" 
    PAGE="0" 
    NAME="第一章 集合和命题"
    OPEN="1"
    FONTSTYLE="0"
    COLOR="4278190080"
    ZOOMMODE="0"
    PARMA="230.269577,772.485474,0.000000,0.000000">
    <!-- 子书签 -->
</ITEM>
```

## 测试

运行测试：
```bash
python -m pytest tests/test_toc_bookmarks_utils.py -v
```

测试覆盖率：
- 单元测试：PDFBookmarkItem类的基本功能
- 集成测试：XML导出/导入的完整流程
- 错误处理：测试异常情况

## 示例

查看完整示例：
```bash
python examples/pdf_bookmarks_example.py
```

## 设计特点

1. **简洁性**：代码行数控制在合理范围内，避免过度抽象
2. **兼容性**：支持示例XML格式的所有属性
3. **健壮性**：包含完善的错误处理
4. **可测试性**：使用pytest编写全面的测试用例
5. **实用性**：提供命令行接口和Python API两种使用方式

## 与现有代码的对比

相比参考代码 `demo/提取目录定制引用/pdf_toc_extractor.py`：
- 更模块化的设计，分离了数据结构和处理逻辑
- 支持双向转换（PDF↔XML）
- 更好的错误处理和类型提示
- 更简洁的API设计

## 文件结构

```
pdf-tools/
├── utils/toc_bookmarks_utils.py      # 主实现文件
├── tests/test_toc_bookmarks_utils.py # 测试文件
├── examples/pdf_bookmarks_example.py # 使用示例
├── plans/pdf_bookmarks_handler_plan.md # 设计文档
└── README_PDF_BOOKMARKS.md          # 本文档
```

## 性能考虑

- 使用pypdf库处理PDF，性能良好
- XML处理使用标准库xml.etree.ElementTree
- 递归算法处理嵌套书签结构
- 内存使用合理，适合处理大型PDF文件

## 限制

1. 依赖于pypdf库的PDF解析能力
2. XML格式需要符合示例结构
3. 页码处理基于pypdf的内部表示，可能与实际页码有差异

## 扩展建议

如需扩展功能，可以考虑：
1. 添加书签编辑功能（合并、拆分、重命名）
2. 支持更多输出格式（JSON、YAML、Markdown）
3. 添加批量处理功能
4. 支持书签样式自定义