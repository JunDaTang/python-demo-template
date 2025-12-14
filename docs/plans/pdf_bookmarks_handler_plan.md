# PDF目录标签处理类实现计划

## 概述
创建一个简洁的Python类，用于处理PDF目录标签（书签）的导入和导出，支持XML格式。

## 设计目标
1. 代码简洁精炼，行数控制在200行以内
2. 使用pypdf库处理PDF
3. 支持示例XML格式的导入/导出
4. 包含pytest测试用例

## 类设计

### PDFBookmarkItem 类
表示单个书签项，包含：
- `title`: 书签标题
- `page`: 页码（0-based）
- `level`: 层级（1为一级，2为二级...）
- `children`: 子书签列表
- `attributes`: 其他XML属性字典

### PDFBookmarksHandler 类
主要处理类，提供以下方法：

#### 1. 提取功能
- `extract_from_pdf(pdf_path)`: 从PDF提取书签，返回PDFBookmarkItem列表
- `export_to_xml(bookmarks, xml_path, include_attributes=True)`: 导出书签到XML文件

#### 2. 导入功能
- `import_from_xml(xml_path)`: 从XML文件导入书签，返回PDFBookmarkItem列表
- `add_to_pdf(pdf_path, bookmarks, output_path)`: 将书签添加到PDF

## XML格式处理
基于示例XML文件，需要处理的属性：
- `INDENT`: 缩进级别（对应level）
- `PAGE`: 页码
- `NAME`: 书签标题
- `OPEN`: 是否展开（可选）
- `COLOR`: 颜色（可选）
- `FONTSTYLE`: 字体样式（可选）
- `ZOOMMODE`: 缩放模式（可选）
- `PARMA`: 位置参数（可选）

## 实现步骤

### 步骤1：创建基础数据结构
1. 定义PDFBookmarkItem类
2. 实现to_dict()和from_dict()方法

### 步骤2：实现PDF提取功能
1. 使用pypdf读取PDF大纲
2. 递归解析大纲结构
3. 转换为PDFBookmarkItem树

### 步骤3：实现XML导出功能
1. 使用xml.etree.ElementTree创建XML
2. 递归遍历书签树
3. 添加所有属性

### 步骤4：实现XML导入功能
1. 解析XML文件
2. 递归构建书签树
3. 处理属性映射

### 步骤5：实现PDF添加功能
1. 使用pypdf复制PDF页面
2. 按层级添加书签
3. 保存输出文件

### 步骤6：编写测试用例
1. 创建测试PDF文件（或使用现有文件）
2. 测试提取-导出-导入-添加的完整流程
3. 测试边界情况

## 文件结构
```
utils/toc_bookmarks_utils.py  # 主实现文件
tests/test_toc_bookmarks_utils.py  # 测试文件
data/提取目录定制引用/input/资料高考数学基础知识手册_有目录.pdf  # 测试输入
data/提取目录定制引用/input/【书签】资料高考数学基础知识手册_pdf.xml  # 测试XML
```

## 简洁性考虑
1. 使用Python标准库（xml.etree.ElementTree）
2. 避免过度抽象
3. 合理的默认值处理
4. 清晰的错误处理

## 测试策略
1. 单元测试：测试单个方法
2. 集成测试：测试完整流程
3. 使用pytest fixtures管理测试数据

## 预计代码行数
- PDFBookmarkItem类：~30行
- PDFBookmarksHandler类：~150行
- 测试文件：~100行
- 总计：~280行（符合简洁要求）