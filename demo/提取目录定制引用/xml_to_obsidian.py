#!/usr/bin/env python3
"""
将PDF书签XML转换为Obsidian引用链接
参考定制模板格式，提取指定INDENT级别的书签
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re
from typing import List, Dict, Tuple, Optional


def parse_xml_bookmarks(xml_path: str) -> List[Dict]:
    """
    解析XML书签文件，返回结构化数据
    
    Args:
        xml_path: XML文件路径
        
    Returns:
        书签项列表，每个项包含name, indent, page, children等信息
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    def parse_element(elem: ET.Element, level: int = 0) -> Dict:
        """递归解析XML元素"""
        item = {
            'name': elem.get('NAME', '').strip(),
            'indent': int(elem.get('INDENT', '1')),
            'page': int(elem.get('PAGE', '0')),
            'children': [],
            'level': level
        }
        
        # 递归处理子元素
        for child_elem in elem.findall('ITEM'):
            child = parse_element(child_elem, level + 1)
            item['children'].append(child)
            
        return item
    
    # 解析所有顶级ITEM
    bookmarks = []
    for elem in root.findall('ITEM'):
        bookmarks.append(parse_element(elem))
    
    return bookmarks


def generate_obsidian_links(bookmarks: List[Dict], target_indents: Optional[List[int]] = None) -> str:
    """
    生成Obsidian引用链接
    
    Args:
        bookmarks: 书签数据
        target_indents: 目标INDENT级别列表，默认为[2, 3]
        
    Returns:
        Obsidian格式的Markdown字符串
    """
    if target_indents is None:
        target_indents = [2, 3]
    
    output_lines = []
    
    def process_items(items: List[Dict], parent_title: str = ""):
        """递归处理书签项"""
        for item in items:
            indent = item['indent']
            name = item['name']
            
            # 生成Obsidian链接名称
            # 清理名称中的特殊字符，替换为连字符
            link_name = re.sub(r'[^\w\s\.\-]', '', name)
            link_name = re.sub(r'\s+', '-', link_name.strip())
            link_name = f"Lit-Book-{link_name}"
            
            if indent == 1:
                # INDENT=1 作为章节标题
                output_lines.append(f"\n## {name}")
                if item['children']:
                    process_items(item['children'], name)
                    
            elif indent in target_indents:
                # INDENT=2或3 作为Obsidian链接
                output_lines.append(f"[[{link_name}]]")
                
                # 如果有子项且子项也是目标INDENT，继续处理
                if item['children']:
                    process_items(item['children'], name)
    
    # 添加标题
    output_lines.append("# Lit-Bub-尚硅谷大模型技术之数学基础1.2.1")
    output_lines.append("")
    
    # 处理所有书签
    process_items(bookmarks)
    
    return "\n".join(output_lines)


def save_obsidian_markdown(content: str, output_path_str: str) -> None:
    """
    保存Obsidian Markdown文件
    
    Args:
        content: Markdown内容
        output_path_str: 输出文件路径
    """
    output_path = Path(output_path_str)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已保存到: {output_path}")
    print(f"文件大小: {output_path.stat().st_size} 字节")


def main():
    """主函数"""
    # 输入输出路径
    xml_path = "data/提取目录定制引用/output/尚硅谷大模型技术之数学基础1.2.1_书签.xml"
    output_path = "data/提取目录定制引用/output/尚硅谷大模型技术之数学基础1.2.1_obsidian.md"
    
    print("=" * 60)
    print("XML转Obsidian引用链接工具")
    print("=" * 60)
    print(f"输入XML: {xml_path}")
    print(f"输出文件: {output_path}")
    print(f"目标INDENT级别: 2, 3")
    
    # 检查输入文件
    if not Path(xml_path).exists():
        print(f"错误: XML文件不存在: {xml_path}")
        return
    
    # 解析XML
    print("\n解析XML书签...")
    bookmarks = parse_xml_bookmarks(xml_path)
    print(f"找到 {len(bookmarks)} 个顶级书签")
    
    # 统计INDENT分布
    indent_counts = {1: 0, 2: 0, 3: 0}
    
    def count_indents(items):
        for item in items:
            indent = item['indent']
            if indent in indent_counts:
                indent_counts[indent] += 1
            if item['children']:
                count_indents(item['children'])
    
    count_indents(bookmarks)
    print(f"INDENT分布: 1级={indent_counts[1]}, 2级={indent_counts[2]}, 3级={indent_counts[3]}")
    
    # 生成Obsidian链接
    print("\n生成Obsidian链接...")
    obsidian_content = generate_obsidian_links(bookmarks, [2, 3])
    
    # 保存文件
    save_obsidian_markdown(obsidian_content, output_path)
    
    # 显示预览
    print("\n预览前20行:")
    lines = obsidian_content.split('\n')
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:3d}: {line}")
    
    print("\n完成!")


if __name__ == '__main__':
    main()