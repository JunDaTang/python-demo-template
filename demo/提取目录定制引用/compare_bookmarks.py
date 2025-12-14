#!/usr/bin/env python3
"""
比较从PDF提取的书签与现有XML文件
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.toc_bookmarks_utils import PDFBookmarksHandler


def compare_bookmarks(pdf_path, xml_path, output_xml_path):
    """
    比较从PDF提取的书签与现有XML文件
    
    Args:
        pdf_path: PDF文件路径
        xml_path: 现有XML文件路径
        output_xml_path: 输出XML文件路径
    """
    print("=== 比较PDF书签与XML文件 ===")
    print(f"PDF文件: {pdf_path}")
    print(f"现有XML: {xml_path}")
    print(f"输出XML: {output_xml_path}")
    
    # 1. 从PDF提取书签
    print("\n1. 从PDF提取书签...")
    try:
        bookmarks = PDFBookmarksHandler.extract_from_pdf(pdf_path)
        print(f"   提取到 {len(bookmarks)} 个顶层书签")
        
        # 统计总书签数
        def count_bookmarks(items):
            total = 0
            for item in items:
                total += 1
                if item.children:
                    total += count_bookmarks(item.children)
            return total
        
        total = count_bookmarks(bookmarks)
        print(f"   总共 {total} 个书签（包含子项）")
        
    except Exception as e:
        print(f"   提取失败: {e}")
        return False
    
    # 2. 导出到XML
    print("\n2. 导出到XML...")
    try:
        PDFBookmarksHandler.export_to_xml(bookmarks, output_xml_path)
        print(f"   已导出到: {output_xml_path}")
    except Exception as e:
        print(f"   导出失败: {e}")
        return False
    
    # 3. 比较两个XML文件
    print("\n3. 比较XML文件...")
    try:
        # 读取现有XML
        with open(xml_path, 'r', encoding='utf-8') as f:
            existing_xml = f.read()
        
        # 读取新生成的XML
        with open(output_xml_path, 'r', encoding='utf-8') as f:
            new_xml = f.read()
        
        # 解析XML进行比较
        existing_tree = ET.parse(xml_path)
        existing_root = existing_tree.getroot()
        
        new_tree = ET.parse(output_xml_path)
        new_root = new_tree.getroot()
        
        # 比较ITEM数量
        existing_items = list(existing_root.iter('ITEM'))
        new_items = list(new_root.iter('ITEM'))
        
        print(f"   现有XML有 {len(existing_items)} 个ITEM元素")
        print(f"   新XML有 {len(new_items)} 个ITEM元素")
        
        if len(existing_items) == len(new_items):
            print("   [OK] ITEM数量匹配")
        else:
            print(f"   [ERROR] ITEM数量不匹配: 相差 {abs(len(existing_items) - len(new_items))}")
        
        # 比较前几个ITEM的属性
        print("\n4. 比较前几个ITEM的属性:")
        for i in range(min(5, len(existing_items), len(new_items))):
            existing_item = existing_items[i]
            new_item = new_items[i]
            
            print(f"\n   第 {i+1} 个ITEM:")
            print(f"     现有: NAME={existing_item.get('NAME')}, PAGE={existing_item.get('PAGE')}, INDENT={existing_item.get('INDENT')}")
            print(f"     新生成: NAME={new_item.get('NAME')}, PAGE={new_item.get('PAGE')}, INDENT={new_item.get('INDENT')}")
            
            # 检查关键属性是否匹配
            name_match = existing_item.get('NAME') == new_item.get('NAME')
            page_match = existing_item.get('PAGE') == new_item.get('PAGE')
            indent_match = existing_item.get('INDENT') == new_item.get('INDENT')
            
            if name_match and page_match and indent_match:
                print("     [OK] 关键属性匹配")
            else:
                print("     [ERROR] 关键属性不匹配")
        
        # 检查文件大小
        existing_size = os.path.getsize(xml_path)
        new_size = os.path.getsize(output_xml_path)
        print(f"\n5. 文件大小比较:")
        print(f"   现有XML: {existing_size} 字节")
        print(f"   新XML: {new_size} 字节")
        
        return True
        
    except Exception as e:
        print(f"   比较失败: {e}")
        return False


def main():
    """主函数"""
    # 文件路径
    pdf_path = r"data\提取目录定制引用\input\资料高考数学基础知识手册.pdf"
    xml_path = "data\提取目录定制引用\input\【书签】资料高考数学基础知识手册.xml"
    output_xml_path = "data/提取目录定制引用/output/从代码生成的书签.xml"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_xml_path), exist_ok=True)
    
    # 执行比较
    success = compare_bookmarks(pdf_path, xml_path, output_xml_path)
    
    if success:
        print("\n=== 比较完成 ===")
        print(f"新生成的XML文件已保存到: {output_xml_path}")
        print("请检查文件内容是否与现有XML一致。")
    else:
        print("\n=== 比较失败 ===")
        sys.exit(1)


if __name__ == '__main__':
    main()