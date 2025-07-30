#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验Word文档的实际页数和图片分布
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def analyze_document_structure(docx_path):
    """
    分析文档结构，获取准确的页数和图片分布
    """
    print(f"正在分析文档: {docx_path}")
    print("=" * 60)
    
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # 提取到临时目录
        temp_dir = "temp_verify"
        docx_zip.extractall(temp_dir)
        
        try:
            # 分析document.xml
            document_xml_path = os.path.join(temp_dir, 'word', 'document.xml')
            if not os.path.exists(document_xml_path):
                print("错误：无法找到document.xml文件")
                return
            
            with open(document_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"document.xml 文件大小: {len(content):,} 字符")
            
            # 统计各种元素
            page_breaks = content.count('<w:br w:type="page"')
            page_breaks += content.count('<w:lastRenderedPageBreak')
            section_breaks = content.count('<w:sectPr')
            
            print(f"显式分页符数量: {page_breaks}")
            print(f"章节分隔符数量: {section_breaks}")
            
            # 估算页数（更准确的方法）
            estimated_pages = max(page_breaks + 1, section_breaks)
            
            # 查找所有图片相关标签
            drawing_tags = content.count('<w:drawing')
            pic_tags = content.count('<pic:pic')
            blip_tags = content.count('<a:blip')
            
            print(f"图片绘制标签 (w:drawing): {drawing_tags}")
            print(f"图片标签 (pic:pic): {pic_tags}")
            print(f"图片引用标签 (a:blip): {blip_tags}")
            
            # 检查media文件夹
            media_dir = os.path.join(temp_dir, 'word', 'media')
            if os.path.exists(media_dir):
                media_files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
                print(f"media文件夹中的文件数量: {len(media_files)}")
            else:
                print("未找到media文件夹")
                media_files = []
            
            # 分析文档属性
            app_xml_path = os.path.join(temp_dir, 'docProps', 'app.xml')
            if os.path.exists(app_xml_path):
                with open(app_xml_path, 'r', encoding='utf-8') as f:
                    app_content = f.read()
                
                # 查找页数信息
                pages_match = re.search(r'<Pages>(\d+)</Pages>', app_content)
                if pages_match:
                    actual_pages = int(pages_match.group(1))
                    print(f"文档属性中的页数: {actual_pages} 页")
                else:
                    print("未在文档属性中找到页数信息")
                    actual_pages = None
                
                # 查找字数等其他信息
                words_match = re.search(r'<Words>(\d+)</Words>', app_content)
                if words_match:
                    word_count = int(words_match.group(1))
                    print(f"文档字数: {word_count:,} 字")
            else:
                print("未找到文档属性文件")
                actual_pages = None
            
            print("\n" + "=" * 60)
            print("分析结果:")
            
            if actual_pages:
                print(f"✓ 文档实际页数: {actual_pages} 页")
                if actual_pages >= 188:
                    print(f"✓ 确认文档确实有第188页")
                else:
                    print(f"⚠ 文档只有 {actual_pages} 页，没有第188页")
            else:
                print(f"? 估算页数: 约 {estimated_pages} 页（基于分页符）")
            
            print(f"✓ 图片数量: {len(media_files)} 张")
            
            # 如果文档确实有很多页，重新计算图片分布
            if actual_pages and actual_pages > 100:
                print(f"\n建议的图片分布策略:")
                print(f"- 总图片数: {len(media_files)}")
                print(f"- 总页数: {actual_pages}")
                print(f"- 平均每页图片数: {len(media_files) / actual_pages:.2f}")
                
                # 更合理的分布策略
                if len(media_files) > 0:
                    pages_per_image = actual_pages / len(media_files)
                    print(f"- 平均每 {pages_per_image:.1f} 页有1张图片")
            
        finally:
            # 清理临时目录
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

def main():
    docx_path = "副本《智变时刻：AI重塑HR的未来》20250713_sf.docx"
    
    if not os.path.exists(docx_path):
        print(f"错误：找不到文档文件 {docx_path}")
        return
    
    analyze_document_structure(docx_path)

if __name__ == "__main__":
    main()