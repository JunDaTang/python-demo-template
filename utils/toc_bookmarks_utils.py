#!/usr/bin/env python3
"""
PDF目录标签处理工具类
提供PDF书签的导入、导出功能，支持XML格式
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import pypdf


@dataclass
class PDFBookmarkItem:
    """PDF书签项"""
    title: str
    page: int
    level: int = 1
    children: List['PDFBookmarkItem'] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'page': self.page,
            'level': self.level,
            'attributes': self.attributes,
            'children': [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PDFBookmarkItem':
        """从字典创建"""
        item = cls(
            title=data['title'],
            page=data['page'],
            level=data.get('level', 1),
            attributes=data.get('attributes', {})
        )
        item.children = [cls.from_dict(child) for child in data.get('children', [])]
        return item


class PDFBookmarksHandler:
    """PDF书签处理类"""
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> List[PDFBookmarkItem]:
        """
        从PDF提取书签
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            书签项列表
        """
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                outlines = reader.outline
                
                if not outlines:
                    return []
                
                return PDFBookmarksHandler._parse_pypdf_outline(reader, outlines)
        except Exception as e:
            raise ValueError(f"提取PDF书签失败: {e}")
    
    @staticmethod
    def _parse_pypdf_outline(reader: pypdf.PdfReader, outlines, level: int = 1) -> List[PDFBookmarkItem]:
        """递归解析pypdf大纲结构"""
        bookmarks = []
        i = 0
        
        while i < len(outlines):
            item = outlines[i]
            
            if isinstance(item, list):
                # 嵌套的子目录列表
                if bookmarks:
                    # 如果有父级项目，将这些子项添加为children
                    bookmarks[-1].children.extend(
                        PDFBookmarksHandler._parse_pypdf_outline(reader, item, level + 1)
                    )
                else:
                    # 如果没有父级，直接添加到当前级别
                    bookmarks.extend(
                        PDFBookmarksHandler._parse_pypdf_outline(reader, item, level)
                    )
            else:
                # 单个书签项
                try:
                    title = item.title if hasattr(item, 'title') else "未命名"
                    page = 0
                    
                    # 尝试获取页码 - 使用get_page_number获取页面索引
                    if hasattr(item, 'page') and item.page:
                        try:
                            # 使用reader.get_page_number获取页面索引（从0开始）
                            page_num = reader.get_page_number(item.page)
                            if page_num is not None:
                                page = page_num
                        except Exception:
                            page = 0
                    
                    bookmark = PDFBookmarkItem(
                        title=str(title).strip(),
                        page=page,
                        level=level
                    )
                    
                    bookmarks.append(bookmark)
                    
                    # 检查下一个项目是否是子项列表
                    if i + 1 < len(outlines) and isinstance(outlines[i + 1], list):
                        # 下一个项目是子项列表，递归处理并添加为当前项的children
                        bookmark.children = PDFBookmarksHandler._parse_pypdf_outline(
                            reader, outlines[i + 1], level + 1
                        )
                        i += 1  # 跳过下一个列表项
                
                except Exception as e:
                    # 跳过无法处理的项
                    print(f"警告: 处理书签项时出错: {e}")
            
            i += 1
        
        return bookmarks
    
    @staticmethod
    def export_to_xml(bookmarks: List[PDFBookmarkItem], xml_path: str) -> None:
        """
        导出书签到XML文件
        
        Args:
            bookmarks: 书签项列表
            xml_path: XML文件路径
        """
        root = ET.Element("BOOKMARKS")
        info = ET.SubElement(root, "INFO", PRODUCER="PDF Bookmarks Handler")
        
        for bookmark in bookmarks:
            PDFBookmarksHandler._create_xml_element(bookmark, root)
        
        # 美化XML输出
        from xml.dom import minidom
        xml_str = ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="    ", encoding='utf-8')
        
        with open(xml_path, 'wb') as f:
            f.write(pretty_xml)
    
    @staticmethod
    def _create_xml_element(bookmark: PDFBookmarkItem, parent: ET.Element) -> ET.Element:
        """创建XML元素"""
        # 基础属性
        attrs = {
            'INDENT': str(bookmark.level),
            'PAGE': str(bookmark.page),
            'NAME': bookmark.title,
            'OPEN': '1',
            'FONTSTYLE': '0',
            'COLOR': '4278190080',  # 默认黑色
            'ZOOMMODE': '0',
            'PARMA': '0.000000,0.000000,0.000000,0.000000'
        }
        
        # 合并自定义属性
        attrs.update(bookmark.attributes)
        
        # 创建元素
        elem = ET.SubElement(parent, "ITEM", attrs)
        
        # 递归处理子项
        for child in bookmark.children:
            PDFBookmarksHandler._create_xml_element(child, elem)
        
        return elem
    
    @staticmethod
    def import_from_xml(xml_path: str) -> List[PDFBookmarkItem]:
        """
        从XML文件导入书签
        
        Args:
            xml_path: XML文件路径
            
        Returns:
            书签项列表
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            bookmarks = []
            
            # 处理根目录下的ITEM元素
            for elem in root.findall('ITEM'):
                bookmark = PDFBookmarksHandler._parse_xml_element(elem)
                if bookmark:
                    bookmarks.append(bookmark)
            
            return bookmarks
        except Exception as e:
            raise ValueError(f"导入XML书签失败: {e}")
    
    @staticmethod
    def _parse_xml_element(elem: ET.Element, level: int = 1) -> Optional[PDFBookmarkItem]:
        """解析XML元素"""
        if elem.tag != 'ITEM':
            return None
        
        # 提取属性
        attrs = elem.attrib
        title = attrs.get('NAME', '').strip()
        if not title:
            return None
        
        try:
            page = int(attrs.get('PAGE', '0'))
        except ValueError:
            page = 0
        
        try:
            level = int(attrs.get('INDENT', '1'))
        except ValueError:
            level = 1
        
        # 创建书签项
        bookmark = PDFBookmarkItem(
            title=title,
            page=page,
            level=level,
            attributes=attrs.copy()  # 保存所有原始属性
        )
        
        # 递归处理子项
        for child_elem in elem.findall('ITEM'):
            child = PDFBookmarksHandler._parse_xml_element(child_elem, level + 1)
            if child:
                bookmark.children.append(child)
        
        return bookmark
    
    @staticmethod
    def add_to_pdf(pdf_path: str, bookmarks: List[PDFBookmarkItem], output_path: str) -> None:
        """
        将书签添加到PDF
        
        Args:
            pdf_path: 输入PDF文件路径
            bookmarks: 书签项列表
            output_path: 输出PDF文件路径
        """
        try:
            # 读取PDF
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                writer = pypdf.PdfWriter()
                
                # 复制所有页面
                for page in reader.pages:
                    writer.add_page(page)
                
                # 添加书签
                PDFBookmarksHandler._add_bookmarks_to_writer(writer, bookmarks)
                
                # 写入输出文件
                with open(output_path, 'wb') as out_f:
                    writer.write(out_f)
        
        except Exception as e:
            raise ValueError(f"添加书签到PDF失败: {e}")
    
    @staticmethod
    def _add_bookmarks_to_writer(writer: pypdf.PdfWriter, bookmarks: List[PDFBookmarkItem], 
                                 parent: Optional[Any] = None) -> None:
        """递归添加书签到PdfWriter"""
        for bookmark in bookmarks:
            # 添加书签
            outline = writer.add_outline_item(
                title=bookmark.title,
                page_number=bookmark.page,
                parent=parent
            )
            
            # 递归添加子书签
            if bookmark.children:
                PDFBookmarksHandler._add_bookmarks_to_writer(writer, bookmark.children, outline)


