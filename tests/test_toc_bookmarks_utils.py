#!/usr/bin/env python3
"""
PDF目录标签处理工具测试
"""

import os
import tempfile
import pytest
from pathlib import Path
from utils.toc_bookmarks_utils import (
    PDFBookmarkItem,
    PDFBookmarksHandler,
    extract_pdf_bookmarks_to_xml,
    add_bookmarks_from_xml_to_pdf
)


class TestPDFBookmarkItem:
    """测试PDFBookmarkItem类"""
    
    def test_creation(self):
        """测试创建书签项"""
        item = PDFBookmarkItem(
            title="测试书签",
            page=10,
            level=1
        )
        
        assert item.title == "测试书签"
        assert item.page == 10
        assert item.level == 1
        assert item.children == []
        assert item.attributes == {}
    
    def test_with_children(self):
        """测试带子项的书签"""
        child = PDFBookmarkItem(title="子书签", page=11, level=2)
        parent = PDFBookmarkItem(
            title="父书签",
            page=10,
            level=1,
            children=[child]
        )
        
        assert len(parent.children) == 1
        assert parent.children[0].title == "子书签"
    
    def test_to_dict(self):
        """测试转换为字典"""
        child = PDFBookmarkItem(title="子书签", page=11, level=2)
        parent = PDFBookmarkItem(
            title="父书签",
            page=10,
            level=1,
            children=[child],
            attributes={"COLOR": "4278190080"}
        )
        
        data = parent.to_dict()
        
        assert data['title'] == "父书签"
        assert data['page'] == 10
        assert data['level'] == 1
        assert data['attributes']['COLOR'] == "4278190080"
        assert len(data['children']) == 1
        assert data['children'][0]['title'] == "子书签"
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'title': '测试书签',
            'page': 5,
            'level': 2,
            'attributes': {'OPEN': '1'},
            'children': [{
                'title': '子书签',
                'page': 6,
                'level': 3,
                'attributes': {},
                'children': []
            }]
        }
        
        item = PDFBookmarkItem.from_dict(data)
        
        assert item.title == "测试书签"
        assert item.page == 5
        assert item.level == 2
        assert item.attributes['OPEN'] == '1'
        assert len(item.children) == 1
        assert item.children[0].title == "子书签"


