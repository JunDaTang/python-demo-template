#!/usr/bin/env python3
"""
PDF目录标签处理工具
提供PDF书签的导入、导出功能，支持XML格式
"""

import argparse
import sys
from pathlib import Path

# 添加当前目录到路径，确保可以导入utils模块
sys.path.insert(0, str(Path(__file__).parent))

from utils.toc_bookmarks_utils import (
    PDFBookmarksHandler,
    extract_pdf_bookmarks_to_xml,
    add_bookmarks_from_xml_to_pdf
)


def extract_command(args):
    """提取PDF书签到XML"""
    pdf_path = args.pdf_file
    xml_path = args.xml_file
    
    print(f"正在从PDF提取书签...")
    print(f"  PDF文件: {pdf_path}")
    print(f"  输出XML: {xml_path}")
    
    success = extract_pdf_bookmarks_to_xml(pdf_path, xml_path)
    
    if success:
        print("成功: 提取成功")
        # 显示提取的书签数量
        try:
            bookmarks = PDFBookmarksHandler.extract_from_pdf(pdf_path)
            print(f"  提取到 {len(bookmarks)} 个顶级书签")
            # 统计总书签数（包括子项）
            def count_total(items):
                total = len(items)
                for item in items:
                    total += count_total(item.children)
                return total
            
            total = count_total(bookmarks)
            print(f"  总书签数: {total}")
        except Exception as e:
            print(f"  警告: 无法统计书签数量: {e}")
    else:
        print("失败: 提取失败")
        sys.exit(1)


def add_command(args):
    """从XML添加书签到PDF"""
    pdf_path = args.pdf_file
    xml_path = args.xml_file
    output_path = args.output_pdf
    
    print(f"正在添加书签到PDF...")
    print(f"  输入PDF: {pdf_path}")
    print(f"  书签XML: {xml_path}")
    print(f"  输出PDF: {output_path}")
    
    success = add_bookmarks_from_xml_to_pdf(pdf_path, xml_path, output_path)
    
    if success:
        print("成功: 添加成功")
        # 显示添加的书签数量
        try:
            bookmarks = PDFBookmarksHandler.import_from_xml(xml_path)
            print(f"  添加了 {len(bookmarks)} 个顶级书签")
            # 统计总书签数
            def count_total(items):
                total = len(items)
                for item in items:
                    total += count_total(item.children)
                return total
            
            total = count_total(bookmarks)
            print(f"  总书签数: {total}")
        except Exception as e:
            print(f"  警告: 无法统计书签数量: {e}")
    else:
        print("失败: 添加失败")
        sys.exit(1)


def list_command(args):
    """列出PDF书签"""
    pdf_path = args.pdf_file
    
    print(f"正在列出PDF书签...")
    print(f"  PDF文件: {pdf_path}")
    
    try:
        bookmarks = PDFBookmarksHandler.extract_from_pdf(pdf_path)
        
        if not bookmarks:
            print("警告: 该PDF没有书签")
            return
        
        print(f"找到 {len(bookmarks)} 个顶级书签")
        
        def print_bookmark(bookmark, level=0):
            indent = "  " * level
            page_info = f" (页码: {bookmark.page})" if bookmark.page is not None else ""
            print(f"{indent}+- {bookmark.title}{page_info}")
            
            for child in bookmark.children:
                print_bookmark(child, level + 1)
        
        print("\n书签结构:")
        for bookmark in bookmarks:
            print_bookmark(bookmark)
            
    except Exception as e:
        print(f"失败: 列出书签失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='PDF目录标签处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 提取PDF书签到XML
  python main.py extract document.pdf bookmarks.xml
  
  # 从XML添加书签到PDF
  python main.py add document.pdf bookmarks.xml output.pdf
  
  # 列出PDF书签
  python main.py list document.pdf
  
  # 显示帮助
  python main.py --help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令', required=True)
    
    # 提取命令
    extract_parser = subparsers.add_parser('extract', help='从PDF提取书签到XML')
    extract_parser.add_argument('pdf_file', help='PDF文件路径')
    extract_parser.add_argument('xml_file', help='XML输出文件路径')
    extract_parser.set_defaults(func=extract_command)
    
    # 添加命令
    add_parser = subparsers.add_parser('add', help='从XML添加书签到PDF')
    add_parser.add_argument('pdf_file', help='PDF文件路径')
    add_parser.add_argument('xml_file', help='XML书签文件路径')
    add_parser.add_argument('output_pdf', help='输出PDF文件路径')
    add_parser.set_defaults(func=add_command)
    
    # 列出命令
    list_parser = subparsers.add_parser('list', help='列出PDF书签')
    list_parser.add_argument('pdf_file', help='PDF文件路径')
    list_parser.set_defaults(func=list_command)
    
    args = parser.parse_args()
    
    # 执行对应的命令函数
    args.func(args)


if __name__ == '__main__':
    main()