def extract_pdf_bookmarks_to_xml(pdf_path: str, xml_path: str) -> bool:
    """
    从PDF提取书签并保存为XML文件（便捷函数）
    
    Args:
        pdf_path: PDF文件路径
        xml_path: XML输出文件路径
        
    Returns:
        是否成功
    """
    try:
        bookmarks = PDFBookmarksHandler.extract_from_pdf(pdf_path)
        if not bookmarks:
            print("警告：未找到任何书签")
            return False
        
        PDFBookmarksHandler.export_to_xml(bookmarks, xml_path)
        print(f"成功导出 {len(bookmarks)} 个书签到 {xml_path}")
        return True
    
    except Exception as e:
        print(f"错误：{e}")
        return False


def add_bookmarks_from_xml_to_pdf(pdf_path: str, xml_path: str, output_path: str) -> bool:
    """
    从XML文件添加书签到PDF（便捷函数）
    
    Args:
        pdf_path: 输入PDF文件路径
        xml_path: XML书签文件路径
        output_path: 输出PDF文件路径
        
    Returns:
        是否成功
    """
    try:
        bookmarks = PDFBookmarksHandler.import_from_xml(xml_path)
        if not bookmarks:
            print("警告：未找到任何书签")
            return False
        
        PDFBookmarksHandler.add_to_pdf(pdf_path, bookmarks, output_path)
        print(f"成功添加 {len(bookmarks)} 个书签到 {output_path}")
        return True
    
    except Exception as e:
        print(f"错误：{e}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF目录标签处理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 提取命令
    extract_parser = subparsers.add_parser('extract', help='从PDF提取书签到XML')
    extract_parser.add_argument('pdf_file', help='PDF文件路径')
    extract_parser.add_argument('xml_file', help='XML输出文件路径')
    
    # 添加命令
    add_parser = subparsers.add_parser('add', help='从XML添加书签到PDF')
    add_parser.add_argument('pdf_file', help='PDF文件路径')
    add_parser.add_argument('xml_file', help='XML书签文件路径')
    add_parser.add_argument('output_pdf', help='输出PDF文件路径')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        success = extract_pdf_bookmarks_to_xml(args.pdf_file, args.xml_file)
        exit(0 if success else 1)
    
    elif args.command == 'add':
        success = add_bookmarks_from_xml_to_pdf(args.pdf_file, args.xml_file, args.output_pdf)
        exit(0 if success else 1)
    
    else:
        parser.print_help()
        exit(1)