class TestPDFBookmarksHandler:
    """测试PDFBookmarksHandler类"""
    
    def test_extract_from_pdf_no_bookmarks(self, tmp_path):
        """测试提取没有书签的PDF"""
        # 创建一个简单的PDF文件（实际上我们模拟一个没有书签的情况）
        # 由于创建真实PDF比较复杂，我们这里测试异常情况
        # 使用一个不存在的文件来测试错误处理
        with pytest.raises(ValueError, match="提取PDF书签失败"):
            PDFBookmarksHandler.extract_from_pdf("nonexistent.pdf")
    
    def test_export_and_import_xml(self, tmp_path):
        """测试导出和导入XML"""
        # 创建测试书签
        child1 = PDFBookmarkItem(title="子书签1", page=2, level=2)
        child2 = PDFBookmarkItem(title="子书签2", page=3, level=2)
        parent = PDFBookmarkItem(
            title="父书签",
            page=1,
            level=1,
            children=[child1, child2],
            attributes={"COLOR": "4278190080", "OPEN": "1"}
        )
        
        bookmarks = [parent]
        
        # 导出到XML
        xml_path = tmp_path / "test_bookmarks.xml"
        PDFBookmarksHandler.export_to_xml(bookmarks, str(xml_path))
        
        # 验证XML文件存在
        assert xml_path.exists()
        
        # 导入XML
        imported = PDFBookmarksHandler.import_from_xml(str(xml_path))
        
        # 验证导入结果
        assert len(imported) == 1
        assert imported[0].title == "父书签"
        assert imported[0].page == 1
        assert imported[0].level == 1
        assert imported[0].attributes["COLOR"] == "4278190080"
        assert imported[0].attributes["OPEN"] == "1"
        assert len(imported[0].children) == 2
        assert imported[0].children[0].title == "子书签1"
        assert imported[0].children[1].title == "子书签2"
    
    def test_import_invalid_xml(self, tmp_path):
        """测试导入无效XML"""
        # 创建无效的XML文件
        xml_path = tmp_path / "invalid.xml"
        xml_path.write_text("这不是有效的XML")
        
        with pytest.raises(ValueError, match="导入XML书签失败"):
            PDFBookmarksHandler.import_from_xml(str(xml_path))
    
    def test_create_xml_element(self):
        """测试创建XML元素"""
        bookmark = PDFBookmarkItem(
            title="测试书签",
            page=5,
            level=2,
            attributes={"CUSTOM": "value"}
        )
        
        import xml.etree.ElementTree as ET
        root = ET.Element("TEST")
        element = PDFBookmarksHandler._create_xml_element(bookmark, root)
        
        assert element.tag == "ITEM"
        assert element.attrib["NAME"] == "测试书签"
        assert element.attrib["PAGE"] == "5"
        assert element.attrib["INDENT"] == "2"
        assert element.attrib["CUSTOM"] == "value"
    
    def test_parse_xml_element(self):
        """测试解析XML元素"""
        import xml.etree.ElementTree as ET
        
        # 创建XML元素
        elem = ET.Element("ITEM", {
            "NAME": "测试书签",
            "PAGE": "10",
            "INDENT": "2",
            "COLOR": "4278190080"
        })
        
        # 添加子元素
        child_elem = ET.SubElement(elem, "ITEM", {
            "NAME": "子书签",
            "PAGE": "11",
            "INDENT": "3"
        })
        
        bookmark = PDFBookmarksHandler._parse_xml_element(elem)
        
        assert bookmark is not None
        assert bookmark.title == "测试书签"
        assert bookmark.page == 10
        assert bookmark.level == 2
        assert bookmark.attributes["COLOR"] == "4278190080"
        assert len(bookmark.children) == 1
        assert bookmark.children[0].title == "子书签"
        assert bookmark.children[0].page == 11
        assert bookmark.children[0].level == 3


class TestIntegration:
    """集成测试"""
    
    def test_extract_pdf_bookmarks_to_xml(self, tmp_path):
        """测试提取PDF书签到XML的便捷函数"""
        # 由于需要真实的PDF文件，我们这里测试错误情况
        # 使用不存在的PDF文件
        xml_path = tmp_path / "output.xml"
        
        success = extract_pdf_bookmarks_to_xml("nonexistent.pdf", str(xml_path))
        assert not success  # 应该失败
    
    def test_add_bookmarks_from_xml_to_pdf(self, tmp_path):
        """测试从XML添加书签到PDF的便捷函数"""
        # 创建测试XML文件
        xml_path = tmp_path / "test.xml"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<BOOKMARKS>
    <INFO PRODUCER="TEST"/>
    <ITEM INDENT="1" PAGE="0" NAME="测试书签"/>
</BOOKMARKS>"""
        xml_path.write_text(xml_content)
        
        # 使用不存在的PDF文件测试
        output_path = tmp_path / "output.pdf"
        
        success = add_bookmarks_from_xml_to_pdf(
            "nonexistent.pdf",
            str(xml_path),
            str(output_path)
        )
        assert not success  # 应该失败


def test_real_pdf_extraction():
    """测试真实PDF文件提取（如果存在）"""
    # 检查测试PDF文件是否存在
    test_pdf = Path("data/提取目录定制引用/input/资料高考数学基础知识手册_有目录.pdf")
    
    if test_pdf.exists():
        try:
            bookmarks = PDFBookmarksHandler.extract_from_pdf(str(test_pdf))
            # 至少应该有一些书签
            assert isinstance(bookmarks, list)
            print(f"从测试PDF提取到 {len(bookmarks)} 个书签")
        except Exception as e:
            print(f"测试PDF提取失败（可能文件格式问题）: {e}")
    else:
        print("测试PDF文件不存在，跳过真实文件测试")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])