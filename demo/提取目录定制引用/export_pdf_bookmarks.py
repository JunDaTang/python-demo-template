#!/usr/bin/env python3
"""
从PDF导出书签到XML的脚本
使用 utils.toc_bookmarks_utils 模块
"""

import sys
import os
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.toc_bookmarks_utils import extract_pdf_bookmarks_to_xml


def export_pdf_bookmarks(pdf_path: str, output_dir: Optional[str] = None) -> bool:
    """
    从PDF导出书签到XML
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录（可选，默认为PDF同目录）
    
    Returns:
        是否成功
    """
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.exists():
        print(f"错误: PDF文件不存在: {pdf_path}")
        return False
    
    # 确定输出目录
    if output_dir is None:
        output_dir_obj = pdf_path_obj.parent
    else:
        output_dir_obj = Path(output_dir)
        output_dir_obj.mkdir(parents=True, exist_ok=True)
    
    # 生成输出文件名
    xml_filename = f"{pdf_path_obj.stem}_书签.xml"
    xml_path = output_dir_obj / xml_filename
    
    print(f"PDF文件: {pdf_path}")
    print(f"输出XML: {xml_path}")
    
    # 导出书签
    success = extract_pdf_bookmarks_to_xml(str(pdf_path), str(xml_path))
    
    if success:
        print(f"成功: 已导出书签到 {xml_path}")
        # 检查文件大小
        if xml_path.exists():
            size = xml_path.stat().st_size
            print(f"文件大小: {size} 字节")
    else:
        print("失败: 导出书签失败")
    
    return success


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='从PDF导出书签到XML')
    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出目录（可选）')
    
    args = parser.parse_args()
    
    success = export_pdf_bookmarks(args.pdf_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    # 示例：导出指定PDF
    pdf_file = "data/提取目录定制引用/input/尚硅谷大模型技术之数学基础1.2.1.pdf"
    output_dir = "data/提取目录定制引用/output"
    
    print("=" * 60)
    print("PDF书签导出工具")
    print("=" * 60)
    
    success = export_pdf_bookmarks(pdf_file, output_dir)
    
    if success:
        print("\n成功: 导出完成")
    else:
        print("\n失败: 导出失败")
        sys.exit(1)